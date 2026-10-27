"""
Comprehensive Security Remediation Regression Suite.
Covers:
1. Missing, empty, placeholder, and incorrect admin secrets fail closed.
2. Former admin fallback keys and placeholders rejected through login and protected endpoints.
3. Configuration precedence ensures defaults/placeholders cannot shadow environment secrets.
4. Vendor endpoints reject unauthenticated, backdoor ('dev_admin_key'), and incorrect-key requests.
5. Legitimate authorized vendor-admin sessions and configured admin keys still work.
6. Mock payment signatures cannot grant entitlements or verify orders/webhooks.
7. Legitimate test-mode cryptographic payment verification works.
8. Production configuration fails closed on absent, empty, or placeholder secrets.
"""

import os
import hmac
import hashlib
import json
import uuid
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.config.settings import settings
from app.admin.auth.admin_auth import (
    get_configured_admin_key,
    verify_admin_key,
    validate_admin_security_configuration,
    REVOKED_ADMIN_KEYS,
    hash_password as admin_hash_password,
)
from app.admin.repositories.admin_repository import AdminRepository
from app.db.auth import AuthRepository
from app.db.connection import get_db_connection
from app.licensing.payment import RazorpayPaymentProvider, StripePaymentProvider, MockPaymentProvider
from app.billing.billing_engine import billing_engine

client = TestClient(app)

# =============================================================================
# 1. ADMIN SECRET: MISSING, EMPTY, PLACEHOLDER, AND INCORRECT KEYS
# =============================================================================

@pytest.mark.parametrize("bad_key", [
    None,
    "",
    "   ",
    "saarthi_vendor_secret_key_change_in_production",
    "dev_admin_key",
    "SAARTHI_SECRET_ADMIN_KEY_2026",
    "saarthi_admin_secret_key_2026",
    "change_in_production",
    "admin",
    "password",
    "secret",
    "default_secret",
    "changeme",
])
def test_bad_and_placeholder_secrets_fail_closed_in_helper(monkeypatch, bad_key):
    """
    Ensure missing, empty, whitespace, and known insecure placeholders can never
    be returned as a valid configured admin key and can never verify.
    """
    monkeypatch.setattr(settings, "VENDOR_ADMIN_KEY", bad_key)
    monkeypatch.setattr(settings, "ADMIN_SECRET_KEY", "")
    monkeypatch.delenv("VENDOR_ADMIN_KEY", raising=False)
    monkeypatch.delenv("ADMIN_SECRET_KEY", raising=False)

    assert get_configured_admin_key() is None
    assert verify_admin_key(bad_key) is False

@pytest.mark.parametrize("placeholder_key", [
    "saarthi_vendor_secret_key_change_in_production",
    "dev_admin_key",
    "SAARTHI_SECRET_ADMIN_KEY_2026",
    "saarthi_admin_secret_key_2026",
    "wrong_random_key_9999",
])
def test_placeholder_and_revoked_keys_rejected_in_login(placeholder_key):
    """
    Ensure default vendor-admin placeholder and former fallback keys are rejected (HTTP 401)
    on admin login.
    """
    res = client.post("/api/admin/auth/login", json={"admin_key": placeholder_key})
    assert res.status_code == 401
    assert "Invalid admin secret key" in res.json().get("detail", "")

@pytest.mark.parametrize("placeholder_key", [
    "saarthi_vendor_secret_key_change_in_production",
    "dev_admin_key",
    "SAARTHI_SECRET_ADMIN_KEY_2026",
    "saarthi_admin_secret_key_2026",
    "wrong_random_key_9999",
])
def test_placeholder_and_revoked_keys_rejected_in_header(placeholder_key):
    """
    Ensure default vendor-admin placeholder and former fallback keys are rejected (HTTP 403)
    on protected admin endpoints using X-Admin-Key.
    """
    res = client.get("/api/admin/dashboard", headers={"X-Admin-Key": placeholder_key})
    assert res.status_code == 403

    res_auth = client.get("/api/admin/auth/verify", headers={"X-Admin-Key": placeholder_key})
    assert res_auth.status_code == 403

# =============================================================================
# 2. CONFIGURATION PRECEDENCE AND ENVIRONMENT VALIDATION
# =============================================================================

def test_environment_secret_precedence_over_placeholder_setting(monkeypatch):
    """
    Verify that an explicit environment secret takes precedence and is not
    silently overridden by a default or placeholder setting.
    """
    legit_env_key = "production_env_secret_key_valid_12345"
    monkeypatch.setenv("VENDOR_ADMIN_KEY", legit_env_key)
    monkeypatch.setattr(settings, "VENDOR_ADMIN_KEY", "saarthi_vendor_secret_key_change_in_production")

    assert get_configured_admin_key() == legit_env_key
    assert verify_admin_key(legit_env_key) is True
    # Placeholder candidate cannot authenticate even if in settings
    assert verify_admin_key("saarthi_vendor_secret_key_change_in_production") is False

def test_admin_secret_key_env_fallback_when_vendor_key_unconfigured(monkeypatch):
    """
    Verify that ADMIN_SECRET_KEY in environment is used if VENDOR_ADMIN_KEY is empty/absent.
    """
    admin_env_key = "admin_secret_key_from_env_98765"
    monkeypatch.delenv("VENDOR_ADMIN_KEY", raising=False)
    monkeypatch.setenv("ADMIN_SECRET_KEY", admin_env_key)
    monkeypatch.setattr(settings, "VENDOR_ADMIN_KEY", "")

    assert get_configured_admin_key() == admin_env_key
    assert verify_admin_key(admin_env_key) is True

# =============================================================================
# 3. PRODUCTION CONFIGURATION FAILS CLOSED
# =============================================================================

def test_production_fails_closed_when_secret_absent_or_placeholder(monkeypatch):
    """
    Production security check must fail closed (raise RuntimeError) if admin key
    is absent, empty, or an insecure placeholder.
    """
    for bad_key in (None, "", "   ", "saarthi_vendor_secret_key_change_in_production", "dev_admin_key"):
        monkeypatch.setattr(settings, "VENDOR_ADMIN_KEY", bad_key)
        monkeypatch.delenv("VENDOR_ADMIN_KEY", raising=False)
        monkeypatch.delenv("ADMIN_SECRET_KEY", raising=False)

        with pytest.raises(RuntimeError) as exc_info:
            validate_admin_security_configuration(is_prod=True)
        assert "Production security check failed" in str(exc_info.value)

def test_production_passes_when_strong_secret_configured(monkeypatch):
    """
    Production security check succeeds when a legitimate, non-revoked secret is set.
    """
    strong_key = "strong_production_grade_secret_admin_key_9999"
    strong_jwt = "strong_production_grade_jwt_secret_token_8888"
    monkeypatch.setattr(settings, "VENDOR_ADMIN_KEY", strong_key)
    monkeypatch.setenv("JWT_SECRET", strong_jwt)
    assert validate_admin_security_configuration(is_prod=True) is True

def test_admin_login_in_production_fails_closed_with_500_if_unconfigured(monkeypatch):
    """
    In production mode, if no valid key is configured, admin key login attempts must
    fail closed with HTTP 500 (misconfiguration error), not allow any bypass.
    """
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setattr(settings, "VENDOR_ADMIN_KEY", None)
    monkeypatch.delenv("VENDOR_ADMIN_KEY", raising=False)
    monkeypatch.delenv("ADMIN_SECRET_KEY", raising=False)

    iso_client = TestClient(app, client=("192.0.2.111", 50000))
    res = iso_client.post("/api/admin/auth/login", json={"admin_key": "some_attempt"})
    assert res.status_code == 500
    assert "disabled due to missing production configuration" in res.json().get("detail", "")

# =============================================================================
# 4. VENDOR ENDPOINTS: BACKDOOR REMOVAL & SERVER-SIDE AUTH / RBAC
# =============================================================================

def test_vendor_endpoints_reject_unauthenticated():
    """Vendor endpoints must reject requests lacking authentication with HTTP 401."""
    endpoints = [
        ("GET", "/api/vendor/customers"),
        ("POST", "/api/vendor/customers"),
        ("POST", "/api/vendor/licenses"),
        ("GET", "/api/vendor/audit-logs"),
        ("GET", "/api/vendor/analytics"),
        ("GET", "/api/vendor/monetization-metrics"),
    ]
    for method, path in endpoints:
        if method == "GET":
            res = client.get(path)
        else:
            res = client.post(path, json={})
        assert res.status_code == 401
        assert "Unauthorized" in res.json().get("detail", "")

def test_vendor_endpoints_reject_backdoor_dev_admin_key():
    """
    The former backdoor key 'dev_admin_key' must be strictly rejected on all vendor routes.
    """
    headers = {"X-Vendor-Admin-Key": "dev_admin_key"}
    endpoints = [
        ("GET", "/api/vendor/customers"),
        ("GET", "/api/vendor/audit-logs"),
        ("GET", "/api/vendor/analytics"),
        ("GET", "/api/vendor/monetization-metrics"),
    ]
    for method, path in endpoints:
        res = client.get(path, headers=headers)
        assert res.status_code == 401
        assert "Insecure or revoked admin key rejected" in res.json().get("detail", "") or "Unauthorized" in res.json().get("detail", "")

def test_vendor_endpoints_reject_placeholder_secret():
    """Insecure placeholder secret must be rejected on vendor routes."""
    headers = {"X-Vendor-Admin-Key": "saarthi_vendor_secret_key_change_in_production"}
    res = client.get("/api/vendor/customers", headers=headers)
    assert res.status_code == 401

def test_vendor_endpoints_reject_incorrect_key():
    """Arbitrary incorrect key must be rejected on vendor routes."""
    headers = {"X-Vendor-Admin-Key": "totally_wrong_vendor_key_xyz"}
    res = client.get("/api/vendor/customers", headers=headers)
    assert res.status_code == 401

def test_vendor_endpoints_reject_unauthorized_role():
    """
    Authenticated normal user or analyst account cannot access mutation vendor routes.
    """
    # Create normal user
    email = f"norm_vendor_{uuid.uuid4().hex[:8]}@example.com"
    reg = client.post("/api/auth/register", json={"email": email, "password": "Password123!", "full_name": "Normal Vendor Test"}).json()
    token = reg.get("session", {}).get("session_token")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/api/vendor/customers", json={"name": "Bob", "email": "bob@test.com"}, headers=headers)
    assert res.status_code == 403
    assert "unauthorized" in res.json().get("detail", "").lower() or "not authorized" in res.json().get("detail", "").lower()

def test_legitimate_vendor_admin_key_access(monkeypatch):
    """
    A legitimate configured admin key passed via X-Vendor-Admin-Key or X-Admin-Key
    successfully authorizes vendor operations.
    """
    valid_key = "secure_vendor_admin_key_test_5555"
    monkeypatch.setattr(settings, "VENDOR_ADMIN_KEY", valid_key)

    headers = {"X-Vendor-Admin-Key": valid_key}
    res = client.get("/api/vendor/customers", headers=headers)
    assert res.status_code == 200
    assert "customers" in res.json()

    res_metrics = client.get("/api/vendor/monetization-metrics", headers=headers)
    assert res_metrics.status_code == 200

def test_legitimate_vendor_admin_session_access():
    """
    An authorized admin user session token authorizes vendor operations.
    """
    email = f"vendor_ops_admin_{uuid.uuid4().hex[:8]}@saarthi.local"
    pw_hash = admin_hash_password("SuperPass123!")
    AdminRepository.create_admin_user(email=email, password_hash=pw_hash, role="ADMIN", full_name="Vendor Admin")

    login = client.post("/api/admin/auth/login", json={"email": email, "password": "SuperPass123!"}).json()
    token = login["token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/vendor/customers", headers=headers)
    assert res.status_code == 200
    assert "customers" in res.json()

# =============================================================================
# 5. HARDENED PAYMENT SIGNATURE VERIFICATION
# =============================================================================

@pytest.mark.parametrize("mock_sig", [
    "sandbox_bypass_signature",
    "mock_sig",
    "sig",
    "mock_signature",
    "sandbox_test_signature",
    "sig_test_valid",
    "some_arbitrary_string",
])
def test_mock_signatures_cannot_grant_payment_or_entitlements(mock_sig):
    """
    Ensure mock signatures and bypass tokens NEVER grant payment or entitlements.
    Must fail with HTTP 400.
    """
    email = f"anti_mock_{uuid.uuid4().hex[:8]}@example.com"
    reg = client.post("/api/auth/register", json={"email": email, "password": "Password123!"}).json()
    token = reg["session"]["session_token"]
    headers = {"Authorization": f"Bearer {token}"}

    chk = client.post("/api/payment/checkout", json={"plan_name": "POWER", "provider": "RAZORPAY"}, headers=headers).json()
    order_id = chk["order"]["order_id"]
    pay_id = f"pay_{uuid.uuid4().hex[:8]}"

    # Attempt verification using mock signature
    ver = client.post("/api/payment/verify", json={
        "order_id": order_id,
        "payment_id": pay_id,
        "signature": mock_sig,
        "provider": "RAZORPAY"
    }, headers=headers)

    assert ver.status_code == 400
    assert "verification failed" in ver.json().get("detail", "").lower()

    # Verify user plan was NOT upgraded
    me = client.get("/api/auth/me", headers=headers).json()
    assert me["user"]["subscription_plan"] == "FREE"

def test_legitimate_cryptographic_test_payment_verification():
    """
    Legitimate test-mode payment verification succeeds when signature is
    cryptographically calculated against provider test secret.
    """
    email = f"legit_pay_{uuid.uuid4().hex[:8]}@example.com"
    reg = client.post("/api/auth/register", json={"email": email, "password": "Password123!"}).json()
    token = reg["session"]["session_token"]
    headers = {"Authorization": f"Bearer {token}"}

    chk = client.post("/api/payment/checkout", json={"plan_name": "PERSONAL", "provider": "RAZORPAY"}, headers=headers).json()
    order_id = chk["order"]["order_id"]
    pay_id = f"pay_{uuid.uuid4().hex[:8]}"

    # Compute valid cryptographic HMAC-SHA256 signature
    msg = f"{order_id}|{pay_id}".encode("utf-8")
    valid_sig = hmac.new(b"rzp_test_secret", msg, hashlib.sha256).hexdigest()

    ver = client.post("/api/payment/verify", json={
        "order_id": order_id,
        "payment_id": pay_id,
        "signature": valid_sig,
        "provider": "RAZORPAY"
    }, headers=headers)

    assert ver.status_code == 200
    assert ver.json()["status"] == "success"

    # User plan upgraded
    me = client.get("/api/auth/me", headers=headers).json()
    assert me["user"]["subscription_plan"] == "PERSONAL"

def test_mock_provider_fails_closed_in_production(monkeypatch):
    """
    MockPaymentProvider must fail closed with RuntimeError if executed in production.
    """
    monkeypatch.setenv("ENVIRONMENT", "production")
    mock_prov = MockPaymentProvider()

    with pytest.raises(RuntimeError) as exc_info:
        import asyncio
        asyncio.run(mock_prov.create_order("u1", "PERSONAL"))
    assert "strictly disabled in production" in str(exc_info.value)

    with pytest.raises(RuntimeError) as exc_info2:
        asyncio.run(mock_prov.verify_payment("o1", "p1", "mock_verified_123"))
    assert "strictly disabled in production" in str(exc_info2.value)

def test_test_provider_disabled_in_production(monkeypatch):
    """
    BillingEngine must reject TEST_PROVIDER in production.
    """
    monkeypatch.setenv("ENVIRONMENT", "production")
    with pytest.raises(Exception):
        billing_engine.get_provider("TEST_PROVIDER")

def test_razorpay_webhook_verification_valid_and_counterfeit():
    """
    Razorpay webhooks must cryptographically verify signature over raw payload.
    Counterfeit signatures must be rejected (HTTP 400); authentic signatures must succeed.
    """
    payload_data = {
        "event_id": f"evt_{uuid.uuid4().hex[:8]}",
        "event": "payment.captured",
        "payload": {"payment": {"entity": {"id": f"pay_{uuid.uuid4().hex[:8]}", "amount": 39900}}}
    }
    payload_bytes = json.dumps(payload_data).encode("utf-8")

    # 1. Counterfeit webhook signature
    for bad_sig in ("fake_sig", "sandbox_bypass_signature", "mock_sig", "invalid_hex"):
        res = client.post(
            "/api/payment/webhook/razorpay",
            content=payload_bytes,
            headers={"Content-Type": "application/json", "X-Razorpay-Signature": bad_sig}
        )
        assert res.status_code == 400
        assert "Invalid payment webhook signature" in res.json().get("detail", "")

    # 2. Authentic cryptographic webhook signature
    valid_sig = hmac.new(b"rzp_test_secret", payload_bytes, hashlib.sha256).hexdigest()
    res_ok = client.post(
        "/api/payment/webhook/razorpay",
        content=payload_bytes,
        headers={"Content-Type": "application/json", "X-Razorpay-Signature": valid_sig}
    )
    assert res_ok.status_code == 200
    assert res_ok.json().get("status") in ("success", "ok", "processed")

def test_staging_provider_resolution_protects_payments_while_allowing_razorpay_test_mode(monkeypatch):
    """
    Confirm staging environment (ENVIRONMENT=staging):
    - Rejects MockPaymentProvider (fails closed with RuntimeError)
    - Rejects TestPaymentProvider (verify_payment_sync returns False)
    - Rejects TEST_PROVIDER in BillingEngine (raises 400)
    - BUT successfully resolves RAZORPAY adapter and performs legitimate cryptographic test verification
    """
    monkeypatch.setenv("ENVIRONMENT", "staging")

    # 1. MockPaymentProvider fails closed in staging
    mock_prov = MockPaymentProvider()
    with pytest.raises(RuntimeError):
        import asyncio
        asyncio.run(mock_prov.create_order("u_staging", "STUDENT"))

    # 2. TestPaymentProvider fails closed in staging
    from app.billing.providers.test_provider import test_payment_provider
    assert test_payment_provider.verify_payment_sync("o1", "p1", "test_sig_123") is False
    assert test_payment_provider.verify_signature(b"payload", "test_webhook_123") is False

    # 3. BillingEngine rejects TEST_PROVIDER in staging
    with pytest.raises(Exception):
        billing_engine.get_provider("TEST_PROVIDER")

    # 4. BillingEngine allows RAZORPAY provider in staging
    prov = billing_engine.get_provider("RAZORPAY")
    assert prov.provider_id == "RAZORPAY"
    # Cryptographic verification works with valid HMAC
    order_id = "order_staging_test"
    pay_id = "pay_staging_test"
    expected_hmac = hmac.new(b"rzp_test_secret", f"{order_id}|{pay_id}".encode("utf-8"), hashlib.sha256).hexdigest()
    assert prov.verify_payment_sync(order_id, pay_id, expected_hmac) is True
    # Forged signature fails
    assert prov.verify_payment_sync(order_id, pay_id, "forged_sig") is False

def test_exhaustive_vendor_mutation_routes_rbac():
    """
    Verify all vendor mutation endpoints enforce strict RBAC:
    - Reject unauthenticated (401)
    - Reject backdoor dev_admin_key (401)
    - Reject normal users (403)
    - Reject analyst role (403)
    - Accept authorized admin session
    """
    # Create normal user
    normal_email = f"norm_rbac_{uuid.uuid4().hex[:8]}@example.com"
    norm_reg = client.post("/api/auth/register", json={"email": normal_email, "password": "Password123!", "full_name": "Normal"}).json()
    normal_token = norm_reg["session"]["session_token"]

    # Create analyst user
    analyst_email = f"analyst_rbac_{uuid.uuid4().hex[:8]}@example.com"
    an_reg = client.post("/api/auth/register", json={"email": analyst_email, "password": "Password123!", "full_name": "Analyst"}).json()
    analyst_user_id = an_reg["user"]["user_id"]
    analyst_token = an_reg["session"]["session_token"]
    with get_db_connection() as conn:
        conn.execute("UPDATE users SET role = 'ANALYST' WHERE user_id = ?", (analyst_user_id,))
        conn.commit()

    # Create authorized admin user
    admin_email = f"admin_rbac_{uuid.uuid4().hex[:8]}@saarthi.local"
    AdminRepository.create_admin_user(admin_email, admin_hash_password("AdminPass123!"), role="ADMIN", full_name="Vendor Admin")
    admin_login = client.post("/api/admin/auth/login", json={"email": admin_email, "password": "AdminPass123!"}).json()
    admin_token = admin_login["token"]

    dummy_lic_id = "lic_nonexistent_test"
    mutation_routes = [
        ("POST", f"/api/vendor/licenses/{dummy_lic_id}/suspend", {}),
        ("POST", f"/api/vendor/licenses/{dummy_lic_id}/restore", {}),
        ("POST", f"/api/vendor/licenses/{dummy_lic_id}/revoke", {}),
        ("POST", f"/api/vendor/licenses/{dummy_lic_id}/renew", {"extension_days": 30}),
        ("POST", f"/api/vendor/licenses/{dummy_lic_id}/entitlement", {"new_plan": "POWER"}),
    ]

    for method, path, json_body in mutation_routes:
        # 1. Unauthenticated -> 401
        res_noauth = client.post(path, json=json_body)
        assert res_noauth.status_code == 401, f"Failed on {path} with status {res_noauth.status_code}"

        # 2. Backdoor dev_admin_key -> 401
        res_backdoor = client.post(path, json=json_body, headers={"X-Vendor-Admin-Key": "dev_admin_key"})
        assert res_backdoor.status_code == 401, f"Backdoor was not rejected on {path}"

        # 3. Normal user session -> 403
        res_user = client.post(path, json=json_body, headers={"Authorization": f"Bearer {normal_token}"})
        assert res_user.status_code == 403, f"Normal user not blocked on {path}"

        # 4. Analyst user session -> 403
        res_analyst = client.post(path, json=json_body, headers={"Authorization": f"Bearer {analyst_token}"})
        assert res_analyst.status_code == 403, f"Analyst user not blocked on {path}"

        # 5. Admin session -> authorized (returns 404 License not found because ID is dummy, but authentication & RBAC passed!)
        res_admin = client.post(path, json=json_body, headers={"Authorization": f"Bearer {admin_token}"})
        assert res_admin.status_code == 404, f"Admin session failed RBAC check on {path}: {res_admin.status_code}"

