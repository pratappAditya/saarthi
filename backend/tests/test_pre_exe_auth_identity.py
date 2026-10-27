"""
Phase 2 — Automated Tests for Authentication & Identity Boundary.
Verifies that anonymous users default to FREE, entitlements originate from backend,
user profile belongs to local user, identity is preserved, and no hardcoded personal names exist.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.profile import ProfileRepository, BenchmarkRepository
from app.licensing.middleware import default_client_manager
from app.licensing.models import LicenseStatus, LicensePlan

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_clean_state():
    """Ensure clean state before each test."""
    ProfileRepository.clear_profile()
    BenchmarkRepository.clear_benchmarks()
    default_client_manager.clear_license()
    yield
    ProfileRepository.clear_profile()
    BenchmarkRepository.clear_benchmarks()
    default_client_manager.clear_license()


def test_anonymous_user_defaults_to_free():
    """Verify an unauthenticated/anonymous user receives FREE tier entitlements."""
    res = client.get("/api/license/status")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == LicenseStatus.UNLICENSED.value
    assert data["entitlements"]["plan"] == LicensePlan.FREE.value
    assert data["entitlements"]["requires_watermark"] is True


def test_no_payment_remains_free():
    """Verify that without valid backend license, plan remains FREE."""
    res = client.get("/api/license/status")
    data = res.json()
    assert data["entitlements"]["plan"] == LicensePlan.FREE.value


def test_user_identity_persistence_across_app_restarts():
    """Verify user profile persists across simulated application restarts."""
    # 1. User sets profile
    profile_input = {
        "full_name": "Alex Mercer",
        "email": "alex.mercer@workstation.local",
        "phone": "+15550192834",
        "location": "Seattle, WA",
        "skills": ["Python", "Rust", "PyTorch"]
    }
    save_res = client.post("/api/profile", json=profile_input)
    assert save_res.status_code == 200

    # 2. Simulate fresh client connection (application restart)
    new_client = TestClient(app)
    get_res = new_client.get("/api/profile")
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["authenticated"] is True
    assert data["full_name"] == "Alex Mercer"
    assert data["email"] == "alex.mercer@workstation.local"
    assert data["skills"] == ["Python", "Rust", "PyTorch"]


def test_no_hardcoded_personal_identities_in_startup_state():
    """Verify no hardcoded names (Pratap, Aditya) in startup state."""
    profile_res = client.get("/api/profile").json()
    session_res = client.get("/api/auth/session").json()

    assert "Pratap" not in str(profile_res)
    assert "Aditya" not in str(profile_res)
    assert "Pratap" not in str(session_res)
    assert "Aditya" not in str(session_res)
