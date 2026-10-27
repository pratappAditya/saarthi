import json
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from fastapi import HTTPException
from app.db.connection import get_db_connection
from app.core.plans import PlanService
from app.admin.audit.admin_audit_service import admin_audit_service

logger = logging.getLogger("app.admin.services.plan_mgmt")

class PlanManagementService:
    CANONICAL_PLANS = ["FREE", "STUDENT", "PERSONAL", "POWER", "TEAMS", "ENTERPRISE"]

    @classmethod
    def get_canonical_catalog(cls) -> Dict[str, Any]:
        catalog = {}
        for plan in cls.CANONICAL_PLANS:
            caps = PlanService.PLANS.get(plan, {})
            catalog[plan] = caps
        return {
            "canonical_plans": cls.CANONICAL_PLANS,
            "catalog": catalog
        }

    @classmethod
    def get_plan_distribution(cls) -> Dict[str, int]:
        with get_db_connection() as conn:
            rows = conn.execute("SELECT subscription_plan, COUNT(*) as count FROM users GROUP BY subscription_plan").fetchall()
            dist = {p: 0 for p in cls.CANONICAL_PLANS}
            for r in rows:
                p_name = r["subscription_plan"]
                if p_name in dist:
                    dist[p_name] = r["count"]
                else:
                    dist[p_name] = r["count"]
            return dist

    @classmethod
    def inspect_user_entitlements(cls, user_id: str) -> Dict[str, Any]:
        with get_db_connection() as conn:
            user = conn.execute("SELECT user_id, subscription_plan FROM users WHERE user_id = ?", (user_id,)).fetchone()
            if not user:
                raise HTTPException(status_code=404, detail="User not found.")

            override = conn.execute("SELECT * FROM entitlement_overrides WHERE user_id = ?", (user_id,)).fetchone()
            override_row = dict(override) if override else None
            plan_name = user["subscription_plan"]
            base_caps = PlanService.PLANS.get(plan_name, {})

            override_dict = {}
            if override_row and override_row.get("capabilities_json"):
                try:
                    override_dict = json.loads(override_row["capabilities_json"])
                except Exception:
                    pass

            effective_caps = {**base_caps, **override_dict}
            if override_row and override_row.get("plan_override"):
                effective_caps = {**PlanService.PLANS.get(override_row["plan_override"], {}), **override_dict}

            return {
                "user_id": user_id,
                "current_plan": plan_name,
                "base_capabilities": base_caps,
                "has_override": bool(override),
                "plan_override": override["plan_override"] if override else None,
                "capability_overrides": override_dict,
                "effective_capabilities": effective_caps
            }

    @classmethod
    def set_entitlement_override(
        cls,
        user_id: str,
        plan_override: Optional[str],
        capabilities_override: Optional[Dict[str, Any]],
        admin_id: str,
        expires_at: Optional[str] = None,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        if plan_override and plan_override.upper() not in cls.CANONICAL_PLANS:
            raise HTTPException(status_code=400, detail=f"Invalid plan override. Canonical plans: {cls.CANONICAL_PLANS}")

        prev_info = cls.inspect_user_entitlements(user_id)
        now_str = datetime.now(timezone.utc).isoformat()
        caps_json = json.dumps(capabilities_override or {})

        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO entitlement_overrides (user_id, plan_override, capabilities_json, expires_at, created_by, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    plan_override = excluded.plan_override,
                    capabilities_json = excluded.capabilities_json,
                    expires_at = excluded.expires_at,
                    created_by = excluded.created_by,
                    updated_at = excluded.updated_at
            """, (user_id, plan_override.upper() if plan_override else None, caps_json, expires_at, admin_id, now_str))
            conn.commit()

        res_info = cls.inspect_user_entitlements(user_id)
        admin_audit_service.record_event(
            admin_id=admin_id,
            action="SET_ENTITLEMENT_OVERRIDE",
            target=user_id,
            reason=reason or "Entitlement override applied",
            previous_state=prev_info,
            resulting_state=res_info
        )

        return res_info

plan_mgmt_service = PlanManagementService()
