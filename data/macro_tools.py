"""
Macro factor fetchers via the FRED API -- CPI, PPI, Fed funds rate, USD
index. Requires FRED_API_KEY in .env. If missing, returns a graceful
"not configured" message per factor instead of crashing.
"""

import os
import requests

from data.cache import get_or_fetch, TTL_SLOW

FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"


def _fred_latest(series_id: str) -> str:
    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        return "Not configured (FRED_API_KEY missing in .env)"
    try:
        params = {
            "series_id": series_id, "api_key": api_key,
            "file_type": "json", "sort_order": "desc", "limit": 1,
        }
        resp = requests.get(FRED_BASE, params=params, timeout=10)
        resp.raise_for_status()
        obs = resp.json().get("observations", [])
        if not obs:
            return "No data available"
        return f"{obs[0]['value']} (as of {obs[0]['date']})"
    except Exception as e:
        return f"Unavailable ({type(e).__name__})"


def get_macro_snapshot() -> dict:
    return {
        "cpi": get_or_fetch("macro:cpi", TTL_SLOW, lambda: _fred_latest("CPIAUCSL")),
        "ppi": get_or_fetch("macro:ppi", TTL_SLOW, lambda: _fred_latest("PPIACO")),
        "fed_rate": get_or_fetch("macro:fed_rate", TTL_SLOW, lambda: _fred_latest("FEDFUNDS")),
        "usd_index": get_or_fetch("macro:usd_index", TTL_SLOW, lambda: _fred_latest("DTWEXBGS")),
    }