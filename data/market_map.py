"""
Data for the 3D market map: about 60 large S&P 500 companies grouped by sector.

Tile size uses an approximate market-cap weight (in $bn, reviewed by hand and
softened with a power so small companies stay visible), so the map needs no
market-cap lookups. Prices come from ONE batched yfinance call and are cached
for 2 hours. If a fetch fails, the last real snapshot is reused; nothing is
ever invented, and with no snapshot at all the map simply shows "not yet
available".
"""
import json
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st
import yfinance as yf

CACHE_TTL_SECONDS = 2 * 60 * 60

# (ticker, short name, sector, approximate market cap in $bn)
MARKET_MAP = [
    ("NVDA", "Nvidia", "Technology", 4300), ("AAPL", "Apple", "Technology", 3900),
    ("MSFT", "Microsoft", "Technology", 3800), ("AVGO", "Broadcom", "Technology", 1600),
    ("ORCL", "Oracle", "Technology", 800), ("AMD", "AMD", "Technology", 350),
    ("CSCO", "Cisco", "Technology", 270), ("CRM", "Salesforce", "Technology", 250),
    ("ADBE", "Adobe", "Technology", 150), ("INTC", "Intel", "Technology", 110),
    ("TXN", "Texas Instruments", "Technology", 170),
    ("GOOGL", "Alphabet", "Communication", 3000), ("META", "Meta", "Communication", 1700),
    ("NFLX", "Netflix", "Communication", 500), ("TMUS", "T-Mobile", "Communication", 270),
    ("DIS", "Disney", "Communication", 200), ("T", "AT&T", "Communication", 170),
    ("VZ", "Verizon", "Communication", 170),
    ("AMZN", "Amazon", "Consumer Discretionary", 2400), ("TSLA", "Tesla", "Consumer Discretionary", 1300),
    ("HD", "Home Depot", "Consumer Discretionary", 380), ("MCD", "McDonald's", "Consumer Discretionary", 210),
    ("LOW", "Lowe's", "Consumer Discretionary", 150), ("NKE", "Nike", "Consumer Discretionary", 100),
    ("SBUX", "Starbucks", "Consumer Discretionary", 100),
    ("WMT", "Walmart", "Consumer Staples", 800), ("COST", "Costco", "Consumer Staples", 420),
    ("PG", "Procter & Gamble", "Consumer Staples", 360), ("KO", "Coca-Cola", "Consumer Staples", 300),
    ("PEP", "PepsiCo", "Consumer Staples", 200), ("TGT", "Target", "Consumer Staples", 45),
    ("BRK-B", "Berkshire Hathaway", "Financials", 1000), ("JPM", "JPMorgan Chase", "Financials", 850),
    ("V", "Visa", "Financials", 650), ("MA", "Mastercard", "Financials", 500),
    ("BAC", "Bank of America", "Financials", 380), ("WFC", "Wells Fargo", "Financials", 270),
    ("GS", "Goldman Sachs", "Financials", 220), ("AXP", "American Express", "Financials", 230),
    ("LLY", "Eli Lilly", "Health Care", 900), ("JNJ", "Johnson & Johnson", "Health Care", 450),
    ("ABBV", "AbbVie", "Health Care", 380), ("UNH", "UnitedHealth", "Health Care", 300),
    ("MRK", "Merck", "Health Care", 250), ("TMO", "Thermo Fisher", "Health Care", 200),
    ("ISRG", "Intuitive Surgical", "Health Care", 180), ("PFE", "Pfizer", "Health Care", 150),
    ("GE", "GE Aerospace", "Industrials", 300), ("CAT", "Caterpillar", "Industrials", 280),
    ("RTX", "RTX", "Industrials", 230), ("HON", "Honeywell", "Industrials", 140),
    ("DE", "Deere", "Industrials", 140), ("UPS", "UPS", "Industrials", 90),
    ("XOM", "Exxon Mobil", "Energy", 480), ("CVX", "Chevron", "Energy", 280),
    ("COP", "ConocoPhillips", "Energy", 120),
    ("LIN", "Linde", "Materials, utilities, real estate", 220), ("NEE", "NextEra Energy", "Materials, utilities, real estate", 150),
    ("PLD", "Prologis", "Materials, utilities, real estate", 100), ("SHW", "Sherwin-Williams", "Materials, utilities, real estate", 90),
]

_FALLBACK_PATH = Path(__file__).resolve().parent / "_market_map_last_known_good.json"


def _pct(closes, back):
    """Percent change from `back` sessions ago to the latest close (None if not enough history)."""
    if len(closes) <= back:
        return None
    start = float(closes.iloc[-1 - back])
    if not start:
        return None
    return round((float(closes.iloc[-1]) / start - 1.0) * 100.0, 2)


def _save_fallback(payload):
    try:
        with open(_FALLBACK_PATH, "w", encoding="utf-8") as f:
            json.dump(payload, f)
    except Exception:
        pass


def _load_fallback():
    try:
        if _FALLBACK_PATH.exists():
            with open(_FALLBACK_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return None


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def get_market_map_data():
    """{"asof": ISO time, "rows": [{t, n, s, w, p, d1, w1, m1}]} or None if no real data exists yet."""
    try:
        tickers = [m[0] for m in MARKET_MAP]
        data = yf.download(
            tickers=" ".join(tickers), period="2mo", interval="1d",
            group_by="ticker", threads=True, progress=False,
        )
        rows, ok = [], 0
        for t, name, sector, cap in MARKET_MAP:
            row = {"t": t, "n": name, "s": sector, "w": round(cap ** 0.7, 2), "p": None, "d1": None, "w1": None, "m1": None}
            try:
                closes = data[t]["Close"].dropna()
                if len(closes) >= 2:
                    row["p"] = round(float(closes.iloc[-1]), 2)
                    row["d1"], row["w1"], row["m1"] = _pct(closes, 1), _pct(closes, 5), _pct(closes, 21)
                    ok += 1
            except Exception:
                pass
            rows.append(row)
        if ok:
            payload = {"asof": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), "rows": rows}
            _save_fallback(payload)
            return payload
        raise ValueError("no tickers returned usable data")
    except Exception:
        return _load_fallback()


def get_market_map_json():
    """JSON text for embedding in a page ('null' when there is no data)."""
    try:
        payload = get_market_map_data()
    except Exception:
        payload = None
    return json.dumps(payload).replace("</", "<\\/")
