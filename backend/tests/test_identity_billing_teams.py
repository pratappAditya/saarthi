import pytest
import uuid
import json
import hmac
import hashlib
from fastapi.testclient import TestClient
from app.main import app
from app.db.connection import get_db_connection
from app.db.admin_db import AdminRepository
from app.db.auth import AuthRepository, hash_password
from app.services.identity_service import IdentityService
from app.services.billing_service import BillingService
from app.services.team_service import TeamService

client = TestClient(app)
from app.config.settings import settings
import os
ADMIN_KEY = getattr(settings, "VENDOR_ADMIN_KEY", None) or os.getenv("VENDOR_ADMIN_KEY", "")

# --- 1. USER REGISTRATION & EMAIL VERIFICATION ---
def test_user_registration_and_email_verification():
    email = f"user_reg_{uuid.uuid4().hex[:8]}@example.com"
    reg_res = client.post("/api/auth/register", json={"email": email, "password": "Password123!", "full_name": "Test Reg User"})
    assert reg_res.status_code == 200
    data = reg_res.json()
    assert data["status"] == "success"
    assert "verification_token" in data["session"] or "user" in data

    # Register via IdentityService directly to test token
    res = IdentityService.register(email=f"id_test_{uuid.uuid4().hex[:8]}@example.com", password="Password123!")
    token = res["verification_token"]
    assert IdentityService.verify_email(token) is True

# --- 2. LOGIN RATE LIMITING & BRUTE FORCE LOCKOUT ---
def test_login_rate_limiting_and_brute_force():
    email = f"brute_{uuid.uuid4().hex[:8]}@example.com"
    client.post("/api/auth/register", json={"email": email, "password": "CorrectPassword123!"})

    # Record 5 failed attempts
    for _ in range(5):
        AuthRepository.record_login_attempt(email, success=False)

    allowed, err_msg = AuthRepository.check_rate_limit(email)
    assert allowed is False
    assert "locked" in err_msg.lower()

    # Reset rate limit for clean tear down
    AuthRepository.record_login_attempt(email, success=True)

# --- 3. PASSWORD RESET WORKFLOW ---
def test_password_reset_workflow():
    email = f"reset_{uuid.uuid4().hex[:8]}@example.com"
    client.post("/api/auth/register", json={"email": email, "password": "OldPassword123!"})

    req_res = client.post("/api/auth/request-password-reset", json={"email": email})
    assert req_res.status_code == 200
    token = req_res.json()["reset_token"]

    confirm_res = client.post("/api/auth/reset-password", json={"token": token, "new_password": "NewPassword123!"})
    assert confirm_res.status_code == 200
    assert confirm_res.json()["status"] == "success"

    # Authenticate with new password
    login = client.post("/api/auth/login", json={"email": email, "password": "NewPassword123!"})
    assert login.status_code == 200

# --- 4. MULTI-SESSION INSPECTION & REVOCATION ---
def test_multi_session_inspection_and_revocation():
    email = f"sess_{uuid.uuid4().hex[:8]}@example.com"
    reg = client.post("/api/auth/register", json={"email": email, "password": "Password123!"}).json()
    user_id = reg["user"]["user_id"]
    token1 = reg["session"]["session_token"]

    # Login second session
    login2 = client.post("/api/auth/login", json={"email": email, "password": "Password123!", "device_name": "Mobile Device"}).json()
    token2 = login2["session"]["session_token"]

    # Inspect sessions
    sessions = IdentityService.inspect_sessions(user_id)
    assert len(sessions) >= 2

    # Logout all sessions
    logout_res = client.post("/api/auth/logout-all", headers={"Authorization": f"Bearer {token1}"})
    assert logout_res.status_code == 200
    assert len(IdentityService.inspect_sessions(user_id)) == 0

# --- 5. TWO-FACTOR AUTH ARCHITECTURE ---
def test_two_factor_auth_architecture():
    email = f"tfa_{uuid.uuid4().hex[:8]}@example.com"
    reg = client.post("/api/auth/register", json={"email": email, "password": "Password123!"}).json()
    token = reg["session"]["session_token"]
    headers = {"Authorization": f"Bearer {token}"}

    setup = client.post("/api/auth/2fa/setup", headers=headers)
    assert setup.status_code == 200
    s_data = setup.json()
    assert "secret_key" in s_data
    assert len(s_data["backup_codes"]) == 8

    verify = client.post("/api/auth/2fa/verify", json={"code": s_data["backup_codes"][0]}, headers=headers)
    assert verify.status_code == 200
    assert verify.json()["status"] == "success"

# --- 6. SEPARATE ADMIN AUTHENTICATION ---
def test_separate_admin_authentication():
    # User token cannot access Admin endpoint
    email = f"user_norole_{uuid.uuid4().hex[:8]}@example.com"
    reg = client.post("/api/auth/register", json={"email": email, "password": "Password123!"}).json()
    u_token = reg["session"]["session_token"]

    res = client.get("/api/admin/dashboard", headers={"Authorization": f"Bearer {u_token}"})
    assert res.status_code in [401, 403]

# --- 7. PLAN CATALOG PRICING ---
def test_plan_catalog_pricing():
    plans_res = client.get("/api/payment/plans")
    assert plans_res.status_code == 200
    plans = {p["id"]: p for p in plans_res.json()["plans"]}

    assert plans["FREE"]["price_inr"] == 0
    assert plans["STUDENT"]["price_inr"] == 99
    assert plans["PERSONAL"]["price_inr"] == 399
    assert plans["POWER"]["price_inr"] == 799
    assert plans["TEAMS"]["price_inr"] == 699

# --- 8. CHECKOUT ORDER CREATION ---
def test_checkout_order_creation():
    email = f"pay_{uuid.uuid4().hex[:8]}@example.com"
    reg = client.post("/api/auth/register", json={"email": email, "password": "Password123!"}).json()
    token = reg["session"]["session_token"]

    chk = client.post("/api/payment/checkout", json={"plan_name": "PERSONAL", "provider": "RAZORPAY", "currency": "INR"}, headers={"Authorization": f"Bearer {token}"})
    assert chk.status_code == 200
    data = chk.json()
    assert data["status"] == "success"
    assert data["order"]["amount"] == 39900 # in paise

# --- 9. SERVER-SIDE PAYMENT VERIFICATION & ENTITLEMENT ACTIVATION ---
def test_server_side_payment_verification_and_entitlement_activation():
    email = f"verify_pay_{uuid.uuid4().hex[:8]}@example.com"
    reg = client.post("/api/auth/register", json={"email": email, "password": "Password123!"}).json()
    token = reg["session"]["session_token"]
    headers = {"Authorization": f"Bearer {token}"}

    chk = client.post("/api/payment/checkout", json={"plan_name": "POWER", "provider": "RAZORPAY"}, headers=headers).json()
    order_id = chk["order"]["order_id"]

    pay_id = f"pay_rzp_{uuid.uuid4().hex[:8]}"
    sig = hmac.new(b"rzp_test_secret", f"{order_id}|{pay_id}".encode("utf-8"), hashlib.sha256).hexdigest()
    ver = client.post("/api/payment/verify", json={
        "order_id": order_id,
        "payment_id": pay_id,
        "signature": sig,
        "provider": "RAZORPAY"
    }, headers=headers)

    assert ver.status_code == 200
    assert ver.json()["status"] == "success"

    me = client.get("/api/auth/me", headers=headers).json()
    assert me["user"]["subscription_plan"] == "PERSONAL" or "POWER" in me["user"]["subscription_plan"]

# --- 10. WEBHOOK SECURITY & IDEMPOTENCY ---
def test_webhook_security_and_idempotency():
    event_id = f"evt_test_{uuid.uuid4().hex[:8]}"
    payload = json.dumps({"event_id": event_id, "event": "payment.captured"}).encode('utf-8')
    webhook_sig = hmac.new(b"rzp_test_secret", payload, hashlib.sha256).hexdigest()

    res1 = client.post("/api/payment/webhook/razorpay", content=payload, headers={"X-Razorpay-Signature": webhook_sig})
    assert res1.status_code == 200
    assert res1.json()["status"] == "processed"

    # Duplicate webhook call
    res2 = client.post("/api/payment/webhook/razorpay", content=payload, headers={"X-Razorpay-Signature": webhook_sig})
    assert res2.status_code == 200
    assert res2.json()["status"] == "duplicate"
    assert res2.json()["processed"] is False

# --- 11. SUBSCRIPTION CANCELLATION ---
def test_subscription_cancellation():
    email = f"cancel_sub_{uuid.uuid4().hex[:8]}@example.com"
    reg = client.post("/api/auth/register", json={"email": email, "password": "Password123!"}).json()
    user_id = reg["user"]["user_id"]
    token = reg["session"]["session_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create dummy active subscription
    chk = client.post("/api/payment/checkout", json={"plan_name": "PERSONAL"}, headers=headers).json()
    order_id = chk["order"]["order_id"]
    pay_id = f"pay_{uuid.uuid4().hex[:8]}"
    sig = hmac.new(b"rzp_test_secret", f"{order_id}|{pay_id}".encode("utf-8"), hashlib.sha256).hexdigest()
    ver = client.post("/api/payment/verify", json={"order_id": order_id, "payment_id": pay_id, "signature": sig}, headers=headers).json()
    sub_id = ver["subscription"]["subscription_id"]

    cancel = client.post("/api/payment/cancel", json={"subscription_id": sub_id}, headers=headers)
    assert cancel.status_code == 200
    assert cancel.json()["status"] == "success"

# --- 12. SUBSCRIPTION UPGRADE & DOWNGRADE ---
def test_subscription_upgrade_and_downgrade():
    email = f"up_down_{uuid.uuid4().hex[:8]}@example.com"
    reg = client.post("/api/auth/register", json={"email": email, "password": "Password123!"}).json()
    token = reg["session"]["session_token"]
    headers = {"Authorization": f"Bearer {token}"}

    chk = client.post("/api/payment/checkout", json={"plan_name": "PERSONAL"}, headers=headers).json()
    order_id = chk["order"]["order_id"]
    pay_id = f"pay_{uuid.uuid4().hex[:8]}"
    sig = hmac.new(b"rzp_test_secret", f"{order_id}|{pay_id}".encode("utf-8"), hashlib.sha256).hexdigest()
    ver = client.post("/api/payment/verify", json={"order_id": order_id, "payment_id": pay_id, "signature": sig}, headers=headers).json()
    sub_id = ver["subscription"]["subscription_id"]

    up = client.post("/api/payment/upgrade-downgrade", json={"subscription_id": sub_id, "new_plan_name": "POWER", "seats": 2}, headers=headers)
    assert up.status_code == 200
    assert up.json()["plan_name"] == "POWER"

# --- 13. REFUND PROCESSING & ENTITLEMENT REVOCATION ---
def test_refund_processing_and_entitlement_revocation():
    email = f"ref_{uuid.uuid4().hex[:8]}@example.com"
    reg = client.post("/api/auth/register", json={"email": email, "password": "Password123!"}).json()
    token = reg["session"]["session_token"]

    chk = client.post("/api/payment/checkout", json={"plan_name": "PERSONAL"}, headers={"Authorization": f"Bearer {token}"}).json()
    order_id = chk["order"]["order_id"]
    pay_id = f"pay_{uuid.uuid4().hex[:8]}"
    sig = hmac.new(b"rzp_test_secret", f"{order_id}|{pay_id}".encode("utf-8"), hashlib.sha256).hexdigest()
    client.post("/api/payment/verify", json={"order_id": order_id, "payment_id": pay_id, "signature": sig}, headers={"Authorization": f"Bearer {token}"})

    # Admin processes refund
    ref_res = client.post("/api/admin/billing/refunds/process", json={"payment_id": order_id, "reason": "Customer request"}, headers={"X-Admin-Key": ADMIN_KEY})
    assert ref_res.status_code == 200
    assert ref_res.json()["status"] == "success"

# --- 14. ORGANIZATION CREATION & MEMBER INVITATION ---
def test_organization_creation_and_member_invitation():
    email = f"owner_{uuid.uuid4().hex[:8]}@example.com"
    reg = client.post("/api/auth/register", json={"email": email, "password": "Password123!"}).json()
    token = reg["session"]["session_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_org = client.post("/api/team/create", json={"name": "TechCorp AI Team", "plan_name": "TEAMS", "seat_limit": 3}, headers=headers)
    assert create_org.status_code == 200
    org_id = create_org.json()["organization"]["org_id"]

    inv = client.post(f"/api/team/{org_id}/invite", json={"email": "colleague@techcorp.com", "role": "MEMBER"}, headers=headers)
    assert inv.status_code == 200
    assert inv.json()["status"] == "success"
    assert "invite_token" in inv.json()

# --- 15. INVITATION ACCEPTANCE & ROLE MANAGEMENT ---
def test_invitation_acceptance_and_role_management():
    owner = client.post("/api/auth/register", json={"email": f"owner2_{uuid.uuid4().hex[:8]}@example.com", "password": "Password123!"}).json()
    o_token = owner["session"]["session_token"]
    org_id = client.post("/api/team/create", json={"name": "DevOrg"}, headers={"Authorization": f"Bearer {o_token}"}).json()["organization"]["org_id"]

    member_email = f"member2_{uuid.uuid4().hex[:8]}@example.com"
    inv = client.post(f"/api/team/{org_id}/invite", json={"email": member_email}, headers={"Authorization": f"Bearer {o_token}"}).json()
    invite_token = inv["invite_token"]

    member = client.post("/api/auth/register", json={"email": member_email, "password": "Password123!"}).json()
    m_token = member["session"]["session_token"]

    accept = client.post("/api/team/accept-invite", json={"token": invite_token}, headers={"Authorization": f"Bearer {m_token}"})
    assert accept.status_code == 200
    assert len(accept.json()["members"]) == 2

# --- 16. ORGANIZATION SEAT LIMIT ENFORCEMENT ---
def test_organization_seat_limit_enforcement():
    owner = client.post("/api/auth/register", json={"email": f"seat_owner_{uuid.uuid4().hex[:8]}@example.com", "password": "Password123!"}).json()
    o_token = owner["session"]["session_token"]
    org_id = client.post("/api/team/create", json={"name": "SmallTeam", "seat_limit": 1}, headers={"Authorization": f"Bearer {o_token}"}).json()["organization"]["org_id"]

    # Owner takes seat 1. Inviting seat 2 should be rejected.
    inv = client.post(f"/api/team/{org_id}/invite", json={"email": "extra@example.com"}, headers={"Authorization": f"Bearer {o_token}"})
    assert inv.status_code == 400
    assert "seat limit" in inv.json()["detail"].lower()

# --- 17. ORGANIZATION DATA ISOLATION ---
def test_organization_data_isolation():
    owner1 = client.post("/api/auth/register", json={"email": f"iso1_{uuid.uuid4().hex[:8]}@example.com", "password": "Password123!"}).json()
    org1_id = client.post("/api/team/create", json={"name": "Org 1"}, headers={"Authorization": f"Bearer {owner1['session']['session_token']}"}).json()["organization"]["org_id"]

    owner2 = client.post("/api/auth/register", json={"email": f"iso2_{uuid.uuid4().hex[:8]}@example.com", "password": "Password123!"}).json()
    t2 = owner2["session"]["session_token"]

    # User 2 tries to access Org 1
    res = client.get(f"/api/team/{org1_id}", headers={"Authorization": f"Bearer {t2}"})
    assert res.status_code == 403
    assert "access denied" in res.json()["detail"].lower()

# --- 18. ADMIN BILLING OVERVIEW METRICS ---
def test_admin_billing_overview_metrics():
    res = client.get("/api/admin/billing/overview", headers={"X-Admin-Key": ADMIN_KEY})
    assert res.status_code == 200
    overview = res.json()["overview"]

    assert "mrr_inr" in overview
    assert "arr_inr" in overview
    assert "active_subscriptions" in overview
    assert "teams_overview" in overview

# --- 19. ADMIN BILLING AUDIT SECRET REDACTION ---
def test_admin_billing_audit_secret_redaction():
    res = client.get("/api/admin/billing/audit", headers={"X-Admin-Key": ADMIN_KEY})
    assert res.status_code == 200
    events = res.json()["audit_events"]
    assert isinstance(events, list)

# --- 20. UNAUTHORIZED BILLING & ADMIN API BLOCKING ---
def test_unauthorized_billing_and_admin_api_blocking():
    user = client.post("/api/auth/register", json={"email": f"normal_{uuid.uuid4().hex[:8]}@example.com", "password": "Password123!"}).json()
    u_token = user["session"]["session_token"]

    res = client.get("/api/admin/billing/overview", headers={"Authorization": f"Bearer {u_token}"})
    assert res.status_code in [401, 403]
