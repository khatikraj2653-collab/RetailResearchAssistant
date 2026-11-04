"""
Price-tag stat card — butter background with a punched hole, mono label,
serif value, coral sublabel.
"""

import streamlit as st


def gradient_stat_card(label: str, value: str, sublabel: str = "", gradient: str = "purple", icon: str = ""):
    """Renders one price-tag stat card."""
    st.markdown(
        f"""
        <div style="
            position: relative;
            background: #FFF1D0;
            border: 1px solid #EAD9AE;
            border-radius: 14px;
            padding: 18px 20px;
            box-shadow: 0 3px 0 #EAD9AE;
            min-height: 100px;
        ">
            <div style="position:absolute;top:12px;right:14px;width:10px;height:10px;border-radius:50%;
                        background:#FFF8EE;border:1.5px solid #D6C6A2;box-shadow:inset 0 1.5px 2px rgba(0,0,0,0.22);"></div>
            <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                <div style="font-family:'DM Mono',ui-monospace,Menlo,Consolas,monospace;font-size:0.72rem;letter-spacing:0.05em;text-transform:uppercase;color:#6B5E45;">{label}</div>
                <div style="font-size:1rem;">{icon}</div>
            </div>
            <div style="font-family:'Fraunces',Georgia,serif;font-size:1.7rem;font-weight:800;margin-top:6px;color:#12372A;">{value}</div>
            <div style="font-family:'DM Mono',ui-monospace,Menlo,Consolas,monospace;font-size:0.72rem;color:#D9482B;margin-top:6px;">{sublabel}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )