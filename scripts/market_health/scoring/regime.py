from __future__ import annotations


def classify_regime(score: float) -> str:
    if score >= 80:
        return "Healthy Bull"
    if score >= 68:
        return "Expansion"
    if score >= 55:
        return "Late Cycle"
    if score >= 42:
        return "Distribution"
    if score >= 28:
        return "High Risk"
    return "Crash Watch"


def prediction_from_score(score: float) -> str:
    if score >= 70:
        return "Bullish"
    if score >= 52:
        return "Neutral"
    if score >= 35:
        return "Cautious"
    return "Defensive"


def confidence_from_score(score: float, available_symbols: int, total_symbols: int) -> float:
    distance = abs(score - 50)
    data_quality = available_symbols / total_symbols if total_symbols else 0
    confidence = 45 + distance * 0.8 + data_quality * 25
    return round(max(0, min(95, confidence)), 2)

