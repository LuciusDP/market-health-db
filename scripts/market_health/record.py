from __future__ import annotations

from scripts.market_health.utils import utc_now_iso


def build_daily_record(today: str, indicators: dict, scores: dict, fetch_errors: dict) -> dict:
    return {
        "date": today,
        "market_health_score": scores["market_health_score"],
        "risk_regime": scores["risk_regime"],
        "stance": scores["prediction"],
        "confidence": scores["confidence"],
        "sub_scores": scores["subscores"],
        "indicators": indicators,
        "prediction": {
            "stance": scores["prediction"],
            "expected_market": scores["risk_regime"],
            "next_day_bias": scores["prediction"],
            "confidence": scores["confidence"],
        },
        "reasoning": [
            "Score is a weighted blend of liquidity, credit, AI fundamentals, breadth, valuation, macro, and geopolitical proxies.",
            "Each subscore uses stable, explainable market-derived indicators so records remain comparable over time.",
        ],
        "backtest": {
            "filled_next_day": False,
            "actual_sp500_return": None,
            "actual_nasdaq_return": None,
            "actual_nvda_return": None,
            "actual_soxx_return": None,
            "actual_vix_return": None,
            "prediction_correct": None,
        },
        "metadata": {
            "engine_version": "1.0",
            "generated_at": utc_now_iso(),
            "data_source": "Yahoo Finance chart endpoint",
            "fetch_errors": fetch_errors,
        },
    }

