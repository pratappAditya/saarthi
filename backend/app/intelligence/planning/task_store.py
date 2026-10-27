import sqlite3
import os
import json
import logging
from typing import Dict, Any, List, Optional

from app.db.connection import get_db_connection
from app.config.settings import settings

logger = logging.getLogger("app.intelligence.task_store")

class TaskStoreService:
    def __init__(self, db_path: Optional[str] = None):
        self._db_path = db_path
        self._init_tables()

    @property
    def db_path(self) -> str:
        return self._db_path or settings.DATABASE_PATH

    @db_path.setter
    def db_path(self, val: str):
        self._db_path = val

    def _get_connection(self):
        return get_db_connection(self.db_path)

    def _init_tables(self):
        conn = self._get_connection()
        try:
            with conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS agent_tasks (
                        task_id TEXT PRIMARY KEY,
                        title TEXT DEFAULT '',
                        prompt TEXT DEFAULT '',
                        goal TEXT DEFAULT '',
                        objective TEXT DEFAULT '',
                        domain TEXT DEFAULT 'general',
                        status TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        steps_json TEXT NOT NULL,
                        metadata_json TEXT DEFAULT '{}'
                    );
                """)
                cursor = conn.execute("PRAGMA table_info(agent_tasks)")
                columns = [row["name"] if hasattr(row, "keys") else row[1] for row in cursor.fetchall()]
                for col_name, col_type in [
                    ("title", "TEXT DEFAULT ''"),
                    ("prompt", "TEXT DEFAULT ''"),
                    ("domain", "TEXT DEFAULT 'general'"),
                    ("goal", "TEXT DEFAULT ''"),
                    ("objective", "TEXT DEFAULT ''"),
                    ("metadata_json", "TEXT DEFAULT '{}'"),
                    ("steps_json", "TEXT DEFAULT '[]'")
                ]:
                    if col_name not in columns:
                        conn.execute(f"ALTER TABLE agent_tasks ADD COLUMN {col_name} {col_type}")
        finally:
            conn.close()

    def save_task(self, task_id: str, objective: str, domain: str, status: str, user_id: str, steps: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        import datetime
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        metadata_str = json.dumps(metadata or {})
        steps_str = json.dumps(steps)

        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.execute("PRAGMA table_info(agent_tasks)")
                columns = [col[1] for col in cursor.fetchall()]

                fields = ["task_id", "status", "user_id", "created_at", "updated_at"]
                values = [task_id, status, user_id, now, now]

                if "title" in columns:
                    fields.append("title")
                    values.append(objective)
                if "prompt" in columns:
                    fields.append("prompt")
                    values.append(objective)
                if "goal" in columns:
                    fields.append("goal")
                    values.append(objective)
                if "objective" in columns:
                    fields.append("objective")
                    values.append(objective)
                if "domain" in columns:
                    fields.append("domain")
                    values.append(domain)
                if "steps_json" in columns:
                    fields.append("steps_json")
                    values.append(steps_str)
                if "steps" in columns and "steps_json" not in columns:
                    fields.append("steps")
                    values.append(steps_str)
                if "metadata_json" in columns:
                    fields.append("metadata_json")
                    values.append(metadata_str)

                placeholders = ", ".join(["?"] * len(fields))
                field_names = ", ".join(fields)

                conn.execute(f"INSERT OR REPLACE INTO agent_tasks ({field_names}) VALUES ({placeholders})", values)
            return self.get_task(task_id) or {}
        finally:
            conn.close()

    def update_task_status(self, task_id: str, status: str, steps: Optional[List[Dict[str, Any]]] = None) -> Optional[Dict[str, Any]]:
        import datetime
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()

        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.execute("PRAGMA table_info(agent_tasks)")
                columns = [row["name"] if hasattr(row, "keys") else row[1] for row in cursor.fetchall()]
                if "steps_json" in columns:
                    steps_col = "steps_json"
                elif "plan_dag_json" in columns:
                    steps_col = "plan_dag_json"
                elif "steps" in columns:
                    steps_col = "steps"
                else:
                    conn.execute("ALTER TABLE agent_tasks ADD COLUMN steps_json TEXT DEFAULT '[]'")
                    steps_col = "steps_json"

                if steps is not None:
                    conn.execute(f"""
                        UPDATE agent_tasks
                        SET status = ?, {steps_col} = ?, updated_at = ?
                        WHERE task_id = ?
                    """, (status, json.dumps(steps), now, task_id))
                else:
                    conn.execute("""
                        UPDATE agent_tasks
                        SET status = ?, updated_at = ?
                        WHERE task_id = ?
                    """, (status, now, task_id))
            return self.get_task(task_id)
        finally:
            conn.close()

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            row = conn.execute("SELECT * FROM agent_tasks WHERE task_id = ?", (task_id,)).fetchone()
            if not row:
                return None
            d = dict(row)
            steps_raw = d.get("steps_json") or d.get("steps") or "[]"
            meta_raw = d.get("metadata_json") or "{}"
            d["steps"] = json.loads(steps_raw) if isinstance(steps_raw, str) else steps_raw
            d["metadata"] = json.loads(meta_raw) if isinstance(meta_raw, str) else meta_raw
            d["goal"] = d.get("goal") or d.get("prompt") or d.get("title") or d.get("objective") or ""
            d["objective"] = d["goal"]
            d["title"] = d["goal"]
            return d
        finally:
            conn.close()

    def list_tasks(self, user_id: str = "default_local_user", limit: int = 50) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            rows = conn.execute("SELECT * FROM agent_tasks WHERE user_id = ? ORDER BY updated_at DESC LIMIT ?", (user_id, limit)).fetchall()
            results = []
            for r in rows:
                d = dict(r)
                steps_raw = d.get("steps_json") or d.get("steps") or "[]"
                meta_raw = d.get("metadata_json") or "{}"
                d["steps"] = json.loads(steps_raw) if isinstance(steps_raw, str) else steps_raw
                d["metadata"] = json.loads(meta_raw) if isinstance(meta_raw, str) else meta_raw
                d["goal"] = d.get("goal") or d.get("prompt") or d.get("title") or d.get("objective") or ""
                d["objective"] = d["goal"]
                results.append(d)
            return results
        finally:
            conn.close()

    def update_task_metadata(self, task_id: str, metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            with conn:
                conn.execute("""
                    UPDATE agent_tasks
                    SET metadata_json = ?
                    WHERE task_id = ?
                """, (json.dumps(metadata), task_id))
            return self.get_task(task_id)
        finally:
            conn.close()

    def save_checkpoint(self, task_id: str, checkpoint_id: str, checkpoint_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        task = self.get_task(task_id)
        if not task:
            return None
        meta = task.get("metadata", {})
        if "checkpoints" not in meta:
            meta["checkpoints"] = {}
        meta["checkpoints"][checkpoint_id] = checkpoint_data
        return self.update_task_metadata(task_id, meta)

    def get_checkpoints(self, task_id: str) -> Dict[str, Any]:
        task = self.get_task(task_id)
        if not task:
            return {}
        return task.get("metadata", {}).get("checkpoints", {})

task_store = TaskStoreService()
