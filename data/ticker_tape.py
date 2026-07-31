"""
Live scrolling ticker tape — top 30 S&P 500 companies by market cap,
light theme to match Sovrenn's clean aesthetic.
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
def get_tape_prices():
    try:
        data = yf.download(
            tickers=" ".join(TOP30), period="5d", interval="1d",
            group_by="ticker", threads=True, progress=False,
        )
        rows = []
        for t in TOP30:
            try:
                closes = data[t]["Close"].dropna()
                if len(closes) < 2:
                    raise ValueError("not enough price history")
                price = round(float(closes.iloc[-1]), 2)
                prev = round(float(closes.iloc[-2]), 2)
                change = round(price - prev, 2)
                pct = round((change / prev) * 100, 2)
                arrow = "▲" if change >= 0 else "▼"
                color = "#0F9D82" if change >= 0 else "#DC2626"
                rows.append(
                    f"<span style='margin-right:28px'>"
                    f"<strong style='color:#374151'>{t}</strong> "
                    f"<span style='color:#111827'>${price}</span> "
                    f"<span style='color:{color};font-weight:700'>{arrow} {abs(pct)}%</span>"
                    f"</span>"
                )
            except Exception:
                rows.append(
                    f"<span style='margin-right:28px'>"
                    f"<strong style='color:#374151'>{t}</strong> "
                    f"<span style='color:#9CA3AF'>N/A</span></span>"
                )
        return "".join(rows)
    except Exception:
        return "".join(
            f"<span style='margin-right:28px'>"
            f"<strong style='color:#374151'>{t}</strong> "
            f"<span style='color:#9CA3AF'>N/A</span></span>"
            for t in TOP30
        )


def render_ticker_tape():
    ticker_html = get_tape_prices()
    st.markdown(
        f"""
        <style>
        .rra-ticker-wrap {{
            position: fixed; bottom: 0; left: 0; right: 0; z-index: 9999;
            background: #FFFFFF;
            border-top: 1px solid #E5E7EB;
            padding: 8px 0; overflow: hidden;
            box-shadow: 0 -2px 8px rgba(15,23,42,0.05);
        }}
        .rra-ticker-move {{
            display: inline-block; white-space: nowrap;
            animation: rra-ticker-scroll 60s linear infinite;
            font-size: 0.78rem; font-family: 'Inter', sans-serif;
        }}
        @keyframes rra-ticker-scroll {{
            0% {{ transform: translateX(100vw); }}
            100% {{ transform: translateX(-100%); }}
        }}
        .block-container {{ padding-bottom: 60px !important; }}
        </style>
        <div class='rra-ticker-wrap'>
            <div class='rra-ticker-move'>{ticker_html}&nbsp;&nbsp;&nbsp;&nbsp;{ticker_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )