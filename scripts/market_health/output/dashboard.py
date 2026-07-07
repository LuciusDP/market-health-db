from __future__ import annotations

from html import escape

from scripts.market_health.config import DASHBOARD_DIR


SCORE_BANDS = [
    (75, "Strong", "Build or hold winners", "Conditions support risk-taking in quality AI leaders."),
    (60, "Constructive", "Selective risk-on", "Add only where trend and fundamentals agree."),
    (45, "Mixed", "Watch closely", "Keep AI exposure focused; avoid chasing extended moves."),
    (30, "Caution", "Reduce weak links", "Protect capital and demand cleaner setups."),
    (0, "Risk-off", "Defensive posture", "Liquidity, credit, or trend stress can overpower the AI story."),
]

SUBSCORE_ICONS = {
    "liquidity": "LQ",
    "credit": "CR",
    "ai_fundamentals": "AI",
    "market_breadth": "BR",
    "valuation_risk": "VR",
    "macro_risk": "MR",
    "geopolitical_risk": "GR",
}

SUBSCORE_TITLES = {
    "liquidity": "Liquidity",
    "credit": "Credit",
    "ai_fundamentals": "AI Fundamentals",
    "market_breadth": "Market Breadth",
    "valuation_risk": "Valuation Risk",
    "macro_risk": "Macro Risk",
    "geopolitical_risk": "Geopolitical Risk",
}


def _band(value: float | None) -> tuple[str, str, str]:
    if value is None:
        return "Unknown", "Wait for data", "The engine needs fresh market data."
    for threshold, label, action, meaning in SCORE_BANDS:
        if value >= threshold:
            return label, action, meaning
    return SCORE_BANDS[-1][1:]


def _bar(value: float | None) -> str:
    score = 0 if value is None else max(0, min(100, int(round(value))))
    return f"<div class='bar'><span style='width:{score}%'></span></div>"


def _fmt(value: float | int | None, suffix: str = "") -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        value = round(value, 2)
    return f"{value}{suffix}"


def _evidence_rows(payload: dict) -> str:
    rows = []
    for item in payload.get("evidence", []):
        rows.append(
            f"""
            <tr>
              <td>{escape(item.get("label", ""))}</td>
              <td><code>{escape(item.get("symbol", ""))}</code></td>
              <td>{escape(str(item.get("display", "n/a")))}</td>
            </tr>
            """
        )
    return "\n".join(rows)


def _reasoning_items(payload: dict) -> str:
    return "\n".join(f"<li>{escape(item)}</li>" for item in payload.get("reasoning", []))


def _threshold_table() -> str:
    rows = []
    for threshold, label, action, meaning in SCORE_BANDS:
        range_text = f"{threshold}-100" if threshold == 75 else f"{threshold}-74"
        if threshold == 0:
            range_text = "0-29"
        elif threshold == 30:
            range_text = "30-44"
        elif threshold == 45:
            range_text = "45-59"
        elif threshold == 60:
            range_text = "60-74"
        rows.append(
            f"""
            <tr>
              <td>{range_text}</td>
              <td><span class="pill">{escape(label)}</span></td>
              <td>{escape(action)}</td>
              <td>{escape(meaning)}</td>
            </tr>
            """
        )
    return "\n".join(rows)


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
              <div class="eyebrow">{escape(group.upper())}</div>
              <ul class="headline-list">{''.join(items) or '<li>No headlines available.</li>'}</ul>
            </section>
            """
        )
    return "\n".join(sections)


def _accuracy_panel(history: dict) -> str:
    accuracy = history.get("prediction_accuracy", {})
    records = accuracy.get("records", [])
    latest = records[-1] if records else None
    latest_text = "No validated prediction yet. The next trading-day run backfills the prior daily record."
    if latest:
        verdict = "Correct" if latest.get("prediction_correct") else "Wrong"
        latest_text = (
            f"{escape(latest.get('date', 'unknown'))}: {verdict}; "
            f"SPY next-session return {_fmt(latest.get('actual_sp500_return'), '%')}."
        )
    return f"""
    <section class="panel">
      <div class="metric-row">
        <div>
          <div class="label">Lifetime Accuracy</div>
          <strong>{_fmt(accuracy.get("accuracy"), "%")}</strong>
        </div>
        <div>
          <div class="label">Evaluated</div>
          <strong>{_fmt(accuracy.get("total_evaluated"))}</strong>
        </div>
        <div>
          <div class="label">Correct / Wrong</div>
          <strong>{_fmt(accuracy.get("correct"))} / {_fmt(accuracy.get("wrong"))}</strong>
        </div>
      </div>
      <p class="callout">{latest_text}</p>
    </section>
    """


def generate_dashboard(record: dict, history: dict) -> None:
    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
    subscores = record.get("sub_scores", {})
    score_history = history.get("score_history", [])[-180:]
    band_label, action, meaning = _band(record.get("market_health_score"))
    points = ", ".join(
        f"{row.get('date')}: {_fmt(row.get('market_health_score'))}"
        for row in score_history[-30:]
    )
    subscore_cards = "\n".join(
        _subscore_card(name, payload)
        for name, payload in subscores.items()
    )

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Market Health Dashboard</title>
  <style>
    :root {{
      --ink: #162033;
      --muted: #667085;
      --line: #d9e1ee;
      --paper: #ffffff;
      --bg: #f3f6fb;
      --green: #15803d;
      --teal: #0f766e;
      --amber: #b45309;
      --red: #b42318;
      --blue: #1d4ed8;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: var(--ink); background: var(--bg); }}
    main {{ max-width: 1240px; margin: 0 auto; padding: 30px 20px 48px; }}
    header {{ display: flex; justify-content: space-between; gap: 20px; align-items: flex-start; margin-bottom: 22px; }}
    h1 {{ margin: 0 0 6px; font-size: 34px; letter-spacing: 0; }}
    h2 {{ margin: 30px 0 12px; font-size: 21px; letter-spacing: 0; }}
    code {{ background: #eef2f7; border-radius: 4px; padding: 2px 5px; }}
    a {{ color: var(--blue); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .muted, .label {{ color: var(--muted); }}
    .eyebrow {{ color: var(--blue); font-size: 12px; font-weight: 800; letter-spacing: .08em; }}
    .hero {{ display: grid; grid-template-columns: 1.1fr .9fr; gap: 16px; }}
    .panel, .card {{ background: var(--paper); border: 1px solid var(--line); border-radius: 8px; padding: 18px; box-shadow: 0 8px 24px rgba(29, 78, 216, .05); }}
    .score {{ font-size: 64px; line-height: 1; margin: 10px 0; font-weight: 800; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(330px, 1fr)); gap: 14px; }}
    .card strong {{ display: block; font-size: 30px; margin: 8px 0; }}
    .card-top {{ display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; }}
    .icon {{ width: 42px; height: 42px; border-radius: 8px; display: grid; place-items: center; color: white; background: linear-gradient(135deg, #1d4ed8, #0f766e); font-weight: 800; }}
    .pill {{ display: inline-flex; align-items: center; border: 1px solid #bdd7ff; background: #eff6ff; color: #1d4ed8; border-radius: 999px; padding: 3px 9px; font-size: 12px; font-weight: 700; }}
    .action {{ margin-top: 10px; padding: 10px 12px; border-radius: 8px; background: #f8fafc; border: 1px solid #e5eaf2; }}
    .bar {{ height: 12px; background: #e5e8ef; border-radius: 999px; overflow: hidden; }}
    .bar span {{ display: block; height: 100%; background: linear-gradient(90deg, var(--red), var(--amber), var(--teal), var(--green)); }}
    .reasoning {{ margin: 14px 0; padding-left: 18px; color: #344054; }}
    .reasoning li {{ margin-bottom: 7px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th, td {{ border-top: 1px solid #edf0f5; padding: 8px 4px; text-align: left; vertical-align: top; }}
    th {{ color: var(--muted); font-weight: 700; }}
    .headline-list {{ list-style: none; padding: 0; margin: 12px 0 0; }}
    .headline-list li {{ border-top: 1px solid #edf0f5; padding: 10px 0; }}
    .headline-list li:first-child {{ border-top: 0; }}
    .headline-list span {{ display: block; margin-top: 4px; color: var(--muted); font-size: 12px; }}
    .metric-row {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 14px; }}
    .metric-row strong {{ font-size: 26px; }}
    .callout {{ margin: 14px 0 0; padding: 12px; border-left: 4px solid var(--blue); background: #f8fbff; border-radius: 6px; }}
    pre {{ white-space: pre-wrap; background: #101828; color: #f8fafc; padding: 16px; border-radius: 8px; overflow-x: auto; }}
    @media (max-width: 760px) {{ header, .hero {{ display: block; }} .panel {{ margin-bottom: 12px; }} .score {{ font-size: 52px; }} }}
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <h1>Market Health Dashboard</h1>
        <div class="muted">Generated for {escape(record.get("date", "unknown"))}</div>
      </div>
      <div class="pill">Engine v{escape(record.get("metadata", {}).get("engine_version", "1.0"))}</div>
    </header>

    <section class="hero">
      <div class="panel">
        <div class="eyebrow">TODAY'S MARKET HEALTH</div>
        <div class="score">{_fmt(record.get("market_health_score"))}</div>
        {_bar(record.get("market_health_score"))}
        <div class="action"><strong>{escape(band_label)}: {escape(action)}</strong><br>{escape(meaning)}</div>
      </div>
      <div class="panel">
        <div class="eyebrow">REGIME AND AI STANCE</div>
        <h2>{escape(record.get("risk_regime", "n/a"))}</h2>
        <p><strong>{escape(record.get("stance", "n/a"))}</strong> stance with {_fmt(record.get("confidence"), "%")} confidence.</p>
        <p class="muted">The score is not a price target. It is a risk climate check for AI-heavy equity exposure.</p>
      </div>
    </section>

    <h2>Score Thresholds</h2>
    <section class="panel">
      <table>
        <thead><tr><th>Score</th><th>Regime</th><th>Action</th><th>AI portfolio meaning</th></tr></thead>
        <tbody>{_threshold_table()}</tbody>
      </table>
    </section>

    <h2>Subscores</h2>
    <section class="grid">{subscore_cards}</section>

    <h2>Daily Headlines</h2>
    <section class="grid">{_headline_groups(record)}</section>

    <h2>Prediction Accuracy</h2>
    {_accuracy_panel(history)}

    <h2>Recent Score History</h2>
    <pre>{escape(points or "No history yet.")}</pre>
  </main>
</body>
</html>
"""
    (DASHBOARD_DIR / "index.html").write_text(html, encoding="utf-8")


def _subscore_card(name: str, payload: dict) -> str:
    score = payload.get("score")
    band_label, action, meaning = _band(score)
    title = SUBSCORE_TITLES.get(name, name.replace("_", " ").title())
    icon = SUBSCORE_ICONS.get(name, "SC")
    return f"""
    <section class="card subscore-card">
      <div class="card-top">
        <div>
          <div class="eyebrow">{escape(title.upper())}</div>
          <strong>{_fmt(score)}</strong>
          <span class="pill">{escape(band_label)}</span>
        </div>
        <div class="icon">{escape(icon)}</div>
      </div>
      {_bar(score)}
      <div class="action"><strong>{escape(action)}</strong><br>{escape(meaning)}</div>
      <ul class="reasoning">{_reasoning_items(payload)}</ul>
      <table>
        <thead><tr><th>Indicator</th><th>Symbol</th><th>Value</th></tr></thead>
        <tbody>{_evidence_rows(payload)}</tbody>
      </table>
    </section>
    """
