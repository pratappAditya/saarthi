import pytest
from app.licensing.models import LicensePlan, LicenseStatus
from app.licensing.vendor_server import VendorServer
from app.licensing.client_manager import ClientLicenseManager
from app.licensing.device import get_device_fingerprint

@pytest.fixture
def env():
    vendor = VendorServer(db_path=":memory:")
    client = ClientLicenseManager(db_path=":memory:", public_key_pem=vendor.public_key_pem.encode('utf-8'))
    return vendor, client

def test_recovery_from_corrupted_local_database(env):
    vendor, client = env
    fp = get_device_fingerprint()
    
    # Active Customer
    cust = vendor.create_customer("Recovery User", "recov@example.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY)
    token = vendor.activate_license(lic.license_key, fp)
    payload = {"license_id": lic.license_id, "plan": "MONTHLY", "status": "ACTIVE", "device_fingerprint": fp, "issued_at": lic.issued_at, "expires_at": lic.expires_at, "nonce": "n_rec1"}
    client.store_activation_token(lic.license_key, token, payload)
    
    assert client.evaluate_license(fp)[0] == LicenseStatus.ACTIVE
    
    # Corrupt local database table (simulate DB format/corruption)
    client.clear_license()
    assert client.evaluate_license(fp)[0] == LicenseStatus.UNLICENSED
    
    # Recovery: Re-activate license key with vendor
    recov_token = vendor.activate_license(lic.license_key, fp)
    client.store_activation_token(lic.license_key, recov_token, payload)
    assert client.evaluate_license(fp)[0] == LicenseStatus.ACTIVE

@pytest.mark.parametrize("i", range(1, 11))
def test_recovery_flow_isolation(env, i):
    vendor, client = env
    cust = vendor.create_customer(f"Recov User {i}", f"recov_{i}@test.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY)
    fp = f"fp_recov_{i}"
    
    token = vendor.activate_license(lic.license_key, fp)
    payload = {"license_id": lic.license_id, "plan": "MONTHLY", "status": "ACTIVE", "device_fingerprint": fp, "issued_at": lic.issued_at, "expires_at": lic.expires_at, "nonce": f"n_rec_{i}"}
    client.store_activation_token(lic.license_key, token, payload)
    
    client.clear_license()
    assert client.evaluate_license(fp)[0] == LicenseStatus.UNLICENSED
    
    rec_token = vendor.activate_license(lic.license_key, fp)
    client.store_activation_token(lic.license_key, rec_token, payload)
    assert client.evaluate_license(fp)[0] == LicenseStatus.ACTIVE
