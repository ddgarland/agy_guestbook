import sqlite3
import html
from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr
import os

DB_PATH = os.environ.get("DB_PATH", "guestbook.db")

class GuestbookEntry(BaseModel):
    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    message: str = Field(..., min_length=1, max_length=500)
    created_at: Optional[str] = None

def get_db_connection():
    # Ensure directory exists if DB_PATH is inside a directory
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()

def add_entry(name: str, email: str, message: str) -> int:
    # Sanitize inputs
    clean_name = html.escape(name.strip())
    clean_email = email.strip().lower()
    clean_message = html.escape(message.strip())
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO entries (name, email, message, created_at) VALUES (?, ?, ?, ?)",
        (clean_name, clean_email, clean_message, now)
    )
    entry_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return entry_id

def get_entries(limit: int = 50) -> List[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, email, message, created_at FROM entries ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
