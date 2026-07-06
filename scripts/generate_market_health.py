from datetime import date
import json
from pathlib import Path

today = date.today().isoformat()

record = {
    "date": today,
    "market_health_score": None,
    "stance": None,
    "confidence": None,
    "sub_scores": {
        "liquidity": None,
        "credit": None,
        "ai_fundamentals": None,
        "market_breadth": None,
        "valuation_risk": None,
        "macro_risk": None,
        "geopolitical_risk": None
    },
    "indicators": {
        "vix": None,
        "us_10y_yield": None,
        "high_yield_spread": None,
        "nasdaq_100_return": None,
        "sp500_return": None,
        "nvda_return": None,
        "qqq_return": None,
        "smh_return": None
    },
    "prediction": {
        "next_day_bias": None,
        "expected_market": None
    },
    "backtest": {
        "filled_next_day": False,
        "actual_spx_return": None,
        "actual_nasdaq_return": None,
        "actual_nvda_return": None,
        "prediction_correct": None
    }
}

out_dir = Path("data/daily")
out_dir.mkdir(parents=True, exist_ok=True)

out_file = out_dir / f"{today}.json"
out_file.write_text(json.dumps(record, indent=2), encoding="utf-8")

print(f"Created {out_file}")
