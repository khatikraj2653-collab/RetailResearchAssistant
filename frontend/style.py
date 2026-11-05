"""
Price tag boutique theme (light) + inverted paper theme (dark).
Light: cream paper, pegboard dots, forest ink, tag-coral + butter accents.
Dark:  deep paper, dim pegboard, cream ink, warm-coral + butter accents.

Theme is stored in st.session_state['retail_theme'] and persists via
a localStorage round-trip. A tiny toggle in the sidebar switches it.
"""

import streamlit as st


# ---------- Light palette ----------
LIGHT = {
    "ACCENT": "#12372A", "ACCENT_DARK": "#0A2219",
    "ACCENT_HOVER": "#FF6B4A", "ACCENT_HOVER_DARK": "#D9482B",
    "BG": "#FFF8EE", "CARD_BG": "#FFFDF8",
    "BORDER": "#EADFC9", "BORDER_STRONG": "#D6C6A2",
    "BUTTER": "#FFD36B", "BUTTER_SOFT": "#FFF1D0",
    "TEXT": "#1A1A1A", "TEXT_MUTED": "#6B5E45", "TEXT_HEADING": "#12372A",
    "DOT_RGBA": "rgba(18,55,42,0.12)",
    "H1_SHADOW": "1px 1px 0 #EADFC9, 2px 2px 0 #E0D2B4",
}

# ---------- Dark palette (same aesthetic, inverted) ----------
DARK = {
    "ACCENT": "#4FC38A", "ACCENT_DARK": "#2F8A5D",
    "ACCENT_HOVER": "#FF8C6B", "ACCENT_HOVER_DARK": "#D96A48",
    "BG": "#121816", "CARD_BG": "#1B2420",
    "BORDER": "#2A3530", "BORDER_STRONG": "#3B4A42",
    "BUTTER": "#E3B559", "BUTTER_SOFT": "#2A2616",
    "TEXT": "#F5EEDA", "TEXT_MUTED": "#9CA89F", "TEXT_HEADING": "#E8DDB8",
    "DOT_RGBA": "rgba(245,238,218,0.07)",
    "H1_SHADOW": "1px 1px 0 #2A3530, 2px 2px 0 #1B2420",
}


def _current_theme_name() -> str:
    """Return 'light' or 'dark' from session_state (default 'light')."""
    return st.session_state.get("retail_theme", "light")


def _current_palette() -> dict:
    return DARK if _current_theme_name() == "dark" else LIGHT


# Backwards-compatible constants (other modules import these)
ACCENT_COLOR = LIGHT["ACCENT"]
ACCENT_DARK = LIGHT["ACCENT_DARK"]
ACCENT_HOVER = LIGHT["ACCENT_HOVER"]
ACCENT_HOVER_DARK = LIGHT["ACCENT_HOVER_DARK"]
BACKGROUND = LIGHT["BG"]
CARD_BACKGROUND = LIGHT["CARD_BG"]
BORDER_COLOR = LIGHT["BORDER"]
BORDER_STRONG = LIGHT["BORDER_STRONG"]
BUTTER = LIGHT["BUTTER"]
BUTTER_SOFT = LIGHT["BUTTER_SOFT"]
TEXT_MAIN = LIGHT["TEXT"]
TEXT_MUTED = LIGHT["TEXT_MUTED"]
TEXT_HEADING = LIGHT["TEXT_HEADING"]

GRADIENTS = {
    "coral": "linear-gradient(135deg, #FFFFFF, #FFFFFF)",
    "blue": "linear-gradient(135deg, #FFFFFF, #FFFFFF)",
    "teal": "linear-gradient(135deg, #FFFFFF, #FFFFFF)",
    "purple": "linear-gradient(135deg, #FFFFFF, #FFFFFF)",
}


def _render_theme_toggle():
    """Render the Light/Dark toggle in the sidebar."""
    current = _current_theme_name()
    with st.sidebar:
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        label = "☀️ Switch to light" if current == "dark" else "🌙 Switch to dark"
        if st.button(label, use_container_width=True, key="_retail_theme_toggle"):
            st.session_state["retail_theme"] = "light" if current == "dark" else "dark"
            st.rerun()


def apply_style():
    _render_theme_toggle()
    p = _current_palette()
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,wght@0,600;0,800;1,600&family=DM+Mono:wght@400;500&family=Inter:wght@400;500;600;700&display=swap');

        html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
            font-family: 'Inter', sans-serif !important;
            color: {p['TEXT']} !important;
        }}
        .stApp {{
            background:
                radial-gradient({p['DOT_RGBA']} 1.3px, transparent 1.6px) 0 0 / 26px 26px,
                {p['BG']} !important;
            color: {p['TEXT']} !important;
        }}
        [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
            background: transparent !important;
        }}

        [data-testid="stHeader"], [data-testid="stToolbar"] {{
            background-color: transparent !important;
        }}
        [data-testid="stDecoration"] {{
            background: linear-gradient(90deg, {p['ACCENT_HOVER']}, {p['BUTTER']}) !important;
            height: 3px !important;
        }}

        section[data-testid="stSidebar"] {{
            background-color: {p['CARD_BG']} !important;
            border-right: 1px solid {p['BORDER']} !important;
        }}
        section[data-testid="stSidebar"] * {{
            color: {p['TEXT']} !important;
        }}

        h1, h2, h3, h4 {{
            font-family: 'Fraunces', Georgia, serif !important;
            font-weight: 800 !important;
            color: {p['TEXT_HEADING']} !important;
            letter-spacing: -0.01em;
        }}
        h1 {{ text-shadow: {p['H1_SHADOW']}; }}

        p, span, label, .stMarkdown, [data-testid="stMarkdownContainer"] {{
            color: {p['TEXT']};
        }}
        .stCaption, [data-testid="stCaptionContainer"] {{
            color: {p['TEXT_MUTED']} !important;
            font-family: 'DM Mono', ui-monospace, Menlo, Consolas, monospace !important;
            font-size: 0.78rem !important;
            letter-spacing: 0.02em;
        }}
        label p {{
            font-family: 'DM Mono', ui-monospace, Menlo, Consolas, monospace !important;
            color: {p['TEXT_MUTED']} !important;
            font-size: 0.74rem !important;
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }}

        div[data-testid="stMetricValue"] {{
            color: {p['TEXT_HEADING']} !important;
            font-family: 'DM Mono', ui-monospace, Menlo, Consolas, monospace !important;
            font-weight: 500 !important;
        }}
        div[data-testid="stMetricLabel"] {{
            color: {p['TEXT_MUTED']} !important;
            font-family: 'DM Mono', ui-monospace, Menlo, Consolas, monospace !important;
            font-size: 0.72rem !important;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }}

        /* Extruded keys */
        .stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {{
            background: {p['ACCENT']} !important;
            color: {p['BG']} !important;
            border-radius: 8px !important;
            border: none !important;
            padding: 0.5rem 1.2rem;
            font-family: 'DM Mono', ui-monospace, Menlo, Consolas, monospace !important;
            font-weight: 500 !important;
            font-size: 0.82rem !important;
            letter-spacing: 0.04em;
            box-shadow: 0 4px 0 {p['ACCENT_DARK']}, 0 14px 22px -12px rgba(0,0,0,0.35) !important;
            transition: transform .12s, box-shadow .12s, background .15s;
        }}
        .stButton > button p, .stDownloadButton > button p, .stFormSubmitButton > button p {{
            color: {p['BG']} !important;
            font-family: 'DM Mono', ui-monospace, Menlo, Consolas, monospace !important;
        }}
        .stButton > button:hover, .stDownloadButton > button:hover, .stFormSubmitButton > button:hover {{
            background: {p['ACCENT_HOVER']} !important;
            color: {p['TEXT']} !important;
            transform: translateY(-2px);
            box-shadow: 0 6px 0 {p['ACCENT_HOVER_DARK']}, 0 16px 24px -12px rgba(217,72,43,0.5) !important;
        }}
        .stButton > button:hover p {{ color: {p['TEXT']} !important; }}
        .stButton > button:active, .stDownloadButton > button:active, .stFormSubmitButton > button:active {{
            transform: translateY(3px);
            box-shadow: 0 1px 0 {p['ACCENT_HOVER_DARK']} !important;
        }}

        /* Cards */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: {p['CARD_BG']} !important;
            border-radius: 14px !important;
            border: 1px solid {p['BORDER']} !important;
            box-shadow: 0 1px 0 {p['BORDER_STRONG']}, 0 2px 0 {p['CARD_BG']}, 0 3px 0 {p['BORDER_STRONG']},
                        0 22px 34px -24px rgba(0,0,0,0.5) !important;
            padding: 0.75rem;
        }}

        div[data-testid="stMetric"] {{
            background-color: {p['BUTTER_SOFT']} !important;
            border: 1px solid {p['BORDER_STRONG']} !important;
            border-radius: 14px !important;
            padding: 1rem;
            box-shadow: 0 3px 0 {p['BORDER_STRONG']} !important;
        }}

        .stTextInput input, .stNumberInput input, .stTextArea textarea {{
            background-color: {p['CARD_BG']} !important;
            border: 1px solid {p['BORDER_STRONG']} !important;
            border-radius: 8px !important;
            color: {p['TEXT']} !important;
        }}
        .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {{
            border-color: {p['ACCENT']} !important;
            box-shadow: 0 0 0 3px rgba(255,107,74,0.22) !important;
        }}

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{ gap: 4px; border-bottom: 1px solid {p['BORDER_STRONG']}; }}
        .stTabs [data-baseweb="tab"] {{
            font-family: 'DM Mono', ui-monospace, Menlo, Consolas, monospace;
            color: {p['TEXT_MUTED']};
            letter-spacing: 0.04em;
        }}
        .stTabs [aria-selected="true"] {{ color: {p['ACCENT']} !important; }}
        .stTabs [data-baseweb="tab-highlight"] {{ background: {p['ACCENT_HOVER']} !important; height: 3px !important; }}
        .stTabs [data-baseweb="tab-border"] {{ background: transparent !important; }}

        div[data-testid="stDataFrame"], div[data-testid="stDataEditor"] {{
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid {p['BORDER']} !important;
        }}
        div[data-testid="stDataFrame"] thead tr th {{
            color: {p['ACCENT_HOVER_DARK']} !important;
            font-weight: 700 !important;
        }}

        [data-testid="stFileUploader"] {{
            background-color: {p['CARD_BG']} !important;
            border: 1.5px dashed {p['BORDER_STRONG']} !important;
            border-radius: 10px !important;
        }}

        div[data-testid="stAlert"] {{
            background-color: {p['BUTTER_SOFT']} !important;
            color: {p['TEXT']} !important;
            border-radius: 10px !important;
            border: 1px dashed {p['ACCENT']} !important;
        }}

        .stRadio label {{ color: {p['TEXT']} !important; }}
        hr {{ border-color: {p['BORDER_STRONG']} !important; }}

        .theme-pill {{
            display: inline-block;
            background-color: {p['BUTTER']};
            color: {p['ACCENT']};
            border-radius: 6px 20px 20px 6px;
            padding: 0.15rem 0.8rem;
            font-family: 'DM Mono', ui-monospace, Menlo, Consolas, monospace;
            font-size: 0.7rem;
            font-weight: 500;
            letter-spacing: 0.05em;
            margin: 0.15rem 0.3rem 0.5rem 0;
            border: 1.5px dashed {p['ACCENT']};
        }}

        footer {{ visibility: hidden; }}
        </style>
        """,
        unsafe_allow_html=True,
    )
