from __future__ import annotations

from scripts.market_health.backtest.evaluator import backfill_previous_record
from scripts.market_health.config import DAILY_DIR
from scripts.market_health.fetch.market_data import collect_market_data
from scripts.market_health.fetch.news import collect_headlines
from scripts.market_health.history import rebuild_history
from scripts.market_health.indicators import build_indicators
from scripts.market_health.output.dashboard import generate_dashboard
from scripts.market_health.output.readme import update_readme
from scripts.market_health.record import build_daily_record
from scripts.market_health.scoring.engine import calculate_scores
from scripts.market_health.utils import today_iso, write_json


def _record_date(today: str | None, indicators: dict) -> str:
    if today:
        return today
    return indicators.get("SPY", {}).get("date") or today_iso()


def run(today: str | None = None) -> dict:
    market_data = collect_market_data()
    news = collect_headlines()
    indicators = build_indicators(market_data)
    target_date = _record_date(today, indicators)
    scores = calculate_scores(indicators)
    backfill_previous_record(target_date, indicators, market_data)

    record = build_daily_record(target_date, indicators, scores, market_data.get("errors", {}), news)
    output_path = DAILY_DIR / f"{target_date}.json"
    write_json(output_path, record)

    history = rebuild_history()
    generate_dashboard(record, history)
    update_readme(record, history)

    return {"record": record, "output_path": str(output_path), "history": history}
