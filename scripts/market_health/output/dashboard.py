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


def _evidence_rows(payload: dict) -> str:
    rows = []
    for item in payload.get("evidence", []):
        rows.append(
            f"""
            <tr>
              <td>{escape(item.get("label", ""))}</td>
              <td>{escape(item.get("symbol", ""))}</td>
              <td>{escape(str(item.get("display", "n/a")))}</td>
            </tr>
            """
        )
    return "\n".join(rows)


def _reasoning_items(payload: dict) -> str:
    return "\n".join(f"<li>{escape(item)}</li>" for item in payload.get("reasoning", []))


def _headline_groups(record: dict) -> str:
    groups = record.get("news", {}).get("groups", {})
    if not groups:
        return "<p class='muted'>No headlines available.</p>"

    sections = []
    for group, headlines in groups.items():
        items = []
        for headline in headlines:
            title = escape(headline.get("title") or "Untitled")
            link = escape(headline.get("link") or "#")
            source = escape(headline.get("source") or "Yahoo Finance")
            published = escape(headline.get("published") or "")
            items.append(
                f"""
                <li>
                  <a href="{link}" target="_blank" rel="noopener noreferrer">{title}</a>
                  <span>{source} {published}</span>
                </li>
                """
            )
        sections.append(
            f"""
            <section class="card">
              <div class="label">{escape(group.title())}</div>
              <ul class="headline-list">{''.join(items) or '<li>No headlines available.</li>'}</ul>
            </section>
            """
        )
    return "\n".join(sections)


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
        <section class="card subscore-card">
          <div class="card-top">
            <div>
              <div class="label">{escape(name.replace("_", " ").title())}</div>
              <strong>{_fmt(payload.get("score"))}</strong>
            </div>
          </div>
          {_bar(payload.get("score"))}
          <ul class="reasoning">{_reasoning_items(payload)}</ul>
          <table>
            <thead><tr><th>Indicator</th><th>Symbol</th><th>Value</th></tr></thead>
            <tbody>{_evidence_rows(payload)}</tbody>
          </table>
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
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 12px; }}
    .card strong {{ display: block; font-size: 28px; margin: 8px 0; }}
    .bar {{ height: 10px; background: #e5e8ef; border-radius: 999px; overflow: hidden; }}
    .bar span {{ display: block; height: 100%; background: #166534; }}
    .reasoning {{ margin: 14px 0; padding-left: 18px; color: #344054; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th, td {{ border-top: 1px solid #edf0f5; padding: 8px 4px; text-align: left; vertical-align: top; }}
    th {{ color: #5f6b7a; font-weight: 600; }}
    a {{ color: #0b5cad; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .headline-list {{ list-style: none; padding: 0; margin: 12px 0 0; }}
    .headline-list li {{ border-top: 1px solid #edf0f5; padding: 10px 0; }}
    .headline-list li:first-child {{ border-top: 0; }}
    .headline-list span {{ display: block; margin-top: 4px; color: #667085; font-size: 12px; }}
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

    <h2>Daily Headlines</h2>
    <section class="grid">{_headline_groups(record)}</section>

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
