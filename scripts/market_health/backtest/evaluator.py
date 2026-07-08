from __future__ import annotations

from pathlib import Path

from scripts.market_health.config import DAILY_DIR
from scripts.market_health.utils import read_json, write_json


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


def _daily_files() -> list[Path]:
    return sorted(DAILY_DIR.glob("*.json"))


def backfill_previous_record(today: str, indicators: dict) -> dict | None:
    files = [path for path in _daily_files() if path.stem < today]
    if not files:
        return None

    previous_path = files[-1]
    previous = read_json(previous_path, {})
    backtest = previous.setdefault("backtest", {})
    if backtest.get("filled_next_day"):
        return backtest

    spy_return = indicators.get("SPY", {}).get("return_1d")
    qqq_return = indicators.get("QQQ", {}).get("return_1d")
    nvda_return = indicators.get("NVDA", {}).get("return_1d")
    soxx_return = indicators.get("SOXX", {}).get("return_1d")
    vix_return = indicators.get("^VIX", {}).get("return_1d")
    prediction = previous.get("prediction", {}).get("stance") or previous.get("stance")
    if spy_return is None:
        return backtest

    backtest.update(
        {
            "filled_next_day": True,
            "evaluated_on": today,
            "actual_sp500_return": spy_return,
            "actual_nasdaq_return": qqq_return,
            "actual_nvda_return": nvda_return,
            "actual_soxx_return": soxx_return,
            "actual_vix_return": vix_return,
            "prediction_correct": _prediction_correct(prediction, spy_return),
            "evaluation_notes": [
                "Prediction is evaluated primarily against next-session SPY return.",
                "Neutral is correct when SPY is roughly flat; Cautious is correct when downside is contained.",
            ],
        }
    )
    write_json(previous_path, previous)
    return backtest
