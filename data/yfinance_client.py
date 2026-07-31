"""
Thin yfinance wrapper. Every function goes through data.cache.get_or_fetch
so repeated lookups (same ticker, multiple users/pages) hit SQLite instead
of Yahoo Finance.
"""

import yfinance as yf

from data.cache import get_or_fetch, TTL_SLOW, TTL_FAST


def _extract_ceo(info: dict):
    for officer in info.get("companyOfficers", []) or []:
        if "CEO" in (officer.get("title") or ""):
            return officer.get("name")
    return None


def _fetch_info_raw(ticker: str) -> dict:
    t = yf.Ticker(ticker)
    info = t.info
    return {
        "ticker": ticker,
        "shortName": info.get("shortName"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "marketCap": info.get("marketCap"),
        "trailingPE": info.get("trailingPE"),
        "forwardPE": info.get("forwardPE"),
        "priceToBook": info.get("priceToBook"),
        "profitMargins": info.get("profitMargins"),
        "revenueGrowth": info.get("revenueGrowth"),
        "earningsGrowth": info.get("earningsGrowth"),
        "dividendYield": info.get("dividendYield"),
        "beta": info.get("beta"),
        "targetMeanPrice": info.get("targetMeanPrice"),
        "recommendationKey": info.get("recommendationKey"),
        "numberOfAnalystOpinions": info.get("numberOfAnalystOpinions"),
        "longBusinessSummary": info.get("longBusinessSummary"),
        "ceo": _extract_ceo(info),
    }


def get_company_info(ticker: str) -> dict:
    return get_or_fetch(f"info:{ticker}", TTL_SLOW, lambda: _fetch_info_raw(ticker))


def _fetch_quote_raw(ticker: str) -> dict:
    t = yf.Ticker(ticker)
    fast = t.fast_info
    return {
        "ticker": ticker,
        "lastPrice": fast.get("lastPrice"),
        "previousClose": fast.get("previousClose"),
        "dayHigh": fast.get("dayHigh"),
        "dayLow": fast.get("dayLow"),
        "yearHigh": fast.get("yearHigh"),
        "yearLow": fast.get("yearLow"),
    }


def get_quote(ticker: str) -> dict:
    return get_or_fetch(f"quote:{ticker}", TTL_FAST, lambda: _fetch_quote_raw(ticker))


def _fetch_history_raw(ticker: str, period: str) -> list:
    t = yf.Ticker(ticker)
    hist = t.history(period=period)
    if hist.empty:
        return []
    hist = hist.reset_index()
    hist["Date"] = hist["Date"].astype(str)
    return hist[["Date", "Close"]].to_dict("records")


def get_price_history(ticker: str, period: str = "1y") -> list:
    return get_or_fetch(
        f"history:{ticker}:{period}", TTL_SLOW, lambda: _fetch_history_raw(ticker, period)
    )


def _fetch_news_raw(ticker: str) -> list:
    t = yf.Ticker(ticker)
    items = t.news or []
    parsed = []
    for n in items[:5]:
        # yfinance's news schema changed: newer versions nest fields under
        # "content", older versions had them flat. Handle both.
        content = n.get("content", n)
        title = content.get("title")
        publisher = (content.get("provider") or {}).get("displayName") or content.get("publisher")
        link = (content.get("canonicalUrl") or {}).get("url") or content.get("link")
        if title:
            parsed.append({"title": title, "publisher": publisher, "link": link})
    return parsed


def get_recent_news(ticker: str) -> list:
    return get_or_fetch(f"news:{ticker}", TTL_FAST, lambda: _fetch_news_raw(ticker))


def _fetch_insider_raw(ticker: str) -> dict:
    t = yf.Ticker(ticker)
    try:
        df = t.insider_transactions
        if df is None or df.empty:
            return {"summary": "No recent insider transaction data available."}
        recent = df.head(5)
        lines = []
        for _, row in recent.iterrows():
            lines.append(f"{row.get('Insider', 'Unknown')}: {row.get('Transaction', '')} {row.get('Shares', '')} shares")
        return {"summary": "; ".join(lines)}
    except Exception:
        return {"summary": "Insider transaction data not available for this ticker."}


def get_insider_activity(ticker: str) -> dict:
    return get_or_fetch(f"insider:{ticker}", TTL_SLOW, lambda: _fetch_insider_raw(ticker))


def get_peer_companies(ticker: str, limit: int = 5) -> list:
    """Same-sector companies from the S&P 500 universe, as a practical
    stand-in for 'competitors' -- not a perfect competitive analysis, but
    a reasonable, honest proxy from data we actually have.

    Uses the ticker's OWN GICS sector from our universe data (not
    yfinance's differently-named sector field, e.g. yfinance says
    "Technology" while our universe/GICS data says "Information
    Technology" -- comparing across those two taxonomies silently
    matched nothing)."""
    from universe.sp500 import get_universe
    universe = get_universe()
    this_company = next((r for r in universe if r["ticker"] == ticker.upper()), None)
    if not this_company:
        return []
    sector = this_company["sector"]
    peers = [r for r in universe if r["sector"] == sector and r["ticker"] != ticker.upper()]
    return [p["ticker"] + " (" + p["name"] + ")" for p in peers[:limit]]


def get_technical_signal(ticker: str) -> str:
    history = get_price_history(ticker, period="1y")
    if not history or len(history) < 200:
        return "Not enough price history to compute moving averages."
    closes = [h["Close"] for h in history]
    ma50 = sum(closes[-50:]) / 50
    ma200 = sum(closes[-200:]) / 200
    # No $ sign at all -- Streamlit's markdown renderer treats a pair of
    # dollar signs as LaTeX math mode, which garbled this line no matter
    # how it was escaped. Using "USD" instead sidesteps the issue entirely.
    if ma50 > ma200:
        return f"50-day average ({ma50:.2f} USD) is above the 200-day average ({ma200:.2f} USD)."
    return f"50-day average ({ma50:.2f} USD) is below the 200-day average ({ma200:.2f} USD)."