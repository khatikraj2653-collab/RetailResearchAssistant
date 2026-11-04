"""
3D market map for the Discovery page: about 60 large S&P 500 companies as tiles
on a shelf board, grouped by sector. Height and colour show the price change
(1D / 1W / 1M). A three.js scene in a transparent components iframe
(see static/marketmap3d.html); prices come from data/market_map.py (2 hour cache).
"""
import os
import sys
from pathlib import Path

import streamlit.components.v1 as components

sys.path.append(str(Path(__file__).resolve().parents[1]))
from data.market_map import get_market_map_json

_TEMPLATE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "marketmap3d.html")


def render_market_map(height=600):
    with open(_TEMPLATE_PATH, "r", encoding="utf-8") as f:
        html = f.read()
    html = html.replace("/*__MM_DATA__*/null", get_market_map_json())
    components.html(html, height=height, scrolling=False)
