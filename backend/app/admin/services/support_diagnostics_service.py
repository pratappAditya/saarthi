import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from fastapi import HTTPException
from app.config.settings import settings
from app.db.connection import get_db_connection
from app.db.auth import AuthRepository
from app.admin.health.system_health_monitor import system_health_monitor

logger = logging.getLogger("app.admin.services.support_diagnostics")

class SupportDiagnosticsService:
    @classmethod
    def lookup_user_issue(cls, user_id_or_email: str) -> Dict[str, Any]:
        with get_db_connection() as conn:
            user = conn.execute(
                "SELECT * FROM users WHERE user_id = ? OR email = ?",
                (user_id_or_email, user_id_or_email)
            ).fetchone()

            if not user:
                raise HTTPException(status_code=404, detail=f"User '{user_id_or_email}' not found.")

            u_dict = dict(user)
            u_id = u_dict["user_id"]

            quota = conn.execute("SELECT * FROM free_usage_quota WHERE user_id_or_device = ?", (u_id,)).fetchone()
            sessions = conn.execute("SELECT session_token, expires_at, created_at FROM sessions WHERE user_id = ?", (u_id,)).fetchall()
            devices = AuthRepository.list_user_devices(u_id)
            support_feedback = conn.execute("SELECT * FROM support_feedback WHERE user_id = ?", (u_id,)).fetchall()

            return {
                "status": "success",
                "user_summary": u_dict,
                "quota_usage": dict(quota) if quota else None,
                "active_sessions_count": len(sessions),
                "registered_devices_count": len(devices),
                "feedback_history": [dict(f) for f in support_feedback]
            }

    @classmethod
    def generate_diagnostic_bundle(cls, admin_id: str) -> Dict[str, Any]:
        health = system_health_monitor.get_full_health_report()
        now_str = datetime.now(timezone.utc).isoformat()
        
        bundle = {
            "bundle_id": f"diag_{int(datetime.now().timestamp())}",
            "generated_at": now_str,
            "generated_by": admin_id,
            "system_health": health,
            "environment_summary": {
                "os": os.name,
                "python_version": os.sys.version.split()[0],
                "database_path": settings.DATABASE_PATH
            }
        }
        return bundle

support_diagnostics_service = SupportDiagnosticsService()
