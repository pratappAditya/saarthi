import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.profile import ProfileRepository
from app.licensing.middleware import default_client_manager
from app.licensing.models import LicenseStatus, LicensePlan, Entitlements
from app.licensing.vendor_server import VendorServer
from app.licensing.device import get_device_fingerprint

from app.db.profile import ProfileRepository, BenchmarkRepository

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_clean_state():
    """Ensure clean profile, benchmarks, and license cache before each test."""
    ProfileRepository.clear_profile()
    BenchmarkRepository.clear_benchmarks()
    default_client_manager.clear_license()
    yield
    ProfileRepository.clear_profile()
    BenchmarkRepository.clear_benchmarks()
    default_client_manager.clear_license()


def test_fresh_session_not_demo_user():
    """Verify that a fresh session returns no authenticated user and an unauthenticated profile."""
    res = client.get("/api/profile")
    assert res.status_code == 200
    data = res.json()
    assert data["authenticated"] is False
    assert data["full_name"] == ""
    assert data["email"] == ""


def test_fresh_session_auth_session_endpoint():
    """Verify /api/auth/session returns authenticated: False and user: None for fresh session."""
    res = client.get("/api/auth/session")
    assert res.status_code == 200
    data = res.json()
    assert data["authenticated"] is False
    assert data["user"] is None


def test_profile_creation_and_persistence():
    """Verify profile creation authenticates the session and persists user identity."""
    profile_data = {
        "full_name": "Test User",
        "email": "test@example.com",
        "phone": "+1234567890",
        "location": "New York, NY",
        "education": [],
        "skills": ["Python", "React"],
        "experience": [],
        "projects": [],
        "links": {},
        "work_authorization": "Authorized to work",
        "notice_period_days": 15,
        "preferred_locations": ["New York"]
    }
    save_res = client.post("/api/profile", json=profile_data)
    assert save_res.status_code == 200
    save_data = save_res.json()
    assert save_data["authenticated"] is True
    assert save_data["profile"]["full_name"] == "Test User"

    # Fetch again to verify persistence
    get_res = client.get("/api/profile")
    assert get_res.status_code == 200
    fetched = get_res.json()
    assert fetched["authenticated"] is True
    assert fetched["full_name"] == "Test User"
    assert fetched["email"] == "test@example.com"


def test_clear_profile_restores_anonymous_state():
    """Verify deleting/clearing profile restores clean anonymous state."""
    client.post("/api/profile", json={"full_name": "Temporary User", "email": "temp@example.com"})
    del_res = client.delete("/api/profile")
    assert del_res.status_code == 200
    assert del_res.json()["authenticated"] is False

    get_res = client.get("/api/profile")
    assert get_res.json()["authenticated"] is False
    assert get_res.json()["full_name"] == ""


def test_unauthenticated_user_gets_free_entitlements():
    """Verify an unauthenticated or unlicensed user gets FREE entitlements with watermarking required."""
    res = client.get("/api/license/status")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == LicenseStatus.UNLICENSED.value
    assert data["entitlements"]["plan"] == LicensePlan.FREE.value
    assert data["entitlements"]["requires_watermark"] is True
    assert data["entitlements"]["can_use_privileged_terminal"] is False
    assert data["entitlements"]["max_job_applications_per_month"] == 3


def test_unauthenticated_user_export_is_watermarked():
    """Verify document export for free/unlicensed user receives watermark."""
    res = client.post("/api/career/export-document", json={
        "document_type": "tailored_resume",
        "content": "# Candidate Resume Body\n- Developed high-performance system",
        "format": "markdown"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["watermarked"] is True
    assert "Created with Saarthi" in data["exported_content"] or "Saarthi Free Plan" in data["exported_content"]


def test_unauthenticated_user_cannot_switch_to_paid_models():
    """Verify free tier users cannot switch to paid 8B Nemotron models."""
    res = client.post("/api/nemotron/switch-model", json={"model_id": "nemotron-3-8b"})
    assert res.status_code == 403
    assert "requires Personal or Power plan" in res.json()["detail"]


def test_paid_user_verified_entitlements():
    """Verify cryptographically activated paid license unlocks clean exports and paid entitlements."""
    vendor = VendorServer()
    fp = get_device_fingerprint()
    cust = vendor.create_customer("Commercial Customer", "paid@saarthi.ai")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.POWER)
    token = vendor.activate_license(lic.license_key, fp, "Workstation-1")

    payload = {
        "plan": lic.plan.value,
        "status": lic.status.value,
        "device_fingerprint": fp,
        "issued_at": lic.issued_at,
        "expires_at": lic.expires_at
    }
    default_client_manager.public_key = vendor.public_key
    default_client_manager.store_activation_token(lic.license_key, token, payload)

    # Check status endpoint
    status_res = client.get("/api/license/status")
    assert status_res.status_code == 200
    data = status_res.json()
    assert data["status"] == LicenseStatus.ACTIVE.value
    assert data["entitlements"]["plan"] == LicensePlan.POWER.value
    assert data["entitlements"]["requires_watermark"] is False
    assert data["entitlements"]["can_use_privileged_terminal"] is True
    assert data["entitlements"]["max_job_applications_per_month"] == -1

    # Check document export endpoint (must be clean without watermark)
    export_res = client.post("/api/career/export-document", json={
        "document_type": "tailored_resume",
        "content": "# Clean Resume Body\n- Developed high-performance system",
        "format": "markdown"
    })
    assert export_res.status_code == 200
    exp_data = export_res.json()
    assert exp_data["watermarked"] is False
    assert "Created with Saarthi" not in exp_data["exported_content"]


def test_unpaid_fake_key_activation_rejected():
    """Verify that attempting to activate an unissued/unpaid license key is rejected with HTTP 400."""
    res = client.post("/api/license/activate", json={
        "license_key": "SAARTHI-POWER-ONLINE",
        "device_name": "Test-Device"
    })
    assert res.status_code == 400
    assert "Invalid or unverified license key" in res.json()["detail"]

    # Verify licensing status remains UNLICENSED / FREE baseline
    status_res = client.get("/api/license/status")
    assert status_res.status_code == 200
    data = status_res.json()
    assert data["status"] == LicenseStatus.UNLICENSED.value
    assert data["entitlements"]["plan"] == LicensePlan.FREE.value
    assert data["entitlements"]["requires_watermark"] is True


def test_chat_response_normalization():
    """Verify that chat response output returns unwrapped plain text instead of raw JSON protocol objects."""
    res = client.post("/api/chat", json={
        "message": "Hello Saarthi",
        "session_id": "test-session-123"
    })
    assert res.status_code == 200
    data = res.json()
    assert "status" in data and data["status"] == "success"
    response_text = data["response"]
    assert not response_text.strip().startswith('{"type":"text"')
    assert not response_text.strip().startswith('{"type": "text"')


def test_fresh_session_telemetry_not_benchmarked():
    """Verify that a fresh session without a benchmark returns is_benchmarked: False and Not benchmarked label."""
    res = client.get("/api/nemotron/benchmark")
    assert res.status_code == 200
    data = res.json()
    assert data["is_benchmarked"] is False
    assert data["measured_tps"] is None
    assert data["label"] == "Not benchmarked"

    # Check hardware endpoint
    hw_res = client.get("/api/nemotron/hardware")
    assert hw_res.status_code == 200
    hw_data = hw_res.json()
    assert hw_data["is_benchmarked"] is False
    assert hw_data["measured_tps"] is None


def test_post_benchmark_returns_live_measured_telemetry(monkeypatch):
    """Verify that running a physical hardware benchmark measures actual TPS and stores the result."""
    from unittest.mock import AsyncMock, MagicMock

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "eval_count": 180,
        "eval_duration": 10000000000 # 10s -> 18.0 t/s
    }

    class DummyAsyncClient:
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            pass
        async def post(self, *args, **kwargs):
            return mock_resp

    monkeypatch.setattr("httpx.AsyncClient", DummyAsyncClient)

    res = client.post("/api/nemotron/benchmark")
    assert res.status_code == 200
    data = res.json()
    assert data["is_benchmarked"] is True
    assert data["measured_tps"] == 18.0
    assert "18.0 t/s" in data["label"]

    # Verify subsequent GET returns the measured benchmark
    get_res = client.get("/api/nemotron/benchmark")
    assert get_res.status_code == 200
    get_data = get_res.json()
    assert get_data["is_benchmarked"] is True
    assert get_data["measured_tps"] == 18.0


