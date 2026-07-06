from __future__ import annotations

from scripts.market_health.scoring.score_utils import (
    average_score,
    bool_score,
    score_higher_is_better,
    score_lower_is_better,
    score_return,
)
from scripts.market_health.utils import mean


def _value(indicators: dict, symbol: str, field: str) -> float | bool | None:
    return indicators.get(symbol, {}).get(field)


def _basket(indicators: dict, symbols: list[str], field: str) -> list[float | None]:
    return [_value(indicators, symbol, field) for symbol in symbols]


def score_liquidity(indicators: dict) -> tuple[float, list[str]]:
    score = average_score(
        [
            score_lower_is_better(_value(indicators, "^VIX", "close"), good=14, bad=32),
            score_return(_value(indicators, "DX-Y.NYB", "return_20d"), bullish_threshold=-2, bearish_threshold=3),
            bool_score(_value(indicators, "SPY", "above_50d")),
            bool_score(_value(indicators, "QQQ", "above_50d")),
        ]
    )
    return score, [
        "Liquidity proxy uses VIX, dollar trend, and SPY/QQQ 50-day trend.",
        "Higher score means calmer volatility and easier risk conditions.",
    ]


def score_credit(indicators: dict) -> tuple[float, list[str]]:
    score = average_score(
        [
            score_return(_value(indicators, "HYG", "return_20d"), bullish_threshold=1.5, bearish_threshold=-3),
            score_return(_value(indicators, "JNK", "return_20d"), bullish_threshold=1.5, bearish_threshold=-3),
            bool_score(_value(indicators, "HYG", "above_50d")),
            bool_score(_value(indicators, "JNK", "above_50d")),
        ]
    )
    return score, [
        "Credit proxy uses HYG/JNK performance and trend.",
        "Weak high-yield bonds usually warn before equity stress becomes obvious.",
    ]


def score_ai_fundamentals(indicators: dict) -> tuple[float, list[str]]:
    ai_symbols = ["NVDA", "AMD", "AVGO", "TSM", "ASML", "MU", "SMH", "SOXX"]
    trend_score = average_score([bool_score(_value(indicators, symbol, "above_50d")) for symbol in ai_symbols])
    momentum_score = average_score(
        [score_return(value, bullish_threshold=8, bearish_threshold=-10) for value in _basket(indicators, ai_symbols, "return_20d")]
    )
    score = average_score([trend_score, momentum_score])
    return score, [
        "AI fundamentals proxy uses semiconductor and AI infrastructure equity trends.",
        "This is a market-implied proxy until earnings, CapEx, and funding data are added.",
    ]


def score_market_breadth(indicators: dict) -> tuple[float, list[str]]:
    symbols = ["SPY", "QQQ", "RSP", "IWM"]
    above_50 = average_score([bool_score(_value(indicators, symbol, "above_50d")) for symbol in symbols])
    above_200 = average_score([bool_score(_value(indicators, symbol, "above_200d")) for symbol in symbols])
    momentum = average_score(
        [score_return(value, bullish_threshold=4, bearish_threshold=-6) for value in _basket(indicators, symbols, "return_20d")]
    )
    score = average_score([above_50, above_200, momentum])
    return score, [
        "Breadth proxy compares cap-weighted, equal-weight, Nasdaq, and small-cap trends.",
        "Healthy markets should not depend on only a tiny set of mega-cap winners.",
    ]


def score_valuation_risk(indicators: dict) -> tuple[float, list[str]]:
    stretches = _basket(indicators, ["SPY", "QQQ", "SMH", "NVDA"], "distance_from_200d")
    valid_stretches = [value for value in stretches if isinstance(value, (int, float))]
    average_stretch = mean(valid_stretches) if valid_stretches else None
    score = score_lower_is_better(average_stretch, good=8, bad=35)
    return round(score, 2), [
        "Valuation risk proxy uses distance above 200-day trend.",
        "Very extended leadership can still rise, but forward risk/reward becomes less forgiving.",
    ]


def score_macro_risk(indicators: dict) -> tuple[float, list[str]]:
    ten_year = _value(indicators, "^TNX", "close")
    ten_year_20d = _value(indicators, "^TNX", "return_20d")
    score = average_score(
        [
            score_lower_is_better(ten_year, good=35, bad=55),
            score_lower_is_better(ten_year_20d, good=-4, bad=15),
            score_lower_is_better(_value(indicators, "DX-Y.NYB", "return_20d"), good=-1, bad=4),
        ]
    )
    return score, [
        "Macro risk proxy uses Treasury yield pressure and dollar strength.",
        "Dedicated CPI, payrolls, ISM, and FOMC event modules can be layered in later.",
    ]


def score_geopolitical_risk(indicators: dict) -> tuple[float, list[str]]:
    vix_score = score_lower_is_better(_value(indicators, "^VIX", "close"), good=16, bad=35)
    spy_shock = score_return(_value(indicators, "SPY", "return_5d"), bullish_threshold=2, bearish_threshold=-5)
    score = average_score([vix_score, spy_shock])
    return score, [
        "Geopolitical risk proxy uses volatility and short-term market shock behavior.",
        "News-quality event detection should be added only from credible sources.",
    ]


def build_subscores(indicators: dict) -> dict:
    scoring_functions = {
        "liquidity": score_liquidity,
        "credit": score_credit,
        "ai_fundamentals": score_ai_fundamentals,
        "market_breadth": score_market_breadth,
        "valuation_risk": score_valuation_risk,
        "macro_risk": score_macro_risk,
        "geopolitical_risk": score_geopolitical_risk,
    }
    result: dict[str, dict] = {}
    for name, func in scoring_functions.items():
        score, reasoning = func(indicators)
        result[name] = {"score": score, "reasoning": reasoning}
    return result

