from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.market_health.pipeline import run


if __name__ == "__main__":
    result = run()
    record = result["record"]
    print(f"Created {result['output_path']}")
    print(
        "Score: "
        f"{record['market_health_score']} | "
        f"Regime: {record['risk_regime']} | "
        f"Stance: {record['stance']} | "
        f"Confidence: {record['confidence']}%"
    )
