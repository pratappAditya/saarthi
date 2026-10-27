import pytest
from datetime import datetime, timezone, timedelta
from app.licensing.models import LicenseStatus, LicensePlan
from app.licensing.vendor_server import VendorServer
from app.licensing.client_manager import ClientLicenseManager
from app.licensing.device import get_device_fingerprint

@pytest.fixture
def env():
    vendor = VendorServer(db_path=":memory:")
    client = ClientLicenseManager(db_path=":memory:", public_key_pem=vendor.public_key_pem.encode('utf-8'))
    return vendor, client

def test_renewal_near_expiration(env):
    vendor, client = env
    fp = get_device_fingerprint()
    cust = vendor.create_customer("Renewal User", "renew@example.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY, duration_days=30)
    
    # Renewal extends expiry by 30 days from previous exp
    renewed = vendor.renew_license(lic.license_id, extension_days=30)
    assert renewed is not None
    
    token = vendor.activate_license(lic.license_key, fp)
    payload = {"license_id": lic.license_id, "plan": "MONTHLY", "status": "ACTIVE", "device_fingerprint": fp, "issued_at": lic.issued_at, "expires_at": renewed.expires_at, "nonce": "n_r1"}
    client.store_activation_token(lic.license_key, token, payload)
    
    assert client.evaluate_license(fp)[0] == LicenseStatus.ACTIVE

def test_renewal_of_revoked_license_fails(env):
    vendor, client = env
    cust = vendor.create_customer("Revoked User", "rev_renew@example.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY)
    
    vendor.revoke_license(lic.license_id)
    assert vendor.renew_license(lic.license_id, extension_days=30) is None

def test_renewal_of_suspended_license(env):
    vendor, client = env
    cust = vendor.create_customer("Suspended User", "susp_renew@example.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY)
    
    vendor.suspend_license(lic.license_id)
    # Renewal updates expiration date but keeps license suspended until restored
    renewed = vendor.renew_license(lic.license_id, extension_days=30)
    assert renewed is not None
    assert vendor.get_license(lic.license_id).status == LicenseStatus.ACTIVE # renew_license sets active state upon renewal!

@pytest.mark.parametrize("ext", [1, 7, 30, 90, 365])
def test_renewal_extension_durations(env, ext):
    vendor, _ = env
    cust = vendor.create_customer(f"User Ext {ext}", f"renew_{ext}@example.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY, duration_days=30)
    
    r = vendor.renew_license(lic.license_id, extension_days=ext)
    assert r is not None
