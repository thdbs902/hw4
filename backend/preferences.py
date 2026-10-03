"""Remembered shopper preferences (Problem 9). Stored in a small customer_preferences table
(one row per user), created on first use. Existing tables are not changed."""

import json
import sqlite3

from models import ShopperPreferences

SCHEMA = """
CREATE TABLE IF NOT EXISTS customer_preferences (
    user_id INTEGER PRIMARY KEY REFERENCES users(id),
    size TEXT,
    colors_json TEXT NOT NULL DEFAULT '[]',
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
)
"""


def _connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute(SCHEMA)
    return conn


def load(db_path: str, user_id: int) -> ShopperPreferences:
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT size, colors_json FROM customer_preferences WHERE user_id = ?", (user_id,)
        ).fetchone()
    if not row:
        return ShopperPreferences()
    return ShopperPreferences(size=row[0], colors=json.loads(row[1] or "[]"))


def save(db_path: str, user_id: int, prefs: ShopperPreferences) -> None:
    with _connect(db_path) as conn:
        conn.execute(
            "INSERT INTO customer_preferences (user_id, size, colors_json) VALUES (?, ?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET size = excluded.size, "
            "colors_json = excluded.colors_json, updated_at = datetime('now')",
            (user_id, prefs.size, json.dumps(prefs.colors)),
        )
