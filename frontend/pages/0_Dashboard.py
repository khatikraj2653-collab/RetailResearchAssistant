import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))
sys.path.append(str(Path(__file__).resolve().parents[1]))

import streamlit as st

from style import apply_style
from components import gradient_stat_card

st.set_page_config(page_title="Retail Research Assistant", page_icon="📊", layout="wide")
apply_style()

from log_client import log_event
if "visit_logged_dashboard" not in st.session_state:
    st.session_state.visit_logged_dashboard = True
    log_event("visit", detail="Dashboard page")

from nav_bar import render_nav_bar
render_nav_bar(active="Dashboard")

st.title("📊 Retail Research Assistant")
st.caption("S&P 500 research tools — built for research, not prediction.")

st.write("")

col1, col2, col3 = st.columns(3)
with col1:
    gradient_stat_card("Companies Covered", "503", "Full S&P 500 index", icon="🏢")
with col2:
    gradient_stat_card("Theme Buckets", "18", "Sector & technology groups", icon="🔍")
with col3:
    gradient_stat_card("Research Tools", "5", "Built for research, not prediction", icon="⚡")

st.write("")
st.write("")

FEATURES = [
    {
        "icon": "🔎",
        "label": "Stock Research",
        "description": "Get a plain-English profile for any S&P 500 company — overview, valuation, and recent news.",
        "tags": ["Company profiles", "Valuation", "News"],
        "page": "pages/1_Stock_Research.py",
    },
    {
        "icon": "⚖️",
        "label": "Compare",
        "description": "Put 2-4 stocks side by side with a factual delta summary — no winner declared.",
        "tags": ["Side-by-side", "Valuation", "Growth"],
        "page": "pages/2_Compare.py",
    },
    {
        "icon": "📈",
        "label": "Portfolio Analysis",
        "description": "Upload or enter your holdings to see concentration, sector, and correlation risk flags.",
        "tags": ["Concentration", "Correlation", "Multi-format"],
        "page": "pages/3_Portfolio.py",
    },
    {
        "icon": "🔍",
        "label": "Discovery",
        "description": "Browse the S&P 500 by sector/technology theme — AI, semiconductors, biotech, and more.",
        "tags": ["18 themes", "503 companies"],
        "page": "pages/4_Discovery.py",
    },
    {
        "icon": "📚",
        "label": "Learning",
        "description": "Five original chapters on stock market fundamentals, downloadable, with a chapter-scoped Q&A assistant.",
        "tags": ["5 chapters", "Downloadable"],
        "page": "pages/5_Learning.py",
    },
]

cols = st.columns(2)
for i, feature in enumerate(FEATURES):
    with cols[i % 2]:
        with st.container(border=True):
            st.markdown(f"### {feature['icon']} {feature['label']}")
            st.write(feature["description"])

            tags_html = "".join(
                f'<span class="theme-pill">{tag}</span>' for tag in feature["tags"]
            )
            st.markdown(tags_html, unsafe_allow_html=True)

            if st.button(f"Open {feature['label']} →", key=f"open_{feature['label']}"):
                st.switch_page(feature["page"])

st.write("")
st.info(
    "This tool covers **research only** — stock profiles, comparisons, and portfolio "
    "risk analysis. It does not predict prices or give buy/sell recommendations."
)

from data.ticker_tape import render_ticker_tape
render_ticker_tape()