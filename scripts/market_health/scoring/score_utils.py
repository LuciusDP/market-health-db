from __future__ import annotations

from scripts.market_health.utils import clamp, mean


def score_return(value: float | None, bullish_threshold: float, bearish_threshold: float) -> float:
    if value is None:
        return 50.0
    if value >= bullish_threshold:
        return 90.0
    if value <= bearish_threshold:
        return 20.0
    span = bullish_threshold - bearish_threshold
    return clamp(20.0 + ((value - bearish_threshold) / span) * 70.0)


def score_lower_is_better(value: float | None, good: float, bad: float) -> float:
    if value is None:
        return 50.0
    if value <= good:
        return 90.0
    if value >= bad:
        return 15.0
    return clamp(90.0 - ((value - good) / (bad - good)) * 75.0)


def score_higher_is_better(value: float | None, good: float, bad: float) -> float:
    if value is None:
        return 50.0
    if value >= good:
        return 90.0
    if value <= bad:
        return 15.0
    return clamp(15.0 + ((value - bad) / (good - bad)) * 75.0)


def average_score(values: list[float | None]) -> float:
    return round(mean(values) or 50.0, 2)


def bool_score(value: bool | None) -> float:
    if value is None:
        return 50.0
    return 80.0 if value else 25.0

