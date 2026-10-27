import pytest
from app.licensing.models import LicenseStatus, LicensePlan
from app.licensing.vendor_server import VendorServer
from app.licensing.client_manager import ClientLicenseManager
from app.licensing.crypto import sign_payload

@pytest.fixture
def setup_mgrs():
    vendor = VendorServer(db_path=":memory:")
    client = ClientLicenseManager(db_path=":memory:", public_key_pem=vendor.public_key_pem.encode('utf-8'))
    return vendor, client

def test_revoked_license_persistent_local_blocking(setup_mgrs):
    vendor, client = setup_mgrs
    cust = vendor.create_customer("Revoked User", "rev_user@example.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY)
    fp = "fp_rev_machine"
    
    token = vendor.activate_license(lic.license_key, fp)
    payload = {"plan": "MONTHLY", "status": "ACTIVE", "device_fingerprint": fp, "issued_at": lic.issued_at, "expires_at": lic.expires_at}
    client.store_activation_token(lic.license_key, token, payload)
    
    assert client.evaluate_license(fp)[0] == LicenseStatus.ACTIVE
    
    # Record revocation locally
    client.record_revocation(lic.license_id, "Revoked by vendor")
    
    status, ent, msg = client.evaluate_license(fp)
    assert status == LicenseStatus.REVOKED
    assert ent is None

def test_re_activation_of_revoked_key_fails_on_vendor(setup_mgrs):
    vendor, client = setup_mgrs
    cust = vendor.create_customer("User", "u_rev@example.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY)
    
    vendor.revoke_license(lic.license_id)
    
    with pytest.raises(ValueError, match="permanently revoked"):
        vendor.activate_license(lic.license_key, "fp_new")

def test_suspended_license_evaluation(setup_mgrs):
    vendor, client = setup_mgrs
    cust = vendor.create_customer("Suspended User", "susp@example.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY)
    fp = "fp_susp"
    
    token = vendor.activate_license(lic.license_key, fp)
    
    # Vendor suspends license and re-issues token with SUSPENDED status
    vendor.suspend_license(lic.license_id)
    susp_payload = {"license_id": lic.license_id, "plan": "MONTHLY", "status": "SUSPENDED", "device_fingerprint": fp, "issued_at": lic.issued_at, "expires_at": lic.expires_at, "nonce": "n1"}
    susp_token = sign_payload(susp_payload, vendor.private_key)
    client.store_activation_token(lic.license_key, susp_token, susp_payload)
    
    status, ent, msg = client.evaluate_license(fp)
    assert status == LicenseStatus.SUSPENDED
    assert "suspended" in msg.lower()

def test_clear_license_resets_to_unlicensed(setup_mgrs):
    vendor, client = setup_mgrs
    cust = vendor.create_customer("User", "u_clear@example.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY)
    token = vendor.activate_license(lic.license_key, "fp_clear")
    payload = {"plan": "MONTHLY", "status": "ACTIVE", "device_fingerprint": "fp_clear", "issued_at": lic.issued_at, "expires_at": lic.expires_at}
    client.store_activation_token(lic.license_key, token, payload)
    
    client.clear_license()
    status, _, _ = client.evaluate_license("fp_clear")
    assert status == LicenseStatus.UNLICENSED

@pytest.mark.parametrize("i", range(1, 16))
def test_abuse_revocation_batch_checks(setup_mgrs, i):
    vendor, client = setup_mgrs
    cust = vendor.create_customer(f"Rev User {i}", f"rev_{i}@abuse.org")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY)
    fp = f"fp_abuse_{i}"
    
    token = vendor.activate_license(lic.license_key, fp)
    payload = {"plan": "MONTHLY", "status": "ACTIVE", "device_fingerprint": fp, "issued_at": lic.issued_at, "expires_at": lic.expires_at}
    client.store_activation_token(lic.license_key, token, payload)
    
    assert client.evaluate_license(fp)[0] == LicenseStatus.ACTIVE
    
    client.record_revocation(lic.license_id, f"Abuse reason {i}")
    assert client.evaluate_license(fp)[0] == LicenseStatus.REVOKED
