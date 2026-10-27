import json
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from app.db.connection import get_db_connection, with_db_retry
from app.db.admin_db import AdminRepository as BaseAdminRepository, init_admin_tables

# Ensure admin tables are initialized on import
init_admin_tables()

class AdminRepository(BaseAdminRepository):
    # --- ADMIN USERS & SESSIONS ---

    @staticmethod
    @with_db_retry()
    def get_admin_by_id(admin_id: str) -> Optional[Dict[str, Any]]:
        with get_db_connection() as conn:
            row = conn.execute("SELECT * FROM admin_users WHERE admin_id = ?", (admin_id,)).fetchone()
            return dict(row) if row else None

    @staticmethod
    @with_db_retry()
    def get_admin_by_email(email: str) -> Optional[Dict[str, Any]]:
        with get_db_connection() as conn:
            row = conn.execute("SELECT * FROM admin_users WHERE email = ?", (email.lower(),)).fetchone()
            return dict(row) if row else None

    @staticmethod
    @with_db_retry()
    def create_admin_user(email: str, password_hash: str, role: str = "ADMIN", full_name: str = "") -> Dict[str, Any]:
        admin_id = f"adm_{uuid.uuid4().hex[:12]}"
        now_str = datetime.now(timezone.utc).isoformat()
        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO admin_users (admin_id, email, password_hash, role, full_name, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, 'ACTIVE', ?, ?)
            """, (admin_id, email.lower(), password_hash, role.upper(), full_name, now_str, now_str))
            conn.commit()
            row = conn.execute("SELECT * FROM admin_users WHERE admin_id = ?", (admin_id,)).fetchone()
            return dict(row)

    @staticmethod
    @with_db_retry()
    def create_session(admin_id: str, ip_address: str = "127.0.0.1", duration_hours: int = 24) -> Dict[str, Any]:
        session_token = f"adm_sess_{uuid.uuid4().hex}"
        now = datetime.now(timezone.utc)
        expires_at = (now + timedelta(hours=duration_hours)).isoformat()
        now_str = now.isoformat()

        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO admin_sessions (session_token, admin_id, expires_at, ip_address, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (session_token, admin_id, expires_at, ip_address, now_str))
            conn.commit()
            return {
                "session_token": session_token,
                "admin_id": admin_id,
                "expires_at": expires_at,
                "ip_address": ip_address,
                "created_at": now_str
            }

    @staticmethod
    @with_db_retry()
    def get_session(session_token: str) -> Optional[Dict[str, Any]]:
        with get_db_connection() as conn:
            row = conn.execute("SELECT * FROM admin_sessions WHERE session_token = ?", (session_token,)).fetchone()
            if not row:
                return None
            sess = dict(row)
            exp_raw = sess["expires_at"]
            if isinstance(exp_raw, datetime):
                exp = exp_raw if exp_raw.tzinfo else exp_raw.replace(tzinfo=timezone.utc)
            else:
                exp = datetime.fromisoformat(str(exp_raw))
                if exp.tzinfo is None:
                    exp = exp.replace(tzinfo=timezone.utc)
            if exp < datetime.now(timezone.utc):
                return None
            sess["expires_at"] = exp.isoformat()
            return sess

    @staticmethod
    @with_db_retry()
    def revoke_session(session_token: str):
        with get_db_connection() as conn:
            conn.execute("DELETE FROM admin_sessions WHERE session_token = ?", (session_token,))
            conn.commit()

    @staticmethod
    @with_db_retry()
    def get_role_permissions(role_name: str) -> List[str]:
        with get_db_connection() as conn:
            row = conn.execute("SELECT permissions_json FROM admin_roles WHERE role_name = ?", (role_name.upper(),)).fetchone()
            if row and row["permissions_json"]:
                try:
                    return json.loads(row["permissions_json"])
                except Exception:
                    return []
            return []
