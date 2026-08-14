import streamlit as st
import os
import sys
import json
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
sys.path.append(str(Path(__file__).resolve().parent.parent))

st.set_page_config(
    page_title="Retail Research Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# SEO tags injected into the real top-level document (st.markdown runs in
# Streamlit's own DOM, unlike st.components.v1.html which sandboxes into an
# iframe Google's crawler won't associate with this page's <head>).
st.markdown("""
<script>
(function() {
  document.title = "Retail Research Assistant — S&P 500 Research Platform";
  function setMeta(attr, key, content) {
    let el = document.querySelector(`meta[${attr}="${key}"]`);
    if (!el) { el = document.createElement('meta'); el.setAttribute(attr, key); document.head.appendChild(el); }
    el.setAttribute('content', content);
  }
  const desc = "S&P 500 research tools for company profiles, comparisons, and portfolio risk analysis — built for research, not prediction, by Raj Tejpal Khatik.";
  setMeta('name', 'description', desc);
  setMeta('property', 'og:title', "Retail Research Assistant — S&P 500 Research Platform");
  setMeta('property', 'og:description', desc);
  setMeta('property', 'og:type', 'website');
  setMeta('property', 'og:url', 'https://retailresearch-raj.streamlit.app/');
  setMeta('name', 'twitter:card', 'summary_large_image');
  setMeta('name', 'twitter:title', "Retail Research Assistant — S&P 500 Research Platform");
  setMeta('name', 'twitter:description', desc);

  let canonical = document.querySelector('link[rel="canonical"]');
  if (!canonical) { canonical = document.createElement('link'); canonical.setAttribute('rel', 'canonical'); document.head.appendChild(canonical); }
  canonical.setAttribute('href', 'https://retailresearch-raj.streamlit.app/');

  if (!document.getElementById('retailresearch-jsonld')) {
    const s = document.createElement('script');
    s.type = 'application/ld+json';
    s.id = 'retailresearch-jsonld';
    s.textContent = JSON.stringify({
      "@context": "https://schema.org",
      "@type": "SoftwareApplication",
      "name": "Retail Research Assistant",
      "applicationCategory": "FinanceApplication",
      "operatingSystem": "Web",
      "url": "https://retailresearch-raj.streamlit.app/",
      "description": desc,
      "author": {
        "@type": "Person",
        "name": "Raj Tejpal Khatik",
        "sameAs": [
          "https://www.linkedin.com/in/raj-khatik-6ab086395",
          "https://github.com/khatikraj2653-collab",
          "https://portfolio-raj.pages.dev/"
        ]
      }
    });
    document.head.appendChild(s);
  }
})();
</script>
""", unsafe_allow_html=True)

from log_client import log_event
if "visit_logged_landing" not in st.session_state:
    st.session_state.visit_logged_landing = True
    log_event("visit", detail="landing page")

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


# ============================================================
# S&P 500 multi-timeframe chart: real data for every tab (1D,
# 5D, 1M, 6M, YTD, 1Y, 5Y, Max), real Open/High/Low/Prev Close/
# 52-wk High/Low stats, all fetched once server-side and handed
# to the browser so tab-switching is instant client-side JS with
# no further server round-trips. Same honest fallback policy as
# the rest of the app: on any fetch failure, falls back to the
# last successfully-fetched REAL data (persisted to a local JSON
# file), never a fabricated number or shape.
# ============================================================
_SP500_FALLBACK_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "data", "_sp500_last_known_good.json"
)

PERIODS = {
    "1D": ("1d", "15m"),
    "5D": ("5d", "30m"),
    "1M": ("1mo", "1d"),
    "6M": ("6mo", "1d"),
    "YTD": ("ytd", "1d"),
    "1Y": ("1y", "1d"),
    "5Y": ("5y", "1wk"),
    "Max": ("max", "1mo"),
}


def _save_sp500_fallback(payload):
    try:
        with open(_SP500_FALLBACK_PATH, "w", encoding="utf-8") as f:
            json.dump(payload, f)
    except Exception:
        pass


def _load_sp500_fallback():
    try:
        if os.path.exists(_SP500_FALLBACK_PATH):
            with open(_SP500_FALLBACK_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return None


@st.cache_data(ttl=300)
def get_sp500_full_payload():
    try:
        import yfinance as yf
        ticker = yf.Ticker("^GSPC")

        day_hist = ticker.history(period="1d", interval="15m")
        if day_hist is None or day_hist.empty:
            raise ValueError("no 1D data available")

        current = round(float(day_hist["Close"].dropna().iloc[-1]), 2)
        day_open = round(float(day_hist["Open"].iloc[0]), 2)
        day_high = round(float(day_hist["High"].max()), 2)
        day_low = round(float(day_hist["Low"].min()), 2)

        info = {}
        try:
            info = ticker.fast_info or {}
        except Exception:
            info = {}
        prev_close = round(float(info.get("previousClose") or day_open), 2)
        wk52_high = round(float(info.get("yearHigh") or day_high), 2)
        wk52_low = round(float(info.get("yearLow") or day_low), 2)

        change = round(current - prev_close, 2)
        pct = round((change / prev_close) * 100, 2) if prev_close else 0.0

        series = {}
        for label, (period, interval) in PERIODS.items():
            try:
                hist = ticker.history(period=period, interval=interval)
                closes = hist["Close"].dropna().tolist()
                if len(closes) < 2:
                    continue
                series[label] = [round(float(c), 2) for c in closes]
            except Exception:
                continue

        if "1D" not in series:
            series["1D"] = day_hist["Close"].dropna().round(2).tolist()

        payload = {
            "available": True,
            "current": current,
            "change": change,
            "pct": abs(pct),
            "up": change >= 0,
            "open": day_open,
            "high": day_high,
            "low": day_low,
            "prevClose": prev_close,
            "wk52High": wk52_high,
            "wk52Low": wk52_low,
            "series": series,
        }
        _save_sp500_fallback(payload)
        return payload

    except Exception:
        fallback = _load_sp500_fallback()
        if fallback:
            return fallback
        return {"available": False}


def build_sp500_chart_html():
    payload = get_sp500_full_payload()
    if not payload.get("available"):
        return '<div class="sp-chart-empty">S&P 500 chart data not yet available.</div>'

    color = "#0D9488"
    arrow = "▲" if payload["up"] else "▼"
    sign = "+" if payload["up"] else "-"
    badge_bg = "#ECFDF5" if payload["up"] else "#FEF2F2"
    badge_color = "#0B7C68" if payload["up"] else "#B91C1C"
    data_json = json.dumps(payload["series"]).replace("</script>", "<\\/script>")

    tabs_html = "".join(
        f'<button class="sp-tab{" active" if p == "1D" else ""}" onclick="renderSPChart(\'{p}\')" data-period="{p}">{p}</button>'
        for p in PERIODS.keys()
    )

    return f'''
    <div class="sp-chart-card">
        <div class="sp-chart-top">
            <div>
                <div class="sp-chart-label">S&P 500</div>
                <div class="sp-chart-sublabel">Index · yfinance live data</div>
            </div>
        </div>
        <div class="sp-chart-row">
            <div class="sp-chart-value" id="sp-current">{payload["current"]:,.2f}</div>
            <div class="sp-chart-badge" id="sp-badge" style="background:{badge_bg};color:{badge_color}">{arrow} {payload["pct"]:.2f}%</div>
            <div class="sp-chart-change" id="sp-change" style="color:{badge_color}">{sign}{abs(payload["change"]):.2f} today</div>
        </div>
        <div class="sp-chart-sub">Live · updates every 5 min</div>
        <div class="sp-tabs">{tabs_html}</div>
        <svg width="100%" height="140" viewBox="0 0 620 140" id="sp-svg">
            <defs><linearGradient id="spg" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="{color}" stop-opacity="0.22"/>
                <stop offset="100%" stop-color="{color}" stop-opacity="0"/>
            </linearGradient></defs>
            <line id="sp-refline" x1="0" y1="0" x2="620" y2="0" stroke="#CBD5E1" stroke-width="1" stroke-dasharray="3,3"/>
            <polygon id="sp-fill" points="" fill="url(#spg)"/>
            <polyline id="sp-line" points="" fill="none" stroke="{color}" stroke-width="2"/>
        </svg>
        <div class="sp-stats-grid">
            <div><span class="sp-stat-label">Open</span><span class="sp-stat-value">{payload["open"]:,.2f}</span></div>
            <div><span class="sp-stat-label">High</span><span class="sp-stat-value">{payload["high"]:,.2f}</span></div>
            <div><span class="sp-stat-label">Low</span><span class="sp-stat-value">{payload["low"]:,.2f}</span></div>
            <div><span class="sp-stat-label">Prev close</span><span class="sp-stat-value">{payload["prevClose"]:,.2f}</span></div>
            <div><span class="sp-stat-label">52-wk high</span><span class="sp-stat-value">{payload["wk52High"]:,.2f}</span></div>
            <div><span class="sp-stat-label">52-wk low</span><span class="sp-stat-value">{payload["wk52Low"]:,.2f}</span></div>
        </div>
    </div>
    <script>
    window.__SP500_SERIES__ = {data_json};
    function renderSPChart(period) {{
        var data = window.__SP500_SERIES__[period];
        if (!data || data.length < 2) return;
        var lo = Math.min.apply(null, data), hi = Math.max.apply(null, data);
        var span = (hi - lo) || 1;
        var n = data.length, pts = [];
        for (var i = 0; i < n; i++) {{
            var x = (i / (n - 1)) * 620;
            var y = 120 - ((data[i] - lo) / span) * 110;
            pts.push(x.toFixed(1) + "," + y.toFixed(1));
        }}
        var line = pts.join(" ");
        document.getElementById("sp-line").setAttribute("points", line);
        document.getElementById("sp-fill").setAttribute("points", line + " 620,140 0,140");
        var refY = 120 - ((data[0] - lo) / span) * 110;
        document.getElementById("sp-refline").setAttribute("y1", refY.toFixed(1));
        document.getElementById("sp-refline").setAttribute("y2", refY.toFixed(1));
        document.querySelectorAll(".sp-tab").forEach(function(btn) {{
            btn.classList.toggle("active", btn.getAttribute("data-period") === period);
        }});
    }}
    renderSPChart("1D");
    </script>
    '''


# --- Live ticker data for the landing page's top strip.
def build_landing_ticker_html():
    try:
        from data.ticker_tape import get_tape_data
    except Exception:
        return '<div class="ti"><span class="tsym">Ticker data not yet available</span></div>'

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
        return '<div class="ti"><span class="tsym">Ticker data not yet available</span></div>'

    return "".join(items) + "".join(items)


# --- Live news headlines
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


landing_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "landing.html")
with open(landing_path, "r", encoding="utf-8") as f:
    html_content = f.read()

html_content = html_content.replace("<!--LIVE_TICKER_ITEMS-->", build_landing_ticker_html())
html_content = html_content.replace("<!--SP500_CHART-->", build_sp500_chart_html())
html_content = html_content.replace("<!--NEWS_ITEMS-->", build_news_html())

PAGE_PATHS = [
    "/Dashboard", "/Stock_Research", "/Compare", "/Portfolio", "/Discovery", "/Learning",
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

iframe_fixes = """
<style>
body { background: #F8FAFC !important; }
</style>
"""
html_content = html_content.replace("<head>", "<head>" + iframe_fixes)

st.components.v1.html(html_content, height=4650, scrolling=True)