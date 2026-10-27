import sqlite3
import json
import datetime
from typing import List, Dict, Any, Optional
from app.memory.base_store import BaseMemoryStore
from app.db.connection import get_db_connection
from app.config.settings import settings

class SQLiteMemoryStore(BaseMemoryStore):
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
            try:
                cursor.execute("PRAGMA table_info(memories)")
                cols = [col[1] for col in cursor.fetchall()]
                if cols and "key" not in cols:
                    cursor.execute("ALTER TABLE memories ADD COLUMN key TEXT DEFAULT ''")
                if cols and "category" not in cols:
                    cursor.execute("ALTER TABLE memories ADD COLUMN category TEXT DEFAULT 'FACT'")
                if cols and "status" not in cols:
                    cursor.execute("ALTER TABLE memories ADD COLUMN status TEXT DEFAULT 'ACTIVE'")
                if cols and "metadata" not in cols:
                    cursor.execute("ALTER TABLE memories ADD COLUMN metadata TEXT DEFAULT '{}'")
            except Exception:
                pass
            conn.commit()

    def _row_to_dict(self, row) -> Dict[str, Any]:
        return {
            "id": row[0],
            "category": row[1],
            "key": row[2],
            "content": row[3],
            "project_id": row[4],
            "importance": row[5],
            "source": row[6],
            "created_at": row[7],
            "updated_at": row[8],
            "last_accessed_at": row[9],
            "status": row[10],
            "metadata": json.loads(row[11] or "{}")
        }

    def create_memory(
        self,
        category: str,
        key: str,
        content: str,
        project_id: Optional[str] = None,
        importance: int = 0,
        source: str = "user",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        meta_str = json.dumps(metadata or {})
        now = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO memories (category, key, content, project_id, importance, source, created_at, updated_at, last_accessed_at, status, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE', ?)
                """,
                (category, key, content, project_id, importance, source, now, now, now, meta_str)
            )
            memory_id = cursor.lastrowid
            conn.commit()
        return self.get_memory(memory_id)

    def get_memory(self, memory_id: int) -> Optional[Dict[str, Any]]:
        now = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE memories SET last_accessed_at = ? WHERE id = ?", (now, memory_id))
            cursor.execute("SELECT id, category, key, content, project_id, importance, source, created_at, updated_at, last_accessed_at, status, metadata FROM memories WHERE id = ?", (memory_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_dict(row)
        return None

    def search_memories(
        self,
        query: str,
        category: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        sql = "SELECT id, category, key, content, project_id, importance, source, created_at, updated_at, last_accessed_at, status, metadata FROM memories WHERE status = 'ACTIVE' AND (key LIKE ? OR content LIKE ?)"
        params = [f"%{query}%", f"%{query}%"]
        
        if category:
            sql += " AND category = ?"
            params.append(category)
        if project_id:
            sql += " AND project_id = ?"
            params.append(project_id)
            
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]

    def update_memory(self, memory_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        if not kwargs:
            return self.get_memory(memory_id)
            
        now = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
        kwargs["updated_at"] = now
        
        if "metadata" in kwargs and isinstance(kwargs["metadata"], dict):
            kwargs["metadata"] = json.dumps(kwargs["metadata"])
            
        fields = []
        params = []
        for k, v in kwargs.items():
            fields.append(f"{k} = ?")
            params.append(v)
            
        params.append(memory_id)
        sql = f"UPDATE memories SET {', '.join(fields)} WHERE id = ?"
        
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            
        return self.get_memory(memory_id)

    def list_memories(
        self,
        category: Optional[str] = None,
        project_id: Optional[str] = None,
        status: str = "ACTIVE"
    ) -> List[Dict[str, Any]]:
        sql = "SELECT id, category, key, content, project_id, importance, source, created_at, updated_at, last_accessed_at, status, metadata FROM memories WHERE 1=1"
        params = []
        
        if status:
            sql += " AND status = ?"
            params.append(status)
        if category:
            sql += " AND category = ?"
            params.append(category)
        if project_id:
            sql += " AND project_id = ?"
            params.append(project_id)
            
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
