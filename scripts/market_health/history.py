from __future__ import annotations

from scripts.market_health.config import DAILY_DIR, HISTORY_DIR
from scripts.market_health.utils import read_json, write_json


def _records() -> list[dict]:
    records: list[dict] = []
    for path in sorted(DAILY_DIR.glob("*.json")):
        records.append(read_json(path, {}))
    return records


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

    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    write_json(HISTORY_DIR / "score_history.json", score_history)
    write_json(HISTORY_DIR / "regime_history.json", regime_history)
    write_json(HISTORY_DIR / "prediction_accuracy.json", prediction_accuracy)
    return {
        "score_history": score_history,
        "regime_history": regime_history,
        "prediction_accuracy": prediction_accuracy,
    }

