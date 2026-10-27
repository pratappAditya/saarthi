import pytest
from app.licensing.models import LicenseStatus, LicensePlan
from app.licensing.vendor_server import VendorServer
from app.licensing.client_manager import ClientLicenseManager
from app.licensing.device import get_device_fingerprint

@pytest.fixture
def env():
    vendor = VendorServer(db_path=":memory:")
    client = ClientLicenseManager(db_path=":memory:", public_key_pem=vendor.public_key_pem.encode('utf-8'))
    return vendor, client

@pytest.mark.parametrize("i", range(1, 51))
def test_cloned_license_token_rejected_on_different_machine(env, i):
    vendor, client = env
    cust = vendor.create_customer(f"Legit User {i}", f"legit_{i}@company.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY)
    
    legit_fp = f"legit_hardware_fingerprint_pc_{i}"
    cloned_fp = f"cloned_hardware_fingerprint_pc_{i}"
    
    token = vendor.activate_license(lic.license_key, legit_fp)
    payload = {"license_id": lic.license_id, "plan": "MONTHLY", "status": "ACTIVE", "device_fingerprint": legit_fp, "issued_at": lic.issued_at, "expires_at": lic.expires_at, "nonce": f"n_{i}"}
    client.store_activation_token(lic.license_key, token, payload)
    
    # Valid on legit machine
    st_legit, _, _ = client.evaluate_license(legit_fp)
    assert st_legit == LicenseStatus.ACTIVE
    
    # Rejected on cloned machine
    st_clone, _, msg_clone = client.evaluate_license(cloned_fp)
    assert st_clone == LicenseStatus.UNLICENSED
    assert "mismatch" in msg_clone.lower()

def test_legitimate_vendor_device_replacement_workflow(env):
    vendor, client = env
    cust = vendor.create_customer("User Upgrade", "upgrade@example.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY, max_devices=1)
    
    old_fp = "old_laptop_fp"
    new_fp = "new_laptop_fp"
    
    # Activation on old laptop
    token_old = vendor.activate_license(lic.license_key, old_fp)
    payload_old = {"license_id": lic.license_id, "plan": "MONTHLY", "status": "ACTIVE", "device_fingerprint": old_fp, "issued_at": lic.issued_at, "expires_at": lic.expires_at, "nonce": "n1"}
    client.store_activation_token(lic.license_key, token_old, payload_old)
    assert client.evaluate_license(old_fp)[0] == LicenseStatus.ACTIVE
    
    # Activating on new laptop without vendor recovery fails (limit 1)
    with pytest.raises(ValueError, match="Device limit exceeded"):
        vendor.activate_license(lic.license_key, new_fp)
        
    # Vendor administrative replacement: Revoke old device activation
    with vendor._get_connection() as conn:
        conn.cursor().execute("DELETE FROM device_activations WHERE license_id = ? AND device_fingerprint = ?", (lic.license_id, old_fp))
        conn.commit()
        
    # Now activation on new laptop succeeds!
    token_new = vendor.activate_license(lic.license_key, new_fp)
    payload_new = {"license_id": lic.license_id, "plan": "MONTHLY", "status": "ACTIVE", "device_fingerprint": new_fp, "issued_at": lic.issued_at, "expires_at": lic.expires_at, "nonce": "n2"}
    client.store_activation_token(lic.license_key, token_new, payload_new)
    assert client.evaluate_license(new_fp)[0] == LicenseStatus.ACTIVE

@pytest.mark.parametrize("bad_fp", [
    "",
    "none",
    "0000000000000000",
    "short_fp",
    "invalid_fp_string"
])
def test_invalid_hardware_fingerprint_strings(env, bad_fp):
    _, client = env
    st, _, _ = client.evaluate_license(bad_fp)
    assert st == LicenseStatus.UNLICENSED
