import pytest
from app.licensing.device import get_device_fingerprint, get_hardware_identifiers
from app.licensing.vendor_server import VendorServer
from app.licensing.client_manager import ClientLicenseManager
from app.licensing.models import LicenseStatus, LicensePlan

def test_hardware_identifiers_structure():
    info = get_hardware_identifiers()
    assert isinstance(info, dict)
    assert "system" in info
    assert "mac_hash" in info

def test_device_fingerprint_consistency():
    fp1 = get_device_fingerprint()
    fp2 = get_device_fingerprint()
    assert len(fp1) == 64 # SHA-256 hex string
    assert fp1 == fp2

def test_device_fingerprint_custom_info():
    info1 = {"cpu": "intel_i7", "board": "board_123"}
    info2 = {"board": "board_123", "cpu": "intel_i7"}
    info3 = {"cpu": "amd_ryzen", "board": "board_123"}
    
    assert get_device_fingerprint(info1) == get_device_fingerprint(info2)
    assert get_device_fingerprint(info1) != get_device_fingerprint(info3)

def test_hardware_mismatch_rejection():
    vendor = VendorServer(db_path=":memory:")
    client = ClientLicenseManager(db_path=":memory:", public_key_pem=vendor.public_key_pem.encode('utf-8'))
    
    cust = vendor.create_customer("HW User", "hw@example.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY)
    
    authorized_fp = "device_fingerprint_authorized_pc"
    unauthorized_fp = "device_fingerprint_rogue_pc"
    
    token = vendor.activate_license(lic.license_key, authorized_fp)
    payload = {"plan": "MONTHLY", "status": "ACTIVE", "device_fingerprint": authorized_fp, "issued_at": lic.issued_at, "expires_at": lic.expires_at}
    client.store_activation_token(lic.license_key, token, payload)
    
    # Evaluating on authorized device -> ACTIVE
    st1, _, _ = client.evaluate_license(authorized_fp)
    assert st1 == LicenseStatus.ACTIVE
    
    # Evaluating on rogue device -> UNLICENSED (mismatch)
    st2, _, msg2 = client.evaluate_license(unauthorized_fp)
    assert st2 == LicenseStatus.UNLICENSED
    assert "mismatch" in msg2.lower()

@pytest.mark.parametrize("dev_count", [1, 2, 5])
def test_multi_device_enforcement(dev_count):
    vendor = VendorServer(db_path=":memory:")
    cust = vendor.create_customer("Multi Dev", f"multi_{dev_count}@example.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY, max_devices=dev_count)
    
    for i in range(dev_count):
        t = vendor.activate_license(lic.license_key, f"fp_dev_{i}")
        assert t is not None
        
    with pytest.raises(ValueError, match="Device limit exceeded"):
        vendor.activate_license(lic.license_key, f"fp_dev_{dev_count}")

@pytest.mark.parametrize("i", range(1, 21))
def test_hardware_fingerprint_unique_inputs(i):
    fp1 = get_device_fingerprint({"id": f"device_{i}", "mac": f"mac_{i}"})
    fp2 = get_device_fingerprint({"id": f"device_{i+1000}", "mac": f"mac_{i}"})
    assert len(fp1) == 64
    assert len(fp2) == 64
    assert fp1 != fp2
