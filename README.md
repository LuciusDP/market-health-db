# market-health-db

Automated market health intelligence database for AI-heavy equity investing.

## Latest Snapshot

- Date: 2026-07-06
- Market Health Score: 68.52
- Risk Regime: Expansion
- Stance: Neutral
- Confidence: 84.82%
- Lifetime Accuracy: None

## Outputs

- Daily records: `data/daily/YYYY-MM-DD.json`
- Score history: `data/history/score_history.json`
- Regime history: `data/history/regime_history.json`
- Prediction accuracy: `data/history/prediction_accuracy.json`
- Dashboard: `dashboard/index.html`

## Automation

The `Daily Market Health` workflow runs at `07:00 UTC` every Monday through Friday and can also be run manually from GitHub Actions.

## Dashboard Contents

The dashboard includes:

- top-level Market Health Score, Risk Regime, stance, and confidence
- subscore explanations and source indicator evidence
- daily market, AI, and macro headlines from public RSS sources
- lifetime prediction accuracy once backtests accumulate
- recent score history

## GitHub Pages

The `Deploy Dashboard` workflow publishes the `dashboard/` folder through GitHub Pages.

## Design Notes

See `docs/market-health-intelligence-engine.md` for the long-term system vision.
