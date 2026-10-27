import os
import sqlite3
from typing import List, Dict, Optional
from app.memory.base import MemoryProvider
from app.db.connection import with_db_retry, get_db_connection
from app.config.settings import settings

class SQLiteMemoryProvider(MemoryProvider):
    def __init__(self, db_path: Optional[str] = None):
        self._db_path = db_path
        self._init_db()

    @property
    def db_path(self) -> str:
        return self._db_path or settings.DATABASE_PATH

    @db_path.setter
    def db_path(self, val: str):
        self._db_path = val

    def _get_connection(self):
        return get_db_connection(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    sender TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    @with_db_retry()
    async def add_message(self, session_id: str, sender: str, message: str) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO chat_history (session_id, sender, message) VALUES (?, ?, ?)",
                (session_id, sender, message)
            )
            conn.commit()

    @with_db_retry()
    async def get_messages(self, session_id: str, limit: int = 50) -> List[Dict[str, str]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT sender, message FROM (SELECT id, sender, message FROM chat_history WHERE session_id = ? ORDER BY id DESC LIMIT ?) ORDER BY id ASC",
                (session_id, limit)
            )
            rows = cursor.fetchall()
            return [{"sender": row[0], "message": row[1]} for row in rows]

    async def clear_session(self, session_id: str) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM chat_history WHERE session_id = ?", (session_id,))
            conn.commit()

