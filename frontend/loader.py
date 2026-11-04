"""Shared full-screen loader for Retail Research Assistant pages.

Usage:
    import streamlit as st
    st.set_page_config(...)
    from loader import show_loader
    _loader = show_loader("Loading Dashboard…")
    # ... rest of the page ...
    _loader.empty()
"""
import streamlit as st

_SPINNER_HTML = """
<div style="position:fixed;inset:0;display:flex;align-items:center;justify-content:center;
            background:#0E1117;z-index:999999;flex-direction:column;gap:14px;">
  <div style="width:44px;height:44px;border:3px solid rgba(76,175,80,.2);
              border-top-color:#4CAF50;border-radius:50%;
              animation:rr-sp 0.9s linear infinite;"></div>
  <div style="color:#C7D1DF;font-family:Inter,sans-serif;font-size:14px;">
    {message}
  </div>
  <style>@keyframes rr-sp{{to{{transform:rotate(360deg)}}}}</style>
</div>
"""


def show_loader(message: str = "Loading…"):
    """Render a full-screen green-themed spinner and return the placeholder
    so the caller can .empty() it once the page has rendered."""
    placeholder = st.empty()
    placeholder.markdown(_SPINNER_HTML.format(message=message), unsafe_allow_html=True)
    return placeholder
