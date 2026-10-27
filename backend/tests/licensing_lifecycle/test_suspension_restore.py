import pytest
from app.licensing.models import LicenseStatus, LicensePlan
from app.licensing.vendor_server import VendorServer
from app.licensing.client_manager import ClientLicenseManager
from app.licensing.crypto import sign_payload
from app.licensing.device import get_device_fingerprint

@pytest.fixture
def env():
    vendor = VendorServer(db_path=":memory:")
    client = ClientLicenseManager(db_path=":memory:", public_key_pem=vendor.public_key_pem.encode('utf-8'))
    return vendor, client

def test_suspension_and_restoration_cycle(env):
    vendor, client = env
    fp = get_device_fingerprint()
    
    # 1. Active Customer
    cust = vendor.create_customer("Susp User", "susp_cycle@saarthi.ai")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY)
    token = vendor.activate_license(lic.license_key, fp)
    payload = {"license_id": lic.license_id, "plan": "MONTHLY", "status": "ACTIVE", "device_fingerprint": fp, "issued_at": lic.issued_at, "expires_at": lic.expires_at, "nonce": "n_sc1"}
    client.store_activation_token(lic.license_key, token, payload)
    
    assert client.evaluate_license(fp)[0] == LicenseStatus.ACTIVE
    
    # 2. Vendor Suspends
    vendor.suspend_license(lic.license_id)
    
    # Client receives updated token
    susp_payload = payload.copy()
    susp_payload["status"] = "SUSPENDED"
    susp_token = sign_payload(susp_payload, vendor.private_key)
    client.store_activation_token(lic.license_key, susp_token, susp_payload)
    
    assert client.evaluate_license(fp)[0] == LicenseStatus.SUSPENDED
    
    # 3. User attempts local database edit (`status = 'ACTIVE'`)
    with client._get_connection() as conn:
        conn.cursor().execute("UPDATE client_license_cache SET status = 'ACTIVE'")
        conn.commit()
        
    # Fails closed because signature unpacks "SUSPENDED" from token payload
    assert client.evaluate_license(fp)[0] == LicenseStatus.SUSPENDED
    
    # 4. Vendor Restores
    assert vendor.restore_license(lic.license_id) is True
    
    restored_token = vendor.activate_license(lic.license_key, fp)
    restored_payload = payload.copy()
    restored_payload["status"] = "ACTIVE"
    client.store_activation_token(lic.license_key, restored_token, restored_payload)
    
    assert client.evaluate_license(fp)[0] == LicenseStatus.ACTIVE

@pytest.mark.parametrize("i", range(1, 11))
def test_suspension_bypass_attempts_fuzzing(env, i):
    vendor, client = env
    cust = vendor.create_customer(f"User {i}", f"susp_fuzz_{i}@saarthi.ai")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY)
    fp = f"fp_susp_fuzz_{i}"
    
    token = vendor.activate_license(lic.license_key, fp)
    payload = {"license_id": lic.license_id, "plan": "MONTHLY", "status": "ACTIVE", "device_fingerprint": fp, "issued_at": lic.issued_at, "expires_at": lic.expires_at, "nonce": f"n_sf_{i}"}
    client.store_activation_token(lic.license_key, token, payload)
    
    vendor.suspend_license(lic.license_id)
    susp_payload = payload.copy()
    susp_payload["status"] = "SUSPENDED"
    susp_token = sign_payload(susp_payload, vendor.private_key)
    client.store_activation_token(lic.license_key, susp_token, susp_payload)
    
    assert client.evaluate_license(fp)[0] == LicenseStatus.SUSPENDED
