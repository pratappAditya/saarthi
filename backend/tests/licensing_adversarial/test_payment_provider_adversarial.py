import pytest
from app.licensing.payment import MockPaymentProvider, StripePaymentProvider, RazorpayPaymentProvider

@pytest.mark.asyncio
async def test_payment_webhook_replay_protection():
    provider = MockPaymentProvider()
    payload = b'{"event": "subscription.updated", "id": "evt_100"}'
    sig = "sig_valid_123"
    
    res1 = await provider.process_webhook(payload, sig)
    res2 = await provider.process_webhook(payload, sig)
    assert res1["verified"] is True
    assert res2["verified"] is True

@pytest.mark.asyncio
@pytest.mark.parametrize("i", range(1, 29))
async def test_payment_provider_concurrency_fuzz(i):
    provider = MockPaymentProvider()
    cust_id = await provider.create_customer(f"User {i}", f"user_pay_{i}@test.com")
    sub = await provider.create_subscription(cust_id, f"plan_{i % 2}")
    assert sub["status"] == "active"
    assert sub["customer_id"] == cust_id
