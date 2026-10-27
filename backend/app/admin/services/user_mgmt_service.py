import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from fastapi import HTTPException
from app.db.connection import get_db_connection
from app.db.auth import AuthRepository
from app.admin.audit.admin_audit_service import admin_audit_service

logger = logging.getLogger("app.admin.services.user_mgmt")

class UserManagementService:
    @staticmethod
    def list_users(query: Optional[str] = None, role: Optional[str] = None, plan: Optional[str] = None) -> List[Dict[str, Any]]:
        with get_db_connection() as conn:
            sql = "SELECT user_id, email, full_name, is_verified, role, subscription_plan, created_at, updated_at FROM users WHERE 1=1"
            params = []
            if query:
                sql += " AND (email LIKE ? OR full_name LIKE ? OR user_id LIKE ?)"
                params.extend([f"%{query}%", f"%{query}%", f"%{query}%"])
            if role:
                sql += " AND role = ?"
                params.append(role.upper())
            if plan:
                sql += " AND subscription_plan = ?"
                params.append(plan.upper())

            sql += " ORDER BY id DESC LIMIT 200"
            rows = conn.execute(sql, params).fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def get_user_details(user_id: str) -> Dict[str, Any]:
        user = AuthRepository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User '{user_id}' not found.")

        devices = AuthRepository.list_user_devices(user_id)
        with get_db_connection() as conn:
            orders = [dict(r) for r in conn.execute("SELECT * FROM payment_orders WHERE user_id = ?", (user_id,)).fetchall()]
            quota = dict(conn.execute("SELECT * FROM free_usage_quota WHERE user_id_or_device = ?", (user_id,)).fetchone() or {})
            sessions = [dict(r) for r in conn.execute("SELECT * FROM sessions WHERE user_id = ?", (user_id,)).fetchall()]

        return {
            "status": "success",
            "user": user,
            "devices": devices,
            "sessions": sessions,
            "payment_orders": orders,
            "quota": quota
        }

    @staticmethod
    def update_user_role(user_id: str, new_role: str, admin_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        valid_roles = ["USER", "ADMIN", "SUPER_ADMIN", "SUPPORT", "ANALYST", "SUSPENDED"]
        if new_role.upper() not in valid_roles:
            raise HTTPException(status_code=400, detail=f"Invalid role. Allowed: {valid_roles}")

        user = AuthRepository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        prev_state = {"role": user.get("role")}
        now_str = datetime.now(timezone.utc).isoformat()

        with get_db_connection() as conn:
            conn.execute("UPDATE users SET role = ?, updated_at = ? WHERE user_id = ?",
                         (new_role.upper(), now_str, user_id))
            conn.commit()

        resulting_state = {"role": new_role.upper()}
        admin_audit_service.record_event(
            admin_id=admin_id,
            action="UPDATE_USER_ROLE",
            target=user_id,
            reason=reason or "Role update",
            previous_state=prev_state,
            resulting_state=resulting_state
        )

        return {"user_id": user_id, "updated_role": new_role.upper()}

    @staticmethod
    def update_user_plan(user_id: str, new_plan: str, admin_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        canonical_plans = ["FREE", "STUDENT", "PERSONAL", "POWER", "TEAMS", "ENTERPRISE"]
        if new_plan.upper() not in canonical_plans:
            raise HTTPException(status_code=400, detail=f"Invalid plan taxonomy. Canonical plans: {canonical_plans}")

        user = AuthRepository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        prev_state = {"subscription_plan": user.get("subscription_plan")}
        AuthRepository.update_user_plan(user_id, new_plan.upper())

        resulting_state = {"subscription_plan": new_plan.upper()}
        admin_audit_service.record_event(
            admin_id=admin_id,
            action="UPDATE_USER_PLAN",
            target=user_id,
            reason=reason or "Plan update",
            previous_state=prev_state,
            resulting_state=resulting_state
        )

        return {"user_id": user_id, "updated_plan": new_plan.upper()}

    @staticmethod
    def suspend_user(user_id: str, admin_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        user = AuthRepository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        prev_state = {"role": user.get("role")}
        now_str = datetime.now(timezone.utc).isoformat()

        with get_db_connection() as conn:
            conn.execute("UPDATE users SET role = 'SUSPENDED', updated_at = ? WHERE user_id = ?", (now_str, user_id))
            conn.commit()

        AuthRepository.revoke_all_user_sessions(user_id)

        resulting_state = {"role": "SUSPENDED", "sessions_revoked": True}
        admin_audit_service.record_event(
            admin_id=admin_id,
            action="SUSPEND_USER",
            target=user_id,
            reason=reason or "Account suspended",
            previous_state=prev_state,
            resulting_state=resulting_state
        )

        return {"message": f"User '{user_id}' suspended and all sessions revoked."}

    @staticmethod
    def restore_user(user_id: str, admin_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        user = AuthRepository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        prev_state = {"role": user.get("role")}
        now_str = datetime.now(timezone.utc).isoformat()

        with get_db_connection() as conn:
            conn.execute("UPDATE users SET role = 'USER', updated_at = ? WHERE user_id = ?", (now_str, user_id))
            conn.commit()

        resulting_state = {"role": "USER"}
        admin_audit_service.record_event(
            admin_id=admin_id,
            action="RESTORE_USER",
            target=user_id,
            reason=reason or "Account restored",
            previous_state=prev_state,
            resulting_state=resulting_state
        )

        return {"message": f"User '{user_id}' restored to active USER status."}

    @staticmethod
    def delete_user(user_id: str, admin_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        user = AuthRepository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        prev_state = {"user_id": user_id, "email": user.get("email")}
        AuthRepository.delete_account(user_id)

        admin_audit_service.record_event(
            admin_id=admin_id,
            action="DELETE_USER",
            target=user_id,
            reason=reason or "Account deleted",
            previous_state=prev_state,
            resulting_state={"deleted": True}
        )

        return {"message": f"User '{user_id}' deleted."}

user_mgmt_service = UserManagementService()
