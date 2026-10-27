import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config.settings import settings
from app.admin.auth.admin_auth import (
    verify_admin_key,
    get_configured_admin_key,
    REVOKED_ADMIN_KEYS,
    hash_password,
)
from app.admin.repositories.admin_repository import AdminRepository
from app.db.auth import AuthRepository

client = TestClient(app)

# -----------------------------------------------------------------------------
# 1. Direct Unit Tests on Key Verification Helper
# -----------------------------------------------------------------------------

def test_revoked_keys_are_rejected_by_helper():
    assert "SAARTHI_SECRET_ADMIN_KEY_2026" in REVOKED_ADMIN_KEYS
    assert "saarthi_admin_secret_key_2026" in REVOKED_ADMIN_KEYS

    # Directly verify helper returns False for both revoked keys
    assert verify_admin_key("SAARTHI_SECRET_ADMIN_KEY_2026") is False
    assert verify_admin_key("saarthi_admin_secret_key_2026") is False

def test_unconfigured_or_invalid_secret_fails_closed(monkeypatch):
    # Simulate unconfigured/missing admin secret
    monkeypatch.setattr(settings, "VENDOR_ADMIN_KEY", None)
    monkeypatch.delenv("VENDOR_ADMIN_KEY", raising=False)
    monkeypatch.delenv("ADMIN_SECRET_KEY", raising=False)

    assert get_configured_admin_key() is None
    assert verify_admin_key("some_key") is False
    assert verify_admin_key("") is False
    assert verify_admin_key("   ") is False
    assert verify_admin_key(None) is False

def test_empty_candidate_key_rejected():
    assert verify_admin_key("") is False
    assert verify_admin_key("   ") is False
    assert verify_admin_key(None) is False

def test_valid_configured_key_accepted(monkeypatch):
    test_secret = "test_secure_configured_admin_key_9999"
    monkeypatch.setattr(settings, "VENDOR_ADMIN_KEY", test_secret)

    assert get_configured_admin_key() == test_secret
    assert verify_admin_key(test_secret) is True
    # Non-matching candidate
    assert verify_admin_key("wrong_key") is False

# -----------------------------------------------------------------------------
# 2. Endpoint Regression Tests: Former Fallback Keys Rejected
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("revoked_key", [
    "SAARTHI_SECRET_ADMIN_KEY_2026",
    "saarthi_admin_secret_key_2026",
])
def test_endpoint_rejects_former_fallback_keys_in_header(revoked_key):
    """
    Ensure former fallback keys are rejected with HTTP 403 on protected admin endpoints.
    """
    res1 = client.get("/api/admin/dashboard", headers={"X-Admin-Key": revoked_key})
    assert res1.status_code == 403
    assert "Unauthorized admin access" in res1.json().get("detail", "")

    res2 = client.get("/admin/dashboard", headers={"X-Admin-Key": revoked_key})
    assert res2.status_code == 403

    res3 = client.get("/api/admin/auth/verify", headers={"X-Admin-Key": revoked_key})
    assert res3.status_code == 403

@pytest.mark.parametrize("revoked_key", [
    "SAARTHI_SECRET_ADMIN_KEY_2026",
    "saarthi_admin_secret_key_2026",
])
def test_endpoint_rejects_former_fallback_keys_in_login_body(revoked_key):
    """
    Ensure former fallback keys are rejected with HTTP 401 on admin login endpoint.
    """
    res = client.post("/api/admin/auth/login", json={"admin_key": revoked_key})
    assert res.status_code == 401
    assert "Invalid admin secret key" in res.json().get("detail", "")

# -----------------------------------------------------------------------------
# 3. Endpoint Regression Tests: Arbitrary Incorrect Keys Rejected
# -----------------------------------------------------------------------------

def test_endpoint_rejects_arbitrary_incorrect_key_in_header():
    res = client.get("/api/admin/dashboard", headers={"X-Admin-Key": "totally_bogus_key_12345"})
    assert res.status_code == 403
    assert "Unauthorized admin access" in res.json().get("detail", "")

def test_endpoint_rejects_arbitrary_incorrect_key_in_login():
    res = client.post("/api/admin/auth/login", json={"admin_key": "totally_bogus_key_12345"})
    assert res.status_code == 401
    assert "Invalid admin secret key" in res.json().get("detail", "")

# -----------------------------------------------------------------------------
# 4. Fail Closed: When Secret is Unconfigured
# -----------------------------------------------------------------------------

def test_endpoints_fail_closed_when_admin_secret_is_unconfigured(monkeypatch):
    """
    If VENDOR_ADMIN_KEY is removed/unconfigured, all admin key attempts must fail closed.
    """
    monkeypatch.setattr(settings, "VENDOR_ADMIN_KEY", None)
    monkeypatch.delenv("VENDOR_ADMIN_KEY", raising=False)
    monkeypatch.delenv("ADMIN_SECRET_KEY", raising=False)

    # Header check fails closed (403)
    res_header = client.get("/api/admin/dashboard", headers={"X-Admin-Key": "any_key"})
    assert res_header.status_code == 403

    # Login check fails closed (401)
    res_login = client.post("/api/admin/auth/login", json={"admin_key": "any_key"})
    assert res_login.status_code == 401

# -----------------------------------------------------------------------------
# 5. Legitimate Configured Key Authentication Succeeded
# -----------------------------------------------------------------------------

def test_legitimate_configured_admin_key_header_access(monkeypatch):
    """
    With a legitimate configured key, X-Admin-Key grants SUPER_ADMIN access.
    """
    valid_key = "test_verified_production_grade_secret_key_8888"
    monkeypatch.setattr(settings, "VENDOR_ADMIN_KEY", valid_key)

    headers = {"X-Admin-Key": valid_key}
    res_verify = client.get("/api/admin/auth/verify", headers=headers)
    assert res_verify.status_code == 200
    data = res_verify.json()
    assert data["authenticated"] is True
    assert data["admin"]["role"] == "SUPER_ADMIN"
    assert data["admin"]["auth_method"] == "ADMIN_KEY"

    res_dash = client.get("/api/admin/dashboard", headers=headers)
    assert res_dash.status_code == 200

def test_legitimate_configured_admin_key_login(monkeypatch):
    """
    With a legitimate configured key, login endpoint creates a valid SUPER_ADMIN session.
    """
    valid_key = "test_verified_production_grade_secret_key_8888"
    monkeypatch.setattr(settings, "VENDOR_ADMIN_KEY", valid_key)

    login_res = client.post("/api/admin/auth/login", json={"admin_key": valid_key})
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert login_data["status"] == "success"
    assert "token" in login_data
    assert login_data["admin"]["role"] == "SUPER_ADMIN"

    # Use the returned session token to access dashboard
    bearer_token = login_data["token"]
    res_dash = client.get("/api/admin/dashboard", headers={"Authorization": f"Bearer {bearer_token}"})
    assert res_dash.status_code == 200

# -----------------------------------------------------------------------------
# 6. Preservation of Legitimate Session Auth and RBAC
# -----------------------------------------------------------------------------

def test_admin_user_session_authentication_preserved():
    """
    Ensure email/password admin user authentication and role-based permissions
    continue to work seamlessly without admin key.
    """
    email = f"ops_admin_{uuid.uuid4().hex[:8]}@saarthi.local"
    pw_hash = hash_password("SuperSecretAdminPass123!")
    AdminRepository.create_admin_user(
        email=email,
        password_hash=pw_hash,
        role="ADMIN",
        full_name="Operations Admin"
    )

    # Login with credentials
    login_res = client.post("/api/admin/auth/login", json={"email": email, "password": "SuperSecretAdminPass123!"})
    assert login_res.status_code == 200
    token = login_res.json()["token"]

    # Verify session
    verify_res = client.get("/api/admin/auth/verify", headers={"Authorization": f"Bearer {token}"})
    assert verify_res.status_code == 200
    verify_data = verify_res.json()
    assert verify_data["authenticated"] is True
    assert verify_data["admin"]["role"] == "ADMIN"
    assert verify_data["admin"]["auth_method"] == "ADMIN_SESSION"

def test_normal_user_cannot_access_admin_endpoints():
    """
    Ensure standard user account session cannot access admin endpoints.
    """
    email = f"standard_{uuid.uuid4().hex[:8]}@example.com"
    reg = client.post("/api/auth/register", json={"email": email, "password": "UserPass123!", "full_name": "Standard User"})
    assert reg.status_code == 200
    token = reg.json().get("session", {}).get("session_token")
    if not token:
        # Login to get token
        login = client.post("/api/auth/login", json={"email": email, "password": "UserPass123!"})
        token = login.json()["session"]["session_token"]

    admin_res = client.get("/api/admin/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert admin_res.status_code == 403
