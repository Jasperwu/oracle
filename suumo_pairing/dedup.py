"""
SQLite-backed deduplication store.

Schema: one row per (pair_key, area_pair, tier) first seen on a given date.
"""
import os
import sqlite3
from datetime import date
from typing import Set

DB_PATH = os.path.join(os.path.dirname(__file__), "seen_pairs.db")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS seen_pairs (
    pair_key        TEXT NOT NULL,
    area_pair       TEXT NOT NULL,
    tier            TEXT NOT NULL,
    first_seen_date TEXT NOT NULL,
    run_count       INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (pair_key)
);
"""


def open_db(db_path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.executescript(_SCHEMA)
    conn.commit()
    return conn


def load_seen_keys(conn: sqlite3.Connection) -> Set[str]:
    rows = conn.execute("SELECT pair_key FROM seen_pairs").fetchall()
    return {row[0] for row in rows}


def record_pairs(
    conn: sqlite3.Connection,
    pair_keys: list[str],
    area_pair: str,
    tier: str,
    run_date: str | None = None,
) -> None:
    today = run_date or date.today().isoformat()
    conn.executemany(
        """
        INSERT INTO seen_pairs (pair_key, area_pair, tier, first_seen_date)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(pair_key) DO UPDATE SET run_count = run_count + 1
        """,
        [(key, area_pair, tier, today) for key in pair_keys],
    )
    conn.commit()


def least_used_pair_index(conn: sqlite3.Connection, area_pairs: list) -> int:
    """
    Return the index into area_pairs of the pair that has been used least
    (by total rows in seen_pairs for that area_pair string).
    """
    rows = conn.execute(
        "SELECT area_pair, COUNT(*) FROM seen_pairs GROUP BY area_pair"
    ).fetchall()
    counts = {row[0]: row[1] for row in rows}

    best_idx = 0
    best_count = float("inf")
    for i, pair in enumerate(area_pairs):
        key = f"{pair[0]}-{pair[1]}"
        c = counts.get(key, 0)
        if c < best_count:
            best_count = c
            best_idx = i
    return best_idx
