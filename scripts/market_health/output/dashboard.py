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
    "liquidity": "Money Environment",
    "credit": "Risk appetite",
    "ai_fundamentals": "AI stocks",
    "market_breadth": "Rally breadth",
    "valuation_risk": "Too stretched?",
    "macro_risk": "Rates & dollar",
    "geopolitical_risk": "Volatility",
}

SUBSCORE_THRESHOLDS = {
    "liquidity": (70, 50, "Below 50 means funding conditions may be getting tighter for AI and growth stocks."),
    "credit": (60, 50, "Below 50 is an early warning that investors are less willing to take risk."),
    "ai_fundamentals": (65, 50, "Below 50 means the AI stock group is not confirming the story."),
    "market_breadth": (65, 45, "Below 45 means the rally is too narrow to trust comfortably."),
    "valuation_risk": (70, 55, "Below 55 means prices may be stretched enough to be careful with new buys."),
    "macro_risk": (65, 45, "Below 45 means rates or dollar pressure may be hurting growth stocks."),
    "geopolitical_risk": (70, 50, "Below 50 means volatility is becoming a real problem."),
}

WATCH_ITEMS = [
    ("NVDA", "NVIDIA", "AI leader", "return_20d", "%"),
    ("SMH", "Semiconductor ETF", "AI chip group", "return_20d", "%"),
    ("SOXX", "Chip ETF", "Chip breadth", "return_20d", "%"),
    ("HYG", "High yield bonds", "Are investors still willing to take risk?", "return_20d", "%"),
    ("^VIX", "VIX", "Is fear rising?", "close", ""),
    ("^TNX", "10Y yield", "Are rates pressuring growth stocks?", "close", ""),
    ("BZ=F", "Brent oil", "Is Middle East risk hitting energy prices?", "return_5d", "%"),
    ("GC=F", "Gold", "Is safe-haven demand rising?", "return_5d", "%"),
    ("TLT", "Long bonds", "Are investors hiding in duration?", "return_5d", "%"),
    ("XLE", "Energy stocks", "Is money rotating toward oil exposure?", "return_5d", "%"),
]

GLOSSARY = {
    "Money Environment": "This is not cash sitting on the sidelines. It asks whether funding conditions are friendly for AI and growth stocks today.",
    "VIX level": "VIX is the market's fear gauge. Higher VIX usually means investors expect bigger daily moves.",
    "Shock-risk level": "A quick fear check. If this jumps, crowded AI stocks can move sharply even without company news.",
    "close": "The latest available market price or index level.",
    "level": "The current reading of an index, yield, or price, not a percentage change.",
    "return_5d": "The percentage move over roughly the last 5 trading days.",
    "return_20d": "The percentage move over roughly the last 20 trading days, about one trading month.",
    "5-day return": "How much something moved over roughly one trading week.",
    "20-day return": "How much something moved over roughly one trading month.",
    "above_50d": "Whether price is above its 50-day average. Above is usually healthier; below means momentum is weaker.",
    "above 50-day": "Price is above its average price from the last 50 trading days.",
    "HYG above 50-day": "HYG tracks high-yield bonds. If it is below its 50-day average, investors may be less comfortable taking risk.",
    "Oil shock": "A fast Brent or WTI oil rise can raise inflation fear and pressure growth stocks.",
    "Gold bid": "Gold rising quickly can mean investors are buying safety, not growth risk.",
    "Dollar bid": "A quick dollar rise can tighten global financial conditions and pressure risk assets.",
    "Energy over AI": "Energy stocks beating chip stocks can signal rotation toward oil shock beneficiaries and away from AI risk.",
    "10Y Treasury yield proxy": "The 10-year US Treasury yield. Higher yields can pressure growth stocks because future profits get discounted more heavily.",
    "10Y yield 20-day change": "How much the 10-year yield changed over about one month. Negative means yield eased; positive means rate pressure increased.",
    "Dollar 20-day return": "How much the US dollar moved over about one month. A stronger dollar can tighten financial conditions.",
    "distance from 200-day": "How far price is above or below its 200-day average. Very high can mean the trade is stretched.",
    "SPY": "ETF tracking the S&P 500. Good for checking the broad US stock market.",
    "QQQ": "ETF tracking Nasdaq 100. Useful for growth and mega-cap tech.",
    "NVDA": "NVIDIA. A core AI leader, so weakness here matters for AI-stock confidence.",
    "SMH": "Semiconductor ETF. Useful for checking whether the AI chip group is healthy.",
    "SOXX": "Chip ETF. Another semiconductor group check.",
    "HYG": "High-yield bond ETF. It helps show whether investors still want risky assets.",
    "JNK": "High-yield bond ETF, similar risk appetite signal to HYG.",
    "BZ=F": "Yahoo's Brent crude oil futures symbol.",
    "CL=F": "Yahoo's WTI crude oil futures symbol.",
    "GC=F": "Yahoo's gold futures symbol.",
    "SI=F": "Yahoo's silver futures symbol.",
    "TLT": "ETF tracking long-duration US Treasury bonds.",
    "XLE": "Energy sector ETF. Useful for seeing whether money is rotating into oil-linked stocks.",
    "USO": "Oil ETF. Useful as another oil-price proxy.",
    "^TNX": "Yahoo's 10-year Treasury yield proxy.",
    "^VIX": "Yahoo's VIX symbol, the market fear gauge.",
}

SO_WHAT = {
    "liquidity": {
        "title": "So what?",
        "body": "This is the funding-environment check. If it is green, fresh money has fewer reasons to avoid AI and growth stocks. If it turns yellow or red, do not assume good AI company news will be enough; valuation multiples can compress.",
        "watch": "Watch VIX, DXY, QQQ vs 50-day, HYG, SMH/SOXX, and the 10Y yield.",
    },
    "credit": {
        "title": "So what?",
        "body": "This tells you whether investors are comfortable owning risk. Weak credit often shows up before equity holders fully react.",
        "watch": "Watch HYG/JNK returns and whether HYG is above its 50-day average.",
    },
    "ai_fundamentals": {
        "title": "So what?",
        "body": "This checks whether the AI trade itself is confirming the story. If NVDA, SMH, and SOXX are weak, be careful calling the setup healthy.",
        "watch": "Watch NVDA, SMH, SOXX, AVGO, and whether chip leadership is broadening.",
    },
    "market_breadth": {
        "title": "So what?",
        "body": "This tells you if the rally is broad or only a few large stocks. Narrow rallies can work, but they are more fragile.",
        "watch": "Watch SPY, QQQ, equal-weight S&P, and small caps.",
    },
    "valuation_risk": {
        "title": "So what?",
        "body": "This tells you whether prices are stretched. A weak reading does not mean sell automatically, but it means new buys need more patience.",
        "watch": "Watch distance from the 200-day average for SPY, QQQ, SMH, and NVDA.",
    },
    "macro_risk": {
        "title": "So what?",
        "body": "This checks whether rates and the dollar are creating headwind for growth stocks.",
        "watch": "Watch the 10Y yield, its 20-day move, and the dollar trend.",
    },
    "geopolitical_risk": {
        "title": "So what?",
        "body": "This is the event-risk check. If oil, gold, dollar, and VIX rise while QQQ/SMH weaken, the headline is becoming a portfolio problem for AI stocks.",
        "watch": "Watch Brent/WTI, gold, dollar, TLT, VIX, QQQ, SMH, and XLE vs SMH.",
    },
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
    return f"<div class='bar {escape(_status_class(value))}'><span style='width:{score}%'></span></div>"


def _fmt(value: float | int | None, suffix: str = "") -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        value = round(value, 2)
    return f"{value}{suffix}"


def _tip(text: str, key: str | None = None) -> str:
    explanation = GLOSSARY.get(key or text)
    if not explanation:
        return escape(text)
    return (
        f"{escape(text)} "
        f"<span class='tip' tabindex='0' data-tip='{escape(explanation)}'>?</span>"
    )


def _status_class(value: float | int | None, name: str | None = None) -> str:
    if value is None:
        return "status-neutral"
    if name and name in SUBSCORE_THRESHOLDS:
        good, watch, _note = SUBSCORE_THRESHOLDS[name]
    else:
        good, watch = 70, 50
    if value >= good:
        return "status-good"
    if value >= watch:
        return "status-watch"
    return "status-danger"


def _status_label(value: float | int | None, name: str | None = None) -> str:
    status = _status_class(value, name)
    if status == "status-good":
        return "Looks okay"
    if status == "status-watch":
        return "Watch"
    if status == "status-danger":
        return "Needs attention"
    return "No data"


def _field_tip(field: str) -> str:
    if field == "return_5d":
        return _tip("5-day return", "5-day return")
    if field == "return_20d":
        return _tip("20-day return", "20-day return")
    if field == "above_50d":
        return _tip("above 50-day", "above 50-day")
    if field == "close":
        return _tip("level", "level")
    if field == "distance_from_200d":
        return _tip("distance from 200-day", "distance from 200-day")
    return escape(field)


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


def _largest_subscore_moves(record: dict, previous: dict | None) -> str:
    if not previous:
        return "No previous daily record yet, so there is no day-over-day explanation."
    moves = []
    previous_scores = previous.get("sub_scores", {})
    for name, payload in record.get("sub_scores", {}).items():
        today = payload.get("score")
        yesterday = previous_scores.get(name, {}).get("score")
        delta = _change(today, yesterday)
        if delta is None:
            continue
        moves.append((abs(delta), delta, name, today, yesterday))
    if not moves:
        return "No comparable subscore data was available."
    moves = sorted(moves, reverse=True)[:3]
    parts = []
    for _abs_delta, delta, name, today, yesterday in moves:
        title = SUBSCORE_TITLES.get(name, name.replace("_", " ").title())
        direction = "rose" if delta > 0 else "fell" if delta < 0 else "was flat"
        parts.append(f"{title} {direction} from {_fmt(yesterday)} to {_fmt(today)}")
    return "Why the score moved: " + "; ".join(parts) + "."


def _evidence_rows(payload: dict) -> str:
    rows = []
    for item in payload.get("evidence", []):
        label = item.get("label", "")
        symbol = item.get("symbol", "")
        field = item.get("field", "")
        rows.append(
            f"""
            <tr>
              <td>{_tip(label)}<br><small>{_field_tip(field)}</small></td>
              <td><code>{_tip(symbol)}</code></td>
              <td>{escape(str(item.get("display", "n/a")))}</td>
            </tr>
            """
        )
    return "\n".join(rows)


def _reasoning_items(payload: dict) -> str:
    return "\n".join(f"<li>{escape(item)}</li>" for item in payload.get("reasoning", []))


def _so_what_details(name: str) -> str:
    item = SO_WHAT.get(name)
    if not item:
        return ""
    return f"""
      <details class="deep-dive">
        <summary>{escape(item["title"])} <span>How to use this score</span></summary>
        <p>{escape(item["body"])}</p>
        <div class="watch-note"><strong>Check next:</strong> {escape(item["watch"])}</div>
      </details>
    """


def _contribution_rows(payload: dict) -> str:
    rows = []
    for item in payload.get("contributions", []):
        points = item.get("points", 0)
        if points > 0:
            point_class = "positive"
            point_text = f"+{points}"
        elif points < 0:
            point_class = "negative"
            point_text = str(points)
        else:
            point_class = "neutral"
            point_text = "0"
        rows.append(
            f"""
            <tr>
              <td><strong>{escape(str(item.get("label", "Factor")))}</strong><br><small>{escape(str(item.get("why", "")))}</small></td>
              <td>{escape(str(item.get("value", "n/a")))}</td>
              <td><span class="contribution-points {point_class}">{escape(point_text)}</span></td>
            </tr>
            """
        )
    if not rows:
        return ""
    return f"""
      <div class="contribution-block">
        <div class="eyebrow">WHY THIS SCORE?</div>
        <table>
          <thead><tr><th>Factor</th><th>Today</th><th>Impact</th></tr></thead>
          <tbody>{''.join(rows)}</tbody>
        </table>
      </div>
    """


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
        status = _status_class(score, name)
        status_label = _status_label(score, name)
        intent = "helped" if mode == "leader" else "check"
        rows.append(
            f"""
            <article class="driver-tile {escape(status)}">
              <div class="driver-head">
                <span class="driver-icon">{escape(SUBSCORE_ICONS.get(name, "?"))}</span>
                <div>
                  <strong>{escape(label)}</strong>
                  <span class="delta">{_fmt(delta, " from 50")}</span>
                </div>
              </div>
              <div class="driver-meta">
                <span class="pill {escape(status)}">{escape(status_label)}</span>
                <span class="intent">{escape(intent)}</span>
              </div>
              <p>{escape(driver)}</p>
            </article>
            """
        )
    return f"""
    <section class="card driver-card {escape('driver-positive' if mode == 'leader' else 'driver-caution')}">
      <div class="eyebrow">{escape(title.upper())}</div>
      <div class="driver-grid">{''.join(rows)}</div>
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
    <section class="panel diagnosis hero-card">
      <div class="hero-topline">
        <div class="eyebrow">TODAY'S READ</div>
        <span class="pill {_status_class(record.get("market_health_score"))}">{escape(record.get("stance", "n/a"))}</span>
      </div>
      <h2>{escape(record.get("risk_regime", "n/a"))}</h2>
      <div class="score-line">
        <span class="big-score">{_fmt(record.get("market_health_score"))}</span>
        {score_delta}
      </div>
      <p class="plain-read">{escape(_plain_score_sentence(record.get("market_health_score")))}</p>
      <div class="focus-strip">
        <div class="focus-chip good"><span>{escape(SUBSCORE_ICONS.get(top_leader[0], "+"))}</span><div><small>Biggest help</small><strong>{escape(leader_name)}</strong></div></div>
        <div class="focus-chip danger"><span>{escape(SUBSCORE_ICONS.get(top_drag[0], "!"))}</span><div><small>Check first</small><strong>{escape(drag_name)}</strong></div></div>
      </div>
      <p>{escape(drag_detail)}</p>
      <p class="callout">{escape(_largest_subscore_moves(record, previous))}</p>
      <p class="muted">
        Read this like a morning checklist, not a buy/sell order. It tells you where to look before touching AI stocks.
      </p>
    </section>
    """


def _event_value(indicators: dict, symbol: str, field: str) -> float | int | bool | None:
    return indicators.get(symbol, {}).get(field)


def _average_event_value(indicators: dict, symbols: list[str], field: str) -> float | None:
    values = [
        value for value in (_event_value(indicators, symbol, field) for symbol in symbols)
        if isinstance(value, (int, float))
    ]
    if not values:
        return None
    return round(sum(float(value) for value in values) / len(values), 2)


def _relative_event_value(indicators: dict, leader: str, laggard: str, field: str) -> float | None:
    leader_value = _event_value(indicators, leader, field)
    laggard_value = _event_value(indicators, laggard, field)
    if not isinstance(leader_value, (int, float)) or not isinstance(laggard_value, (int, float)):
        return None
    return round(float(leader_value) - float(laggard_value), 2)


def _event_status(value: float | int | None, watch: float, danger: float, lower_is_bad: bool = False) -> str:
    if value is None:
        return "status-neutral"
    if lower_is_bad:
        if value <= danger:
            return "status-danger"
        if value <= watch:
            return "status-watch"
        return "status-good"
    if value >= danger:
        return "status-danger"
    if value >= watch:
        return "status-watch"
    return "status-good"


def _event_badge(value: float | int | None, watch: float, danger: float, lower_is_bad: bool = False) -> str:
    status = _event_status(value, watch, danger, lower_is_bad)
    if status == "status-danger":
        label = "Risk rising"
    elif status == "status-watch":
        label = "Watch"
    elif status == "status-good":
        label = "Contained"
    else:
        label = "No data"
    return f"<span class='pill {escape(status)}'>{escape(label)}</span>"


def _event_risk_panel(record: dict, previous: dict | None) -> str:
    indicators = record.get("indicators", {})
    previous_indicators = (previous or {}).get("indicators", {})
    oil = _average_event_value(indicators, ["BZ=F", "CL=F"], "return_5d")
    previous_oil = _average_event_value(previous_indicators, ["BZ=F", "CL=F"], "return_5d")
    gold = _event_value(indicators, "GC=F", "return_5d")
    dollar = _event_value(indicators, "DX-Y.NYB", "return_5d")
    vix = _event_value(indicators, "^VIX", "close")
    qqq = _event_value(indicators, "QQQ", "return_5d")
    tlt = _event_value(indicators, "TLT", "return_5d")
    energy_vs_ai = _relative_event_value(indicators, "XLE", "SMH", "return_5d")
    previous_energy_vs_ai = _relative_event_value(previous_indicators, "XLE", "SMH", "return_5d")
    geo_score = record.get("sub_scores", {}).get("geopolitical_risk", {}).get("score")
    rows = [
        ("Oil shock", "Brent/WTI 5-day", oil, previous_oil, "%", 4, 8, False, "Oil jumping means inflation and supply-chain fear can hit growth multiples."),
        ("Gold bid", "Gold 5-day", gold, _event_value(previous_indicators, "GC=F", "return_5d"), "%", 2.5, 5, False, "Gold strength says investors may be buying protection."),
        ("Dollar bid", "Dollar 5-day", dollar, _event_value(previous_indicators, "DX-Y.NYB", "return_5d"), "%", 1.2, 2.5, False, "A fast dollar rally tightens global money conditions."),
        ("VIX fear", "VIX level", vix, _event_value(previous_indicators, "^VIX", "close"), "", 20, 30, False, "VIX shows whether fear is spreading into broad market pricing."),
        ("QQQ shock", "QQQ 5-day", qqq, _event_value(previous_indicators, "QQQ", "return_5d"), "%", -3, -6, True, "If QQQ is falling, event risk is hitting growth stocks directly."),
        ("Energy over AI", "XLE minus SMH 5-day", energy_vs_ai, previous_energy_vs_ai, "%", 4, 8, False, "Energy beating chips can mean money is rotating away from AI toward oil exposure."),
        ("Bond hiding", "TLT 5-day", tlt, _event_value(previous_indicators, "TLT", "return_5d"), "%", 2.5, 5, False, "Long bonds rising can mean investors are hiding from risk."),
    ]
    cards = []
    danger_count = 0
    watch_count = 0
    for label, metric, value, previous_value, suffix, watch, danger, lower_is_bad, why in rows:
        status = _event_status(value, watch, danger, lower_is_bad)
        if status == "status-danger":
            danger_count += 1
        elif status == "status-watch":
            watch_count += 1
        cards.append(
            f"""
            <article class="event-tile {escape(status)}">
              <div class="event-top">
                <strong>{_tip(label)}</strong>
                {_event_badge(value, watch, danger, lower_is_bad)}
              </div>
              <div class="event-value">{_fmt(value, suffix)}</div>
              <small>{escape(metric)} · yesterday {_fmt(previous_value, suffix)}</small>
              <p>{escape(why)}</p>
            </article>
            """
        )
    if danger_count:
        summary = "Event risk is no longer just a headline. Verify oil, VIX, QQQ, and energy-vs-AI before adding risk."
    elif watch_count:
        summary = "Some stress signals are moving. Keep AI buys smaller until oil, dollar, and VIX calm down."
    else:
        summary = "Headline risk is visible, but market pricing is not confirming a broad panic yet."
    return f"""
    <section class="panel event-radar">
      <div class="event-radar-head">
        <div>
          <div class="eyebrow">EVENT RISK RADAR</div>
          <h2>War / Oil / Safe-Haven Check</h2>
          <p>{escape(summary)}</p>
        </div>
        <div class="event-score">
          <span>Geopolitical score</span>
          <strong>{_fmt(geo_score)}</strong>
          <small>Lower means more market stress</small>
        </div>
      </div>
      <div class="event-grid">{''.join(cards)}</div>
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
              <td><code>{_tip(symbol)}</code></td>
              <td><strong>{escape(label)}</strong><br><span>{escape(why)}</span><br><small>{_field_tip(field)}</small></td>
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


def _core_actions(record: dict) -> str:
    score = record.get("market_health_score") or 0
    subscores = record.get("sub_scores", {})
    credit = subscores.get("credit", {}).get("score") or 0
    ai = subscores.get("ai_fundamentals", {}).get("score") or 0
    macro = subscores.get("macro_risk", {}).get("score") or 0
    valuation = subscores.get("valuation_risk", {}).get("score") or 0
    geopolitical = subscores.get("geopolitical_risk", {}).get("score") or 0

    actions = []
    if geopolitical < 50:
        actions.append(("1", "Event risk", "Before touching AI, check oil, gold, VIX, and QQQ. If oil and VIX are both jumping, reduce new risk first."))
    elif score >= 75 and ai >= 65:
        actions.append(("1", "AI stocks", "Market is helping. Holding strong AI names makes sense; new buys still need clean setups."))
    elif score >= 60:
        actions.append(("1", "AI stocks", "Do not rush. Keep watchlist tight and prefer AI names that are already acting better than SMH/SOXX."))
    else:
        actions.append(("1", "AI stocks", "Be defensive. Avoid adding broad AI exposure until the score and AI-stock group improve."))

    if credit < 50:
        actions.append(("2", "Risk appetite", "Check HYG/JNK before buying. Weak credit says investors are not fully comfortable with risk."))
    else:
        actions.append(("2", "Risk appetite", "Credit is not flashing red. Still watch whether HYG gets back above its 50-day average."))

    if geopolitical < 50:
        actions.append(("3", "Oil / havens", "Do not chase oil or gold blindly. First verify whether XLE/USO and gold are confirming the headline for more than one day."))
    elif macro >= 70:
        actions.append(("3", "Bonds / rates", "Rates are not the main problem today. If yields keep easing, growth stocks get breathing room."))
    elif macro < 50:
        actions.append(("3", "Bonds / rates", "Rates are a problem. Consider waiting, or watch bond exposure rather than chasing AI strength."))
    elif valuation < 55:
        actions.append(("3", "Stretched prices", "Do not chase extended winners. Wait for pullbacks or stronger confirmation."))
    else:
        actions.append(("3", "Other sectors", "No clear oil or bond rotation signal from this model yet. It is mainly saying: watch AI strength, credit, and rates."))

    rows = "\n".join(
        f"""
        <li class="action-item">
          <span class="action-number">{escape(number)}</span>
          <div><strong>{escape(title)}</strong><p>{escape(text)}</p></div>
        </li>
        """
        for number, title, text in actions
    )
    return f"""
    <section class="card core-actions">
      <div class="eyebrow">3 THINGS TO DO FIRST</div>
      <ul>{rows}</ul>
      <p class="muted">This is a checklist, not personal financial advice. Use it to decide what to verify before trading.</p>
    </section>
    """


def _correlation_panel(history: dict) -> str:
    records = history.get("prediction_accuracy", {}).get("records", [])
    evaluated = [
        row for row in records
        if row.get("actual_sp500_return") is not None
    ]
    if len(evaluated) < 30:
        return f"""
        <section class="panel">
          <div class="eyebrow">DOES THIS MODEL MATCH HISTORY?</div>
          <p><strong>Not enough data yet.</strong></p>
          <p>
            We need at least 30 validated daily records before this section can say anything useful.
            Right now there are {len(evaluated)}. After enough history builds up, this will compare
            the score against next-day SPY moves and show whether the framework is actually useful.
          </p>
        </section>
        """
    returns = [float(row["actual_sp500_return"]) for row in evaluated]
    wins = [1 if value > 0 else 0 for value in returns]
    positive_days = sum(wins)
    avg_return = sum(returns) / len(returns)
    return f"""
    <section class="panel">
      <div class="eyebrow">DOES THIS MODEL MATCH HISTORY?</div>
      <p>Validated days: <strong>{len(evaluated)}</strong></p>
      <p>SPY was positive on <strong>{positive_days}</strong> of those days.</p>
      <p>Average next-day SPY move: <strong>{round(avg_return, 2)}%</strong></p>
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


def _tiny_sparkline(values: list[float | int | None]) -> str:
    clean_values = [float(value) for value in values if value is not None]
    if len(clean_values) < 2:
        return "<div class='tiny-chart muted'>More days needed</div>"
    width = 220
    height = 58
    step = width / (len(clean_values) - 1)
    points = []
    for index, value in enumerate(clean_values):
        x = round(index * step, 2)
        y = round(height - (value / 100) * height, 2)
        points.append(f"{x},{y}")
    status = _status_class(clean_values[-1])
    return f"""
    <svg class="tiny-chart {escape(status)}" viewBox="0 0 {width} {height}" role="img" aria-label="Subscore mini trend">
      <line x1="0" y1="{height * 0.5}" x2="{width}" y2="{height * 0.5}" class="guide"></line>
      <polyline points="{' '.join(points)}"></polyline>
      <circle cx="{round((len(clean_values) - 1) * step, 2)}" cy="{round(height - (clean_values[-1] / 100) * height, 2)}" r="3.5"></circle>
    </svg>
    """


def _subscore_history_values(name: str, history: dict, current_record: dict) -> list[float | None]:
    values: list[float | None] = []
    for row in history.get("score_history", [])[-29:]:
        daily_path = DAILY_DIR / f"{row.get('date')}.json"
        if not daily_path.exists():
            continue
        daily = json.loads(daily_path.read_text(encoding="utf-8"))
        values.append(daily.get("sub_scores", {}).get(name, {}).get("score"))
    current_value = current_record.get("sub_scores", {}).get(name, {}).get("score")
    if not values or values[-1] != current_value:
        values.append(current_value)
    return values


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
        _subscore_card(name, payload, history, record)
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
    .hero-card {{ background: linear-gradient(135deg, #ffffff 0%, #f8fbff 48%, #eefdf5 100%); border-color: #c7d7ee; }}
    .hero-topline {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; }}
    .score {{ font-size: 64px; line-height: 1; margin: 10px 0; font-weight: 800; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(330px, 1fr)); gap: 14px; }}
    .card strong {{ display: block; font-size: 30px; margin: 8px 0; }}
    .card-top {{ display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; }}
    .icon {{ width: 42px; height: 42px; border-radius: 8px; display: grid; place-items: center; color: white; background: linear-gradient(135deg, #1d4ed8, #0f766e); font-weight: 800; }}
    .pill {{ display: inline-flex; align-items: center; border: 1px solid #bdd7ff; background: #eff6ff; color: #1d4ed8; border-radius: 999px; padding: 3px 9px; font-size: 12px; font-weight: 700; }}
    .pill.status-good {{ border-color: #86efac; background: #dcfce7; color: #166534; }}
    .pill.status-watch {{ border-color: #fde68a; background: #fef3c7; color: #92400e; }}
    .pill.status-danger {{ border-color: #fecaca; background: #fee2e2; color: #b42318; }}
    .action {{ margin-top: 10px; padding: 10px 12px; border-radius: 8px; background: #f8fafc; border: 1px solid #e5eaf2; }}
    .deep-dive {{ margin-top: 12px; border: 1px solid #dbeafe; border-radius: 8px; background: linear-gradient(135deg, #eff6ff, #f0fdfa); overflow: hidden; }}
    .deep-dive summary {{ list-style: none; display: flex; align-items: center; justify-content: space-between; gap: 10px; cursor: pointer; padding: 11px 12px; color: #0f172a; font-weight: 850; }}
    .deep-dive summary::-webkit-details-marker {{ display: none; }}
    .deep-dive summary::before {{ content: "?"; display: inline-grid; place-items: center; width: 24px; height: 24px; border-radius: 7px; background: var(--blue); color: #fff; font-size: 14px; margin-right: 8px; flex: 0 0 auto; }}
    .deep-dive summary span {{ margin-left: auto; color: var(--blue); font-size: 12px; font-weight: 800; text-transform: uppercase; }}
    .deep-dive p {{ margin: 0; padding: 0 12px 10px; color: #344054; }}
    .watch-note {{ margin: 0 12px 12px; padding: 10px; border-radius: 8px; background: rgba(255,255,255,.75); color: #344054; }}
    .contribution-block {{ margin-top: 12px; border: 1px solid #edf0f5; border-radius: 8px; overflow: hidden; background: #fff; }}
    .contribution-block .eyebrow {{ padding: 10px 12px; background: #f8fafc; }}
    .contribution-block table {{ font-size: 12px; }}
    .contribution-block th, .contribution-block td {{ padding: 9px 10px; }}
    .contribution-block td strong {{ display: inline; font-size: 13px; margin: 0; }}
    .contribution-points {{ display: inline-grid; place-items: center; min-width: 34px; height: 26px; border-radius: 999px; font-weight: 900; }}
    .contribution-points.positive {{ color: #166534; background: #dcfce7; }}
    .contribution-points.negative {{ color: #b42318; background: #fee2e2; }}
    .contribution-points.neutral {{ color: #475467; background: #eef2f7; }}
    .bar {{ height: 12px; background: #e5e8ef; border-radius: 999px; overflow: hidden; }}
    .bar span {{ display: block; height: 100%; background: var(--blue); }}
    .bar.status-good span {{ background: var(--green); }}
    .bar.status-watch span {{ background: var(--amber); }}
    .bar.status-danger span {{ background: var(--red); }}
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
    .focus-strip {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 10px; margin: 16px 0 12px; }}
    .focus-chip {{ display: grid; grid-template-columns: 42px 1fr; align-items: center; gap: 10px; border-radius: 8px; padding: 12px; border: 1px solid #e5eaf2; background: #fff; }}
    .focus-chip > span {{ width: 42px; height: 42px; display: grid; place-items: center; border-radius: 8px; color: white; font-weight: 900; }}
    .focus-chip small {{ display: block; margin-bottom: 2px; }}
    .focus-chip strong {{ font-size: 18px; }}
    .focus-chip.good {{ border-color: #bbf7d0; background: #f0fdf4; }}
    .focus-chip.good > span {{ background: var(--green); }}
    .focus-chip.danger {{ border-color: #fecaca; background: #fff7ed; }}
    .focus-chip.danger > span {{ background: var(--red); }}
    .driver-card {{ padding: 0; overflow: hidden; }}
    .driver-card > .eyebrow {{ display: block; padding: 14px 16px; color: #0f172a; }}
    .driver-positive > .eyebrow {{ background: #dcfce7; }}
    .driver-caution > .eyebrow {{ background: #fee2e2; }}
    .driver-grid {{ display: grid; gap: 10px; padding: 14px; }}
    .driver-tile {{ border: 1px solid #e5eaf2; border-radius: 8px; padding: 12px; background: #fff; }}
    .driver-tile.status-good {{ border-color: #bbf7d0; background: #f7fff9; }}
    .driver-tile.status-watch {{ border-color: #fde68a; background: #fffbeb; }}
    .driver-tile.status-danger {{ border-color: #fecaca; background: #fff7f7; }}
    .driver-head {{ display: grid; grid-template-columns: 38px 1fr; align-items: center; gap: 10px; }}
    .driver-head strong {{ display: inline; font-size: 21px; margin: 0; }}
    .driver-icon {{ width: 38px; height: 38px; display: grid; place-items: center; border-radius: 8px; background: #eaf2ff; color: var(--blue); font-weight: 900; }}
    .driver-meta {{ display: flex; align-items: center; gap: 8px; margin: 10px 0 0; }}
    .intent {{ color: var(--muted); font-size: 12px; font-weight: 800; text-transform: uppercase; }}
    .driver-tile p {{ margin: 9px 0 0; color: #344054; }}
    .delta {{ color: var(--muted); font-size: 12px; margin-left: 6px; }}
    .event-radar {{ margin-top: 16px; background: linear-gradient(135deg, #ffffff 0%, #fff7ed 48%, #f8fafc 100%); border-color: #fed7aa; }}
    .event-radar h2 {{ margin: 4px 0 8px; }}
    .event-radar-head {{ display: grid; grid-template-columns: 1fr 180px; gap: 16px; align-items: start; }}
    .event-radar-head p {{ margin: 0; color: #344054; }}
    .event-score {{ border: 1px solid #fed7aa; background: #fff; border-radius: 8px; padding: 12px; }}
    .event-score span, .event-score small {{ display: block; color: var(--muted); }}
    .event-score strong {{ display: block; font-size: 34px; line-height: 1; margin: 6px 0; }}
    .event-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 10px; margin-top: 14px; }}
    .event-tile {{ border: 1px solid #e5eaf2; border-radius: 8px; padding: 12px; background: #fff; }}
    .event-tile.status-good {{ border-color: #bbf7d0; background: #f7fff9; }}
    .event-tile.status-watch {{ border-color: #fde68a; background: #fffbeb; }}
    .event-tile.status-danger {{ border-color: #fecaca; background: #fff7f7; }}
    .event-top {{ display: flex; align-items: center; justify-content: space-between; gap: 8px; }}
    .event-top strong {{ font-size: 15px; }}
    .event-value {{ font-size: 30px; line-height: 1; font-weight: 850; margin: 10px 0 4px; }}
    .event-tile p {{ margin: 8px 0 0; color: #344054; font-size: 13px; }}
    .threshold-row {{ border-top: 1px solid #edf0f5; padding: 10px 0; display: grid; grid-template-columns: 58px 1fr; gap: 8px; }}
    .threshold-row:first-child {{ border-top: 0; }}
    .threshold-row span {{ color: var(--muted); font-size: 12px; }}
    .threshold-row small {{ grid-column: 2; color: #344054; }}
    .mini-icon {{ display: inline-grid; place-items: center; width: 26px; height: 26px; margin-right: 8px; border-radius: 7px; background: #eaf2ff; color: var(--blue); font-weight: 850; font-size: 12px; }}
    .tip {{ position: relative; display: inline-grid; place-items: center; width: 17px; height: 17px; margin-left: 4px; border-radius: 50%; background: #e0ecff; color: var(--blue); font-size: 11px; font-weight: 900; cursor: help; overflow: visible; }}
    .tip::after {{ content: attr(data-tip); position: absolute; left: 50%; bottom: calc(100% + 8px); transform: translateX(-50%); width: min(280px, 70vw); padding: 10px 12px; border-radius: 8px; background: #111827; color: #fff; font-size: 12px; line-height: 1.35; font-weight: 600; box-shadow: 0 12px 28px rgba(16,24,40,.22); opacity: 0; pointer-events: none; z-index: 20; transition: opacity .12s ease, transform .12s ease; }}
    .tip::before {{ content: ""; position: absolute; left: 50%; bottom: calc(100% + 2px); transform: translateX(-50%); border: 6px solid transparent; border-top-color: #111827; opacity: 0; z-index: 21; transition: opacity .12s ease; }}
    .tip:hover::after, .tip:focus::after {{ opacity: 1; transform: translateX(-50%) translateY(-2px); }}
    .tip:hover::before, .tip:focus::before {{ opacity: 1; }}
    .up, .down, .flat {{ display: inline-flex; align-items: center; border-radius: 999px; padding: 3px 8px; font-size: 12px; font-weight: 800; white-space: nowrap; }}
    .up {{ color: #166534; background: #dcfce7; }}
    .down {{ color: #b42318; background: #fee2e2; }}
    .flat {{ color: #475467; background: #eef2f7; }}
    .chart {{ width: 100%; height: 180px; margin-top: 8px; background: #fbfdff; border: 1px solid #e5eaf2; border-radius: 8px; padding: 10px; }}
    .chart polyline {{ fill: none; stroke: var(--blue); stroke-width: 4; stroke-linecap: round; stroke-linejoin: round; }}
    .chart circle {{ fill: var(--blue); }}
    .chart .guide {{ stroke: #d9e1ee; stroke-width: 1; stroke-dasharray: 4 5; }}
    .tiny-chart {{ width: 100%; height: 62px; margin-top: 12px; background: #fbfdff; border: 1px solid #e5eaf2; border-radius: 8px; padding: 7px; }}
    .tiny-chart polyline {{ fill: none; stroke: var(--blue); stroke-width: 3; stroke-linecap: round; stroke-linejoin: round; }}
    .tiny-chart circle {{ fill: var(--blue); }}
    .tiny-chart .guide {{ stroke: #e5eaf2; stroke-width: 1; stroke-dasharray: 4 5; }}
    .tiny-chart.status-good polyline, .tiny-chart.status-good circle {{ stroke: var(--green); fill: var(--green); }}
    .tiny-chart.status-watch polyline, .tiny-chart.status-watch circle {{ stroke: var(--amber); fill: var(--amber); }}
    .tiny-chart.status-danger polyline, .tiny-chart.status-danger circle {{ stroke: var(--red); fill: var(--red); }}
    .subscore-card.status-good {{ border-color: #bbf7d0; }}
    .subscore-card.status-watch {{ border-color: #fde68a; }}
    .subscore-card.status-danger {{ border-color: #fecaca; }}
    td span {{ color: var(--muted); }}
    small {{ color: var(--muted); font-size: 12px; }}
    .core-actions {{ background: linear-gradient(180deg, #ffffff, #f8fbff); }}
    .core-actions ul {{ list-style: none; margin: 12px 0; padding: 0; }}
    .core-actions li {{ display: grid; grid-template-columns: 34px 1fr; gap: 10px; border-top: 1px solid #edf0f5; padding: 12px 0; }}
    .core-actions li:first-child {{ border-top: 0; }}
    .core-actions p {{ margin: 4px 0 0; color: #344054; }}
    .action-number {{ display: grid; place-items: center; width: 28px; height: 28px; border-radius: 8px; background: #102a43; color: white; font-weight: 900; }}
    .action-item:nth-child(1) .action-number {{ background: var(--blue); }}
    .action-item:nth-child(2) .action-number {{ background: var(--amber); }}
    .action-item:nth-child(3) .action-number {{ background: var(--green); }}
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
        {_core_actions(record)}
        <h2>Thresholds</h2>
        {_threshold_sidebar()}
      </aside>
    </section>

    {_event_risk_panel(record, previous)}

    <h2>Charts</h2>
    <section class="hero">
      <section class="panel">
        <div class="eyebrow">HEALTH SCORE TREND</div>
        {_sparkline(score_history)}
      </section>
      {_subscore_comparison(record, previous)}
    </section>

    <h2>History Check</h2>
    {_correlation_panel(history)}

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


def _subscore_card(name: str, payload: dict, history: dict, record: dict) -> str:
    score = payload.get("score")
    band_label, action, meaning = _band(score)
    title = SUBSCORE_TITLES.get(name, name.replace("_", " ").title())
    icon = SUBSCORE_ICONS.get(name, "SC")
    good, watch, note = SUBSCORE_THRESHOLDS.get(name, (70, 50, "Below the watch line deserves attention."))
    status = _status_class(score, name)
    status_label = _status_label(score, name)
    sparkline = _tiny_sparkline(_subscore_history_values(name, history, record))
    return f"""
    <section class="card subscore-card {escape(status)}">
      <div class="card-top">
        <div>
          <div class="eyebrow">{escape(title.upper())}</div>
          <strong>{_fmt(score)}</strong>
          <span class="pill {escape(status)}">{escape(status_label)}</span>
        </div>
        <div class="icon">{escape(icon)}</div>
      </div>
      {_bar(score)}
      {sparkline}
      <div class="action">
        <strong>Thresholds: green at {good}+; red below {watch}</strong><br>
        {escape(note)}
      </div>
      {_so_what_details(name)}
      {_contribution_rows(payload)}
      <ul class="reasoning">{_reasoning_items(payload)}</ul>
      <table>
        <thead><tr><th>Indicator</th><th>Symbol</th><th>Value</th></tr></thead>
        <tbody>{_evidence_rows(payload)}</tbody>
      </table>
    </section>
    """
