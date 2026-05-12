"""SQLite connection helpers for the API.

Uses the same database file as the ingestion pipeline writes to. Connection
is opened per-request (SQLite is happy with this at v1 scale).
"""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "daylight.db"


def _db_path() -> Path:
    return Path(os.environ.get("DAYLIGHT_DB_PATH", DEFAULT_DB_PATH))


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(_db_path(), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def fetchone(query: str, params: tuple = ()) -> sqlite3.Row | None:
    conn = get_connection()
    try:
        cursor = conn.execute(query, params)
        return cursor.fetchone()
    finally:
        conn.close()


def fetchall(query: str, params: tuple = ()) -> list[sqlite3.Row]:
    conn = get_connection()
    try:
        cursor = conn.execute(query, params)
        return cursor.fetchall()
    finally:
        conn.close()
