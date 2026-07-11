from __future__ import annotations

from pathlib import Path

from scripts.market_health.config import DAILY_DIR
from scripts.market_health.utils import pct_change, read_json, write_json


def _prediction_correct(prediction: str | None, spy_return: float | None) -> bool | None:
    if prediction is None or spy_return is None:
        return None
    if prediction == "Bullish":
        return spy_return > 0
    if prediction == "Neutral":
        return abs(spy_return) <= 0.5
    if prediction == "Cautious":
        return spy_return >= -0.75
    if prediction == "Defensive":
        return spy_return < 0
    return None


def _expected_return_from_score(score: float | int | None) -> float | None:
    if score is None:
        return None
    # One-day expected SPY bias in percentage points. This keeps 64 meaning
    # modestly better than 50, and 68 slightly stronger than 64.
    return round(max(-2.0, min(2.0, (float(score) - 50.0) * 0.04)), 2)


def _score_bucket(score: float | int | None) -> str | None:
    if score is None:
        return None
    if score >= 75:
        return "75-100"
    if score >= 60:
        return "60-74"
    if score >= 45:
        return "45-59"
    if score >= 30:
        return "30-44"
    return "0-29"


def _direction_correct(score: float | int | None, actual_return: float | None) -> bool | None:
    if score is None or actual_return is None:
        return None
    if score >= 60:
        return actual_return > 0
    if score <= 45:
        return actual_return < 0
    return abs(actual_return) <= 0.5


def _daily_files() -> list[Path]:
    return sorted(DAILY_DIR.glob("*.json"))


def _next_session_return(market_data: dict | None, symbol: str, after_date: str | None) -> tuple[float | None, str | None]:
    if not market_data or not after_date:
        return None, None
    prices = market_data.get("assets", {}).get(symbol, {}).get("prices", [])
    for index, point in enumerate(prices):
        if point.get("date") <= after_date or index == 0:
            continue
        previous = prices[index - 1]
        return pct_change(point.get("close"), previous.get("close")), point.get("date")
    return None, None


def backfill_previous_record(today: str, indicators: dict, market_data: dict | None = None) -> dict | None:
    files = [path for path in _daily_files() if path.stem < today]
    if not files:
        return None

    previous_path = files[-1]
    previous = read_json(previous_path, {})
    backtest = previous.setdefault("backtest", {})
    if backtest.get("filled_next_day"):
        return backtest

    previous_date = previous.get("date")
    spy_return, evaluated_on = _next_session_return(market_data, "SPY", previous_date)
    qqq_return, _ = _next_session_return(market_data, "QQQ", previous_date)
    nvda_return, _ = _next_session_return(market_data, "NVDA", previous_date)
    soxx_return, _ = _next_session_return(market_data, "SOXX", previous_date)
    vix_return, _ = _next_session_return(market_data, "^VIX", previous_date)
    if spy_return is None:
        spy_return = indicators.get("SPY", {}).get("return_1d")
        qqq_return = indicators.get("QQQ", {}).get("return_1d")
        nvda_return = indicators.get("NVDA", {}).get("return_1d")
        soxx_return = indicators.get("SOXX", {}).get("return_1d")
        vix_return = indicators.get("^VIX", {}).get("return_1d")
        evaluated_on = today
    prediction = previous.get("prediction", {}).get("stance") or previous.get("stance")
    previous_score = previous.get("market_health_score")
    expected_spy_return = _expected_return_from_score(previous_score)
    if spy_return is None:
        return backtest

    backtest.update(
        {
            "filled_next_day": True,
            "evaluated_on": evaluated_on,
            "actual_sp500_return": spy_return,
            "actual_nasdaq_return": qqq_return,
            "actual_nvda_return": nvda_return,
            "actual_soxx_return": soxx_return,
            "actual_vix_return": vix_return,
            "score_at_prediction": previous_score,
            "score_bucket": _score_bucket(previous_score),
            "expected_sp500_return": expected_spy_return,
            "sp500_return_error": None if expected_spy_return is None else round(spy_return - expected_spy_return, 4),
            "direction_correct": _direction_correct(previous_score, spy_return),
            "prediction_correct": _prediction_correct(prediction, spy_return),
            "evaluation_notes": [
                "Prediction is evaluated against next-session SPY return and stored as a continuous score-vs-return record.",
                "Neutral is correct when SPY is roughly flat; Cautious is correct when downside is contained.",
            ],
        }
    )
    write_json(previous_path, previous)
    return backtest
