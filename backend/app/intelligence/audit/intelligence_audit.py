import sqlite3
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from app.db.connection import get_db_connection
from app.config.settings import settings

logger = logging.getLogger("app.intelligence.audit")

class IntelligenceAuditService:
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
                    CREATE TABLE IF NOT EXISTS intelligence_audit (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        session_id TEXT,
                        task_id TEXT,
                        agent_id TEXT,
                        tool_name TEXT,
                        risk_level TEXT,
                        permission_status TEXT,
                        model_name TEXT,
                        domain TEXT,
                        action_summary TEXT,
                        metadata_json TEXT
                    );
                """)
        finally:
            conn.close()

    def log_event(
        self,
        user_id: str = "default_local_user",
        session_id: Optional[str] = None,
        task_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        tool_name: Optional[str] = None,
        risk_level: str = "READ_ONLY",
        permission_status: str = "AUTHORIZED",
        model_name: Optional[str] = "nemotron-3-nano:4b",
        domain: str = "general",
        action_summary: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        import json
        meta_str = json.dumps(metadata or {})

        conn = self._get_connection()
        try:
            with conn:
                cur = conn.execute("""
                    INSERT INTO intelligence_audit (
                        timestamp, user_id, session_id, task_id, agent_id,
                        tool_name, risk_level, permission_status, model_name,
                        domain, action_summary, metadata_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    now, user_id, session_id, task_id, agent_id,
                    tool_name, risk_level, permission_status, model_name,
                    domain, action_summary, meta_str
                ))
                audit_id = cur.lastrowid
            return {
                "id": audit_id,
                "timestamp": now,
                "user_id": user_id,
                "tool_name": tool_name,
                "risk_level": risk_level,
                "permission_status": permission_status,
                "domain": domain
            }
        finally:
            conn.close()

    def list_audit_logs(
        self,
        limit: int = 50,
        user_id: str = "default_local_user"
    ) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            rows = conn.execute("""
                SELECT * FROM intelligence_audit
                WHERE user_id = ?
                ORDER BY id DESC LIMIT ?
            """, (user_id, limit)).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

audit_service = IntelligenceAuditService()
