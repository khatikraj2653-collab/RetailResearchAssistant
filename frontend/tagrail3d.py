"""
3D price-tag rail for the dashboard: retail tickers hang from a rail and swing
when dragged. A three.js scene in a transparent components iframe
(see static/tagrail3d.html). The scene is illustrative and uses no live data.
"""
import os

import streamlit.components.v1 as components

_TEMPLATE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "tagrail3d.html")


def render_tag_rail(height=300):
    with open(_TEMPLATE_PATH, "r", encoding="utf-8") as f:
        html = f.read()
    components.html(html, height=height, scrolling=False)
