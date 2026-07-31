"""
Long-term memory: persists analysis snapshots across sessions/restarts
in their own SQLite database (separate from the short-lived data cache),
so each feature's chatbot can reference past sessions, and Portfolio can
diff the current holdings against the most recently saved snapshot.
"""

import sqlite3
import json
import time
from pathlib import Path

DB_PATH = Path("history.sqlite3")


def _get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            feature TEXT NOT NULL,
            key_label TEXT NOT NULL,
            timestamp REAL NOT NULL,
            data_json TEXT NOT NULL
        )
        """
    )
    conn.commit()
    return conn


def save_history(feature: str, key_label: str, data: dict) -> int:
    conn = _get_conn()
    cur = conn.execute(
        "INSERT INTO history (feature, key_label, timestamp, data_json) VALUES (?, ?, ?, ?)",
        (feature, key_label, time.time(), json.dumps(data)),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def load_history(feature: str, key_label: str = None, limit: int = 10) -> list:
    conn = _get_conn()
    if key_label:
        rows = conn.execute(
            "SELECT id, key_label, timestamp, data_json FROM history "
            "WHERE feature = ? AND key_label = ? ORDER BY id DESC LIMIT ?",
            (feature, key_label, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT id, key_label, timestamp, data_json FROM history "
            "WHERE feature = ? ORDER BY id DESC LIMIT ?",
            (feature, limit),
        ).fetchall()
    conn.close()
    return [
        {"id": r[0], "key_label": r[1], "timestamp": r[2], "data": json.loads(r[3])}
        for r in rows
    ]


def load_most_recent(feature: str, key_label: str = None):
    results = load_history(feature, key_label, limit=1)
    return results[0] if results else None