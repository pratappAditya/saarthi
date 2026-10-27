import sqlite3
import os
import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.db.connection import get_db_connection
from app.config.settings import settings

logger = logging.getLogger("app.intelligence.project_manager")

class ProjectItem(BaseModel):
    id: Optional[int] = None
    project_id: str
    name: str
    description: str = ""
    domain: str = "general"
    subdomains: List[str] = Field(default_factory=list)
    user_id: str = "default_local_user"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ProjectManager:
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
                    CREATE TABLE IF NOT EXISTS projects (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        project_id TEXT UNIQUE NOT NULL,
                        name TEXT NOT NULL,
                        description TEXT,
                        domain TEXT NOT NULL DEFAULT 'general',
                        user_id TEXT NOT NULL DEFAULT 'default_local_user',
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    );
                """)
        finally:
            conn.close()

    def create_project(
        self,
        name: str,
        description: str = "",
        domain: str = "general",
        user_id: str = "default_local_user"
    ) -> ProjectItem:
        proj_id = f"proj_{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc).isoformat()
        item = ProjectItem(
            project_id=proj_id,
            name=name,
            description=description,
            domain=domain,
            user_id=user_id,
            created_at=now,
            updated_at=now
        )

        conn = self._get_connection()
        try:
            with conn:
                cur = conn.execute("""
                    INSERT INTO projects (project_id, name, description, domain, user_id, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (proj_id, name, description, domain, user_id, now, now))
                item.id = cur.lastrowid
            return item
        finally:
            conn.close()

    def get_project(self, project_id: str) -> Optional[ProjectItem]:
        conn = self._get_connection()
        try:
            row = conn.execute("SELECT * FROM projects WHERE project_id = ?", (project_id,)).fetchone()
            if not row:
                return None
            d = dict(row)
            return ProjectItem(**d)
        finally:
            conn.close()

    def list_projects(self, user_id: str = "default_local_user") -> List[ProjectItem]:
        conn = self._get_connection()
        try:
            rows = conn.execute("SELECT * FROM projects WHERE user_id = ? ORDER BY id DESC", (user_id,)).fetchall()
            return [ProjectItem(**dict(r)) for r in rows]
        finally:
            conn.close()

    def delete_project(self, project_id: str) -> bool:
        conn = self._get_connection()
        try:
            with conn:
                conn.execute("DELETE FROM projects WHERE project_id = ?", (project_id,))
            return True
        finally:
            conn.close()

project_manager = ProjectManager()
