import sqlite3
import os
import json
import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from app.intelligence.permissions.permission_models import (
    PermissionRequest, PermissionStatus, PermissionScope
)
from app.db.connection import get_db_connection
from app.config.settings import settings

logger = logging.getLogger("app.intelligence.permission_engine")

class PermissionEngine:
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
                    CREATE TABLE IF NOT EXISTS permissions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        request_id TEXT UNIQUE NOT NULL,
                        user_id TEXT NOT NULL,
                        session_id TEXT,
                        tool_id TEXT NOT NULL,
                        action_description TEXT NOT NULL,
                        arguments_json TEXT NOT NULL,
                        risk_level TEXT NOT NULL,
                        scope TEXT NOT NULL,
                        status TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    );
                """)
        finally:
            conn.close()

    def request_permission(
        self,
        tool_id: str,
        action_description: str,
        arguments: Dict[str, Any],
        risk_level: str = "MODERATE",
        scope: PermissionScope = PermissionScope.ONE_TIME,
        session_id: str = "default_session",
        user_id: str = "default_local_user"
    ) -> PermissionRequest:
        req_id = f"perm_{uuid.uuid4().hex[:10]}"
        now = datetime.now(timezone.utc).isoformat()
        item = PermissionRequest(
            request_id=req_id,
            user_id=user_id,
            session_id=session_id,
            tool_id=tool_id,
            action_description=action_description,
            arguments=arguments,
            risk_level=risk_level,
            scope=scope,
            status=PermissionStatus.PENDING,
            created_at=now,
            updated_at=now
        )

        conn = self._get_connection()
        try:
            with conn:
                cur = conn.execute("""
                    INSERT INTO permissions (
                        request_id, user_id, session_id, tool_id,
                        action_description, arguments_json, risk_level,
                        scope, status, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    req_id, user_id, session_id, tool_id,
                    action_description, json.dumps(arguments), risk_level,
                    scope.value, PermissionStatus.PENDING.value, now, now
                ))
                item.id = cur.lastrowid
            return item
        finally:
            conn.close()

    def grant_permission(self, request_id: str) -> Optional[PermissionRequest]:
        return self._update_status(request_id, PermissionStatus.APPROVED)

    def deny_permission(self, request_id: str) -> Optional[PermissionRequest]:
        return self._update_status(request_id, PermissionStatus.DENIED)

    def revoke_permission(self, request_id: str) -> Optional[PermissionRequest]:
        return self._update_status(request_id, PermissionStatus.REVOKED)

    def _update_status(self, request_id: str, status: PermissionStatus) -> Optional[PermissionRequest]:
        now = datetime.now(timezone.utc).isoformat()
        conn = self._get_connection()
        try:
            with conn:
                conn.execute("""
                    UPDATE permissions
                    SET status = ?, updated_at = ?
                    WHERE request_id = ?
                """, (status.value, now, request_id))
            return self.get_permission_request(request_id)
        finally:
            conn.close()

    def get_permission_request(self, request_id: str) -> Optional[PermissionRequest]:
        conn = self._get_connection()
        try:
            row = conn.execute("SELECT * FROM permissions WHERE request_id = ?", (request_id,)).fetchone()
            if not row:
                return None
            d = dict(row)
            return PermissionRequest(
                id=d["id"],
                request_id=d["request_id"],
                user_id=d["user_id"],
                session_id=d["session_id"],
                tool_id=d["tool_id"],
                action_description=d["action_description"],
                arguments=json.loads(d["arguments_json"] or "{}"),
                risk_level=d["risk_level"],
                scope=PermissionScope(d["scope"]),
                status=PermissionStatus(d["status"]),
                created_at=d["created_at"],
                updated_at=d["updated_at"]
            )
        finally:
            conn.close()

    def list_pending_permissions(self, user_id: str = "default_local_user") -> List[PermissionRequest]:
        conn = self._get_connection()
        try:
            rows = conn.execute("""
                SELECT * FROM permissions
                WHERE user_id = ? AND status = 'pending'
                ORDER BY id DESC
            """, (user_id,)).fetchall()
            res = []
            for r in rows:
                d = dict(r)
                res.append(PermissionRequest(
                    id=d["id"],
                    request_id=d["request_id"],
                    user_id=d["user_id"],
                    session_id=d["session_id"],
                    tool_id=d["tool_id"],
                    action_description=d["action_description"],
                    arguments=json.loads(d["arguments_json"] or "{}"),
                    risk_level=d["risk_level"],
                    scope=PermissionScope(d["scope"]),
                    status=PermissionStatus(d["status"]),
                    created_at=d["created_at"],
                    updated_at=d["updated_at"]
                ))
            return res
        finally:
            conn.close()

permission_engine = PermissionEngine()
