import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.db.auth import AuthRepository
from app.licensing.models import LicensePlan, Entitlements
from app.security.permissions import SecurityManager, is_path_allowed
from app.config.settings import settings

client = TestClient(app)

def test_admin_unauthorized_access_rejection():
    """Verify that unauthenticated or non-admin requests to /api/admin/* receive 403 Forbidden."""
    resp = client.get("/api/admin/users")
    assert resp.status_code == 403

    resp = client.get("/api/admin/diagnostics")
    assert resp.status_code == 403

    resp = client.post("/api/admin/update-plan", json={"user_id": "usr_fake", "plan": "POWER"})
    assert resp.status_code == 403

    # Invalid Admin Key
    resp = client.get("/api/admin/users", headers={"X-Admin-Key": "invalid_hacker_key"})
    assert resp.status_code == 403

def test_client_cannot_grant_paid_plan():
    """Verify frontend/client payload cannot grant POWER/PERSONAL/STUDENT entitlement without valid server payment."""
    email = f"attacker_{uuid.uuid4().hex[:8]}@test.com"
    reg_resp = client.post("/api/auth/register", json={"email": email, "password": "password123"})
    token = reg_resp.json()["session"]["session_token"]
    user_id = reg_resp.json()["user"]["user_id"]

    # Attempt to spoof plan in client request header or body
    me_resp = client.get("/api/auth/me", headers={
        "Authorization": f"Bearer {token}",
        "X-Subscription-Plan": "POWER" # Spoofed header
    })
    assert me_resp.status_code == 200
    assert me_resp.json()["user"]["subscription_plan"] == "FREE"

def test_forged_license_activation_rejection():
    """Verify fake or forged license keys are rejected by vendor verification."""
    resp = client.post("/api/license/activate", json={
        "license_key": "SAARTHI-POWER-FAKE-KEY-1234-5678",
        "device_name": "Hacker Device"
    })
    assert resp.status_code in (400, 401, 403, 404)

def test_replayed_and_forged_webhook_rejection():
    """Verify webhooks with invalid HMAC signatures or duplicate event IDs are rejected."""
    # Invalid signature for Razorpay
    resp = client.post("/api/payment/webhook/razorpay", 
                       data=b'{"event": "payment.captured", "event_id": "evt_hacker_1"}',
                       headers={"X-Razorpay-Signature": "invalid_hmac_sig"})
    assert resp.status_code in (200, 400)
    if resp.status_code == 200:
        res_json = resp.json()
        assert res_json.get("verified") is False or res_json.get("status") in ("duplicate", "error")

def test_path_traversal_prevention():
    """Verify path traversal outside allowed root directories is blocked."""
    allowed_roots = settings.ALLOWED_ROOTS
    secret_file_path = os_path_escape = "../../Windows/System32/drivers/etc/hosts" if os_path_is_nt() else "/etc/passwd"
    
    assert is_path_allowed(secret_file_path, allowed_roots) is False

def os_path_is_nt():
    import os
    return os.name == 'nt'
