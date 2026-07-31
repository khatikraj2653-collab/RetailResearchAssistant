"""
SQLite-backed TTL cache — same pattern used in SemiBot / GoldBot / SilverBot.

Two tiers:
  TTL_SLOW = 24h  -> fundamentals, company profile, analyst targets (change rarely)
  TTL_FAST = 15m  -> live price / intraday quote data

Usage:
    from data.cache import get_or_fetch

    info = get_or_fetch("info:AAPL", ttl_seconds=TTL_SLOW, fetch_fn=lambda: yf_fetch_info("AAPL"))
"""

import sqlite3
import json
import time
import os
from pathlib import Path
from typing import Callable, Any

DB_PATH = Path(os.environ.get("RRA_CACHE_DB", "cache.sqlite3"))

TTL_SLOW = 24 * 60 * 60      # 24 hours — fundamentals, profile, financials
TTL_FAST = 15 * 60           # 15 minutes — price / quote


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS cache (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            fetched_at REAL NOT NULL
        )
        """
    )
    conn.commit()
    return conn


def get_cached(key: str, ttl_seconds: int):
    conn = _get_conn()
    row = conn.execute(
        "SELECT value, fetched_at FROM cache WHERE key = ?", (key,)
    ).fetchone()
    conn.close()
    if row is None:
        return None
    value_json, fetched_at = row
    if time.time() - fetched_at > ttl_seconds:
        return None
    try:
        return json.loads(value_json)
    except json.JSONDecodeError:
        return None


def set_cached(key: str, value: Any) -> None:
    conn = _get_conn()
    conn.execute(
        """
        INSERT INTO cache (key, value, fetched_at) VALUES (?, ?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value, fetched_at = excluded.fetched_at
        """,
        (key, json.dumps(value), time.time()),
    )
    conn.commit()
    conn.close()


def get_or_fetch(key: str, ttl_seconds: int, fetch_fn: Callable[[], Any]) -> Any:
    cached = get_cached(key, ttl_seconds)
    if cached is not None:
        return cached
    fresh = fetch_fn()
    set_cached(key, fresh)
    return fresh