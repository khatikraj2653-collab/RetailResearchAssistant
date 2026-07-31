"""
Sovrenn-style light theme: white background, teal/green accent, clean
data tables, rounded pill buttons, subtle card borders.
"""

import streamlit as st

ACCENT_COLOR = "#0F9D82"      # teal/green — buttons, active tabs
ACCENT_DARK = "#0B7C68"
BACKGROUND = "#F5F6F8"
CARD_BACKGROUND = "#FFFFFF"
BORDER_COLOR = "#E5E7EB"
TEXT_MAIN = "#111827"
TEXT_MUTED = "#6B7280"
TEXT_HEADING = "#0F172A"

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
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
            background-color: {BACKGROUND} !important;
            font-family: 'Inter', sans-serif !important;
            color: {TEXT_MAIN} !important;
        }}

        [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] {{
            background-color: {BACKGROUND} !important;
        }}

        section[data-testid="stSidebar"] {{
            background-color: {CARD_BACKGROUND} !important;
            border-right: 1px solid {BORDER_COLOR} !important;
        }}
        section[data-testid="stSidebar"] * {{
            color: {TEXT_MAIN} !important;
        }}

        h1, h2, h3, h4 {{
            font-weight: 700 !important;
            color: {TEXT_HEADING} !important;
            letter-spacing: -0.01em;
        }}

        p, span, label, .stMarkdown, [data-testid="stMarkdownContainer"] {{
            color: {TEXT_MAIN};
        }}
        .stCaption, [data-testid="stCaptionContainer"] {{
            color: {TEXT_MUTED} !important;
        }}

        div[data-testid="stMetricValue"] {{ color: {TEXT_HEADING} !important; font-weight: 700 !important; }}
        div[data-testid="stMetricLabel"] {{ color: {TEXT_MUTED} !important; font-size: 0.75rem !important; }}

        /* Rounded pill buttons, teal/green, matching "Analyse ↗" style */
        .stButton > button {{
            background: {ACCENT_COLOR} !important;
            color: #fff !important;
            border-radius: 8px !important;
            border: none !important;
            padding: 0.5rem 1.2rem;
            font-weight: 600 !important;
            font-size: 0.85rem !important;
            transition: all 0.15s ease;
        }}
        .stButton > button:hover {{
            background: {ACCENT_DARK} !important;
            color: #fff !important;
        }}

        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: {CARD_BACKGROUND} !important;
            border-radius: 12px !important;
            border: 1px solid {BORDER_COLOR} !important;
            box-shadow: 0 1px 3px rgba(15,23,42,0.04) !important;
            padding: 0.75rem;
        }}

        div[data-testid="stMetric"] {{
            background-color: {CARD_BACKGROUND} !important;
            border: 1px solid {BORDER_COLOR} !important;
            border-radius: 12px !important;
            padding: 1rem;
            box-shadow: 0 1px 3px rgba(15,23,42,0.04) !important;
        }}

        .stTextInput input, .stNumberInput input {{
            background-color: {CARD_BACKGROUND} !important;
            border: 1px solid {BORDER_COLOR} !important;
            border-radius: 8px !important;
            color: {TEXT_MAIN} !important;
        }}
        .stTextInput input:focus, .stNumberInput input:focus {{
            border-color: {ACCENT_COLOR} !important;
            box-shadow: 0 0 0 3px rgba(15,157,130,0.12) !important;
        }}

        div[data-testid="stDataFrame"], div[data-testid="stDataEditor"] {{
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid {BORDER_COLOR} !important;
        }}
        div[data-testid="stDataFrame"] thead tr th {{
            color: {ACCENT_COLOR} !important;
            font-weight: 700 !important;
        }}

        [data-testid="stFileUploader"] {{
            background-color: {CARD_BACKGROUND} !important;
            border: 1px dashed {BORDER_COLOR} !important;
            border-radius: 10px !important;
        }}

        div[data-testid="stAlert"] {{
            background-color: #EAFBF6 !important;
            color: {TEXT_MAIN} !important;
            border-radius: 10px !important;
            border: 1px solid #C9F0E4 !important;
        }}

        .stRadio label {{
            color: {TEXT_MAIN} !important;
        }}

        /* Pill tags — like the "Featured" badge */
        .theme-pill {{
            display: inline-block;
            background-color: #EAFBF6;
            color: {ACCENT_DARK};
            border-radius: 999px;
            padding: 0.15rem 0.7rem;
            font-size: 0.72rem;
            font-weight: 600;
            margin: 0.15rem 0.3rem 0.5rem 0;
            border: 1px solid #C9F0E4;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )