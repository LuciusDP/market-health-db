from __future__ import annotations

import json
from html import escape

from scripts.market_health.config import DAILY_DIR, DASHBOARD_DIR


SCORE_BANDS = [
    (75, "Clear green", "Market is helping", "Good conditions for holding strong AI winners."),
    (60, "Mostly okay", "Be selective", "The market is supportive, but still check the weak spots."),
    (45, "Mixed", "Slow down", "Some things are working, some are warning you."),
    (30, "Warning", "Protect capital", "Do not chase. Wait for cleaner confirmation."),
    (0, "Danger", "Stay defensive", "Market stress can overwhelm even good AI stories."),
]

SUBSCORE_ICONS = {
    "liquidity": "$",
    "credit": "!",
    "ai_fundamentals": "AI",
    "market_breadth": "+",
    "valuation_risk": "%",
    "macro_risk": "R",
    "geopolitical_risk": "~",
}

SUBSCORE_TITLES = {
    "liquidity": "Cash mood",
    "credit": "Risk appetite",
    "ai_fundamentals": "AI stocks",
    "market_breadth": "Rally breadth",
    "valuation_risk": "Too stretched?",
    "macro_risk": "Rates & dollar",
    "geopolitical_risk": "Volatility",
}

WATCH_ITEMS = [
    ("NVDA", "NVIDIA", "AI leader", "return_20d", "%"),
    ("SMH", "Semiconductor ETF", "AI chip group", "return_20d", "%"),
    ("SOXX", "Chip ETF", "Chip breadth", "return_20d", "%"),
    ("HYG", "High yield bonds", "Are investors still willing to take risk?", "return_20d", "%"),
    ("^VIX", "VIX", "Is fear rising?", "close", ""),
    ("^TNX", "10Y yield", "Are rates pressuring growth stocks?", "close", ""),
]


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


def _previous_record(record: dict) -> dict | None:
    current_date = record.get("date")
    if not current_date:
        return None
    previous_files = [path for path in DAILY_DIR.glob("*.json") if path.stem < current_date]
    if not previous_files:
        return None
    return json.loads(sorted(previous_files)[-1].read_text(encoding="utf-8"))


def _change(today: float | int | None, yesterday: float | int | None) -> float | None:
    if today is None or yesterday is None:
        return None
    return round(float(today) - float(yesterday), 2)


def _change_badge(today: float | int | None, yesterday: float | int | None, suffix: str = "") -> str:
    delta = _change(today, yesterday)
    if delta is None:
        return "<span class='flat'>n/a</span>"
    if delta > 0:
        return f"<span class='up'>UP +{delta}{suffix}</span>"
    if delta < 0:
        return f"<span class='down'>DOWN {delta}{suffix}</span>"
    return "<span class='flat'>FLAT</span>"


def _plain_score_sentence(score: float | int | None) -> str:
    if score is None:
        return "No fresh score yet."
    if score >= 75:
        return "The market is helping your AI watchlist today."
    if score >= 60:
        return "The market is okay, but this is not an all-clear signal."
    if score >= 45:
        return "The market is split. Be picky and check the weak spots."
    if score >= 30:
        return "Conditions are shaky. Avoid chasing green candles."
    return "Conditions are hostile. Defense matters more than new buys."


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


def _threshold_sidebar() -> str:
    rows = []
    for threshold, label, action, _meaning in SCORE_BANDS:
        if threshold == 75:
            range_text = "75-100"
        elif threshold == 60:
            range_text = "60-74"
        elif threshold == 45:
            range_text = "45-59"
        elif threshold == 30:
            range_text = "30-44"
        else:
            range_text = "0-29"
        rows.append(
            f"""
            <div class="threshold-row">
              <span>{range_text}</span>
              <strong>{escape(label)}</strong>
              <small>{escape(action)}</small>
            </div>
            """
        )
    return "\n".join(rows)


def _subscore_rankings(record: dict) -> tuple[list[tuple[str, dict]], list[tuple[str, dict]]]:
    items = list(record.get("sub_scores", {}).items())
    leaders = sorted(items, key=lambda item: item[1].get("score") or 0, reverse=True)[:3]
    drags = sorted(items, key=lambda item: item[1].get("score") or 0)[:3]
    return leaders, drags


def _drivers_list(title: str, items: list[tuple[str, dict]], mode: str) -> str:
    rows = []
    for name, payload in items:
        score = payload.get("score")
        delta = None if score is None else round(score - 50, 2)
        label = SUBSCORE_TITLES.get(name, name.replace("_", " ").title())
        driver = _plain_driver(name, payload, mode)
        rows.append(
            f"""
            <li>
              <div><span class="mini-icon">{escape(SUBSCORE_ICONS.get(name, "?"))}</span><strong>{escape(label)}</strong> <span class="delta">{_fmt(delta, " from 50")}</span></div>
              <p>{escape(driver)}</p>
            </li>
            """
        )
    return f"""
    <section class="card">
      <div class="eyebrow">{escape(title.upper())}</div>
      <ul class="driver-list">{''.join(rows)}</ul>
    </section>
    """


def _plain_driver(name: str, payload: dict, mode: str) -> str:
    evidence = payload.get("evidence", [])
    available = [item for item in evidence if item.get("display") != "n/a"]
    if not available:
        return "No reliable driver data was available for this sleeve today."
    facts = "; ".join(
        f"{item.get('label')}: {item.get('display')}"
        for item in available[:3]
    )
    if mode == "leader":
        return f"This part helped today. Check: {facts}."
    score = payload.get("score") or 0
    if score < 50:
        return f"This part is holding the market back. Before buying, check: {facts}."
    return f"This is okay, but not strong enough to relax. Check: {facts}."


def _today_diagnosis(record: dict, previous: dict | None) -> str:
    leaders, drags = _subscore_rankings(record)
    top_leader = leaders[0] if leaders else (None, {})
    top_drag = drags[0] if drags else (None, {})
    leader_name = SUBSCORE_TITLES.get(top_leader[0], "n/a")
    drag_name = SUBSCORE_TITLES.get(top_drag[0], "n/a")
    drag_detail = _plain_driver(top_drag[0], top_drag[1], "drag") if top_drag[0] else ""
    previous_score = previous.get("market_health_score") if previous else None
    score_delta = _change_badge(record.get("market_health_score"), previous_score)
    return f"""
    <section class="panel diagnosis">
      <div class="eyebrow">TODAY'S READ</div>
      <h2>{escape(record.get("risk_regime", "n/a"))}: {escape(record.get("stance", "n/a"))}</h2>
      <div class="score-line">
        <span class="big-score">{_fmt(record.get("market_health_score"))}</span>
        {score_delta}
      </div>
      <p class="plain-read">{escape(_plain_score_sentence(record.get("market_health_score")))}</p>
      <p>
        The biggest help today is <strong>{escape(leader_name)}</strong>.
        The thing to check first is <strong>{escape(drag_name)}</strong>.
      </p>
      <p>{escape(drag_detail)}</p>
      <p class="muted">
        Read this like a morning checklist, not a buy/sell order. It tells you where to look before touching AI stocks.
      </p>
    </section>
    """


def _watchlist_panel(record: dict, previous: dict | None) -> str:
    indicators = record.get("indicators", {})
    previous_indicators = (previous or {}).get("indicators", {})
    rows = []
    for symbol, label, why, field, suffix in WATCH_ITEMS:
        value = indicators.get(symbol, {}).get(field)
        previous_value = previous_indicators.get(symbol, {}).get(field)
        rows.append(
            f"""
            <tr>
              <td><code>{escape(symbol)}</code></td>
              <td><strong>{escape(label)}</strong><br><span>{escape(why)}</span></td>
              <td>{_fmt(previous_value, suffix)}</td>
              <td>{_fmt(value, suffix)}</td>
              <td>{_change_badge(value, previous_value, suffix)}</td>
            </tr>
            """
        )
    return f"""
    <section class="panel">
      <div class="eyebrow">WHAT TO CHECK BEFORE YOU TRADE</div>
      <table>
        <thead><tr><th>Ticker</th><th>Why look here?</th><th>Yesterday</th><th>Today</th><th>Change</th></tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
    </section>
    """


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
              <div class="eyebrow">{escape(group.upper())} CONTEXT TO VERIFY</div>
              <ul class="headline-list">{''.join(items) or '<li>No headlines available.</li>'}</ul>
            </section>
            """
        )
    return "\n".join(sections)


def _sparkline(score_history: list[dict]) -> str:
    values = [row.get("market_health_score") for row in score_history if row.get("market_health_score") is not None]
    if len(values) < 2:
        return "<p class='muted'>More history needed for a chart.</p>"
    width = 520
    height = 150
    step = width / (len(values) - 1)
    points = []
    for index, value in enumerate(values):
        x = round(index * step, 2)
        y = round(height - (float(value) / 100) * height, 2)
        points.append(f"{x},{y}")
    last = values[-1]
    first = values[0]
    return f"""
    <svg class="chart" viewBox="0 0 {width} {height}" role="img" aria-label="Market health score history">
      <line x1="0" y1="37.5" x2="{width}" y2="37.5" class="guide"></line>
      <line x1="0" y1="60" x2="{width}" y2="60" class="guide"></line>
      <line x1="0" y1="82.5" x2="{width}" y2="82.5" class="guide"></line>
      <polyline points="{' '.join(points)}"></polyline>
      <circle cx="{round((len(values) - 1) * step, 2)}" cy="{round(height - (float(last) / 100) * height, 2)}" r="5"></circle>
    </svg>
    <p class="muted">Started at {_fmt(first)}. Latest is {_fmt(last)}.</p>
    """


def _subscore_comparison(record: dict, previous: dict | None) -> str:
    previous_scores = (previous or {}).get("sub_scores", {})
    rows = []
    for name, payload in record.get("sub_scores", {}).items():
        title = SUBSCORE_TITLES.get(name, name.replace("_", " ").title())
        icon = SUBSCORE_ICONS.get(name, "?")
        today = payload.get("score")
        yesterday = previous_scores.get(name, {}).get("score")
        rows.append(
            f"""
            <tr>
              <td><span class="mini-icon">{escape(icon)}</span>{escape(title)}</td>
              <td>{_fmt(yesterday)}</td>
              <td>{_fmt(today)}</td>
              <td>{_change_badge(today, yesterday)}</td>
              <td>{_bar(today)}</td>
            </tr>
            """
        )
    return f"""
    <section class="panel">
      <div class="eyebrow">YESTERDAY VS TODAY</div>
      <table>
        <thead><tr><th>Area</th><th>Yesterday</th><th>Today</th><th>Move</th><th>Level</th></tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
    </section>
    """


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
    previous = _previous_record(record)
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
    leaders, drags = _subscore_rankings(record)

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
    .hero {{ display: grid; grid-template-columns: 1.4fr .6fr; gap: 16px; align-items: start; }}
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
    .diagnosis h2 {{ margin-top: 8px; font-size: 32px; }}
    .score-line {{ display: flex; align-items: center; gap: 12px; margin: 8px 0; }}
    .big-score {{ font-size: 58px; font-weight: 850; line-height: 1; }}
    .plain-read {{ font-size: 18px; font-weight: 700; margin: 10px 0; }}
    .driver-list {{ list-style: none; margin: 12px 0 0; padding: 0; }}
    .driver-list li {{ border-top: 1px solid #edf0f5; padding: 11px 0; }}
    .driver-list li:first-child {{ border-top: 0; }}
    .driver-list p {{ margin: 6px 0 0; color: #344054; }}
    .delta {{ color: var(--muted); font-size: 12px; margin-left: 6px; }}
    .threshold-row {{ border-top: 1px solid #edf0f5; padding: 10px 0; display: grid; grid-template-columns: 58px 1fr; gap: 8px; }}
    .threshold-row:first-child {{ border-top: 0; }}
    .threshold-row span {{ color: var(--muted); font-size: 12px; }}
    .threshold-row small {{ grid-column: 2; color: #344054; }}
    .mini-icon {{ display: inline-grid; place-items: center; width: 26px; height: 26px; margin-right: 8px; border-radius: 7px; background: #eaf2ff; color: var(--blue); font-weight: 850; font-size: 12px; }}
    .up, .down, .flat {{ display: inline-flex; align-items: center; border-radius: 999px; padding: 3px 8px; font-size: 12px; font-weight: 800; white-space: nowrap; }}
    .up {{ color: #166534; background: #dcfce7; }}
    .down {{ color: #b42318; background: #fee2e2; }}
    .flat {{ color: #475467; background: #eef2f7; }}
    .chart {{ width: 100%; height: 180px; margin-top: 8px; background: #fbfdff; border: 1px solid #e5eaf2; border-radius: 8px; padding: 10px; }}
    .chart polyline {{ fill: none; stroke: var(--blue); stroke-width: 4; stroke-linecap: round; stroke-linejoin: round; }}
    .chart circle {{ fill: var(--blue); }}
    .chart .guide {{ stroke: #d9e1ee; stroke-width: 1; stroke-dasharray: 4 5; }}
    td span {{ color: var(--muted); }}
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
      <div>
        {_today_diagnosis(record, previous)}
        <div class="hero" style="grid-template-columns: 1fr 1fr; margin-top: 16px;">
          {_drivers_list("What lifted the score", leaders, "leader")}
          {_drivers_list("Why it is not stronger", drags, "drag")}
        </div>
      </div>
      <aside class="panel">
        <div class="eyebrow">TODAY'S MARKET HEALTH</div>
        <div class="score">{_fmt(record.get("market_health_score"))}</div>
        {_bar(record.get("market_health_score"))}
        <div class="action"><strong>{escape(band_label)}: {escape(action)}</strong><br>{escape(meaning)}</div>
        <h2>Thresholds</h2>
        {_threshold_sidebar()}
      </aside>
    </section>

    <h2>Charts</h2>
    <section class="hero">
      <section class="panel">
        <div class="eyebrow">HEALTH SCORE TREND</div>
        {_sparkline(score_history)}
      </section>
      {_subscore_comparison(record, previous)}
    </section>

    <h2>Trading Checklist</h2>
    {_watchlist_panel(record, previous)}

    <h2>Subscore Detail</h2>
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
