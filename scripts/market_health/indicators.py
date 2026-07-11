from __future__ import annotations

from statistics import mean

from scripts.market_health.utils import pct_change


def _close_series(asset_payload: dict) -> list[float]:
    return [point["close"] for point in asset_payload.get("prices", [])]


def _volume_series(asset_payload: dict) -> list[int | None]:
    return [point.get("volume") for point in asset_payload.get("prices", [])]


def _latest_date(asset_payload: dict) -> str | None:
    prices = asset_payload.get("prices", [])
    return prices[-1]["date"] if prices else None


def _sma(values: list[float], window: int) -> float | None:
    if len(values) < window:
        return None
    return mean(values[-window:])


def _volume_sma(values: list[int | None], window: int) -> float | None:
    available = [value for value in values[-window:] if value is not None]
    if len(available) < window:
        return None
    return mean(available)


def _return(values: list[float], periods: int) -> float | None:
    if len(values) <= periods:
        return None
    return pct_change(values[-1], values[-periods - 1])


def _above_average(latest: float | None, average: float | None) -> bool | None:
    if latest is None or average is None:
        return None
    return latest > average


def build_indicators(market_data: dict) -> dict:
    indicators: dict[str, dict] = {}
    for symbol, payload in market_data["assets"].items():
        closes = _close_series(payload)
        volumes = _volume_series(payload)
        latest = closes[-1] if closes else None
        latest_volume = volumes[-1] if volumes else None
        sma_50 = _sma(closes, 50)
        sma_200 = _sma(closes, 200)
        volume_sma_20 = _volume_sma(volumes, 20)
        indicators[symbol] = {
            "name": payload["name"],
            "group": payload["group"],
            "date": _latest_date(payload),
            "close": latest,
            "volume": latest_volume,
            "volume_sma_20": volume_sma_20,
            "volume_ratio_20d": None if latest_volume is None or volume_sma_20 in (None, 0) else latest_volume / volume_sma_20,
            "return_1d": _return(closes, 1),
            "return_5d": _return(closes, 5),
            "return_20d": _return(closes, 20),
            "return_63d": _return(closes, 63),
            "sma_50": sma_50,
            "sma_200": sma_200,
            "above_50d": _above_average(latest, sma_50),
            "above_200d": _above_average(latest, sma_200),
            "distance_from_50d": pct_change(latest, sma_50),
            "distance_from_200d": pct_change(latest, sma_200),
        }

    indicators["derived"] = {
        "available_symbols": sorted(
            symbol for symbol, value in indicators.items() if symbol != "derived" and value["close"] is not None
        ),
        "unavailable_symbols": sorted(market_data.get("errors", {}).keys()),
    }
    return indicators
