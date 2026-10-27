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

def test_revocation_irreversibility(env):
    vendor, client = env
    fp = get_device_fingerprint()
    
    cust = vendor.create_customer("Rev User", "rev_irrev@saarthi.ai")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY)
    token = vendor.activate_license(lic.license_key, fp)
    payload = {"license_id": lic.license_id, "plan": "MONTHLY", "status": "ACTIVE", "device_fingerprint": fp, "issued_at": lic.issued_at, "expires_at": lic.expires_at, "nonce": "n_rv1"}
    client.store_activation_token(lic.license_key, token, payload)
    
    assert client.evaluate_license(fp)[0] == LicenseStatus.ACTIVE
    
    # Vendor revokes
    vendor.revoke_license(lic.license_id)
    client.record_revocation(lic.license_id, "Abuse revocation")
    
    assert client.evaluate_license(fp)[0] == LicenseStatus.REVOKED
    
    # Vendor cannot restore a revoked key
    assert vendor.restore_license(lic.license_id) is False
    with pytest.raises(ValueError, match="permanently revoked"):
        vendor.activate_license(lic.license_key, fp)

@pytest.mark.parametrize("i", range(1, 11))
def test_revocation_batch_security(env, i):
    vendor, client = env
    cust = vendor.create_customer(f"Rev Cust {i}", f"rev_b_{i}@saarthi.ai")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY)
    fp = f"fp_rev_b_{i}"
    
    token = vendor.activate_license(lic.license_key, fp)
    payload = {"license_id": lic.license_id, "plan": "MONTHLY", "status": "ACTIVE", "device_fingerprint": fp, "issued_at": lic.issued_at, "expires_at": lic.expires_at, "nonce": f"n_rv_{i}"}
    client.store_activation_token(lic.license_key, token, payload)
    
    vendor.revoke_license(lic.license_id)
    client.record_revocation(lic.license_id, f"Reason {i}")
    
    assert client.evaluate_license(fp)[0] == LicenseStatus.REVOKED
