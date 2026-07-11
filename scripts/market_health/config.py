from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
DAILY_DIR = DATA_DIR / "daily"
HISTORY_DIR = DATA_DIR / "history"
BACKTEST_DIR = DATA_DIR / "backtest"
DASHBOARD_DIR = PROJECT_ROOT / "dashboard"
README_PATH = PROJECT_ROOT / "README.md"


@dataclass(frozen=True)
class Asset:
    symbol: str
    name: str
    group: str


BASE_ASSETS = [
    Asset("^GSPC", "S&P 500", "major_index"),
    Asset("^IXIC", "Nasdaq Composite", "major_index"),
    Asset("SPY", "SPDR S&P 500 ETF", "major_etf"),
    Asset("QQQ", "Invesco QQQ ETF", "major_etf"),
    Asset("RSP", "S&P 500 Equal Weight ETF", "breadth"),
    Asset("IWM", "Russell 2000 ETF", "breadth"),
    Asset("SMH", "VanEck Semiconductor ETF", "ai_etf"),
    Asset("SOXX", "iShares Semiconductor ETF", "ai_etf"),
    Asset("HYG", "High Yield Corporate Bond ETF", "credit"),
    Asset("JNK", "High Yield Bond ETF", "credit"),
    Asset("^VIX", "CBOE Volatility Index", "volatility"),
    Asset("^TNX", "US 10Y Treasury Yield", "rates"),
    Asset("DX-Y.NYB", "US Dollar Index", "liquidity"),
    Asset("CL=F", "WTI Crude Oil Futures", "event_risk"),
    Asset("BZ=F", "Brent Crude Oil Futures", "event_risk"),
    Asset("GC=F", "Gold Futures", "safe_haven"),
    Asset("SI=F", "Silver Futures", "safe_haven"),
    Asset("TLT", "20+ Year Treasury Bond ETF", "safe_haven"),
    Asset("XLE", "Energy Select Sector SPDR Fund", "energy"),
    Asset("USO", "United States Oil Fund", "energy"),
    Asset("NVDA", "NVIDIA", "ai_stock"),
    Asset("AMD", "AMD", "ai_stock"),
    Asset("AVGO", "Broadcom", "ai_stock"),
    Asset("TSM", "Taiwan Semiconductor", "ai_stock"),
    Asset("ASML", "ASML", "ai_stock"),
    Asset("MU", "Micron", "ai_stock"),
    Asset("MSFT", "Microsoft", "hyperscaler"),
    Asset("AMZN", "Amazon", "hyperscaler"),
    Asset("META", "Meta", "hyperscaler"),
    Asset("GOOGL", "Alphabet", "hyperscaler"),
    Asset("ORCL", "Oracle", "hyperscaler"),
]

PORTFOLIO_ASSETS = [
    Asset("AMD", "AMD", "portfolio_ai_chip"),
    Asset("AEM", "Agnico Eagle Mines", "portfolio_safe_haven"),
    Asset("BABA", "Alibaba", "portfolio_global_consumer"),
    Asset("AAPL", "Apple", "portfolio_mega_cap"),
    Asset("AIR.PA", "Airbus", "portfolio_travel_industrial"),
    Asset("AENA.MC", "Aena", "portfolio_travel"),
    Asset("BARC.L", "Barclays", "portfolio_uk_financial"),
    Asset("BP.L", "BP", "portfolio_energy"),
    Asset("CRCL", "Circle Internet Group", "portfolio_fintech"),
    Asset("DBK.DE", "Deutsche Bank", "portfolio_eu_financial"),
    Asset("EZJ.L", "easyJet", "portfolio_travel"),
    Asset("GFS", "GlobalFoundries", "portfolio_chip"),
    Asset("IAG.L", "International Consolidated Airlines", "portfolio_travel"),
    Asset("ISP.MI", "Intesa Sanpaolo", "portfolio_eu_financial"),
    Asset("LULU", "Lululemon", "portfolio_consumer"),
    Asset("MKS.L", "Marks and Spencer", "portfolio_uk_consumer"),
    Asset("NDA-FI.HE", "Nordea Bank", "portfolio_eu_financial"),
    Asset("NWG.L", "NatWest Group", "portfolio_financial"),
    Asset("NVTS", "Navitas Semiconductor", "portfolio_ai_chip"),
    Asset("NVDA", "NVIDIA", "portfolio_ai_chip"),
    Asset("ORCL", "Oracle", "portfolio_ai_infra"),
    Asset("PLTR", "Palantir", "portfolio_ai_software"),
    Asset("RYA.IR", "Ryanair", "portfolio_travel"),
    Asset("SGLN.L", "iShares Physical Gold ETC", "portfolio_safe_haven"),
    Asset("SHEL.L", "Shell", "portfolio_energy"),
    Asset("SMCI", "Super Micro Computer", "portfolio_ai_infra"),
    Asset("STM", "STMicroelectronics", "portfolio_chip"),
    Asset("STMPA.PA", "STMicroelectronics Paris", "portfolio_chip"),
    Asset("SWKS", "Skyworks Solutions", "portfolio_chip"),
    Asset("TTE.PA", "TotalEnergies", "portfolio_energy"),
    Asset("TSLA", "Tesla", "portfolio_consumer_ai"),
    Asset("UCG.MI", "UniCredit", "portfolio_eu_financial"),
    Asset("UNH", "UnitedHealth Group", "portfolio_defensive"),
    Asset("UBER", "Uber", "portfolio_consumer_platform"),
]


def _dedupe_assets(*groups: list[Asset]) -> list[Asset]:
    assets: dict[str, Asset] = {}
    for group in groups:
        for asset in group:
            assets.setdefault(asset.symbol, asset)
    return list(assets.values())


ASSETS = _dedupe_assets(BASE_ASSETS, PORTFOLIO_ASSETS)


SUBSCORE_WEIGHTS = {
    "liquidity": 0.16,
    "credit": 0.16,
    "ai_fundamentals": 0.18,
    "market_breadth": 0.18,
    "valuation_risk": 0.12,
    "macro_risk": 0.12,
    "geopolitical_risk": 0.08,
}
