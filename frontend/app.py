import streamlit as st
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

st.set_page_config(
    page_title="Retail Research Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide ALL Streamlit chrome including sidebar and page nav
st.markdown("""
<style>
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
[data-testid="stDecoration"] { display: none; }
[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
[data-testid="stSidebarNav"] { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
[data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: #F8FAFC !important;
}
iframe[title="streamlit_component"] {
    background: transparent !important;
}
</style>
""", unsafe_allow_html=True)


# --- Live ticker data for the landing page's top strip. Reuses the
# exact same cached, real yfinance data (data/ticker_tape.py,
# get_tape_data(), 15-minute TTL) as the in-app bottom-fixed ticker --
# one shared live data source, not a second fetch or fake numbers.
def build_landing_ticker_html():
    try:
        from data.ticker_tape import get_tape_data
    except Exception:
        return '<div class="ti"><span class="tsym">Live prices unavailable</span></div>'

    try:
        rows = get_tape_data()
    except Exception:
        rows = []

    items = []
    for row in rows:
        if row.get("available"):
            dot_cls = "udt" if row["up"] else "ddt"
            chg_cls = "up" if row["up"] else "dn"
            arrow = "▲" if row["up"] else "▼"
            items.append(
                f'<div class="ti"><div class="dot {dot_cls}"></div>'
                f'<span class="tsym">{row["ticker"]}</span>'
                f'<span class="tprice">${row["price"]:.2f}</span>'
                f'<span class="tchg {chg_cls}">{arrow} {row["change_pct"]:.2f}%</span></div>'
            )
        else:
            items.append(
                f'<div class="ti"><span class="tsym">{row["ticker"]}</span>'
                f'<span class="tprice">N/A</span></div>'
            )

    if not items:
        return '<div class="ti"><span class="tsym">Live prices unavailable</span></div>'

    # Duplicate the row once so the CSS scroll animation loops seamlessly
    return "".join(items) + "".join(items)


# --- Fetch a small set of real, live news headlines to inject into the
# landing page. Reuses the same yfinance-backed news function the
# Stock Research page already uses -- no new dependency, no fake data.
# Wrapped defensively so a news-fetch hiccup never breaks the landing page.
NEWS_TICKERS = ["AAPL", "MSFT", "NVDA"]
HEADLINES_PER_TICKER = 2


def build_news_html():
    try:
        from data.yfinance_client import get_recent_news
    except Exception:
        return '<div class="news-empty">Live news is temporarily unavailable. Explore the tools to see full company news.</div>'

    cards = []
    for ticker in NEWS_TICKERS:
        try:
            items = get_recent_news(ticker) or []
        except Exception:
            items = []
        for item in items[:HEADLINES_PER_TICKER]:
            title = (item.get("title") or "").replace('"', "&quot;")
            link = item.get("link") or ""
            publisher = item.get("publisher") or "Source"
            if not title or not link:
                continue
            cards.append(f'''
            <a class="news-card" href="{link}" target="_blank" rel="noopener noreferrer">
                <div class="news-ticker-badge">{ticker}</div>
                <div class="news-title">{title}</div>
                <div class="news-meta">
                    <span class="news-publisher">{publisher}</span>
                    <span class="news-readmore">Read more →</span>
                </div>
            </a>
            ''')

    if not cards:
        return '<div class="news-empty">No live headlines available right now. Check back shortly, or explore Stock Research for company-specific news.</div>'

    return "\n".join(cards[:6])


# Load landing.html from project root
landing_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "landing.html")
with open(landing_path, "r", encoding="utf-8") as f:
    html_content = f.read()

# Inject real live ticker prices and real live news headlines
html_content = html_content.replace("<!--LIVE_TICKER_ITEMS-->", build_landing_ticker_html())
html_content = html_content.replace("<!--NEWS_ITEMS-->", build_news_html())

# Replace the placeholder goApp() with direct same-origin URL navigation.
PAGE_PATHS = [
    "/Dashboard",        # 0
    "/Stock_Research",   # 1
    "/Compare",           # 2
    "/Portfolio",         # 3
    "/Discovery",         # 4
    "/Learning",          # 5
]
goapp_js = (
    "function goApp(idx){"
    "var paths=" + str(PAGE_PATHS).replace("'", '"') + ";"
    "var target=paths[idx||0]||paths[0];"
    "try{window.parent.location.href=target;}"
    "catch(e){window.location.href=target;}"
    "}"
)
html_content = html_content.replace(
    "function goApp(){window.location.href='http://localhost:8501';}",
    goapp_js,
)

# CSS overrides for iframe rendering
iframe_fixes = """
<style>
body {
    background: #F8FAFC !important;
}
</style>
"""
html_content = html_content.replace("<head>", "<head>" + iframe_fixes)

# Render landing page
st.components.v1.html(html_content, height=3400, scrolling=True)