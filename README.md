# market-health-db

Automated market health intelligence database for AI-heavy equity investing.

## Latest Snapshot

- Date: 2026-07-20
- Market Health Score: 54.22
- Risk Regime: Distribution
- Stance: Neutral
- Confidence: 73.38%
- Lifetime Accuracy: 57.14

## Outputs

- Daily records: `data/daily/YYYY-MM-DD.json`
- Score history: `data/history/score_history.json`
- Regime history: `data/history/regime_history.json`
- Prediction accuracy: `data/history/prediction_accuracy.json`
- Score-vs-return validation: `data/history/return_validation.json`
- Dashboard: `dashboard/index.html`

## Automation

The `Daily Market Health` workflow runs four times daily at `06:00`, `11:00`, `15:00`, and `19:00` UTC. During UK summer time this maps to 07:00, 12:00, 16:00, and 20:00 London time. It can also be run manually from GitHub Actions.

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
