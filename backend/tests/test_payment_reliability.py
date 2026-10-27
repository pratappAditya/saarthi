import pytest
import asyncio
from app.licensing.payment import PaymentProviderFactory, RazorpayPaymentProvider, MockPaymentProvider

def test_payment_factory():
    mock_p = PaymentProviderFactory.get_provider("mock")
    assert isinstance(mock_p, MockPaymentProvider)
    
    rzp_p = PaymentProviderFactory.get_provider("razorpay")
    assert isinstance(rzp_p, RazorpayPaymentProvider)

@pytest.mark.asyncio
async def test_mock_payment_lifecycle():
    p = MockPaymentProvider()
    cust_id = await p.create_customer("Test User", "user@test.com")
    assert cust_id.startswith("cust_mock_")
    
    sub = await p.create_subscription(cust_id, "STUDENT")
    assert sub["status"] == "active"
    
    cancel_res = await p.cancel_subscription(sub["subscription_id"])
    assert cancel_res is True

@pytest.mark.asyncio
async def test_razorpay_webhook_verification():
    rzp = RazorpayPaymentProvider(key_id="key123", key_secret="secret123")
    payload = b'{"event": "subscription.charged"}'
    
    # Compute valid signature using key_secret
    import hmac, hashlib
    valid_sig = hmac.new(b"secret123", payload, hashlib.sha256).hexdigest()
    
    res_valid = await rzp.process_webhook(payload, valid_sig)
    assert res_valid["verified"] is True

    res_invalid = await rzp.process_webhook(payload, "invalid_sig_hash")
    assert res_invalid["verified"] is False
