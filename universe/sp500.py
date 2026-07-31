"""
S&P 500 ticker universe with sector tags.

Reads from a locally downloaded CSV (sp500_constituents.csv) instead of
live-scraping Wikipedia — much more reliable, and the constituent list
barely changes (a handful of swaps per year), so a static file refreshed
occasionally is more than good enough.

To refresh later: re-download from
https://raw.githubusercontent.com/datasets/s-and-p-500-companies/main/data/constituents.csv
"""

import csv
from pathlib import Path

CSV_PATH = Path("sp500_constituents.csv")

_FALLBACK = [
    {"ticker": "AAPL", "name": "Apple Inc.", "sector": "Information Technology"},
    {"ticker": "MSFT", "name": "Microsoft Corp.", "sector": "Information Technology"},
    {"ticker": "NVDA", "name": "NVIDIA Corp.", "sector": "Information Technology"},
]


def get_universe(force_refresh: bool = False) -> list:
    if not CSV_PATH.exists():
        return _FALLBACK

    records = []
    with open(CSV_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(
                {
                    "ticker": row["Symbol"].replace(".", "-"),  # yfinance uses '-' e.g. BRK-B
                    "name": row["Security"],
                    "sector": row["GICS Sector"],
                    "sub_industry": row.get("GICS Sub-Industry", ""),
                }
            )
    return records or _FALLBACK


def get_sectors(records=None) -> list:
    records = records or get_universe()
    return sorted({r["sector"] for r in records})