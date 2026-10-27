import pytest
import hmac, hashlib
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_payment_webhook_valid_signature():
    payload_str = '{"event": "subscription.charged", "subscription_id": "sub_test_123"}'
    valid_sig = hmac.new(b"rzp_sandbox_secret", payload_str.encode("utf-8"), hashlib.sha256).hexdigest()
    res = client.post(
        "/api/payments/webhook",
        json={"provider": "razorpay", "payload": payload_str, "signature": valid_sig}
    )
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

def test_payment_webhook_rejects_mock_sig_bypass():
    payload_str = '{"event": "subscription.charged", "subscription_id": "sub_test_123"}'
    # Ensure legacy bypass signatures are strictly rejected with HTTP 400
    for mock_sig in ("mock_sig", "sandbox_bypass_signature", "sig"):
        res = client.post(
            "/api/payments/webhook",
            json={"provider": "razorpay", "payload": payload_str, "signature": mock_sig}
        )
        assert res.status_code == 400

def test_payment_webhook_invalid_signature():
    # If secret is set in Razorpay provider, invalid signature triggers 400
    from app.licensing.payment import RazorpayPaymentProvider
    provider = RazorpayPaymentProvider(key_secret="strict_secret_123")
    
    payload = b'{"event": "subscription.charged"}'
    invalid_sig = "fake_hash_value"
    
    import asyncio
    res = asyncio.run(provider.process_webhook(payload, invalid_sig))
    assert res["verified"] is False
