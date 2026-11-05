"""Shared loader for Retail Research Assistant pages.

Usage:
    import streamlit as st
    st.set_page_config(...)
    from loader import show_loader
    _loader = show_loader("Loading Dashboard…")
    # ... rest of the page ...
    _loader.empty()

Design rules:
- Only show the FULL-SCREEN overlay on the user's FIRST view of this page
  in the session (session_state flag). Later reruns (button clicks,
  typed input, filter changes) use a tiny non-blocking status line
  so the page stays interactive and NEVER goes pure-black mid-click.
- The returned placeholder is always safe to .empty() at script end.
"""
import streamlit as st

_FULLSCREEN_HTML = """
<div style="position:fixed;inset:0;display:flex;align-items:center;justify-content:center;
            background:#0E1117;z-index:999999;flex-direction:column;gap:14px;
            animation:rr-fade .35s ease-in;">
  <div style="width:44px;height:44px;border:3px solid rgba(76,175,80,.2);
              border-top-color:#4CAF50;border-radius:50%;
              animation:rr-sp 0.9s linear infinite;"></div>
  <div style="color:#C7D1DF;font-family:Inter,sans-serif;font-size:14px;">
    {message}
  </div>
  <style>
    @keyframes rr-sp{{to{{transform:rotate(360deg)}}}}
    @keyframes rr-fade{{from{{opacity:0}}to{{opacity:1}}}}
  </style>
</div>
"""

_INLINE_HTML = """
<div style="display:flex;align-items:center;gap:10px;padding:6px 0;margin:0 0 6px;
            color:#6B7280;font-family:Inter,sans-serif;font-size:12.5px;">
  <div style="width:14px;height:14px;border:2px solid rgba(76,175,80,.25);
              border-top-color:#4CAF50;border-radius:50%;
              animation:rr-sp-sm 0.9s linear infinite;"></div>
  <span>{message}</span>
  <style>@keyframes rr-sp-sm{{to{{transform:rotate(360deg)}}}}</style>
</div>
"""


def show_loader(message: str = "Loading…"):
    """Return a placeholder showing the right loader for this rerun.

    First visit: full-screen green overlay (hides heavy cold-start work).
    Subsequent reruns (button clicks, typing, filter changes): a small
    inline status line instead — the page stays visible so the user
    never sees a surprise all-black screen when they click something.
    """
    # Each page sets its own flag so navigating between pages still
    # shows the full-screen loader once per page.
    try:
        import inspect
        caller_file = inspect.stack()[1].filename
    except Exception:
        caller_file = "unknown"
    flag_key = f"_rr_loader_seen::{caller_file}"

    placeholder = st.empty()
    first_view = not st.session_state.get(flag_key, False)
    html = _FULLSCREEN_HTML if first_view else _INLINE_HTML
    placeholder.markdown(html.format(message=message), unsafe_allow_html=True)
    if first_view:
        st.session_state[flag_key] = True
    return placeholder
