import os
import hmac
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Header, Depends, Query, Body, Request
from pydantic import BaseModel, Field

from app.config.settings import settings
from app.db.auth import AuthRepository
from app.admin.auth.admin_auth import verify_admin_access, require_admin_role, hash_password, verify_password, verify_admin_key, get_configured_admin_key
from app.admin.repositories.admin_repository import AdminRepository
from app.admin.audit.admin_audit_service import admin_audit_service
from app.admin.health.system_health_monitor import system_health_monitor

# Admin Service Layer imports
from app.admin.services.user_mgmt_service import user_mgmt_service
from app.admin.services.plan_mgmt_service import plan_mgmt_service
from app.admin.services.agent_ops_service import agent_ops_service
from app.admin.services.ai_ops_service import ai_ops_service
from app.admin.services.domain_ops_service import domain_ops_service
from app.admin.services.automation_ops_service import automation_ops_service
from app.admin.services.security_ops_service import security_ops_service
from app.admin.services.system_health_service import system_health_service
from app.admin.services.support_diagnostics_service import support_diagnostics_service

logger = logging.getLogger("app.api.admin")

router = APIRouter(prefix="/admin", tags=["AdminControlPanel"])

# --- REQUEST SCHEMAS ---

class AdminLoginRequest(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    admin_key: Optional[str] = None

class AdminPlanUpdate(BaseModel):
    user_id: str
    plan: str
    reason: Optional[str] = None

class UserRoleUpdate(BaseModel):
    user_id: str
    role: str
    reason: Optional[str] = None

class UserActionRequest(BaseModel):
    user_id: str
    reason: Optional[str] = None

class RefundRequest(BaseModel):
    order_id: str
    reason: Optional[str] = None

class EntitlementOverrideRequest(BaseModel):
    user_id: str
    plan_override: Optional[str] = None
    capabilities_override: Optional[Dict[str, Any]] = None
    expires_at: Optional[str] = None
    reason: Optional[str] = None

class FeatureFlagUpdate(BaseModel):
    key: str
    enabled: bool
    rollout_percentage: int = 100

class MaintenanceModeUpdate(BaseModel):
    enabled: bool
    message: str = "Saarthi is undergoing scheduled system maintenance."
    bypass_whitelist: str = "127.0.0.1,admin@saarthi.ai"

class ToolPolicyUpdate(BaseModel):
    tool_id: str
    risk_classification: str = "LOW"
    permission_level: str = "AUTOMATIC"
    enabled: bool = True

class QuotaResetRequest(BaseModel):
    user_id_or_device: str

class OrganizationCreateRequest(BaseModel):
    name: str
    plan: str = "TEAMS"
    max_seats: int = 10

class IpBanRequest(BaseModel):
    identifier: str
    ban_type: str = "IP"
    reason: str = ""

class AIConfigUpdate(BaseModel):
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    provider: Optional[str] = None
    model_name: Optional[str] = None
    reason: Optional[str] = None

def get_client_ip(request: Request) -> str:
    return request.client.host if request.client else "127.0.0.1"

# --- 1. ADMIN AUTHENTICATION & VERIFICATION ---

@router.post("/auth/login")
def admin_login(payload: AdminLoginRequest, request: Request):
    client_ip = get_client_ip(request)

    # 1. Admin Key Auth
    is_prod = os.getenv("ENVIRONMENT", "development").lower() in ("production", "staging")

    if payload.admin_key:
        configured_key = get_configured_admin_key()
        if is_prod and not configured_key:
            logger.error("Admin login rejected: Admin secret key is unconfigured or using insecure placeholder in production.")
            raise HTTPException(status_code=500, detail="Admin key authentication is disabled due to missing production configuration.")

        if verify_admin_key(payload.admin_key):
            sess = AdminRepository.create_session("SYSTEM_KEY_ADMIN", ip_address=client_ip)
            admin_audit_service.record_event(
                admin_id="SYSTEM_KEY_ADMIN",
                action="ADMIN_LOGIN",
                target="SYSTEM",
                reason="Login via Admin Secret Key",
                request_metadata={"ip_address": client_ip}
            )
            return {
                "status": "success",
                "token": sess["session_token"],
                "admin": {
                    "admin_id": "SYSTEM_KEY_ADMIN",
                    "email": "admin@saarthi.local",
                    "role": "SUPER_ADMIN"
                }
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid admin secret key.")

    # 2. Email / Password Auth
    if payload.email and payload.password:
        admin_user = AdminRepository.get_admin_by_email(payload.email)
        if admin_user:
            if not verify_password(payload.password, admin_user["password_hash"]):
                raise HTTPException(status_code=401, detail="Invalid admin credentials.")
            sess = AdminRepository.create_session(admin_user["admin_id"], ip_address=client_ip)
            admin_audit_service.record_event(
                admin_id=admin_user["admin_id"],
                action="ADMIN_LOGIN",
                target=admin_user["email"],
                reason="Login via admin account credentials",
                request_metadata={"ip_address": client_ip}
            )
            return {
                "status": "success",
                "token": sess["session_token"],
                "admin": {
                    "admin_id": admin_user["admin_id"],
                    "email": admin_user["email"],
                    "role": admin_user["role"]
                }
            }

        # Fallback check on standard users with elevated role
        user = AuthRepository.authenticate(payload.email, payload.password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid admin credentials.")

        if user.get("role") not in ["ADMIN", "SUPER_ADMIN", "SUPPORT", "ANALYST"]:
            raise HTTPException(status_code=403, detail="User does not have administrative privileges.")

        sess = AuthRepository.create_session(user["user_id"], device_id="admin_console")
        admin_audit_service.record_event(
            admin_id=user["user_id"],
            action="ADMIN_LOGIN",
            target=user["email"],
            reason="Login via user table admin account",
            request_metadata={"ip_address": client_ip}
        )
        return {
            "status": "success",
            "token": sess["session_token"],
            "admin": {
                "admin_id": user["user_id"],
                "email": user["email"],
                "role": user["role"]
            }
        }

    raise HTTPException(status_code=400, detail="Must provide admin_key or email and password.")

@router.get("/auth/verify")
def admin_verify(admin: Dict[str, Any] = Depends(verify_admin_access)):
    return {"status": "success", "authenticated": True, "admin": admin}

@router.post("/auth/logout")
def admin_logout(authorization: Optional[str] = Header(None)):
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        AdminRepository.revoke_session(token)
    return {"status": "success", "message": "Logged out successfully."}

# --- 2. ADMIN DASHBOARD OVERVIEW ---

@router.get("/dashboard")
def get_admin_dashboard(admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "SUPPORT", "ANALYST"]))):
    metrics_users = user_mgmt_service.list_users()
    plan_dist = plan_mgmt_service.get_plan_distribution()
    tasks = agent_ops_service.list_tasks()
    routines_resp = automation_ops_service.list_routines()
    health = system_health_service.get_system_health()

    running_tasks = [t for t in tasks if t.get("status") == "in_progress"]
    failed_tasks = [t for t in tasks if t.get("status") == "failed"]

    return {
        "status": "success",
        "metrics": {
            "total_users": len(metrics_users),
            "active_users": len([u for u in metrics_users if u.get("role") != "SUSPENDED"]),
            "suspended_users": len([u for u in metrics_users if u.get("role") == "SUSPENDED"]),
            "plan_breakdown": plan_dist,
            "running_agent_tasks": len(running_tasks),
            "failed_agent_tasks": len(failed_tasks),
            "total_agent_tasks": len(tasks),
            "active_routines": routines_resp.get("active_routines", 0),
            "total_routines": routines_resp.get("total_routines", 0),
            "system_status": health.get("status", "healthy")
        },
        "system_health": health,
        "server_time": datetime.now(timezone.utc).isoformat()
    }

# --- 3. USER & ACCOUNT MANAGEMENT ---

@router.get("/users")
def list_users(
    query: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    plan: Optional[str] = Query(None),
    admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "SUPPORT", "ANALYST"]))
):
    users = user_mgmt_service.list_users(query=query, role=role, plan=plan)
    return {"status": "success", "users": users}

@router.get("/users/{user_id}/details")
def user_details(
    user_id: str,
    admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "SUPPORT", "ANALYST"]))
):
    return user_mgmt_service.get_user_details(user_id)

@router.post("/users/update-role")
def update_user_role(
    req: UserRoleUpdate,
    admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN"]))
):
    res = user_mgmt_service.update_user_role(req.user_id, req.role, admin_id=admin["admin_id"], reason=req.reason)
    return {"status": "success", **res}

@router.post("/update-plan")
@router.post("/users/update-plan")
def update_user_plan(
    req: AdminPlanUpdate,
    admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN"]))
):
    res = user_mgmt_service.update_user_plan(req.user_id, req.plan, admin_id=admin["admin_id"], reason=req.reason)
    return {"status": "success", **res}

@router.post("/users/suspend")
def suspend_user(
    req: UserActionRequest,
    admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN"]))
):
    res = user_mgmt_service.suspend_user(req.user_id, admin_id=admin["admin_id"], reason=req.reason)
    return {"status": "success", **res}

@router.post("/users/restore")
def restore_user(
    req: UserActionRequest,
    admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN"]))
):
    res = user_mgmt_service.restore_user(req.user_id, admin_id=admin["admin_id"], reason=req.reason)
    return {"status": "success", **res}

@router.delete("/users/{user_id}")
def delete_user(
    user_id: str,
    reason: Optional[str] = Query(None),
    admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN"]))
):
    res = user_mgmt_service.delete_user(user_id, admin_id=admin["admin_id"], reason=reason)
    return {"status": "success", **res}

# --- 4. PLAN & ENTITLEMENT MANAGEMENT ---

@router.get("/subscriptions")
@router.get("/plans/catalog")
def get_plans_and_subscriptions(admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "SUPPORT", "ANALYST"]))):
    from app.billing.plan_registry import plan_registry
    dist = plan_mgmt_service.get_plan_distribution()
    all_plans = plan_registry.list_plans()
    catalog_list = [
        {
            "id": p.plan_id.value,
            "name": p.name,
            "version": p.version,
            "price_inr": p.price_inr,
            "currency": p.currency,
            "interval": p.billing_interval.value if hasattr(p.billing_interval, "value") else str(p.billing_interval),
            "description": p.description,
            "badge": p.badge,
            "is_custom": p.is_custom,
            "limits": p.limits,
            "capabilities": p.capabilities
        }
        for p in all_plans
    ]
    return {
        "status": "success",
        "subscriptions": [{"subscription_plan": k, "user_count": v} for k, v in dist.items()],
        "canonical_plans": [p["id"] for p in catalog_list],
        "catalog": catalog_list
    }

@router.get("/entitlements")
def get_entitlement_matrix(admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "SUPPORT", "ANALYST"]))):
    catalog = plan_mgmt_service.get_canonical_catalog()
    return {"status": "success", "entitlement_matrix": catalog["catalog"]}

@router.get("/entitlements/{user_id}")
def inspect_user_entitlements(user_id: str, admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "SUPPORT", "ANALYST"]))):
    info = plan_mgmt_service.inspect_user_entitlements(user_id)
    return {"status": "success", **info}

@router.post("/entitlements/override")
def set_entitlement_override(
    req: EntitlementOverrideRequest,
    admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN"]))
):
    res = plan_mgmt_service.set_entitlement_override(
        user_id=req.user_id,
        plan_override=req.plan_override,
        capabilities_override=req.capabilities_override,
        admin_id=admin["admin_id"],
        expires_at=req.expires_at,
        reason=req.reason
    )
    return {"status": "success", "override": res}

@router.get("/payments")
def list_payments(admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "SUPPORT", "ANALYST"]))):
    from app.db.connection import get_db_connection
    with get_db_connection() as conn:
        try:
            rows = conn.execute("SELECT * FROM payment_orders ORDER BY id DESC LIMIT 100").fetchall()
            return {"status": "success", "payments": [dict(r) for r in rows]}
        except Exception:
            return {"status": "success", "payments": []}

@router.post("/payments/refund")
def refund_payment(req: RefundRequest, admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN"]))):
    from app.db.connection import get_db_connection
    now_str = datetime.now(timezone.utc).isoformat()
    with get_db_connection() as conn:
        order = conn.execute("SELECT * FROM payment_orders WHERE order_id = ?", (req.order_id,)).fetchone()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found.")
        conn.execute("UPDATE payment_orders SET status = 'REFUNDED', updated_at = ? WHERE order_id = ?", (now_str, req.order_id))
        AuthRepository.update_user_plan(order["user_id"], "FREE")
        conn.commit()

    admin_audit_service.record_event(
        admin_id=admin["admin_id"],
        action="REFUND_PAYMENT",
        target=order["user_id"],
        reason=req.reason or f"Order {req.order_id} refunded",
        resulting_state={"order_id": req.order_id, "status": "REFUNDED"}
    )
    return {"status": "success", "message": f"Order {req.order_id} refunded and user plan reset to FREE."}

# --- 5. USAGE & QUOTA MONITORING ---

@router.get("/quotas")
def list_quotas(admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "SUPPORT", "ANALYST"]))):
    from app.db.connection import get_db_connection
    with get_db_connection() as conn:
        try:
            rows = conn.execute("SELECT * FROM free_usage_quota ORDER BY id DESC LIMIT 100").fetchall()
            return {"status": "success", "quotas": [dict(r) for r in rows]}
        except Exception:
            return {"status": "success", "quotas": []}

@router.post("/quotas/reset")
def reset_quota(req: QuotaResetRequest, admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN"]))):
    from app.db.connection import get_db_connection
    with get_db_connection() as conn:
        conn.execute("UPDATE free_usage_quota SET request_count = 0, token_count = 0, cooldown_until = NULL WHERE user_id_or_device = ?", (req.user_id_or_device,))
        conn.commit()
    admin_audit_service.record_event(
        admin_id=admin["admin_id"],
        action="RESET_QUOTA",
        target=req.user_id_or_device,
        reason="Quota reset by admin"
    )
    return {"status": "success", "message": f"Quota reset for '{req.user_id_or_device}'."}

# --- 6. AGENT OPERATIONS ---

@router.get("/agents/tasks")
@router.get("/agent/tasks")
def list_agent_tasks(
    status: Optional[str] = Query(None),
    admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "SUPPORT", "ANALYST"]))
):
    tasks = agent_ops_service.list_tasks(status_filter=status)
    return {"status": "success", "tasks_count": len(tasks), "tasks": tasks}

@router.get("/agents/tasks/{task_id}")
@router.get("/agent/tasks/{task_id}")
def get_agent_task_diagnostics(task_id: str, admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "SUPPORT", "ANALYST"]))):
    return agent_ops_service.get_task_diagnostics(task_id)

@router.post("/agents/tasks/{task_id}/cancel")
@router.post("/agent/tasks/{task_id}/cancel")
def cancel_agent_task(
    task_id: str,
    reason: Optional[str] = Query(None),
    admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN"]))
):
    res = agent_ops_service.cancel_task(task_id, admin_id=admin["admin_id"], reason=reason)
    return {"status": "success", **res}

@router.post("/agents/tasks/{task_id}/recover")
def recover_agent_task(
    task_id: str,
    reason: Optional[str] = Query(None),
    admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN"]))
):
    res = agent_ops_service.recover_task(task_id, admin_id=admin["admin_id"], reason=reason)
    return {"status": "success", **res}

@router.get("/permissions/pending")
def list_pending_permissions(admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "SUPPORT", "ANALYST"]))):
    pending = agent_ops_service.list_pending_permissions()
    return {"status": "success", "pending_count": len(pending), "pending": pending}

@router.post("/permissions/{req_id}/action")
def admin_permission_action(
    req_id: str,
    action: str = Query("approve"),
    reason: Optional[str] = Query(None),
    admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN"]))
):
    res = agent_ops_service.process_permission_action(req_id, action=action, admin_id=admin["admin_id"], reason=reason)
    return {"status": "success", **res}

# --- 7. AI / MODEL OPERATIONS ---

@router.get("/models/status")
@router.get("/ai/config")
def get_ai_status(admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "SUPPORT", "ANALYST"]))):
    return ai_ops_service.get_ai_status()

@router.post("/models/config")
@router.post("/ai/config")
def update_ai_config(
    req: AIConfigUpdate,
    admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN"]))
):
    cfg = ai_ops_service.update_model_config(
        provider=req.provider,
        model_name=req.model_name,
        temperature=req.temperature,
        max_tokens=req.max_tokens,
        admin_id=admin["admin_id"],
        reason=req.reason
    )
    return {"status": "success", "config": cfg}

# --- 8. DOMAIN OPERATIONS ---

@router.get("/domains")
def list_domains(admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "SUPPORT", "ANALYST"]))):
    return domain_ops_service.list_domain_packs_status()

# --- 9. AUTOMATION OPERATIONS ---

@router.get("/automation/routines")
@router.get("/routines")
def list_routines(admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "SUPPORT", "ANALYST"]))):
    return automation_ops_service.list_routines()

@router.post("/automation/routines/{routine_id}/toggle")
@router.post("/routines/{routine_id}/toggle")
def toggle_routine(
    routine_id: str,
    reason: Optional[str] = Query(None),
    admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN"]))
):
    return automation_ops_service.toggle_routine(routine_id, admin_id=admin["admin_id"], reason=reason)

# --- 10. SECURITY / TRUST / AUDIT ---

@router.get("/security/overview")
def get_security_overview(
    limit: int = Query(100, ge=1, le=500),
    admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "SUPPORT", "ANALYST"]))
):
    return security_ops_service.get_security_overview(limit=limit)

@router.get("/audit-logs")
def list_admin_audit_logs(
    limit: int = Query(100, ge=1, le=500),
    admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "SUPPORT", "ANALYST"]))
):
    events = admin_audit_service.list_events(limit=limit)
    return {"status": "success", "audit_logs": events}

@router.get("/trust-events")
def list_trust_events(
    user_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "SUPPORT", "ANALYST"]))
):
    from app.intelligence.audit.intelligence_audit import audit_service
    logs = audit_service.list_audit_logs(limit=limit, user_id=user_id)
    return {"status": "success", "trust_events": logs}

@router.get("/security/bans")
def list_ip_bans(admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "SUPPORT", "ANALYST"]))):
    bans = AdminRepository.list_ip_bans()
    return {"status": "success", "bans": bans}

@router.post("/security/ban")
def add_ip_ban(
    req: IpBanRequest,
    admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN"]))
):
    res = security_ops_service.add_ban(identifier=req.identifier, ban_type=req.ban_type, reason=req.reason, admin_id=admin["admin_id"])
    return {"status": "success", "ban": res}

@router.post("/security/unban")
def remove_ip_ban(
    identifier: str = Body(..., embed=True),
    admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN"]))
):
    res = security_ops_service.remove_ban(identifier, admin_id=admin["admin_id"])
    return {"status": "success", **res}

# --- 11. TOOL POLICIES & FEATURE FLAGS ---

@router.get("/tools")
def list_tool_policies(admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "SUPPORT", "ANALYST"]))):
    from app.intelligence.tools.tool_registry import ToolRegistry
    registered = ToolRegistry.list_tools()
    policies = {p["tool_id"]: p for p in AdminRepository.list_tool_policies()}

    combined = []
    for tool in registered:
        t_id = tool["id"]
        pol = policies.get(t_id, {})
        combined.append({
            "id": t_id,
            "name": tool["name"],
            "description": tool["description"],
            "risk_classification": pol.get("risk_classification", tool.get("risk_classification", "LOW")),
            "permission_level": pol.get("permission_level", tool.get("permission_level", "AUTOMATIC")),
            "enabled": bool(pol.get("enabled", 1))
        })
    return {"status": "success", "tools": combined}

@router.post("/tools/policy")
def set_tool_policy(
    req: ToolPolicyUpdate,
    admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN"]))
):
    pol = AdminRepository.set_tool_policy(
        tool_id=req.tool_id,
        risk_classification=req.risk_classification,
        permission_level=req.permission_level,
        enabled=req.enabled,
        admin_id=admin["admin_id"]
    )
    admin_audit_service.record_event(
        admin_id=admin["admin_id"],
        action="SET_TOOL_POLICY",
        target=req.tool_id,
        reason=f"Risk={req.risk_classification}, Perm={req.permission_level}"
    )
    return {"status": "success", "policy": pol}

@router.get("/feature-flags")
def list_feature_flags(admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "SUPPORT", "ANALYST"]))):
    flags = AdminRepository.list_feature_flags()
    return {"status": "success", "flags": flags}

@router.post("/feature-flags/update")
def update_feature_flag(
    req: FeatureFlagUpdate,
    admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN"]))
):
    flag = AdminRepository.update_feature_flag(
        key=req.key,
        enabled=req.enabled,
        rollout_percentage=req.rollout_percentage,
        admin_id=admin["admin_id"]
    )
    admin_audit_service.record_event(
        admin_id=admin["admin_id"],
        action="UPDATE_FEATURE_FLAG",
        target=req.key,
        reason=f"Enabled={req.enabled}, Rollout={req.rollout_percentage}%"
    )
    return {"status": "success", "flag": flag}

@router.get("/maintenance")
def get_maintenance_mode(admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "SUPPORT", "ANALYST"]))):
    maint = AdminRepository.get_maintenance_mode()
    return {"status": "success", "maintenance": maint}

@router.post("/maintenance/toggle")
def toggle_maintenance_mode(
    req: MaintenanceModeUpdate,
    admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN"]))
):
    maint = AdminRepository.set_maintenance_mode(
        enabled=req.enabled,
        message=req.message,
        bypass_whitelist=req.bypass_whitelist,
        admin_id=admin["admin_id"]
    )
    admin_audit_service.record_event(
        admin_id=admin["admin_id"],
        action="TOGGLE_MAINTENANCE_MODE",
        reason=f"Enabled={req.enabled}"
    )
    return {"status": "success", "maintenance": maint}

# --- 12. SYSTEM HEALTH & DIAGNOSTICS ---

@router.get("/health")
@router.get("/diagnostics")
def get_system_diagnostics(admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "SUPPORT", "ANALYST"]))):
    return system_health_service.get_system_health()

@router.post("/health/db-check")
@router.post("/diagnostics/db-check")
def run_db_integrity_check(admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "SUPPORT", "ANALYST"]))):
    res = system_health_service.run_database_integrity_check()
    return {
        "status": "success",
        "integrity_check": "ok" if res.get("is_healthy") else "failed",
        "tables_checked": 15,
        **res
    }

@router.get("/diagnostics/user-lookup")
def lookup_user_issue(
    user_id_or_email: str = Query(...),
    admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "SUPPORT", "ANALYST"]))
):
    return support_diagnostics_service.lookup_user_issue(user_id_or_email)

@router.post("/diagnostics/bundle")
def generate_diagnostic_bundle(admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "SUPPORT"]))):
    bundle = support_diagnostics_service.generate_diagnostic_bundle(admin["admin_id"])
    admin_audit_service.record_event(
        admin_id=admin["admin_id"],
        action="GENERATE_DIAGNOSTIC_BUNDLE",
        target="SYSTEM"
    )
    return {"status": "success", "bundle": bundle}

# --- 13. FEEDBACK & SUPPORT ---

@router.get("/feedback")
def list_feedback(admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "SUPPORT", "ANALYST"]))):
    items = AdminRepository.list_support_feedback()
    return {"status": "success", "feedback": items}

@router.post("/feedback")
def submit_feedback(user_id: str = Body(...), feedback_type: str = Body("GENERAL"), content: str = Body(...), rating: Optional[int] = Body(None)):
    item = AdminRepository.submit_feedback(user_id=user_id, feedback_type=feedback_type, content=content, rating=rating)
    return {"status": "success", "feedback": item}

# --- 14. ORGANIZATIONS / TEAMS ---

@router.get("/organizations")
def list_organizations(admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "SUPPORT", "ANALYST"]))):
    orgs = AdminRepository.list_organizations()
    return {"status": "success", "organizations": orgs}

@router.post("/organizations")
def create_organization(
    req: OrganizationCreateRequest,
    admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN"]))
):
    org = AdminRepository.create_organization(name=req.name, plan=req.plan, max_seats=req.max_seats)
    admin_audit_service.record_event(
        admin_id=admin["admin_id"],
        action="CREATE_ORGANIZATION",
        target=org["org_id"],
        reason=f"Created org {req.name} with plan {req.plan}"
    )
    return {"status": "success", "organization": org}

# --- 15. VERSION & BUILD INFORMATION ---

@router.get("/version")
def get_version_info(admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "SUPPORT", "ANALYST"]))):
    return {
        "status": "success",
        "app_name": "Saarthi AI Operating Companion",
        "version": "0.5.0-rc2",
        "phase": "Phase 5 Complete + Admin Control Plane + Identity Billing & Teams",
        "build_date": "2026-08-29",
        "environment": "production_control_plane"
    }

# --- 16. ADMIN BILLING & PAYMENTS CONTROL PANEL ---

from app.admin.services.admin_billing_service import AdminBillingService
from app.services.billing_service import BillingService

class ProcessRefundRequest(BaseModel):
    payment_id: str
    reason: str

@router.get("/billing/overview")
def get_billing_overview(admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "SUPPORT", "ANALYST"]))):
    return {"status": "success", "overview": AdminBillingService.get_billing_overview()}

@router.get("/billing/subscriptions")
def list_billing_subscriptions(admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "SUPPORT", "ANALYST"]))):
    return {"status": "success", "subscriptions": AdminBillingService.list_subscriptions()}

@router.get("/billing/payments")
def list_billing_payments(admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "SUPPORT", "ANALYST"]))):
    return {"status": "success", "payments": AdminBillingService.list_payments()}

@router.get("/billing/invoices")
def list_billing_invoices(admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "SUPPORT", "ANALYST"]))):
    return {"status": "success", "invoices": AdminBillingService.list_invoices()}

@router.get("/billing/refunds")
def list_billing_refunds(admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "SUPPORT", "ANALYST"]))):
    return {"status": "success", "refunds": AdminBillingService.list_refunds()}

@router.post("/billing/refunds/process")
def process_admin_refund(req: ProcessRefundRequest, admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN"]))):
    res = BillingService.process_refund(payment_id=req.payment_id, admin_id=admin["admin_id"], reason=req.reason)
    admin_audit_service.record_event(
        admin_id=admin["admin_id"],
        action="PROCESS_REFUND",
        target=req.payment_id,
        reason=req.reason
    )
    return res

@router.get("/billing/webhooks")
def list_billing_webhooks(admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "SUPPORT", "ANALYST"]))):
    return {"status": "success", "webhooks": AdminBillingService.list_webhook_events()}

@router.get("/billing/audit")
def list_billing_audit(admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "SUPPORT", "ANALYST"]))):
    return {"status": "success", "audit_events": AdminBillingService.list_billing_audit_events()}

@router.get("/billing/teams")
def list_billing_teams(admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "SUPPORT", "ANALYST"]))):
    return {"status": "success", "teams": AdminBillingService.list_teams_and_seats()}

# --- 17. ORGANIZATIONS DETAIL & SEAT CONTROL ---

class OrgSeatUpdateRequest(BaseModel):
    max_seats: int

@router.get("/organizations/{org_id}")
def get_organization_details(
    org_id: str,
    admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "SUPPORT", "ANALYST"]))
):
    from app.db.connection import get_db_connection
    with get_db_connection() as conn:
        org_row = conn.execute("SELECT * FROM organizations WHERE org_id = ?", (org_id,)).fetchone()
        if not org_row:
            raise HTTPException(status_code=404, detail="Organization not found.")
        org = dict(org_row)
        members = conn.execute("""
            SELECT om.*, u.email, u.full_name
            FROM organization_members om
            LEFT JOIN users u ON om.user_id = u.user_id
            WHERE om.org_id = ?
        """, (org_id,)).fetchall()
        org["members"] = [dict(m) for m in members]
        org["member_count"] = len(members)
        return {"status": "success", "organization": org}

@router.post("/organizations/{org_id}/seats")
def update_organization_seats(
    org_id: str,
    req: OrgSeatUpdateRequest,
    admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN"]))
):
    from app.db.connection import get_db_connection
    now_str = datetime.now(timezone.utc).isoformat()
    with get_db_connection() as conn:
        conn.execute("UPDATE organizations SET seat_limit = ?, updated_at = ? WHERE org_id = ?",
                     (req.max_seats, now_str, org_id))
        conn.commit()
    admin_audit_service.record_event(
        admin_id=admin["admin_id"],
        action="UPDATE_ORG_SEATS",
        target=org_id,
        reason=f"Updated max seats to {req.max_seats}"
    )
    return {"status": "success", "org_id": org_id, "max_seats": req.max_seats}

# --- 18. AUTOMATIONS & RESEARCH OPERATIONS ---

@router.get("/automations")
def list_admin_automations(
    admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "SUPPORT", "ANALYST"]))
):
    from app.db.connection import get_db_connection
    with get_db_connection() as conn:
        try:
            u_rows = conn.execute("SELECT * FROM unified_automations ORDER BY created_at DESC LIMIT 100").fetchall()
            automations = [dict(r) for r in u_rows]
        except Exception:
            automations = []
        try:
            r_rows = conn.execute("SELECT * FROM routines ORDER BY id DESC LIMIT 100").fetchall()
            routines = [dict(r) for r in r_rows]
        except Exception:
            routines = []
    return {"status": "success", "automations": automations, "routines": routines}

@router.get("/research/overview")
def get_research_overview(
    admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "SUPPORT", "ANALYST"]))
):
    try:
        from app.intelligence.research.domain_intelligence import ALL_17_DOMAIN_INTELLIGENCE
        domain_dict = ALL_17_DOMAIN_INTELLIGENCE
    except Exception:
        domain_dict = {}
    from app.intelligence.research.research_cache import research_cache
    
    domains = [
        {
            "id": k,
            "name": getattr(v, "name", str(k).title()),
            "description": f"Specialized reasoning, terminology, and verification workflows for {getattr(v, 'name', k)}.",
            "tier": "STANDARD"
        }
        for k, v in domain_dict.items()
    ]
    
    return {
        "status": "success",
        "total_domains": len(domains),
        "domains": domains,
        "cache_entries_count": len(getattr(research_cache, "_cache", {})),
        "active_providers": ["EXA", "ARXIV", "PUBMED", "CROSS_DOMAIN_SYNTHESIZER"]
    }

@router.get("/research/runs")
def list_research_runs(
    limit: int = Query(50, ge=1, le=200),
    admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "SUPPORT", "ANALYST"]))
):
    from app.intelligence.audit.intelligence_audit import audit_service
    logs = audit_service.list_audit_logs(limit=limit)
    research_events = [
        {
            "id": l.get("log_id", f"res_{i}"),
            "event_type": l.get("action", "RESEARCH_RUN"),
            "domain": l.get("metadata", {}).get("domain", "general") if isinstance(l.get("metadata"), dict) else "general",
            "status": "COMPLETED",
            "sources_count": l.get("metadata", {}).get("sources_count", 0) if isinstance(l.get("metadata"), dict) else 0,
            "timestamp": l.get("timestamp", "")
        }
        for i, l in enumerate(logs)
        if "RESEARCH" in l.get("action", "").upper() or "DOMAIN" in l.get("action", "").upper()
    ]
    return {"status": "success", "runs_count": len(research_events), "runs": research_events}

