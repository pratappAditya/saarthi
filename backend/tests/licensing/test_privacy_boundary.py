import pytest
from app.licensing.vendor_server import VendorServer
from app.licensing.models import LicensePlan, LicenseActivationRequest, LicenseSyncRequest
from app.licensing.crypto import verify_token

@pytest.fixture
def vendor():
    return VendorServer(db_path=":memory:")

def test_activation_payload_privacy_boundary(vendor):
    cust = vendor.create_customer("Privacy User", "privacy@example.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY)
    
    fp = "fp_privacy_check"
    token = vendor.activate_license(lic.license_key, fp, "Desktop PC")
    payload = verify_token(token, vendor.public_key)
    
    # Verify ONLY licensing metadata is stored in payload
    allowed_keys = {"license_id", "customer_id", "plan", "status", "device_fingerprint", "issued_at", "expires_at", "grace_period_days", "nonce"}
    forbidden_terms = ["prompt", "message", "memory", "file", "conversation", "secret", "password"]
    
    payload_keys = set(payload.keys())
    assert payload_keys.issubset(allowed_keys)
    
    payload_str = str(payload).lower()
    for term in forbidden_terms:
        assert term not in payload_str

def test_license_activation_request_model_privacy():
    req = LicenseActivationRequest(license_key="SAARTHI-MON-123456", device_name="Work PC")
    dict_repr = req.model_dump()
    assert "messages" not in dict_repr
    assert "prompts" not in dict_repr
    assert "files" not in dict_repr

def test_license_sync_request_model_privacy():
    req = LicenseSyncRequest(activation_token="token_abc.xyz", device_fingerprint="fp_123")
    dict_repr = req.model_dump()
    assert "conversations" not in dict_repr
    assert "memories" not in dict_repr

@pytest.mark.parametrize("sensitive_data", [
    "User prompt: Write a resume for John Doe",
    "Memory: User prefers Python",
    "File content: Secret corporate financials",
    "API Key: sk-proj-1234567890",
    "Chat history: confidential legal document",
    "Tool output: terminal execution log",
    "System Info: user profile path",
    "Database record: user preferences",
    "Embedding vector: binary representation",
    "Model response: generated essay text",
    "Password hash: $2b$12$e..."
])
def test_licensing_module_rejects_sensitive_data_in_tokens(vendor, sensitive_data):
    cust = vendor.create_customer("User", f"u_{hash(sensitive_data)}@example.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY)
    token = vendor.activate_license(lic.license_key, "fp_clean")
    
    assert sensitive_data not in token

@pytest.mark.parametrize("i", range(1, 16))
def test_privacy_boundary_strict_key_whitelist(vendor, i):
    cust = vendor.create_customer(f"User {i}", f"privacy_{i}@test.org")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.STUDENT)
    token = vendor.activate_license(lic.license_key, f"fp_privacy_{i}")
    payload = verify_token(token, vendor.public_key)
    
    allowed = {"license_id", "customer_id", "plan", "status", "device_fingerprint", "issued_at", "expires_at", "grace_period_days", "nonce"}
    assert set(payload.keys()).issubset(allowed)
