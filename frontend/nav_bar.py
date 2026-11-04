"""
Custom top navigation bar in the price tag boutique style — logo,
one extruded forest key for the active page, plain mono links for the rest.

Uses real <a href="/PageName"> links, which Streamlit's multipage router
resolves natively (no JS routing tricks needed) — clicking these performs
an actual page navigation, same as the sidebar.
"""

import streamlit as st

NAV_ITEMS = [
    {"label": "Dashboard", "path": "/Dashboard"},
    {"label": "Stock Research", "path": "/Stock_Research"},
    {"label": "Compare", "path": "/Compare"},
    {"label": "Portfolio", "path": "/Portfolio"},
    {"label": "Discovery", "path": "/Discovery"},
    {"label": "Learning", "path": "/Learning"},
]


def render_nav_bar(active: str):
    links_html = ""
    for item in NAV_ITEMS:
        is_active = item["label"] == active
        if is_active:
            links_html += (
                f'<a href="{item["path"]}" target="_self" style="'
                f'background:#12372A;color:#FFF8EE;padding:8px 18px;border-radius:8px;'
                f'font-family:\'DM Mono\',ui-monospace,Menlo,Consolas,monospace;letter-spacing:0.04em;'
                f'font-weight:500;font-size:0.8rem;text-decoration:none;margin-right:10px;'
                f'box-shadow:0 3px 0 #0A2219;display:inline-block;">{item["label"]}</a>'
            )
        else:
            links_html += (
                f'<a href="{item["path"]}" target="_self" style="'
                f'color:#6B5E45;padding:8px 14px;font-weight:500;font-size:0.8rem;'
                f'font-family:\'DM Mono\',ui-monospace,Menlo,Consolas,monospace;letter-spacing:0.04em;'
                f'text-decoration:none;margin-right:10px;display:inline-block;">'
                f'{item["label"]}</a>'
            )

    st.markdown(
        f"""
        <div style="
            display:flex;align-items:center;justify-content:space-between;
            background:#FFFDF8;border-bottom:1px solid #EADFC9;
            padding:14px 24px;margin:-1rem -1rem 1.5rem -1rem;
        ">
            <div style="display:flex;align-items:center;gap:8px;">
                <span style="font-size:1.3rem;">📊</span>
                <span style="font-family:'Fraunces',Georgia,serif;font-size:1.15rem;font-weight:800;color:#12372A;">
                    Retail<span style="color:#D9482B;">Research</span>
                </span>
            </div>
            <div style="display:flex;align-items:center;">
                {links_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )