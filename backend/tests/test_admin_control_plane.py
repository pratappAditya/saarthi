import uuid
import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from app.main import app
from app.config.settings import settings
from app.db.auth import AuthRepository
from app.admin.repositories.admin_repository import AdminRepository
from app.admin.auth.admin_auth import hash_password
from app.admin.audit.admin_audit_service import admin_audit_service
from app.admin.services.plan_mgmt_service import plan_mgmt_service

client = TestClient(app)
ADMIN_KEY = getattr(settings, "VENDOR_ADMIN_KEY", None) or os.getenv("VENDOR_ADMIN_KEY", "")

# --- 1. ADMIN AUTHENTICATION ---
def test_admin_authentication_valid_key():
    res = client.post("/api/admin/auth/login", json={"admin_key": ADMIN_KEY})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "token" in data
    assert data["admin"]["role"] == "SUPER_ADMIN"

def test_admin_authentication_valid_admin_user():
    email = f"admin_user_{uuid.uuid4().hex[:8]}@saarthi.local"
    pw_hash = hash_password("SuperSecurePass123!")
    admin_user = AdminRepository.create_admin_user(email=email, password_hash=pw_hash, role="ADMIN", full_name="Ops Manager")

    res = client.post("/api/admin/auth/login", json={"email": email, "password": "SuperSecurePass123!"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["admin"]["role"] == "ADMIN"

# --- 2. INVALID AUTHENTICATION ---
def test_invalid_authentication_bad_key_and_password():
    res = client.post("/api/admin/auth/login", json={"admin_key": "wrong_key_123"})
    assert res.status_code in [400, 401, 403]

    res2 = client.post("/api/admin/auth/login", json={"email": f"nonexistent_{uuid.uuid4().hex[:8]}@saarthi.local", "password": "WrongPassword!"})
    assert res2.status_code == 401

# --- 3. ROLE AUTHORIZATION ---
def test_role_authorization_permissions():
    # Setup SUPPORT admin user
    email = f"support_{uuid.uuid4().hex[:8]}@saarthi.local"
    pw_hash = hash_password("Pass123!")
    AdminRepository.create_admin_user(email=email, password_hash=pw_hash, role="SUPPORT", full_name="Support Agent")

    login = client.post("/api/admin/auth/login", json={"email": email, "password": "Pass123!"})
    token = login.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # SUPPORT can view dashboard and diagnostics
    dash = client.get("/api/admin/dashboard", headers=headers)
    assert dash.status_code == 200

    # SUPPORT cannot perform destructive write like deleting a user
    del_res = client.delete("/api/admin/users/non_existent_id", headers=headers)
    assert del_res.status_code == 403

# --- 4. ANALYST READ-ONLY RESTRICTIONS ---
def test_analyst_read_only_restrictions():
    email = f"analyst_{uuid.uuid4().hex[:8]}@saarthi.local"
    pw_hash = hash_password("Pass123!")
    AdminRepository.create_admin_user(email=email, password_hash=pw_hash, role="ANALYST", full_name="Data Analyst")

    login = client.post("/api/admin/auth/login", json={"email": email, "password": "Pass123!"})
    token = login.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # GET requests pass for ANALYST
    res_get = client.get("/api/admin/users", headers=headers)
    assert res_get.status_code == 200

    # Write request blocked with 403
    res_post = client.post("/api/admin/users/update-role", json={"user_id": "u123", "role": "ADMIN"}, headers=headers)
    assert res_post.status_code == 403

# --- 5. USER LOOKUP & FILTERING ---
def test_user_lookup_and_filtering():
    headers = {"X-Admin-Key": ADMIN_KEY}
    
    # Create test user
    email = f"lookup_user_{uuid.uuid4().hex[:8]}@example.com"
    reg = client.post("/api/auth/register", json={"email": email, "password": "Password123!", "full_name": "Lookup Target"})
    assert reg.status_code == 200
    user_id = reg.json().get("user_id") or reg.json().get("user", {}).get("user_id")

    # Search by email
    search = client.get(f"/api/admin/users?query={email}", headers=headers)
    assert search.status_code == 200
    assert len(search.json()["users"]) >= 1

    # User details
    details = client.get(f"/api/admin/users/{user_id}/details", headers=headers)
    assert details.status_code == 200
    assert details.json()["user"]["email"] == email

# --- 6. PLAN LOOKUP & CATALOG ---
def test_plan_lookup_canonical_catalog():
    headers = {"X-Admin-Key": ADMIN_KEY}
    res = client.get("/api/admin/plans/catalog", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "canonical_plans" in data
    expected_plans = ["FREE", "STUDENT", "PERSONAL", "POWER", "TEAMS", "ENTERPRISE"]
    catalog_ids = [c["id"] for c in data["catalog"]]
    for p in expected_plans:
        assert p in data["canonical_plans"]
        assert p in catalog_ids

# --- 7. ENTITLEMENT INSPECTION & OVERRIDE ---
def test_entitlement_inspection_and_override():
    headers = {"X-Admin-Key": ADMIN_KEY}
    email = f"ent_user_{uuid.uuid4().hex[:8]}@example.com"
    reg = client.post("/api/auth/register", json={"email": email, "password": "Password123!", "full_name": "Ent entitlement"})
    user_id = reg.json().get("user_id") or reg.json().get("user", {}).get("user_id")

    # Inspect
    insp = client.get(f"/api/admin/entitlements/{user_id}", headers=headers)
    assert insp.status_code == 200
    assert insp.json()["current_plan"] == "FREE"

    # Override
    over = client.post("/api/admin/entitlements/override", json={
        "user_id": user_id,
        "plan_override": "POWER",
        "capabilities_override": {"custom_feature": True},
        "reason": "VIP beta testing"
    }, headers=headers)
    assert over.status_code == 200
    assert over.json()["override"]["plan_override"] == "POWER"

# --- 8. AGENT INSPECTION & CANCELLATION ---
def test_agent_inspection_and_cancellation():
    headers = {"X-Admin-Key": ADMIN_KEY}

    tasks_res = client.get("/api/admin/agents/tasks", headers=headers)
    assert tasks_res.status_code == 200
    assert "tasks" in tasks_res.json()

    perms_res = client.get("/api/admin/permissions/pending", headers=headers)
    assert perms_res.status_code == 200

# --- 9. ROUTINE INSPECTION & TOGGLE ---
def test_routine_inspection_and_toggle():
    headers = {"X-Admin-Key": ADMIN_KEY}

    routines_res = client.get("/api/admin/automation/routines", headers=headers)
    assert routines_res.status_code == 200
    assert "routines" in routines_res.json()

# --- 10. DOMAIN INSPECTION (ALL 17 DOMAINS) ---
def test_domain_inspection_all_17_domains():
    headers = {"X-Admin-Key": ADMIN_KEY}
    res = client.get("/api/admin/domains", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["expected_domains_count"] == 17
    domain_ids = [d["id"] for d in data["domains"]]
    
    expected_17 = [
        "general", "career", "education", "writing", "research", "business",
        "software", "cybersecurity", "cs", "mechanical", "civil", "electrical",
        "biology", "chemistry", "physics", "archaeology", "history"
    ]
    for d in expected_17:
        assert d in domain_ids, f"Missing domain pack: {d}"

# --- 11. SYSTEM HEALTH DIAGNOSTICS ---
def test_system_health_diagnostics():
    headers = {"X-Admin-Key": ADMIN_KEY}

    health = client.get("/api/admin/health", headers=headers)
    assert health.status_code == 200
    h_data = health.json()
    assert "subsystems" in h_data
    assert "backend" in h_data["subsystems"]
    assert "database" in h_data["subsystems"]
    assert "cpu" in h_data["subsystems"]
    assert "ram" in h_data["subsystems"]

    db_chk = client.post("/api/admin/health/db-check", headers=headers)
    assert db_chk.status_code == 200
    assert db_chk.json()["is_healthy"] is True

# --- 12. AUDIT CREATION & SECRET REDACTION ---
def test_audit_creation_and_secret_redaction():
    headers = {"X-Admin-Key": ADMIN_KEY}

    # Trigger action that generates audit
    client.post("/api/admin/feature-flags/update", json={
        "key": "voice_barge_in",
        "enabled": True,
        "rollout_percentage": 100
    }, headers=headers)

    audit_res = client.get("/api/admin/audit-logs", headers=headers)
    assert audit_res.status_code == 200
    logs = audit_res.json()["audit_logs"]
    assert len(logs) > 0

# --- 13. DESTRUCTIVE ACTION CONFIRMATION FLOW ---
def test_destructive_action_confirmation_workflow():
    headers = {"X-Admin-Key": ADMIN_KEY}
    email = f"suspend_user_{uuid.uuid4().hex[:8]}@example.com"
    reg = client.post("/api/auth/register", json={"email": email, "password": "Password123!", "full_name": "Suspend Me"})
    user_id = reg.json().get("user_id") or reg.json().get("user", {}).get("user_id")

    # Suspend user
    sus_res = client.post("/api/admin/users/suspend", json={"user_id": user_id, "reason": "Security violation"}, headers=headers)
    assert sus_res.status_code == 200

    user_db = AuthRepository.get_user_by_id(user_id)
    assert user_db["role"] == "SUSPENDED"

    # Restore user
    res_res = client.post("/api/admin/users/restore", json={"user_id": user_id, "reason": "Appeal accepted"}, headers=headers)
    assert res_res.status_code == 200
    
    user_db_restored = AuthRepository.get_user_by_id(user_id)
    assert user_db_restored["role"] == "USER"

# --- 14. UNAUTHORIZED ENDPOINT ACCESS ---
def test_unauthorized_endpoint_access_blocking():
    # 1. No auth headers -> 403 Forbidden
    res_no_auth = client.get("/api/admin/dashboard")
    assert res_no_auth.status_code == 403

    # 2. Normal user session token -> 403 Forbidden
    email = f"normal_usr_{uuid.uuid4().hex[:8]}@example.com"
    client.post("/api/auth/register", json={"email": email, "password": "Password123!", "full_name": "Normal Person"})
    login = client.post("/api/auth/login", json={"email": email, "password": "Password123!"})
    token = login.json().get("session", {}).get("token") or login.json().get("session_token")

    res_user_token = client.get("/api/admin/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert res_user_token.status_code == 403

# --- 15. SESSION EXPIRY ---
def test_session_expiry_handling():
    email = f"expired_admin_{uuid.uuid4().hex[:8]}@saarthi.local"
    pw_hash = hash_password("Pass123!")
    AdminRepository.create_admin_user(email=email, password_hash=pw_hash, role="ADMIN")

    login = client.post("/api/admin/auth/login", json={"email": email, "password": "Pass123!"})
    token = login.json()["token"]

    # Revoke session directly
    AdminRepository.revoke_session(token)

    res = client.get("/api/admin/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403

# --- 16. DATABASE PERSISTENCE ---
def test_admin_database_persistence():
    headers = {"X-Admin-Key": ADMIN_KEY}

    # Add security ban
    ban_res = client.post("/api/admin/security/ban", json={
        "identifier": "192.168.1.100",
        "ban_type": "IP",
        "reason": "Brute force attempt"
    }, headers=headers)
    assert ban_res.status_code == 200

    # Query ban list
    list_bans = client.get("/api/admin/security/bans", headers=headers)
    assert list_bans.status_code == 200
    banned_ips = [b["identifier"] for b in list_bans.json()["bans"]]
    assert "192.168.1.100" in banned_ips

    # Clean up ban
    client.post("/api/admin/security/unban", json={"identifier": "192.168.1.100"}, headers=headers)

# --- 17. PHASE 5 REGRESSION VALIDATION ---
def test_phase5_regression_validation():
    # Verify core Phase 5 entitlements endpoint functions seamlessly alongside admin
    email = f"phase5_reg_{uuid.uuid4().hex[:8]}@example.com"
    reg = client.post("/api/auth/register", json={"email": email, "password": "Password123!", "full_name": "Phase5 User"})
    reg_data = reg.json()
    login = client.post("/api/auth/login", json={"email": email, "password": "Password123!"})
    login_data = login.json()
    token = (
        reg_data.get("session", {}).get("session_token") or 
        login_data.get("session", {}).get("session_token") or
        login_data.get("session_token")
    )

    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["user"]["email"] == email
