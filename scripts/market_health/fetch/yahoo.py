from __future__ import annotations

import json
import ssl
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class PricePoint:
    date: str
    close: float
    volume: int | None = None


def fetch_daily_prices(symbol: str, range_: str = "1y") -> list[PricePoint]:
    encoded = urllib.parse.quote(symbol, safe="")
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{encoded}"
        f"?range={range_}&interval=1d&events=history&includeAdjustedClose=true"
    )
    request = urllib.request.Request(url, headers={"User-Agent": "market-health-db/1.0"})
    with urllib.request.urlopen(request, timeout=20, context=_ssl_context()) as response:
        payload = json.loads(response.read().decode("utf-8"))

    result = payload["chart"]["result"][0]
    timestamps = result.get("timestamp") or []
    quote = result["indicators"]["quote"][0]
    closes = quote.get("close") or []
    volumes = quote.get("volume") or []

    points: list[PricePoint] = []
    for index, (timestamp, close) in enumerate(zip(timestamps, closes)):
        if close is None:
            continue
        volume = volumes[index] if index < len(volumes) else None
        day = datetime.fromtimestamp(timestamp).date().isoformat()
        points.append(PricePoint(date=day, close=round(float(close), 6), volume=None if volume is None else int(volume)))
    return points


def _ssl_context() -> ssl.SSLContext:
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:  # noqa: BLE001 - fallback to system trust store.
        return ssl.create_default_context()
