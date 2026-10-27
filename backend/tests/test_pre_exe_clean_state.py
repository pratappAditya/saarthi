"""
Phase 1 — Automated Tests for Clean Application State.
Verifies that fresh Saarthi installation/session is completely clean, anonymous,
without hardcoded candidate names, silent demo mode, or silent paid activations.
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
    """Ensure clean profile, benchmarks, and license cache before each test."""
    ProfileRepository.clear_profile()
    BenchmarkRepository.clear_benchmarks()
    default_client_manager.clear_license()
    yield
    ProfileRepository.clear_profile()
    BenchmarkRepository.clear_benchmarks()
    default_client_manager.clear_license()


def test_fresh_session_no_personal_name():
    """Verify fresh session does NOT return any personal/hardcoded candidate name."""
    res = client.get("/api/profile")
    assert res.status_code == 200
    data = res.json()
    assert data["full_name"] == ""
    assert "Pratap" not in data.get("full_name", "")
    assert "Aditya" not in data.get("full_name", "")


def test_fresh_session_is_anonymous():
    """Verify fresh session starts as anonymous/unauthenticated."""
    res = client.get("/api/auth/session")
    assert res.status_code == 200
    data = res.json()
    assert data["authenticated"] is False
    assert data["user"] is None


def test_fresh_session_default_entitlements_are_free():
    """Verify fresh session is strictly FREE tier, not paid or Power/Personal/Student."""
    res = client.get("/api/license/status")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == LicenseStatus.UNLICENSED.value
    assert data["entitlements"]["plan"] == LicensePlan.FREE.value
    assert data["entitlements"]["plan"] != LicensePlan.POWER.value
    assert data["entitlements"]["plan"] != LicensePlan.PERSONAL.value
    assert data["entitlements"]["plan"] != LicensePlan.STUDENT.value
    assert data["entitlements"]["requires_watermark"] is True


def test_profile_persistence_and_reset():
    """Verify user profile creation persists data and DELETE /api/profile completely resets state."""
    new_profile = {
        "full_name": "Jane Doe",
        "email": "jane.doe@example.com",
        "phone": "+19876543210",
        "location": "Austin, TX",
        "education": [{"degree": "B.S. CS", "school": "UT Austin", "year": "2024"}],
        "skills": ["Python", "FastAPI", "React"],
        "experience": [],
        "projects": [],
        "links": {"github": "https://github.com/janedoe"},
        "work_authorization": "US Citizen",
        "notice_period_days": 0,
        "preferred_locations": ["Austin", "Remote"]
    }
    
    # Save profile
    save_res = client.post("/api/profile", json=new_profile)
    assert save_res.status_code == 200
    
    # Verify persisted profile
    get_res = client.get("/api/profile")
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["authenticated"] is True
    assert data["full_name"] == "Jane Doe"
    assert data["email"] == "jane.doe@example.com"
    assert data["skills"] == ["Python", "FastAPI", "React"]

    # Explicit reset
    reset_res = client.delete("/api/profile")
    assert reset_res.status_code == 200
    
    # Verify clean after reset
    after_reset = client.get("/api/profile").json()
    assert after_reset["authenticated"] is False
    assert after_reset["full_name"] == ""
    assert after_reset["email"] == ""
    assert after_reset["skills"] == []
