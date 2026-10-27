import os
import sqlite3
import datetime
import json
from typing import List, Dict, Any, Optional

from app.db.connection import get_db_connection
from app.config.settings import settings

class SQLiteDatabase:
    def __init__(self, db_path: Optional[str] = None):
        self._db_path = db_path
        self._init_db()

    @property
    def db_path(self) -> str:
        return self._db_path or settings.DATABASE_PATH

    @db_path.setter
    def db_path(self, val: str):
        self._db_path = val

    def _get_conn(self):
        return get_db_connection(self.db_path)

    def _init_db(self):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    sender TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    key TEXT NOT NULL,
                    content TEXT NOT NULL,
                    project_id TEXT,
                    importance INTEGER DEFAULT 0,
                    source TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT NOT NULL DEFAULT 'ACTIVE',
                    metadata TEXT DEFAULT '{}'
                )
            """)
            conn.commit()

    async def initialize(self):
        self._init_db()

    async def close(self):
        pass

    async def save_message(self, session_id: str, role: str = "user", content: str = "") -> None:
        await self.add_message(session_id=session_id, sender=role, message=content)

    async def add_message(self, session_id: str, sender: str, message: str) -> None:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO chat_history (session_id, sender, message) VALUES (?, ?, ?)",
                (session_id, sender, message)
            )
            conn.commit()

    async def get_messages(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT sender, message FROM (SELECT id, sender, message FROM chat_history WHERE session_id = ? ORDER BY id DESC LIMIT ?) ORDER BY id ASC",
                (session_id, limit)
            )
            rows = cursor.fetchall()
            return [
                {
                    "sender": row[0],
                    "role": row[0],
                    "message": row[1],
                    "content": row[1]
                }
                for row in rows
            ]

    async def clear_session(self, session_id: str) -> None:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM chat_history WHERE session_id = ?", (session_id,))
            conn.commit()

    async def add_memory(
        self,
        content: str,
        category: str = "FACT",
        key: Optional[str] = None,
        project_id: Optional[str] = None,
        importance: int = 0
    ) -> Dict[str, Any]:
        secret_patterns = ["password=", "sk-proj-", "bearer ", "supersecret", "postgres://", "private key"]
        content_lower = content.lower()
        if any(pat in content_lower for pat in secret_patterns):
            raise ValueError("Refusing to store credentials or secrets in database memory.")

        if not key:
            key = f"mem_{datetime.datetime.now(datetime.timezone.utc).timestamp()}"

        now = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO memories (category, key, content, project_id, importance, source, created_at, updated_at, last_accessed_at, status, metadata)
                VALUES (?, ?, ?, ?, ?, 'user', ?, ?, ?, 'ACTIVE', '{}')
                """,
                (category.upper(), key, content, project_id, importance, now, now, now)
            )
            mem_id = cursor.lastrowid
            conn.commit()
            return {"id": mem_id, "content": content, "category": category, "key": key}

    async def get_memories(self, category: Optional[str] = None, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = "SELECT id, category, key, content, project_id, importance FROM memories WHERE status = 'ACTIVE'"
        params = []
        if category:
            sql += " AND category = ?"
            params.append(category.upper())
        if project_id:
            sql += " AND project_id = ?"
            params.append(project_id)

        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "category": row[1],
                    "key": row[2],
                    "content": row[3],
                    "project_id": row[4],
                    "importance": row[5]
                }
                for row in rows
            ]
