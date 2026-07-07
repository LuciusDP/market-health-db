# market-health-db

Automated market health intelligence database for AI-heavy equity investing.

## Latest Snapshot

- Date: 2026-07-07
- Market Health Score: 67.9
- Risk Regime: Late Cycle
- Stance: Neutral
- Confidence: 84.32%
- Lifetime Accuracy: 0.0

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
- score thresholds and AI portfolio action bands
- subscore explanations and source indicator evidence
- daily market, AI, and macro headlines from public RSS sources
- lifetime prediction accuracy once backtests accumulate
- recent score history

## Backtesting

Each daily run evaluates the previous daily record when a newer trading session is available. The first record will not show accuracy until at least one later run has created a next-session comparison.

## GitHub Pages

The `Deploy Dashboard` workflow publishes the `dashboard/` folder through GitHub Pages.

## Design Notes

See `docs/market-health-intelligence-engine.md` for the long-term system vision.
