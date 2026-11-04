"""
Price tag boutique theme: cream paper with a pegboard dot grid, forest green
ink, tag-coral and butter accents, Fraunces headings and DM Mono labels.
Buttons are extruded keys, cards get a stacked-sheet edge.
"""

import streamlit as st

ACCENT_COLOR = "#12372A"      # forest — buttons, active tabs
ACCENT_DARK = "#0A2219"
ACCENT_HOVER = "#FF6B4A"      # tag coral
ACCENT_HOVER_DARK = "#D9482B"
BACKGROUND = "#FFF8EE"
CARD_BACKGROUND = "#FFFDF8"
BORDER_COLOR = "#EADFC9"
BORDER_STRONG = "#D6C6A2"
BUTTER = "#FFD36B"
BUTTER_SOFT = "#FFF1D0"
TEXT_MAIN = "#1A1A1A"
TEXT_MUTED = "#6B5E45"
TEXT_HEADING = "#12372A"

GRADIENTS = {
    "coral": "linear-gradient(135deg, #FFFFFF, #FFFFFF)",
    "blue": "linear-gradient(135deg, #FFFFFF, #FFFFFF)",
    "teal": "linear-gradient(135deg, #FFFFFF, #FFFFFF)",
    "purple": "linear-gradient(135deg, #FFFFFF, #FFFFFF)",
}


def apply_style():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,wght@0,600;0,800;1,600&family=DM+Mono:wght@400;500&family=Inter:wght@400;500;600;700&display=swap');

        html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
            font-family: 'Inter', sans-serif !important;
            color: {TEXT_MAIN} !important;
        }}
        .stApp {{
            background:
                radial-gradient(rgba(18,55,42,0.12) 1.3px, transparent 1.6px) 0 0 / 26px 26px,
                {BACKGROUND} !important;
            color: {TEXT_MAIN} !important;
        }}
        [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
            background: transparent !important;
        }}

        [data-testid="stHeader"], [data-testid="stToolbar"] {{
            background-color: transparent !important;
        }}
        [data-testid="stDecoration"] {{
            background: linear-gradient(90deg, {ACCENT_HOVER}, {BUTTER}) !important;
            height: 3px !important;
        }}

        section[data-testid="stSidebar"] {{
            background-color: {CARD_BACKGROUND} !important;
            border-right: 1px solid {BORDER_COLOR} !important;
        }}
        section[data-testid="stSidebar"] * {{
            color: {TEXT_MAIN} !important;
        }}

        h1, h2, h3, h4 {{
            font-family: 'Fraunces', Georgia, serif !important;
            font-weight: 800 !important;
            color: {TEXT_HEADING} !important;
            letter-spacing: -0.01em;
        }}
        h1 {{ text-shadow: 1px 1px 0 #EADFC9, 2px 2px 0 #E0D2B4; }}

        p, span, label, .stMarkdown, [data-testid="stMarkdownContainer"] {{
            color: {TEXT_MAIN};
        }}
        .stCaption, [data-testid="stCaptionContainer"] {{
            color: {TEXT_MUTED} !important;
            font-family: 'DM Mono', ui-monospace, Menlo, Consolas, monospace !important;
            font-size: 0.78rem !important;
            letter-spacing: 0.02em;
        }}
        label p {{
            font-family: 'DM Mono', ui-monospace, Menlo, Consolas, monospace !important;
            color: {TEXT_MUTED} !important;
            font-size: 0.74rem !important;
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }}

        div[data-testid="stMetricValue"] {{
            color: {TEXT_HEADING} !important;
            font-family: 'DM Mono', ui-monospace, Menlo, Consolas, monospace !important;
            font-weight: 500 !important;
        }}
        div[data-testid="stMetricLabel"] {{
            color: {TEXT_MUTED} !important;
            font-family: 'DM Mono', ui-monospace, Menlo, Consolas, monospace !important;
            font-size: 0.72rem !important;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }}

        /* Extruded keys */
        .stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {{
            background: {ACCENT_COLOR} !important;
            color: {BACKGROUND} !important;
            border-radius: 8px !important;
            border: none !important;
            padding: 0.5rem 1.2rem;
            font-family: 'DM Mono', ui-monospace, Menlo, Consolas, monospace !important;
            font-weight: 500 !important;
            font-size: 0.82rem !important;
            letter-spacing: 0.04em;
            box-shadow: 0 4px 0 {ACCENT_DARK}, 0 14px 22px -12px rgba(18,55,42,0.55) !important;
            transition: transform .12s, box-shadow .12s, background .15s;
        }}
        .stButton > button p, .stDownloadButton > button p, .stFormSubmitButton > button p {{
            color: {BACKGROUND} !important;
            font-family: 'DM Mono', ui-monospace, Menlo, Consolas, monospace !important;
        }}
        .stButton > button:hover, .stDownloadButton > button:hover, .stFormSubmitButton > button:hover {{
            background: {ACCENT_HOVER} !important;
            color: {TEXT_MAIN} !important;
            transform: translateY(-2px);
            box-shadow: 0 6px 0 {ACCENT_HOVER_DARK}, 0 16px 24px -12px rgba(217,72,43,0.5) !important;
        }}
        .stButton > button:hover p, .stDownloadButton > button:hover p, .stFormSubmitButton > button:hover p {{
            color: {TEXT_MAIN} !important;
        }}
        .stButton > button:active, .stDownloadButton > button:active, .stFormSubmitButton > button:active {{
            transform: translateY(3px);
            box-shadow: 0 1px 0 {ACCENT_HOVER_DARK} !important;
        }}

        /* Cards: stacked-sheet edge */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: {CARD_BACKGROUND} !important;
            border-radius: 14px !important;
            border: 1px solid {BORDER_COLOR} !important;
            box-shadow: 0 1px 0 {BORDER_STRONG}, 0 2px 0 #FFFDF8, 0 3px 0 {BORDER_STRONG},
                        0 22px 34px -24px rgba(18,55,42,0.45) !important;
            padding: 0.75rem;
        }}

        div[data-testid="stMetric"] {{
            background-color: {BUTTER_SOFT} !important;
            border: 1px solid #EAD9AE !important;
            border-radius: 14px !important;
            padding: 1rem;
            box-shadow: 0 3px 0 #EAD9AE !important;
        }}

        .stTextInput input, .stNumberInput input, .stTextArea textarea {{
            background-color: {CARD_BACKGROUND} !important;
            border: 1px solid {BORDER_STRONG} !important;
            border-radius: 8px !important;
            color: {TEXT_MAIN} !important;
        }}
        .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {{
            border-color: {ACCENT_COLOR} !important;
            box-shadow: 0 0 0 3px rgba(255,107,74,0.22) !important;
        }}

        /* Tabs: coral underline */
        .stTabs [data-baseweb="tab-list"] {{ gap: 4px; border-bottom: 1px solid {BORDER_STRONG}; }}
        .stTabs [data-baseweb="tab"] {{
            font-family: 'DM Mono', ui-monospace, Menlo, Consolas, monospace;
            color: {TEXT_MUTED};
            letter-spacing: 0.04em;
        }}
        .stTabs [aria-selected="true"] {{ color: {ACCENT_COLOR} !important; }}
        .stTabs [data-baseweb="tab-highlight"] {{ background: {ACCENT_HOVER} !important; height: 3px !important; }}
        .stTabs [data-baseweb="tab-border"] {{ background: transparent !important; }}

        div[data-testid="stDataFrame"], div[data-testid="stDataEditor"] {{
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid {BORDER_COLOR} !important;
        }}
        div[data-testid="stDataFrame"] thead tr th {{
            color: {ACCENT_HOVER_DARK} !important;
            font-weight: 700 !important;
        }}

        [data-testid="stFileUploader"] {{
            background-color: {CARD_BACKGROUND} !important;
            border: 1.5px dashed {BORDER_STRONG} !important;
            border-radius: 10px !important;
        }}

        div[data-testid="stAlert"] {{
            background-color: {BUTTER_SOFT} !important;
            color: {TEXT_MAIN} !important;
            border-radius: 10px !important;
            border: 1px dashed {ACCENT_COLOR} !important;
        }}

        .stRadio label {{
            color: {TEXT_MAIN} !important;
        }}

        hr {{ border-color: {BORDER_STRONG} !important; }}

        /* Price-tag pills */
        .theme-pill {{
            display: inline-block;
            background-color: {BUTTER};
            color: {ACCENT_COLOR};
            border-radius: 6px 20px 20px 6px;
            padding: 0.15rem 0.8rem;
            font-family: 'DM Mono', ui-monospace, Menlo, Consolas, monospace;
            font-size: 0.7rem;
            font-weight: 500;
            letter-spacing: 0.05em;
            margin: 0.15rem 0.3rem 0.5rem 0;
            border: 1.5px dashed {ACCENT_COLOR};
        }}

        footer {{ visibility: hidden; }}
        </style>
        """,
        unsafe_allow_html=True,
    )
