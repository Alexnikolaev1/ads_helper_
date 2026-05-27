import os
import sqlite3
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
    password_hash TEXT NOT NULL,
    free_generations_used INTEGER NOT NULL DEFAULT 0,
    paid_until TEXT,
    tokens_used_month INTEGER NOT NULL DEFAULT 0,
    token_month TEXT,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
"""


def get_database_path() -> Path:
    try:
        custom = st.secrets.get("DATABASE_PATH")
        if custom:
            return Path(custom)
    except Exception:
        pass
    env_path = os.getenv("DATABASE_PATH")
    if env_path:
        return Path(env_path)
    return Path("data") / "ads_helper.db"


def get_connection() -> sqlite3.Connection:
    path = get_database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_database() -> None:
    with get_connection() as conn:
        conn.executescript(_SCHEMA)
        conn.commit()
