import pytest
from app.licensing.vendor_server import VendorServer
from app.licensing.models import LicensePlan, LicenseActivationRequest, LicenseSyncRequest
from app.licensing.crypto import verify_token

@pytest.fixture
def vendor():
    return VendorServer(db_path=":memory:")

def test_privacy_boundary_zero_chat_history_in_requests():
    req = LicenseActivationRequest(license_key="SAARTHI-MON-999", device_name="Workstation")
    dump = req.model_dump()
    assert "messages" not in dump
    assert "prompts" not in dump
    assert "history" not in dump
    assert "memories" not in dump

def test_privacy_boundary_zero_file_content_in_sync():
    req = LicenseSyncRequest(activation_token="tok.sig", device_fingerprint="fp1")
    dump = req.model_dump()
    assert "files" not in dump
    assert "documents" not in dump
    assert "code" not in dump

@pytest.mark.parametrize("i", range(1, 24))
def test_privacy_boundary_whitelisted_payload_fields(vendor, i):
    cust = vendor.create_customer(f"User Privacy {i}", f"privacy_adv_{i}@saarthi.ai")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY)
    token = vendor.activate_license(lic.license_key, f"fp_priv_{i}")
    
    payload = verify_token(token, vendor.public_key)
    allowed_keys = {"license_id", "customer_id", "plan", "status", "device_fingerprint", "issued_at", "expires_at", "grace_period_days", "nonce"}
    assert set(payload.keys()).issubset(allowed_keys)
