import sqlite3
import os
import json
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from app.db.connection import get_db_connection
from app.config.settings import settings

logger = logging.getLogger("app.intelligence.assistant_profile")

class AssistantProfile(BaseModel):
    name: str = "Saarthi"
    tone: str = "intelligent, calm, helpful"
    verbosity: str = "concise"
    formality: str = "adaptive"
    proactivity: str = "risk_aware"
    confirmation_policy: str = "risk_based"

class AssistantProfileService:
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
                    CREATE TABLE IF NOT EXISTS assistant_profile (
                        id INTEGER PRIMARY KEY DEFAULT 1,
                        name TEXT NOT NULL,
                        tone TEXT NOT NULL,
                        verbosity TEXT NOT NULL,
                        formality TEXT NOT NULL,
                        proactivity TEXT NOT NULL,
                        confirmation_policy TEXT NOT NULL
                    );
                """)
                # Insert default if missing
                cur = conn.execute("SELECT * FROM assistant_profile WHERE id = 1")
                if not cur.fetchone():
                    conn.execute("""
                        INSERT INTO assistant_profile (id, name, tone, verbosity, formality, proactivity, confirmation_policy)
                        VALUES (1, 'Saarthi', 'intelligent, calm, helpful', 'concise', 'adaptive', 'risk_aware', 'risk_based')
                    """)
        finally:
            conn.close()

    def get_profile(self) -> AssistantProfile:
        conn = self._get_connection()
        try:
            row = conn.execute("SELECT * FROM assistant_profile WHERE id = 1").fetchone()
            if row:
                d = dict(row)
                d.pop("id", None)
                return AssistantProfile(**d)
            return AssistantProfile()
        finally:
            conn.close()

    def update_profile(self, updates: Dict[str, Any]) -> AssistantProfile:
        current = self.get_profile().model_dump()
        current.update(updates)
        conn = self._get_connection()
        try:
            with conn:
                conn.execute("""
                    UPDATE assistant_profile
                    SET name = ?, tone = ?, verbosity = ?, formality = ?, proactivity = ?, confirmation_policy = ?
                    WHERE id = 1
                """, (
                    current["name"], current["tone"], current["verbosity"],
                    current["formality"], current["proactivity"], current["confirmation_policy"]
                ))
            return AssistantProfile(**current)
        finally:
            conn.close()

assistant_profile_service = AssistantProfileService()
assistant_profile = assistant_profile_service.get_profile()
