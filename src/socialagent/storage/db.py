"""SQLite plumbing. One short-lived connection per operation (safe across threads)."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from typing import Iterator

from socialagent.core.settings import DATA_DIR

DB_PATH = DATA_DIR / "socialagent.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    title TEXT NOT NULL,
    brief TEXT NOT NULL DEFAULT '',
    brand_json TEXT NOT NULL,
    content_json TEXT NOT NULL,
    parent_id INTEGER
);
CREATE TABLE IF NOT EXISTS scheduled_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_at TEXT NOT NULL,
    platforms_json TEXT NOT NULL,
    telegram_text TEXT NOT NULL,
    whatsapp_text TEXT NOT NULL,
    image_paths_json TEXT NOT NULL,
    send_images INTEGER NOT NULL DEFAULT 1,
    status TEXT NOT NULL DEFAULT 'pending',
    note TEXT NOT NULL DEFAULT '',
    campaign_id INTEGER
);
"""


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    try:
        conn.executescript(_SCHEMA)
        yield conn
        conn.commit()
    finally:
        conn.close()
