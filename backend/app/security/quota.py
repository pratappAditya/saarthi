from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Tuple
import sqlite3
from app.db.connection import get_db_connection, with_db_retry

FREE_DAILY_REQUEST_LIMIT = 30
COOLDOWN_HOURS = 24

class QuotaManager:
    @staticmethod
    def check_and_increment_quota(entity_id: str, plan: str = "FREE") -> Tuple[bool, Dict[str, Any]]:
        """
        Server-authoritative usage quota check.
        Paid plans (STUDENT, PERSONAL, POWER) bypass daily cooldown.
        FREE plan gets 30 requests/day then 24-hour cooldown.
        """
        if plan.upper() in ("STUDENT", "PERSONAL", "POWER", "TEAMS", "ENTERPRISE"):
            return True, {
                "allowed": True,
                "plan": plan,
                "unlimited": True,
                "remaining_requests": 999999,
                "cooldown_active": False,
                "cooldown_until": None
            }

        now = datetime.now(timezone.utc)
        now_str = now.isoformat()

        with get_db_connection() as conn:
            cursor = conn.cursor()
            row = cursor.execute("SELECT * FROM free_usage_quota WHERE user_id_or_device = ?", (entity_id,)).fetchone()
            
            if not row:
                cursor.execute("""
                    INSERT INTO free_usage_quota (user_id_or_device, request_count, token_count, daily_limit, cooldown_until, last_request_at, created_at)
                    VALUES (?, 1, 0, ?, NULL, ?, ?)
                """, (entity_id, FREE_DAILY_REQUEST_LIMIT, now_str, now_str))
                conn.commit()
                return True, {
                    "allowed": True,
                    "plan": "FREE",
                    "remaining_requests": FREE_DAILY_REQUEST_LIMIT - 1,
                    "cooldown_active": False,
                    "cooldown_until": None
                }

            q = dict(row)
            cooldown_until_str = q.get("cooldown_until")
            if cooldown_until_str:
                cooldown_until_dt = datetime.fromisoformat(cooldown_until_str)
                if now < cooldown_until_dt:
                    seconds_left = int((cooldown_until_dt - now).total_seconds())
                    return False, {
                        "allowed": False,
                        "plan": "FREE",
                        "error": "FREE plan daily allowance exhausted. 24-hour cooldown in effect.",
                        "remaining_requests": 0,
                        "cooldown_active": True,
                        "cooldown_until": cooldown_until_str,
                        "cooldown_seconds_remaining": seconds_left
                    }
                else:
                    # Cooldown expired -> Reset quota
                    cursor.execute("""
                        UPDATE free_usage_quota SET request_count = 1, cooldown_until = NULL, last_request_at = ? WHERE user_id_or_device = ?
                    """, (now_str, entity_id))
                    conn.commit()
                    return True, {
                        "allowed": True,
                        "plan": "FREE",
                        "remaining_requests": FREE_DAILY_REQUEST_LIMIT - 1,
                        "cooldown_active": False,
                        "cooldown_until": None
                    }

            last_req_dt = datetime.fromisoformat(q["last_request_at"])
            if now - last_req_dt > timedelta(hours=24):
                # New day -> reset count
                new_count = 1
                cursor.execute("""
                    UPDATE free_usage_quota SET request_count = ?, last_request_at = ? WHERE user_id_or_device = ?
                """, (new_count, now_str, entity_id))
                conn.commit()
                return True, {
                    "allowed": True,
                    "plan": "FREE",
                    "remaining_requests": FREE_DAILY_REQUEST_LIMIT - new_count,
                    "cooldown_active": False,
                    "cooldown_until": None
                }
            
            # Within 24-hour window
            current_count = q["request_count"] + 1
            if current_count >= FREE_DAILY_REQUEST_LIMIT:
                cooldown_dt = now + timedelta(hours=COOLDOWN_HOURS)
                cooldown_str = cooldown_dt.isoformat()
                cursor.execute("""
                    UPDATE free_usage_quota SET request_count = ?, cooldown_until = ?, last_request_at = ? WHERE user_id_or_device = ?
                """, (current_count, cooldown_str, now_str, entity_id))
                conn.commit()
                return False, {
                    "allowed": False,
                    "plan": "FREE",
                    "error": "FREE plan daily allowance exhausted. 24-hour cooldown in effect.",
                    "remaining_requests": 0,
                    "cooldown_active": True,
                    "cooldown_until": cooldown_str,
                    "cooldown_seconds_remaining": COOLDOWN_HOURS * 3600
                }
            else:
                cursor.execute("""
                    UPDATE free_usage_quota SET request_count = ?, last_request_at = ? WHERE user_id_or_device = ?
                """, (current_count, now_str, entity_id))
                conn.commit()
                return True, {
                    "allowed": True,
                    "plan": "FREE",
                    "remaining_requests": FREE_DAILY_REQUEST_LIMIT - current_count,
                    "cooldown_active": False,
                    "cooldown_until": None
                }

    @staticmethod
    def get_quota_status(entity_id: str, plan: str = "FREE") -> Dict[str, Any]:
        if plan.upper() in ("STUDENT", "PERSONAL", "POWER"):
            return {
                "plan": plan,
                "unlimited": True,
                "remaining_requests": 999999,
                "cooldown_active": False,
                "cooldown_until": None
            }

        now = datetime.now(timezone.utc)
        with get_db_connection() as conn:
            row = conn.execute("SELECT * FROM free_usage_quota WHERE user_id_or_device = ?", (entity_id,)).fetchone()
            if not row:
                return {
                    "plan": "FREE",
                    "unlimited": False,
                    "remaining_requests": FREE_DAILY_REQUEST_LIMIT,
                    "cooldown_active": False,
                    "cooldown_until": None
                }

            q = dict(row)
            cooldown_until_str = q.get("cooldown_until")
            if cooldown_until_str:
                cooldown_until_dt = datetime.fromisoformat(cooldown_until_str)
                if now < cooldown_until_dt:
                    seconds_left = int((cooldown_until_dt - now).total_seconds())
                    return {
                        "plan": "FREE",
                        "unlimited": False,
                        "remaining_requests": 0,
                        "cooldown_active": True,
                        "cooldown_until": cooldown_until_str,
                        "cooldown_seconds_remaining": seconds_left
                    }

            remaining = max(0, FREE_DAILY_REQUEST_LIMIT - q.get("request_count", 0))
            return {
                "plan": "FREE",
                "unlimited": False,
                "remaining_requests": remaining,
                "cooldown_active": False,
                "cooldown_until": None
            }
