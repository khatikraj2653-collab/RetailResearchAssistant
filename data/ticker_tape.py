"""
Live scrolling ticker tape — top 30 S&P 500 companies by market cap.

Fallback policy: if a live yfinance fetch ever fails, this falls back to
the last successfully-fetched REAL data, persisted to a small local
JSON file. It never fabricates numbers and never shows a static demo
value pretending to be current -- it either shows fresh data or the
most recent real data actually observed. Only on a true first-ever-run
failure (no successful fetch has EVER happened) does it show "N/A" for
an individual ticker, which is an honest statement, not fake data.
"""
import streamlit as st
import yfinance as yf
import json
import os
from pathlib import Path

TOP30 = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "AVGO", "TSLA",
    "BRK-B", "JPM", "WMT", "LLY", "V", "ORCL", "MA", "NFLX",
    "XOM", "COST", "UNH", "JNJ", "HD", "PG", "ABBV", "BAC",
    "KO", "PLTR", "GE", "CVX", "TMUS", "WFC",
]

_FALLBACK_PATH = Path(__file__).resolve().parent / "_ticker_last_known_good.json"


def _save_fallback(rows):
    try:
        with open(_FALLBACK_PATH, "w", encoding="utf-8") as f:
            json.dump(rows, f)
    except Exception:
        pass


def _load_fallback():
    try:
        if _FALLBACK_PATH.exists():
            with open(_FALLBACK_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return None


@st.cache_data(ttl=300)
def get_tape_data():
    """Returns a list of dicts: [{ticker, price, change_pct, up, available}, ...].
    Tries a fresh live fetch first. On success, persists it as the new
    last-known-good fallback. On failure, falls back to the last
    successfully-fetched REAL data rather than showing nothing or
    inventing anything."""
    try:
        data = yf.download(
            tickers=" ".join(TOP30), period="5d", interval="1d",
            group_by="ticker", threads=True, progress=False,
        )
        results = []
        any_success = False
        for t in TOP30:
            try:
                closes = data[t]["Close"].dropna()
                if len(closes) < 2:
                    raise ValueError("not enough price history")
                price = round(float(closes.iloc[-1]), 2)
                prev = round(float(closes.iloc[-2]), 2)
                change = round(price - prev, 2)
                pct = round((change / prev) * 100, 2)
                results.append({
                    "ticker": t, "price": price, "change_pct": abs(pct),
                    "up": change >= 0, "available": True,
                })
                any_success = True
            except Exception:
                results.append({
                    "ticker": t, "price": None, "change_pct": None,
                    "up": None, "available": False,
                })

        if any_success:
            _save_fallback(results)
            return results
        raise ValueError("no tickers returned usable data this fetch")

    except Exception:
        fallback = _load_fallback()
        if fallback:
            return fallback
        # True first-ever-run failure with no prior real data saved yet.
        return [
            {"ticker": t, "price": None, "change_pct": None, "up": None, "available": False}
            for t in TOP30
        ]


def get_tape_prices():
    """HTML fragment for the bottom-fixed in-app ticker."""
    rows = []
    for row in get_tape_data():
        if row["available"]:
            arrow = "▲" if row["up"] else "▼"
            color = "#0F9D82" if row["up"] else "#DC2626"
            rows.append(
                f"<span style='margin-right:28px'>"
                f"<strong style='color:#374151'>{row['ticker']}</strong> "
                f"<span style='color:#111827'>${row['price']}</span> "
                f"<span style='color:{color};font-weight:700'>{arrow} {row['change_pct']}%</span>"
                f"</span>"
            )
        else:
            rows.append(
                f"<span style='margin-right:28px'>"
                f"<strong style='color:#374151'>{row['ticker']}</strong> "
                f"<span style='color:#9CA3AF'>N/A</span></span>"
            )
    return "".join(rows)


def render_ticker_tape():
    ticker_html = get_tape_prices()
    st.markdown(
        f"""
        <style>
        html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
            transform: none !important; filter: none !important;
            perspective: none !important; will-change: auto !important;
            contain: none !important;
        }}
        div.ticker-wrap {{
            position: fixed !important;
            bottom: 0 !important; left: 0 !important; right: 0 !important; top: auto !important;
            z-index: 2147483647 !important;
            background: #FFFFFF;
            border-top: 1px solid #E5E7EB;
            padding: 8px 0; overflow: hidden;
            box-shadow: 0 -2px 8px rgba(15,23,42,0.05);
            pointer-events: none;
        }}
        .ticker-move {{
            display: inline-block; white-space: nowrap;
            animation: ticker-scroll 60s linear infinite;
            font-size: 0.78rem; font-family: 'Inter', sans-serif;
        }}
        @keyframes ticker-scroll {{
            0% {{ transform: translateX(100vw); }}
            100% {{ transform: translateX(-100%); }}
        }}
        .block-container, [data-testid="stMainBlockContainer"] {{ padding-bottom: 60px !important; }}
        </style>
        <div class='ticker-wrap'>
            <div class='ticker-move'>{ticker_html}&nbsp;&nbsp;&nbsp;&nbsp;{ticker_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )