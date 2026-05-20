import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from config import Config


def get_connection() -> sqlite3.Connection:
    Config.ensure_dirs()
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token TEXT UNIQUE NOT NULL,
                original_filename TEXT NOT NULL,
                stored_filename TEXT NOT NULL,
                content_type TEXT,
                salt BLOB NOT NULL,
                nonce BLOB NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT,
                download_count INTEGER NOT NULL DEFAULT 0,
                metadata_status TEXT,
                size_bytes INTEGER NOT NULL
            )
            """
        )
        conn.commit()


def insert_file_record(record: Dict[str, Any]) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO files (
                token, original_filename, stored_filename, content_type,
                salt, nonce, created_at, expires_at, download_count,
                metadata_status, size_bytes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record["token"],
                record["original_filename"],
                record["stored_filename"],
                record.get("content_type"),
                record["salt"],
                record["nonce"],
                record["created_at"],
                record.get("expires_at"),
                record.get("download_count", 0),
                record.get("metadata_status"),
                record["size_bytes"],
            ),
        )
        conn.commit()


def get_file_by_token(token: str) -> Optional[sqlite3.Row]:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM files WHERE token = ?", (token,)).fetchone()
        return row


def increment_download_count(token: str) -> None:
    with get_connection() as conn:
        conn.execute("UPDATE files SET download_count = download_count + 1 WHERE token = ?", (token,))
        conn.commit()


def list_file_records(limit: int = 50):
    with get_connection() as conn:
        return conn.execute("SELECT * FROM files ORDER BY id DESC LIMIT ?", (limit,)).fetchall()


def delete_file_record(token: str) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM files WHERE token = ?", (token,))
        conn.commit()


def expired_records():
    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM files WHERE expires_at IS NOT NULL AND expires_at < ?",
            (now,),
        ).fetchall()
