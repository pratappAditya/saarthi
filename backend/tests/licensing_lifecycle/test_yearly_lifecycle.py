import pytest
from datetime import datetime, timezone, timedelta
from app.licensing.models import LicenseStatus, LicensePlan
from app.licensing.vendor_server import VendorServer
from app.licensing.client_manager import ClientLicenseManager
from app.licensing.payment import MockPaymentProvider
from app.licensing.device import get_device_fingerprint

@pytest.fixture
def yearly_env():
    vendor = VendorServer(db_path=":memory:")
    client = ClientLicenseManager(db_path=":memory:", public_key_pem=vendor.public_key_pem.encode('utf-8'))
    payment = MockPaymentProvider()
    return vendor, client, payment

@pytest.mark.asyncio
async def test_complete_yearly_customer_lifecycle(yearly_env):
    vendor, client, payment = yearly_env
    fp = get_device_fingerprint()
    
    # 1. Customer & Payment
    pay_cust_id = await payment.create_customer("Yearly VIP", "yearly@vip.com")
    sub = await payment.create_subscription(pay_cust_id, "plan_yearly")
    assert sub["status"] == "active"
    
    # 2. License Creation (365 days) & Activation
    cust = vendor.create_customer("Yearly VIP", "yearly@vip.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.YEARLY, duration_days=365)
    token = vendor.activate_license(lic.license_key, fp)
    
    # Check 365-day expiry
    exp_dt = datetime.fromisoformat(lic.expires_at)
    issued_dt = datetime.fromisoformat(lic.issued_at)
    assert (exp_dt - issued_dt).days >= 364
    
    payload = {"license_id": lic.license_id, "plan": "YEARLY", "status": "ACTIVE", "device_fingerprint": fp, "issued_at": lic.issued_at, "expires_at": lic.expires_at, "nonce": "n_y1"}
    client.store_activation_token(lic.license_key, token, payload)
    
    # 3. Entitlement Verification (Priority + Expanded History)
    st, ent, _ = client.evaluate_license(fp)
    assert st == LicenseStatus.ACTIVE
    assert ent.plan == LicensePlan.YEARLY
    assert ent.priority_support is True
    assert ent.max_history_messages == 32
    assert ent.can_use_privileged_terminal is True
    
    # 4. Yearly Renewal (+365 days)
    renewed_lic = vendor.renew_license(lic.license_id, extension_days=365)
    assert renewed_lic is not None
    
    # 5. Permanent Revocation
    vendor.revoke_license(lic.license_id)
    with pytest.raises(ValueError, match="permanently revoked"):
        vendor.activate_license(lic.license_key, fp)

@pytest.mark.parametrize("i", range(1, 11))
def test_yearly_license_isolation(yearly_env, i):
    vendor, client, _ = yearly_env
    cust = vendor.create_customer(f"Yearly User {i}", f"y_iso_{i}@vip.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.YEARLY, duration_days=365)
    fp = f"fp_y_iso_{i}"
    token = vendor.activate_license(lic.license_key, fp)
    payload = {"license_id": lic.license_id, "plan": "YEARLY", "status": "ACTIVE", "device_fingerprint": fp, "issued_at": lic.issued_at, "expires_at": lic.expires_at, "nonce": f"n_y_{i}"}
    client.store_activation_token(lic.license_key, token, payload)
    
    st, ent, _ = client.evaluate_license(fp)
    assert st == LicenseStatus.ACTIVE
    assert ent.plan == LicensePlan.YEARLY
