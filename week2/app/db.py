from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "app.db"


def ensure_data_directory_exists() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    ensure_data_directory_exists()
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def _fetchall(query: str, params: tuple = ()) -> list[sqlite3.Row]:
    """Helper to run a SELECT and return all rows."""
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(query, params)
        return list(cursor.fetchall())


def _fetchone(query: str, params: tuple = ()) -> Optional[sqlite3.Row]:
    """Helper to run a SELECT and return a single row or None."""
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()


def _execute(query: str, params: tuple = ()) -> Optional[int]:
    """Helper to execute INSERT/UPDATE/DELETE and return lastrowid when available.

    Returns the lastrowid (int) for INSERT statements, or None otherwise.
    """
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(query, params)
        connection.commit()
        try:
            return int(cursor.lastrowid) if cursor.lastrowid is not None else None
        except Exception:
            return None


def init_db() -> None:
    ensure_data_directory_exists()
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            );
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS action_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id INTEGER,
                text TEXT NOT NULL,
                done INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (note_id) REFERENCES notes(id)
            );
            """
        )
        connection.commit()


def insert_note(content: str) -> int:
    last = _execute("INSERT INTO notes (content) VALUES (?)", (content,))
    # _execute should return the newly inserted row id
    return int(last)  # type: ignore[arg-type]


def list_notes() -> list[sqlite3.Row]:
    return _fetchall("SELECT id, content, created_at FROM notes ORDER BY id DESC")


def get_note(note_id: int) -> Optional[sqlite3.Row]:
    return _fetchone("SELECT id, content, created_at FROM notes WHERE id = ?", (note_id,))


def insert_action_items(items: list[str], note_id: Optional[int] = None) -> list[int]:
    with get_connection() as connection:
        cursor = connection.cursor()
        ids: list[int] = []
        for item in items:
            cursor.execute(
                "INSERT INTO action_items (note_id, text) VALUES (?, ?)",
                (note_id, item),
            )
            ids.append(int(cursor.lastrowid))
        connection.commit()
        return ids


def list_action_items(note_id: Optional[int] = None) -> list[sqlite3.Row]:
    if note_id is None:
        return _fetchall(
            "SELECT id, note_id, text, done, created_at FROM action_items ORDER BY id DESC"
        )
    return _fetchall(
        "SELECT id, note_id, text, done, created_at FROM action_items WHERE note_id = ? ORDER BY id DESC",
        (note_id,),
    )


def mark_action_item_done(action_item_id: int, done: bool) -> None:
    _execute(
        "UPDATE action_items SET done = ? WHERE id = ?", (1 if done else 0, action_item_id)
    )


