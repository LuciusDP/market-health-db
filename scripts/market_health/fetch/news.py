from __future__ import annotations

import ssl
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET


NEWS_QUERIES = {
    "market": ["SPY", "QQQ", "^VIX"],
    "ai": ["NVDA", "AMD", "SMH", "SOXX"],
    "macro": ["^TNX", "DX-Y.NYB"],
    "geopolitical": ["CL=F", "BZ=F", "GC=F", "^VIX"],
    "energy": ["XLE", "USO", "CL=F", "BZ=F"],
}


def collect_headlines(limit_per_group: int = 6) -> dict:
    groups: dict[str, list[dict]] = {}
    errors: dict[str, str] = {}
    seen: set[str] = set()

    for group, symbols in NEWS_QUERIES.items():
        try:
            headlines = fetch_yahoo_rss(symbols)
            filtered: list[dict] = []
            for headline in headlines:
                key = headline.get("link") or headline.get("title")
                if not key or key in seen:
                    continue
                seen.add(key)
                filtered.append(headline)
                if len(filtered) >= limit_per_group:
                    break
            groups[group] = filtered
        except Exception as exc:  # noqa: BLE001 - keep daily workflow alive.
            groups[group] = []
            errors[group] = str(exc)

    return {"groups": groups, "errors": errors, "source": "Yahoo Finance RSS"}


def fetch_yahoo_rss(symbols: list[str]) -> list[dict]:
    symbol_query = ",".join(symbols)
    encoded = urllib.parse.quote(symbol_query, safe=",")
    url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={encoded}&region=US&lang=en-US"
    request = urllib.request.Request(url, headers={"User-Agent": "market-health-db/1.0"})
    with urllib.request.urlopen(request, timeout=20, context=_ssl_context()) as response:
        xml_text = response.read().decode("utf-8")

    root = ET.fromstring(xml_text)
    headlines: list[dict] = []
    for item in root.findall("./channel/item"):
        headlines.append(
            {
                "title": _text(item, "title"),
                "link": _text(item, "link"),
                "published": _text(item, "pubDate"),
                "source": _text(item, "source") or "Yahoo Finance",
            }
        )
    return headlines


def _text(item: ET.Element, tag: str) -> str | None:
    child = item.find(tag)
    if child is None or child.text is None:
        return None
    return child.text.strip()


def _ssl_context() -> ssl.SSLContext:
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:  # noqa: BLE001 - fallback to system trust store.
        return ssl.create_default_context()
