import json
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from app.db.connection import get_db_connection, with_db_retry

logger = logging.getLogger("app.admin.audit")

class AdminAuditService:
    SECRET_KEYS = {
        "password", "secret", "token", "admin_key", "vendor_admin_key",
        "api_key", "authorization", "bearer", "cookie", "private_key"
    }

    @classmethod
    def sanitize_payload(cls, data: Any) -> Any:
        if isinstance(data, dict):
            sanitized = {}
            for k, v in data.items():
                if any(sec in k.lower() for sec in cls.SECRET_KEYS):
                    sanitized[k] = "[REDACTED]"
                else:
                    sanitized[k] = cls.sanitize_payload(v)
            return sanitized
        elif isinstance(data, list):
            return [cls.sanitize_payload(item) for item in data]
        return data

    @classmethod
    @with_db_retry()
    def record_event(
        cls,
        admin_id: str,
        action: str,
        target: Optional[str] = "",
        reason: Optional[str] = "",
        previous_state: Optional[Dict[str, Any]] = None,
        resulting_state: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
        status: str = "SUCCESS"
    ) -> Dict[str, Any]:
        now_str = datetime.now(timezone.utc).isoformat()
        
        clean_prev = json.dumps(cls.sanitize_payload(previous_state or {}))
        clean_res = json.dumps(cls.sanitize_payload(resulting_state or {}))
        clean_meta = json.dumps(cls.sanitize_payload(request_metadata or {}))

        with get_db_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO admin_audit_events
                (admin_id, timestamp, action, target, reason, previous_state, resulting_state, request_metadata, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (admin_id, now_str, action, target or "", reason or "", clean_prev, clean_res, clean_meta, status))
            conn.commit()
            event_id = cursor.lastrowid

            # Also mirror to admin_audit_log for legacy compatibility
            conn.execute("""
                INSERT INTO admin_audit_log (admin_id, action, target_user, details, ip_address, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (admin_id, action, target or "", f"{reason or ''} - Status: {status}".strip(" -"), request_metadata.get("ip_address", "127.0.0.1") if request_metadata else "127.0.0.1", now_str))
            conn.commit()

        return {
            "id": event_id,
            "admin_id": admin_id,
            "timestamp": now_str,
            "action": action,
            "target": target,
            "reason": reason,
            "previous_state": previous_state,
            "resulting_state": resulting_state,
            "request_metadata": request_metadata,
            "status": status
        }

    @classmethod
    def list_events(cls, limit: int = 100, action_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        with get_db_connection() as conn:
            sql = "SELECT * FROM admin_audit_events"
            params = []
            if action_filter:
                sql += " WHERE action LIKE ?"
                params.append(f"%{action_filter}%")
            sql += " ORDER BY id DESC LIMIT ?"
            params.append(limit)

            rows = conn.execute(sql, params).fetchall()
            events = []
            for r in rows:
                item = dict(r)
                try:
                    item["previous_state"] = json.loads(item.get("previous_state") or "{}")
                except Exception:
                    pass
                try:
                    item["resulting_state"] = json.loads(item.get("resulting_state") or "{}")
                except Exception:
                    pass
                try:
                    item["request_metadata"] = json.loads(item.get("request_metadata") or "{}")
                except Exception:
                    pass
                events.append(item)
            return events

admin_audit_service = AdminAuditService()
