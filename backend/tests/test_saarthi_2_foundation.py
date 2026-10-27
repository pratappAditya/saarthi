import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.db.auth import AuthRepository
from app.licensing.models import LicensePlan, Entitlements
from app.security.quota import QuotaManager, FREE_DAILY_REQUEST_LIMIT

client = TestClient(app)

def test_saarthi_2_plans_and_pricing():
    # Verify exact public plans: FREE (0), STUDENT (99), PERSONAL (399), POWER (799)
    free_ent = Entitlements.from_plan(LicensePlan.FREE)
    assert free_ent.price_inr_monthly == 0
    assert free_ent.price_usd_monthly == 0.0
    assert free_ent.requires_watermark is True

    student_ent = Entitlements.from_plan(LicensePlan.STUDENT)
    assert student_ent.price_inr_monthly == 99
    assert student_ent.price_usd_monthly == 1.50
    assert student_ent.requires_watermark is False

    personal_ent = Entitlements.from_plan(LicensePlan.PERSONAL)
    assert personal_ent.price_inr_monthly == 399
    assert personal_ent.price_usd_monthly == 5.00
    assert personal_ent.requires_watermark is False

    power_ent = Entitlements.from_plan(LicensePlan.POWER)
    assert power_ent.price_inr_monthly == 799
    assert power_ent.price_usd_monthly == 10.00
    assert power_ent.requires_watermark is False

def test_auth_registration_and_login():
    unique_id = uuid.uuid4().hex[:8]
    email = f"candidate_{unique_id}@example.com"
    password = "securePassword123"

    # Register
    reg_resp = client.post("/api/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Test Candidate"
    })
    assert reg_resp.status_code == 200
    reg_data = reg_resp.json()
    assert reg_data["status"] == "success"
    assert reg_data["user"]["email"] == email

    # Login
    login_resp = client.post("/api/auth/login", json={
        "email": email,
        "password": password
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["session"]["session_token"]

    # Me Endpoint
    me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["user"]["email"] == email
    assert me_data["user"]["subscription_plan"] == "FREE"

def test_free_quota_enforcement():
    entity_id = f"quota_test_{uuid.uuid4().hex[:8]}"
    # First request
    allowed, status = QuotaManager.check_and_increment_quota(entity_id, plan="FREE")
    assert allowed is True
    assert status["remaining_requests"] == FREE_DAILY_REQUEST_LIMIT - 1

def test_payment_checkout_and_verification():
    unique_id = uuid.uuid4().hex[:8]
    email = f"pay_{unique_id}@example.com"
    reg_resp = client.post("/api/auth/register", json={"email": email, "password": "password123", "full_name": "Pay Test"})
    assert reg_resp.status_code == 200
    token = reg_resp.json()["session"]["session_token"]

    # Checkout
    chk_resp = client.post("/api/payment/checkout", json={
        "plan_name": "PERSONAL",
        "provider": "razorpay"
    }, headers={"Authorization": f"Bearer {token}"})
    assert chk_resp.status_code == 200
    order = chk_resp.json()["order"]
    assert order["amount"] == 39900

    # Verify Payment with legitimate test-mode signature
    import hmac, hashlib
    msg = f"{order['order_id']}|pay_test_123".encode("utf-8")
    valid_sig = hmac.new(b"rzp_test_secret", msg, hashlib.sha256).hexdigest()

    ver_resp = client.post("/api/payment/verify", json={
        "order_id": order["order_id"],
        "payment_id": "pay_test_123",
        "signature": valid_sig,
        "provider": "razorpay"
    }, headers={"Authorization": f"Bearer {token}"})
    assert ver_resp.status_code == 200

    # Check updated user plan
    me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.json()["user"]["subscription_plan"] == "PERSONAL"
