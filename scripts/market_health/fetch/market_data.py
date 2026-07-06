from __future__ import annotations

from scripts.market_health.config import ASSETS
from scripts.market_health.fetch.yahoo import fetch_daily_prices


def collect_market_data() -> dict:
    assets: dict[str, dict] = {}
    errors: dict[str, str] = {}

    for asset in ASSETS:
        try:
            prices = fetch_daily_prices(asset.symbol)
            assets[asset.symbol] = {
                "name": asset.name,
                "group": asset.group,
                "source": "yahoo_chart",
                "prices": [price.__dict__ for price in prices],
            }
        except Exception as exc:  # noqa: BLE001 - keep daily workflow alive.
            assets[asset.symbol] = {
                "name": asset.name,
                "group": asset.group,
                "source": "yahoo_chart",
                "prices": [],
            }
            errors[asset.symbol] = str(exc)

    return {"assets": assets, "errors": errors}

