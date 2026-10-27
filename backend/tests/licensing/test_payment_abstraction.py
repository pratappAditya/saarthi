import pytest
from app.licensing.payment import (
    PaymentProviderFactory, MockPaymentProvider, StripePaymentProvider, RazorpayPaymentProvider
)

@pytest.mark.asyncio
async def test_payment_provider_factory_mock():
    provider = PaymentProviderFactory.get_provider("mock")
    assert isinstance(provider, MockPaymentProvider)

@pytest.mark.asyncio
async def test_payment_provider_factory_stripe():
    provider = PaymentProviderFactory.get_provider("stripe")
    assert isinstance(provider, StripePaymentProvider)

@pytest.mark.asyncio
async def test_payment_provider_factory_razorpay():
    provider = PaymentProviderFactory.get_provider("razorpay")
    assert isinstance(provider, RazorpayPaymentProvider)

@pytest.mark.asyncio
async def test_mock_payment_provider_lifecycle():
    provider = MockPaymentProvider()
    cust_id = await provider.create_customer("Subscriber Alice", "alice_sub@example.com")
    assert cust_id.startswith("cust_mock_")
    
    sub = await provider.create_subscription(cust_id, "plan_monthly")
    assert sub["subscription_id"].startswith("sub_mock_")
    assert sub["status"] == "active"
    
    cancel_res = await provider.cancel_subscription(sub["subscription_id"])
    assert cancel_res is True
    assert provider.subscriptions[sub["subscription_id"]]["status"] == "canceled"

@pytest.mark.asyncio
async def test_mock_payment_provider_invalid_customer():
    provider = MockPaymentProvider()
    with pytest.raises(ValueError, match="not found"):
        await provider.create_subscription("invalid_cust_id", "plan_monthly")

@pytest.mark.asyncio
async def test_mock_payment_provider_webhook():
    provider = MockPaymentProvider()
    res = await provider.process_webhook(b'{"event": "payment_intent.succeeded"}', "sig_123")
    assert res["verified"] is True
    assert res["event_type"] == "invoice.paid"

@pytest.mark.asyncio
@pytest.mark.parametrize("provider_name", ["stripe", "razorpay"])
async def test_stub_providers(provider_name):
    provider = PaymentProviderFactory.get_provider(provider_name)
    cust_id = await provider.create_customer("Test User", "test@example.com")
    assert cust_id is not None
    
    sub = await provider.create_subscription(cust_id, "plan_1")
    assert sub["status"] == "active"
    
    canceled = await provider.cancel_subscription(sub["subscription_id"])
    assert canceled is True
    
    wh = await provider.process_webhook(b'{}', 'sig')
    assert wh["verified"] is True

@pytest.mark.asyncio
@pytest.mark.parametrize("i", range(1, 21))
async def test_payment_provider_batch_subscriptions(i):
    provider = MockPaymentProvider()
    c_id = await provider.create_customer(f"Customer {i}", f"cust_batch_{i}@test.com")
    sub = await provider.create_subscription(c_id, f"plan_{i % 3}")
    assert sub["customer_id"] == c_id
    assert sub["status"] == "active"
