"""
Live scrolling ticker tape — top 30 S&P 500 companies by market cap,
light theme to match Sovrenn's clean aesthetic.

get_tape_data() is the single source of real, cached, live price data
(15-minute TTL). Both the bottom-fixed in-app ticker (render_ticker_tape,
used on Dashboard/Stock Research/etc.) and the landing page's top ticker
strip (built server-side in frontend/app.py) build their HTML markup
from this same shared, real data -- so there is exactly one live data
source, not two separately-fetched or fake copies.
"""
import streamlit as st
import yfinance as yf

TOP30 = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "AVGO", "TSLA",
    "BRK-B", "JPM", "WMT", "LLY", "V", "ORCL", "MA", "NFLX",
    "XOM", "COST", "UNH", "JNJ", "HD", "PG", "ABBV", "BAC",
    "KO", "PLTR", "GE", "CVX", "TMUS", "WFC",
]


@st.cache_data(ttl=900)
def get_tape_data():
    """Returns a list of dicts: [{ticker, price, change_pct, up}, ...]
    for TOP30, using real live/recent yfinance data. Cached 15 minutes
    so this is the single fetch shared by every consumer."""
    results = []
    try:
        data = yf.download(
            tickers=" ".join(TOP30), period="5d", interval="1d",
            group_by="ticker", threads=True, progress=False,
        )
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
            except Exception:
                results.append({
                    "ticker": t, "price": None, "change_pct": None,
                    "up": None, "available": False,
                })
    except Exception:
        for t in TOP30:
            results.append({
                "ticker": t, "price": None, "change_pct": None,
                "up": None, "available": False,
            })
    return results


def get_tape_prices():
    """HTML fragment for the bottom-fixed in-app ticker (dark-on-light
    inline-styled spans), built from the shared get_tape_data()."""
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
        .ticker-wrap {{
            position: fixed; bottom: 0; left: 0; right: 0; z-index: 9999;
            background: #FFFFFF;
            border-top: 1px solid #E5E7EB;
            padding: 8px 0; overflow: hidden;
            box-shadow: 0 -2px 8px rgba(15,23,42,0.05);
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
        .block-container {{ padding-bottom: 60px !important; }}
        </style>
        <div class='ticker-wrap'>
            <div class='ticker-move'>{ticker_html}&nbsp;&nbsp;&nbsp;&nbsp;{ticker_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )