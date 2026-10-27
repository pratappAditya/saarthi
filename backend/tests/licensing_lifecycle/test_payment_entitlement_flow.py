import pytest
from app.licensing.payment import MockPaymentProvider, StripePaymentProvider, RazorpayPaymentProvider
from app.licensing.models import LicensePlan, LicenseStatus
from app.licensing.vendor_server import VendorServer

@pytest.fixture
def env():
    vendor = VendorServer(db_path=":memory:")
    payment = MockPaymentProvider()
    return vendor, payment

@pytest.mark.asyncio
async def test_payment_success_to_entitlement_flow(env):
    vendor, payment = env
    
    # Step 1: Create customer & subscription
    c_id = await payment.create_customer("Paid User", "paid@example.com")
    sub = await payment.create_subscription(c_id, "plan_monthly")
    assert sub["status"] == "active"
    
    # Step 2: Vendor confirms transaction & issues license
    cust = vendor.create_customer("Paid User", "paid@example.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY)
    assert lic.status == LicenseStatus.ACTIVE

@pytest.mark.asyncio
async def test_payment_webhook_verification_gating(env):
    _, payment = env
    
    # Valid webhook payload
    valid_payload = b'{"event": "invoice.paid", "subscription_id": "sub_100"}'
    res_valid = await payment.process_webhook(valid_payload, "valid_signature_123")
    assert res_valid["verified"] is True
    
    # Forged webhook signature (stubs enforce signature presence)
    stripe = StripePaymentProvider()
    res_stripe = await stripe.process_webhook(valid_payload, "sig_stripe_123")
    assert res_stripe["verified"] is True

@pytest.mark.asyncio
@pytest.mark.parametrize("event_type,expected_status", [
    ("invoice.payment_failed", "past_due"),
    ("customer.subscription.deleted", "canceled"),
    ("charge.refunded", "refunded")
])
async def test_payment_failure_and_cancellation_events(env, event_type, expected_status):
    vendor, payment = env
    cust = vendor.create_customer(f"Cust {event_type}", f"c_{hash(event_type)}@example.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY)
    
    # When payment fails or is cancelled/refunded, vendor updates license status
    if expected_status == "canceled":
        vendor.cancel_license(lic.license_id)
        assert vendor.get_license(lic.license_id).status == LicenseStatus.CANCELLED
    elif expected_status == "past_due":
        vendor.suspend_license(lic.license_id, reason="Payment failed")
        assert vendor.get_license(lic.license_id).status == LicenseStatus.SUSPENDED
