import pytest
from app.licensing.models import LicensePlan, LicenseStatus
from app.licensing.vendor_server import VendorServer
from app.licensing.client_manager import ClientLicenseManager

@pytest.fixture
def env():
    vendor = VendorServer(db_path=":memory:")
    client = ClientLicenseManager(db_path=":memory:", public_key_pem=vendor.public_key_pem.encode('utf-8'))
    return vendor, client

def test_device_replacement_workflow(env):
    vendor, client = env
    cust = vendor.create_customer("Device Swap User", "swap@example.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY, max_devices=1)
    
    fp_old = "fp_laptop_1"
    fp_new = "fp_laptop_2"
    
    # 1. Activate on old laptop
    token_old = vendor.activate_license(lic.license_key, fp_old, "Laptop 1")
    assert token_old is not None
    
    # 2. Attempt activate on new laptop -> Device limit exceeded
    with pytest.raises(ValueError, match="Device limit exceeded"):
        vendor.activate_license(lic.license_key, fp_new, "Laptop 2")
        
    # 3. Vendor removes old device registration
    with vendor._get_connection() as conn:
        conn.cursor().execute("DELETE FROM device_activations WHERE license_id = ? AND device_fingerprint = ?", (lic.license_id, fp_old))
        conn.commit()
        
    # 4. Activate on new laptop succeeds
    token_new = vendor.activate_license(lic.license_key, fp_new, "Laptop 2")
    assert token_new is not None

@pytest.mark.parametrize("max_dev", [1, 2, 3, 5])
def test_multi_device_limit_enforcement(env, max_dev):
    vendor, _ = env
    cust = vendor.create_customer(f"Multi User {max_dev}", f"multi_{max_dev}@example.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY, max_devices=max_dev)
    
    for i in range(max_dev):
        t = vendor.activate_license(lic.license_key, f"fp_dev_{i}")
        assert t is not None
        
    with pytest.raises(ValueError, match="Device limit exceeded"):
        vendor.activate_license(lic.license_key, f"fp_dev_{max_dev}")
