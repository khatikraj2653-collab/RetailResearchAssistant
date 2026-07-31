"""
Sovrenn-style stat card — white background, subtle border/shadow,
teal accent value, matching the site's clean card language.
"""

import streamlit as st


def gradient_stat_card(label: str, value: str, sublabel: str = "", gradient: str = "purple", icon: str = ""):
    """Renders one white stat card with a teal accent value."""
    st.markdown(
        f"""
        <div style="
            background: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 12px;
            padding: 18px 20px;
            box-shadow: 0 1px 3px rgba(15,23,42,0.04);
            min-height: 100px;
        ">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                <div style="font-size:0.75rem;font-weight:600;color:#6B7280;">{label}</div>
                <div style="font-size:1rem;">{icon}</div>
            </div>
            <div style="font-size:1.6rem;font-weight:800;margin-top:6px;color:#0F172A;">{value}</div>
            <div style="font-size:0.72rem;color:#0F9D82;margin-top:6px;font-weight:600;">{sublabel}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )