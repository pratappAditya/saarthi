import pytest
from datetime import datetime, timezone, timedelta
from app.licensing.models import LicenseStatus, LicensePlan
from app.licensing.vendor_server import VendorServer
from app.licensing.client_manager import ClientLicenseManager
from app.licensing.payment import MockPaymentProvider
from app.licensing.device import get_device_fingerprint

@pytest.fixture
def monthly_env():
    vendor = VendorServer(db_path=":memory:")
    client = ClientLicenseManager(db_path=":memory:", public_key_pem=vendor.public_key_pem.encode('utf-8'))
    payment = MockPaymentProvider()
    return vendor, client, payment

@pytest.mark.asyncio
async def test_complete_monthly_customer_lifecycle(monthly_env):
    vendor, client, payment = monthly_env
    fp = get_device_fingerprint()
    
    # 1. Customer Created & Payment Confirmed
    pay_cust_id = await payment.create_customer("Monthly User", "monthly@example.com")
    sub = await payment.create_subscription(pay_cust_id, "plan_monthly")
    assert sub["status"] == "active"
    
    # 2. License Issued & Device Activated
    cust = vendor.create_customer("Monthly User", "monthly@example.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY, duration_days=30)
    token = vendor.activate_license(lic.license_key, fp)
    
    payload = {"license_id": lic.license_id, "plan": "MONTHLY", "status": "ACTIVE", "device_fingerprint": fp, "issued_at": lic.issued_at, "expires_at": lic.expires_at, "nonce": "n_m1"}
    client.store_activation_token(lic.license_key, token, payload)
    
    # 3. Normal Operation Evaluation
    st, ent, msg = client.evaluate_license(fp)
    assert st == LicenseStatus.ACTIVE
    assert ent.plan == LicensePlan.MONTHLY
    assert ent.can_use_core_chat is True
    assert ent.can_use_privileged_terminal is True
    assert ent.max_history_messages == 16
    
    # 4. Renewal after 30 days
    renewed_lic = vendor.renew_license(lic.license_id, extension_days=30)
    assert renewed_lic is not None
    renewed_token = vendor.activate_license(lic.license_key, fp)
    renewed_payload = payload.copy()
    renewed_payload["expires_at"] = renewed_lic.expires_at
    client.store_activation_token(lic.license_key, renewed_token, renewed_payload)
    
    assert client.evaluate_license(fp)[0] == LicenseStatus.ACTIVE
    
    # 5. Suspension & Access Blocked
    vendor.suspend_license(lic.license_id)
    with pytest.raises(ValueError, match="currently suspended"):
        vendor.activate_license(lic.license_key, fp)
        
    # 6. Restoration & Access Restored
    assert vendor.restore_license(lic.license_id) is True
    assert client.evaluate_license(fp)[0] == LicenseStatus.ACTIVE
    
    # 7. Cancellation
    assert vendor.cancel_license(lic.license_id) is True
    with pytest.raises(ValueError, match="cancelled"):
        vendor.activate_license(lic.license_key, fp)

@pytest.mark.parametrize("duration", [1, 7, 14, 30])
def test_monthly_plan_expiration_boundaries(monthly_env, duration):
    vendor, client, _ = monthly_env
    cust = vendor.create_customer("Monthly B", f"mb_{duration}@test.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY, duration_days=duration)
    fp = f"fp_mb_{duration}"
    token = vendor.activate_license(lic.license_key, fp)
    payload = {"license_id": lic.license_id, "plan": "MONTHLY", "status": "ACTIVE", "device_fingerprint": fp, "issued_at": lic.issued_at, "expires_at": lic.expires_at, "nonce": f"n_{duration}"}
    client.store_activation_token(lic.license_key, token, payload)
    
    assert client.evaluate_license(fp)[0] == LicenseStatus.ACTIVE
