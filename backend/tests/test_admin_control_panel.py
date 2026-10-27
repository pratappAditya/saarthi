import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config.settings import settings
from app.db.auth import get_db_connection, AuthRepository
from app.db.admin_db import AdminRepository

client = TestClient(app)
ADMIN_KEY = settings.VENDOR_ADMIN_KEY

def test_admin_access_rejection_for_unauthenticated_requests():
    """
    Verify that normal unauthenticated requests to admin endpoints are blocked (HTTP 403).
    """
    res = client.get("/api/admin/dashboard")
    assert res.status_code == 403
    assert "Unauthorized admin access" in res.json().get("detail", "")

def test_admin_access_rejection_for_normal_user_role():
    """
    Verify that authenticated normal USER accounts cannot access admin endpoints.
    """
    # Create normal user
    email = f"normal_user_{uuid.uuid4().hex[:8]}@example.com"
    reg = client.post("/api/auth/register", json={"email": email, "password": "Password123!", "full_name": "Normal User"})
    assert reg.status_code == 200
    reg_data = reg.json()
    user_id = reg_data.get("user_id") or reg_data.get("user", {}).get("user_id")
    
    # Login as normal user
    login = client.post("/api/auth/login", json={"email": email, "password": "Password123!"})
    assert login.status_code == 200
    login_data = login.json()
    token = login_data.get("session", {}).get("session_token") or login_data.get("session", {}).get("token") or login_data.get("session_token")
    
    # Try accessing admin dashboard with normal user token
    res = client.get("/api/admin/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403

def test_admin_login_with_valid_key():
    """
    Verify admin login via Admin Secret Key.
    """
    res = client.post("/api/admin/auth/login", json={"admin_key": ADMIN_KEY})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "token" in data
    assert data["admin"]["role"] == "SUPER_ADMIN"

def test_admin_dashboard_metrics():
    """
    Verify fetching dashboard overview metrics with valid admin key.
    """
    res = client.get("/api/admin/dashboard", headers={"X-Admin-Key": ADMIN_KEY})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "metrics" in data
    assert "total_users" in data["metrics"]
    assert "active_users" in data["metrics"] or "active_sessions" in data["metrics"]
    assert "system_health" in data or "system_hardware" in data

def test_user_management_lifecycle():
    """
    Verify admin user search, role update, plan update, suspension, restoration, and deletion.
    """
    email = f"lifecycle_{uuid.uuid4().hex[:8]}@example.com"
    reg = client.post("/api/auth/register", json={"email": email, "password": "Password123!", "full_name": "Lifecycle Candidate"})
    assert reg.status_code == 200
    reg_data = reg.json()
    user_id = reg_data.get("user_id") or reg_data.get("user", {}).get("user_id")

    headers = {"X-Admin-Key": ADMIN_KEY}

    # 1. User Directory Search
    res_users = client.get(f"/api/admin/users?query={email}", headers=headers)
    assert res_users.status_code == 200
    assert len(res_users.json()["users"]) >= 1

    # 2. Update Plan
    res_plan = client.post("/api/admin/update-plan", json={"user_id": user_id, "plan": "POWER"}, headers=headers)
    assert res_plan.status_code == 200
    assert res_plan.json()["updated_plan"] == "POWER"

    # 3. Update Role to ADMIN
    res_role = client.post("/api/admin/users/update-role", json={"user_id": user_id, "role": "ADMIN"}, headers=headers)
    assert res_role.status_code == 200
    assert res_role.json()["updated_role"] == "ADMIN"

    # 4. Suspend User
    res_sus = client.post("/api/admin/users/suspend", json={"user_id": user_id, "reason": "Test suspension"}, headers=headers)
    assert res_sus.status_code == 200
    
    user_db = AuthRepository.get_user_by_id(user_id)
    assert user_db["role"] == "SUSPENDED"

    # 5. Restore User
    res_res = client.post("/api/admin/users/restore", json={"user_id": user_id, "reason": "Test restoration"}, headers=headers)
    assert res_res.status_code == 200

    # 6. Delete User
    res_del = client.delete(f"/api/admin/users/{user_id}", headers=headers)
    assert res_del.status_code == 200

def test_feature_flags_management():
    headers = {"X-Admin-Key": ADMIN_KEY}
    res = client.get("/api/admin/feature-flags", headers=headers)
    assert res.status_code == 200
    assert "flags" in res.json()

    res_toggle = client.post("/api/admin/feature-flags/update", json={"key": "experimental_features", "enabled": True}, headers=headers)
    assert res_toggle.status_code == 200

def test_maintenance_mode_controls():
    headers = {"X-Admin-Key": ADMIN_KEY}
    res = client.post("/api/admin/maintenance/toggle", json={"enabled": True, "message": "QA System Maintenance Active"}, headers=headers)
    assert res.status_code == 200
    
    maint_data = client.get("/api/admin/maintenance", headers=headers).json()
    assert maint_data["status"] == "success"
    maint = maint_data["maintenance"]
    assert maint["enabled"] in (1, True)
    assert maint["message"] == "QA System Maintenance Active"

    # Reset back to false
    client.post("/api/admin/maintenance/toggle", json={"enabled": False}, headers=headers)

def test_admin_audit_log_recording():
    """
    Verify every consequential admin action is logged in admin_audit_log.
    """
    headers = {"X-Admin-Key": ADMIN_KEY}
    # Perform an action to guarantee an audit entry
    client.post("/api/admin/feature-flags/update", json={"key": "voice", "enabled": True}, headers=headers)
    
    res_logs = client.get("/api/admin/audit-logs", headers=headers)
    assert res_logs.status_code == 200
    logs = res_logs.json()["audit_logs"]
    assert len(logs) > 0
    actions = [l["action"] for l in logs]
    assert "UPDATE_USER_PLAN" in actions or "UPDATE_FEATURE_FLAG" in actions or "ADMIN_LOGIN" in actions
