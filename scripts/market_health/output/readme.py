from __future__ import annotations

from scripts.market_health.config import README_PATH


def update_readme(record: dict, history: dict) -> None:
    accuracy = history.get("prediction_accuracy", {})
    content = f"""# market-health-db

Automated market health intelligence database for AI-heavy equity investing.

## Latest Snapshot

- Date: {record.get("date")}
- Market Health Score: {record.get("market_health_score")}
- Risk Regime: {record.get("risk_regime")}
- Stance: {record.get("stance")}
- Confidence: {record.get("confidence")}%
- Lifetime Accuracy: {accuracy.get("accuracy")}

## Outputs

- Daily records: `data/daily/YYYY-MM-DD.json`
- Score history: `data/history/score_history.json`
- Regime history: `data/history/regime_history.json`
- Prediction accuracy: `data/history/prediction_accuracy.json`
- Dashboard: `dashboard/index.html`

## GitHub Pages

The `Deploy Dashboard` workflow publishes the `dashboard/` folder through GitHub Pages.

## Design Notes

See `docs/market-health-intelligence-engine.md` for the long-term system vision.
"""
    README_PATH.write_text(content, encoding="utf-8")
