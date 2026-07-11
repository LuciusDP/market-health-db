from __future__ import annotations

from scripts.market_health.config import DAILY_DIR, HISTORY_DIR
from scripts.market_health.utils import read_json, write_json


def _records() -> list[dict]:
    records: list[dict] = []
    for path in sorted(DAILY_DIR.glob("*.json")):
        records.append(read_json(path, {}))
    return records


def _avg(values: list[float]) -> float | None:
    if not values:
        return None
    return round(sum(values) / len(values), 4)


def _correlation(pairs: list[tuple[float, float]]) -> float | None:
    if len(pairs) < 3:
        return None
    xs = [pair[0] for pair in pairs]
    ys = [pair[1] for pair in pairs]
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in pairs)
    denominator_x = sum((x - mean_x) ** 2 for x in xs)
    denominator_y = sum((y - mean_y) ** 2 for y in ys)
    if denominator_x == 0 or denominator_y == 0:
        return None
    return round(numerator / ((denominator_x * denominator_y) ** 0.5), 4)


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


def _expected_return_from_score(score: float | int | None) -> float | None:
    if score is None:
        return None
    return round(max(-2.0, min(2.0, (float(score) - 50.0) * 0.04)), 2)


def _direction_correct(score: float | int | None, actual_return: float | None) -> bool | None:
    if score is None or actual_return is None:
        return None
    if score >= 60:
        return actual_return > 0
    if score <= 45:
        return actual_return < 0
    return abs(actual_return) <= 0.5


def _return_error(score: float | int | None, actual_return: float | None) -> float | None:
    expected = _expected_return_from_score(score)
    if expected is None or actual_return is None:
        return None
    return round(actual_return - expected, 4)


def _return_validation(records: list[dict]) -> dict:
    evaluated = [
        record for record in records
        if record.get("backtest", {}).get("actual_sp500_return") is not None
        and record.get("market_health_score") is not None
    ]
    buckets: dict[str, list[dict]] = {}
    for record in evaluated:
        bucket = record.get("backtest", {}).get("score_bucket") or _score_bucket(record.get("market_health_score")) or "unknown"
        buckets.setdefault(bucket, []).append(record)

    bucket_rows = []
    for bucket in ["75-100", "60-74", "45-59", "30-44", "0-29", "unknown"]:
        rows = buckets.get(bucket, [])
        if not rows:
            continue
        spy_returns = [row["backtest"]["actual_sp500_return"] for row in rows if row["backtest"].get("actual_sp500_return") is not None]
        qqq_returns = [row["backtest"]["actual_nasdaq_return"] for row in rows if row["backtest"].get("actual_nasdaq_return") is not None]
        nvda_returns = [row["backtest"]["actual_nvda_return"] for row in rows if row["backtest"].get("actual_nvda_return") is not None]
        soxx_returns = [row["backtest"]["actual_soxx_return"] for row in rows if row["backtest"].get("actual_soxx_return") is not None]
        bucket_rows.append(
            {
                "bucket": bucket,
                "count": len(rows),
                "avg_sp500_return": _avg(spy_returns),
                "avg_nasdaq_return": _avg(qqq_returns),
                "avg_nvda_return": _avg(nvda_returns),
                "avg_soxx_return": _avg(soxx_returns),
                "positive_sp500_rate": round(sum(1 for value in spy_returns if value > 0) / len(spy_returns) * 100, 2) if spy_returns else None,
            }
        )

    def pairs_for(field: str) -> list[tuple[float, float]]:
        return [
            (float(record["market_health_score"]), float(record["backtest"][field]))
            for record in evaluated
            if record.get("backtest", {}).get(field) is not None
        ]

    return {
        "total_return_evaluated": len(evaluated),
        "score_to_sp500_correlation": _correlation(pairs_for("actual_sp500_return")),
        "score_to_nasdaq_correlation": _correlation(pairs_for("actual_nasdaq_return")),
        "score_to_nvda_correlation": _correlation(pairs_for("actual_nvda_return")),
        "score_to_soxx_correlation": _correlation(pairs_for("actual_soxx_return")),
        "bucket_performance": bucket_rows,
        "records": [
            {
                "date": record.get("date"),
                "score": record.get("market_health_score"),
                "bucket": record.get("backtest", {}).get("score_bucket") or _score_bucket(record.get("market_health_score")),
                "expected_sp500_return": record.get("backtest", {}).get("expected_sp500_return") or _expected_return_from_score(record.get("market_health_score")),
                "actual_sp500_return": record.get("backtest", {}).get("actual_sp500_return"),
                "actual_nasdaq_return": record.get("backtest", {}).get("actual_nasdaq_return"),
                "actual_nvda_return": record.get("backtest", {}).get("actual_nvda_return"),
                "actual_soxx_return": record.get("backtest", {}).get("actual_soxx_return"),
                "sp500_return_error": record.get("backtest", {}).get("sp500_return_error")
                if record.get("backtest", {}).get("sp500_return_error") is not None
                else _return_error(record.get("market_health_score"), record.get("backtest", {}).get("actual_sp500_return")),
                "direction_correct": record.get("backtest", {}).get("direction_correct")
                if record.get("backtest", {}).get("direction_correct") is not None
                else _direction_correct(record.get("market_health_score"), record.get("backtest", {}).get("actual_sp500_return")),
            }
            for record in evaluated
        ],
    }


def rebuild_history() -> dict:
    records = _records()
    score_history = [
        {
            "date": record.get("date"),
            "market_health_score": record.get("market_health_score"),
            "risk_regime": record.get("risk_regime"),
            "stance": record.get("stance"),
            "confidence": record.get("confidence"),
        }
        for record in records
        if record.get("date")
    ]

    regime_history = [
        {"date": row["date"], "risk_regime": row["risk_regime"]}
        for row in score_history
        if row.get("risk_regime")
    ]

    evaluated = [
        record
        for record in records
        if record.get("backtest", {}).get("prediction_correct") is not None
    ]
    correct = sum(1 for record in evaluated if record["backtest"]["prediction_correct"])
    total = len(evaluated)
    prediction_accuracy = {
        "total_evaluated": total,
        "correct": correct,
        "wrong": total - correct,
        "accuracy": round((correct / total) * 100, 2) if total else None,
        "records": [
            {
                "date": record.get("date"),
                "stance": record.get("stance"),
                "confidence": record.get("confidence"),
                "prediction_correct": record.get("backtest", {}).get("prediction_correct"),
                "actual_sp500_return": record.get("backtest", {}).get("actual_sp500_return"),
            }
            for record in evaluated
        ],
    }
    return_validation = _return_validation(records)

    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    write_json(HISTORY_DIR / "score_history.json", score_history)
    write_json(HISTORY_DIR / "regime_history.json", regime_history)
    write_json(HISTORY_DIR / "prediction_accuracy.json", prediction_accuracy)
    write_json(HISTORY_DIR / "return_validation.json", return_validation)
    return {
        "score_history": score_history,
        "regime_history": regime_history,
        "prediction_accuracy": prediction_accuracy,
        "return_validation": return_validation,
    }
