from __future__ import annotations

from scripts.market_health.config import ASSETS, SUBSCORE_WEIGHTS
from scripts.market_health.scoring.regime import (
    classify_regime,
    confidence_from_score,
    prediction_from_score,
)
from scripts.market_health.scoring.subscores import build_subscores


def calculate_scores(indicators: dict) -> dict:
    subscores = build_subscores(indicators)
    weighted_score = 0.0
    for name, weight in SUBSCORE_WEIGHTS.items():
        weighted_score += subscores[name]["score"] * weight

    available_symbols = len(indicators["derived"]["available_symbols"])
    total_symbols = len(ASSETS)
    market_health_score = round(weighted_score, 2)
    return {
        "market_health_score": market_health_score,
        "risk_regime": classify_regime(market_health_score),
        "prediction": prediction_from_score(market_health_score),
        "confidence": confidence_from_score(market_health_score, available_symbols, total_symbols),
        "subscores": subscores,
        "weights": SUBSCORE_WEIGHTS,
    }

