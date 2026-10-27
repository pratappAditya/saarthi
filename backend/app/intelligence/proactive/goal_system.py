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

logger = logging.getLogger("app.intelligence.goal_system")

class GoalMilestone(BaseModel):
    id: str
    title: str
    domain: str = "general"
    status: str = "pending" # "pending" | "completed"

class AgentGoal(BaseModel):
    id: str
    title: str
    domain: str = "general"
    subdomains: List[str] = Field(default_factory=list)
    user_id: str = "default_local_user"
    target_date: Optional[str] = None
    progress_percent: float = 0.0
    status: str = "in_progress" # "in_progress" | "completed" | "paused"
    milestones: List[GoalMilestone] = Field(default_factory=list)
    recommended_next_action: str = ""
    created_at: str = ""

class GoalSystem:
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
                    CREATE TABLE IF NOT EXISTS agent_goals (
                        id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        domain TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        target_date TEXT,
                        progress_percent REAL NOT NULL,
                        status TEXT NOT NULL,
                        milestones_json TEXT NOT NULL,
                        recommended_next_action TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    );
                """)
        finally:
            conn.close()

    def create_goal(
        self,
        title: str,
        domain: str = "general",
        user_id: str = "default_local_user",
        milestones: Optional[List[str]] = None,
        recommended_next_action: str = ""
    ) -> AgentGoal:
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        g_id = f"goal_{uuid.uuid4().hex[:8]}"

        m_objs = [
            GoalMilestone(id=f"m_{i+1}", title=m, status="pending")
            for i, m in enumerate(milestones or ["Define scope", "Execute key actions", "Verify completion"])
        ]

        goal = AgentGoal(
            id=g_id,
            title=title,
            domain=domain,
            user_id=user_id,
            progress_percent=0.0,
            status="in_progress",
            milestones=m_objs,
            recommended_next_action=recommended_next_action or f"Execute milestone 1: {m_objs[0].title}",
            created_at=now
        )

        conn = self._get_connection()
        try:
            with conn:
                conn.execute("""
                    INSERT OR REPLACE INTO agent_goals
                    (id, title, domain, user_id, target_date, progress_percent, status, milestones_json, recommended_next_action, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    goal.id, goal.title, goal.domain, goal.user_id,
                    goal.target_date, goal.progress_percent, goal.status,
                    json.dumps([m.model_dump() for m in goal.milestones]),
                    goal.recommended_next_action, goal.created_at
                ))
            return goal
        finally:
            conn.close()

    def list_goals(self, user_id: str = "default_local_user") -> List[AgentGoal]:
        conn = self._get_connection()
        try:
            rows = conn.execute("SELECT * FROM agent_goals WHERE user_id = ? ORDER BY created_at DESC", (user_id,)).fetchall()
            results = []
            for r in rows:
                d = dict(r)
                d["milestones"] = [GoalMilestone(**m) for m in json.loads(d["milestones_json"])]
                del d["milestones_json"]
                results.append(AgentGoal(**d))
            return results
        finally:
            conn.close()

goal_system = GoalSystem()
