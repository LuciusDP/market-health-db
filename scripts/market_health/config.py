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


ASSETS = [
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


SUBSCORE_WEIGHTS = {
    "liquidity": 0.16,
    "credit": 0.16,
    "ai_fundamentals": 0.18,
    "market_breadth": 0.18,
    "valuation_risk": 0.12,
    "macro_risk": 0.12,
    "geopolitical_risk": 0.08,
}

