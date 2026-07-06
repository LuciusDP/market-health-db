from __future__ import annotations

from scripts.market_health.backtest.evaluator import backfill_previous_record
from scripts.market_health.config import DAILY_DIR
from scripts.market_health.fetch.market_data import collect_market_data
from scripts.market_health.history import rebuild_history
from scripts.market_health.indicators import build_indicators
from scripts.market_health.output.dashboard import generate_dashboard
from scripts.market_health.output.readme import update_readme
from scripts.market_health.record import build_daily_record
from scripts.market_health.scoring.engine import calculate_scores
from scripts.market_health.utils import today_iso, write_json


def run(today: str | None = None) -> dict:
    target_date = today or today_iso()
    market_data = collect_market_data()
    indicators = build_indicators(market_data)
    scores = calculate_scores(indicators)
    backfill_previous_record(target_date, indicators)

    record = build_daily_record(target_date, indicators, scores, market_data.get("errors", {}))
    output_path = DAILY_DIR / f"{target_date}.json"
    write_json(output_path, record)

    history = rebuild_history()
    generate_dashboard(record, history)
    update_readme(record, history)

    return {"record": record, "output_path": str(output_path), "history": history}

