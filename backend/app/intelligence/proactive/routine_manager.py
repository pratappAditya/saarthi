import sqlite3
import os
import json
import uuid
import datetime
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from app.db.connection import get_db_connection
from app.config.settings import settings

logger = logging.getLogger("app.intelligence.routine_manager")

class AgentRoutine(BaseModel):
    id: str
    name: str
    trigger_type: str = "scheduled" # "scheduled" | "event" | "manual"
    cron_expression: Optional[str] = "0 9 * * *"
    domain: str = "general"
    user_id: str = "default_local_user"
    tool_id: str = "file.read"
    arguments: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    last_run_at: Optional[str] = None
    created_at: str = ""

class RoutineManager:
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
                    CREATE TABLE IF NOT EXISTS agent_routines (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        trigger_type TEXT NOT NULL,
                        cron_expression TEXT,
                        domain TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        tool_id TEXT NOT NULL,
                        arguments_json TEXT NOT NULL,
                        is_active INTEGER NOT NULL,
                        last_run_at TEXT,
                        created_at TEXT NOT NULL
                    );
                """)
        finally:
            conn.close()

    def create_routine(
        self,
        name: str,
        trigger_type: str = "scheduled",
        cron_expression: str = "0 9 * * *",
        domain: str = "general",
        user_id: str = "default_local_user",
        tool_id: str = "file.read",
        arguments: Optional[Dict[str, Any]] = None
    ) -> AgentRoutine:
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        r_id = f"rout_{uuid.uuid4().hex[:8]}"

        routine = AgentRoutine(
            id=r_id,
            name=name,
            trigger_type=trigger_type,
            cron_expression=cron_expression,
            domain=domain,
            user_id=user_id,
            tool_id=tool_id,
            arguments=arguments or {},
            is_active=True,
            created_at=now
        )

        conn = self._get_connection()
        try:
            with conn:
                conn.execute("""
                    INSERT OR REPLACE INTO agent_routines
                    (id, name, trigger_type, cron_expression, domain, user_id, tool_id, arguments_json, is_active, last_run_at, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    routine.id, routine.name, routine.trigger_type,
                    routine.cron_expression, routine.domain, routine.user_id,
                    routine.tool_id, json.dumps(routine.arguments),
                    1 if routine.is_active else 0, routine.last_run_at, routine.created_at
                ))
            return routine
        finally:
            conn.close()

    def list_routines(self, user_id: str = "default_local_user") -> List[AgentRoutine]:
        conn = self._get_connection()
        try:
            rows = conn.execute("SELECT * FROM agent_routines WHERE user_id = ? ORDER BY created_at DESC", (user_id,)).fetchall()
            results = []
            for r in rows:
                d = dict(r)
                d["arguments"] = json.loads(d["arguments_json"])
                d["is_active"] = bool(d["is_active"])
                del d["arguments_json"]
                results.append(AgentRoutine(**d))
            return results
        finally:
            conn.close()

routine_manager = RoutineManager()
