from __future__ import annotations

from html import escape

from scripts.market_health.config import DASHBOARD_DIR


def _bar(value: float | None) -> str:
    score = 0 if value is None else max(0, min(100, int(round(value))))
    return f"<div class='bar'><span style='width:{score}%'></span></div>"


def _fmt(value: float | int | None, suffix: str = "") -> str:
    if value is None:
        return "n/a"
    return f"{value}{suffix}"


def generate_dashboard(record: dict, history: dict) -> None:
    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
    subscores = record.get("sub_scores", {})
    score_history = history.get("score_history", [])[-180:]
    accuracy = history.get("prediction_accuracy", {})
    points = ", ".join(
        f"{row.get('date')}: {_fmt(row.get('market_health_score'))}"
        for row in score_history[-30:]
    )
    subscore_cards = "\n".join(
        f"""
        <section class="card">
          <div class="label">{escape(name.replace("_", " ").title())}</div>
          <strong>{_fmt(payload.get("score"))}</strong>
          {_bar(payload.get("score"))}
        </section>
        """
        for name, payload in subscores.items()
    )

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Market Health Dashboard</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #17202a; background: #f6f7f9; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 32px 20px 48px; }}
    header {{ display: flex; justify-content: space-between; gap: 20px; align-items: flex-start; margin-bottom: 24px; }}
    h1 {{ margin: 0 0 8px; font-size: 32px; }}
    h2 {{ margin: 32px 0 12px; font-size: 20px; }}
    .muted, .label {{ color: #5f6b7a; }}
    .hero {{ display: grid; grid-template-columns: minmax(220px, 1fr) minmax(220px, 1fr); gap: 16px; }}
    .panel, .card {{ background: #fff; border: 1px solid #d9dee7; border-radius: 8px; padding: 18px; }}
    .score {{ font-size: 56px; line-height: 1; margin: 10px 0; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 12px; }}
    .card strong {{ display: block; font-size: 28px; margin: 8px 0; }}
    .bar {{ height: 10px; background: #e5e8ef; border-radius: 999px; overflow: hidden; }}
    .bar span {{ display: block; height: 100%; background: #166534; }}
    pre {{ white-space: pre-wrap; background: #101828; color: #f8fafc; padding: 16px; border-radius: 8px; overflow-x: auto; }}
    @media (max-width: 760px) {{ header, .hero {{ display: block; }} .panel {{ margin-bottom: 12px; }} }}
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <h1>Market Health Dashboard</h1>
        <div class="muted">Generated for {escape(record.get("date", "unknown"))}</div>
      </div>
      <div class="muted">Engine v{escape(record.get("metadata", {}).get("engine_version", "1.0"))}</div>
    </header>

    <section class="hero">
      <div class="panel">
        <div class="label">Today's Market Health</div>
        <div class="score">{_fmt(record.get("market_health_score"))}</div>
        {_bar(record.get("market_health_score"))}
      </div>
      <div class="panel">
        <div class="label">Risk Regime</div>
        <h2>{escape(record.get("risk_regime", "n/a"))}</h2>
        <p><strong>{escape(record.get("stance", "n/a"))}</strong> stance with {_fmt(record.get("confidence"), "%")} confidence.</p>
      </div>
    </section>

    <h2>Subscores</h2>
    <section class="grid">{subscore_cards}</section>

    <h2>Prediction Accuracy</h2>
    <section class="panel">
      <p>Lifetime accuracy: <strong>{_fmt(accuracy.get("accuracy"), "%")}</strong></p>
      <p>Correct: {_fmt(accuracy.get("correct"))} / Evaluated: {_fmt(accuracy.get("total_evaluated"))}</p>
    </section>

    <h2>Recent Score History</h2>
    <pre>{escape(points or "No history yet.")}</pre>
  </main>
</body>
</html>
"""
    (DASHBOARD_DIR / "index.html").write_text(html, encoding="utf-8")

