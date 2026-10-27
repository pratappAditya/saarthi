import sqlite3
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from fastapi import HTTPException, Depends

from app.core.plans import (
    PLAN_POWER, PLAN_FREE, PLAN_CATALOG,
    PlanService, CAPABILITIES
)

from app.db.connection import get_db_connection
from app.config.settings import settings

logger = logging.getLogger("app.core.entitlements")

class AccountService:
    def __init__(self, db_path: Optional[str] = None):
        self._db_path = db_path
        self._init_account_tables()

    @property
    def db_path(self) -> str:
        return self._db_path or settings.DATABASE_PATH

    @db_path.setter
    def db_path(self, val: str):
        self._db_path = val

    def _get_connection(self):
        return get_db_connection(self.db_path)

    def _init_account_tables(self):
        conn = self._get_connection()
        try:
            with conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS user_subscription (
                        user_id TEXT PRIMARY KEY,
                        plan_id TEXT NOT NULL,
                        subscription_status TEXT NOT NULL,
                        billing_period TEXT NOT NULL,
                        region TEXT NOT NULL,
                        currency TEXT NOT NULL,
                        started_at TEXT NOT NULL,
                        expires_at TEXT,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    );
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS usage_records (
                        user_id TEXT NOT NULL,
                        metric_key TEXT NOT NULL,
                        usage_count INTEGER NOT NULL DEFAULT 0,
                        updated_at TEXT NOT NULL,
                        PRIMARY KEY (user_id, metric_key)
                    );
                """)
                # Insert default development account if missing
                cur = conn.execute("SELECT user_id FROM user_subscription WHERE user_id = 'default_local_user'")
                if not cur.fetchone():
                    now = datetime.now(timezone.utc).isoformat()
                    conn.execute("""
                        INSERT INTO user_subscription (
                            user_id, plan_id, subscription_status, billing_period,
                            region, currency, started_at, expires_at, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        "default_local_user",
                        PLAN_POWER,  # Default dev plan is Power
                        "ACTIVE",
                        "month",
                        "IN",
                        "INR",
                        now,
                        None,
                        now,
                        now
                    ))
        finally:
            conn.close()

    def get_account_subscription(self, user_id: str = "default_local_user") -> Dict[str, Any]:
        conn = self._get_connection()
        try:
            row = conn.execute("SELECT * FROM user_subscription WHERE user_id = ?", (user_id,)).fetchone()
            if row:
                return dict(row)
            # Fallback default
            return {
                "user_id": user_id,
                "plan_id": PLAN_POWER,
                "subscription_status": "ACTIVE",
                "billing_period": "month",
                "region": "IN",
                "currency": "INR"
            }
        finally:
            conn.close()

    def update_account_plan(self, plan_id: str, user_id: str = "default_local_user") -> Dict[str, Any]:
        plan = plan_id.lower()
        if plan not in PLAN_CATALOG:
            raise ValueError(f"Invalid plan ID: {plan_id}")

        now = datetime.now(timezone.utc).isoformat()
        conn = self._get_connection()
        try:
            with conn:
                conn.execute("""
                    UPDATE user_subscription
                    SET plan_id = ?, updated_at = ?
                    WHERE user_id = ?
                """, (plan, now, user_id))
            return self.get_account_subscription(user_id)
        finally:
            conn.close()

class UsageService:
    def __init__(self, db_path: Optional[str] = None):
        self._db_path = db_path

    @property
    def db_path(self) -> str:
        return self._db_path or settings.DATABASE_PATH

    @db_path.setter
    def db_path(self, val: str):
        self._db_path = val

    def _get_connection(self):
        return get_db_connection(self.db_path)

    def get_usage(self, user_id: str = "default_local_user") -> Dict[str, int]:
        conn = self._get_connection()
        try:
            rows = conn.execute("SELECT metric_key, usage_count FROM usage_records WHERE user_id = ?", (user_id,)).fetchall()
            return {row["metric_key"]: row["usage_count"] for row in rows}
        finally:
            conn.close()

    def increment_usage(self, metric_key: str, amount: int = 1, user_id: str = "default_local_user") -> int:
        now = datetime.now(timezone.utc).isoformat()
        conn = self._get_connection()
        try:
            with conn:
                conn.execute("""
                    INSERT INTO usage_records (user_id, metric_key, usage_count, updated_at)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(user_id, metric_key) DO UPDATE SET
                        usage_count = usage_count + excluded.usage_count,
                        updated_at = excluded.updated_at
                """, (user_id, metric_key, amount, now))
                row = conn.execute("SELECT usage_count FROM usage_records WHERE user_id = ? AND metric_key = ?", (user_id, metric_key)).fetchone()
                return row["usage_count"] if row else 0
        finally:
            conn.close()

# Global Instances
account_service = AccountService()
usage_service = UsageService()

def get_current_plan(user_id: str = "default_local_user") -> str:
    sub = account_service.get_account_subscription(user_id)
    return sub.get("plan_id", PLAN_POWER)

def require_capability(capability_id: str):
    """
    FastAPI dependency factory enforcing server-side entitlement.
    Prevents unauthorized access to premium capabilities regardless of frontend state.
    """
    def _dependency():
        current_plan = get_current_plan()
        if not PlanService.is_capability_entitled(current_plan, capability_id):
            cap_desc = CAPABILITIES.get(capability_id, capability_id)
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "ENTITLEMENT_FORBIDDEN",
                    "capability": capability_id,
                    "capability_name": cap_desc,
                    "current_plan": current_plan,
                    "message": f"Capability '{capability_id}' ({cap_desc}) is not included in your '{current_plan.upper()}' plan. Please upgrade to access this feature."
                }
            )
        return True
    return _dependency
