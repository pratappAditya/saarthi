import pytest
from app.licensing.models import LicensePlan, LicenseActivationRequest, LicenseSyncRequest
from app.licensing.vendor_server import VendorServer
from app.licensing.crypto import verify_token

@pytest.fixture
def vendor():
    return VendorServer(db_path=":memory:")

def test_explicit_transmitted_fields_table(vendor):
    cust = vendor.create_customer("Privacy Table User", "privacy_table@saarthi.ai")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY)
    token = vendor.activate_license(lic.license_key, "fp_table_1")
    
    payload = verify_token(token, vendor.public_key)
    
    # Explicit Privacy Checklist
    assert "license_id" in payload
    assert "customer_id" in payload
    assert "device_fingerprint" in payload
    assert "plan" in payload
    assert "status" in payload
    assert "issued_at" in payload
    assert "nonce" in payload
    
    # Absolute Forbidden User Content Checklist
    forbidden = ["chat", "prompt", "memory", "files", "tool_output", "model_response", "reasoning"]
    payload_str = str(payload).lower()
    for item in forbidden:
        assert item not in payload_str, f"PRIVACY VIOLATION: {item} was transmitted in licensing payload!"

@pytest.mark.parametrize("i", range(1, 15))
def test_privacy_isolation_lifecycle_fuzzing(vendor, i):
    cust = vendor.create_customer(f"Priv Cust {i}", f"priv_fz_{i}@test.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.STUDENT)
    token = vendor.activate_license(lic.license_key, f"fp_priv_fz_{i}")
    
    payload = verify_token(token, vendor.public_key)
    allowed = {"license_id", "customer_id", "plan", "status", "device_fingerprint", "issued_at", "expires_at", "grace_period_days", "nonce"}
    assert set(payload.keys()).issubset(allowed)
