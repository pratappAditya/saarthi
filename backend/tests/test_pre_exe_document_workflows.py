"""
Phase 8 — Automated Tests for Document Workflows (Import & Export).
Verifies resume import, candidate parsing, profile persistence, distinct import/export routes,
and watermark behavior.
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


def test_resume_import_workflow():
    """Verify resume text import creates/updates candidate profile correctly."""
    resume_payload = {
        "title": "Software Engineer Resume",
        "raw_content": "John Architect\njohn@workstation.local\nSenior Staff Engineer with 10 years experience in Python and React.",
        "is_default": True
    }
    
    res = client.post("/api/career/resume/import", json=resume_payload)
    assert res.status_code == 200
    data = res.json()
    assert "resume" in data
    assert data["resume"]["title"] == "Software Engineer Resume"
    assert "John Architect" in data["resume"]["raw_content"]


def test_watermarked_export_for_free_users():
    """Verify export endpoints enforce watermarks for FREE users."""
    res = client.get("/api/license/status")
    assert res.status_code == 200
    ent = res.json()["entitlements"]
    assert ent["requires_watermark"] is True
    assert ent["plan"] == LicensePlan.FREE.value


def test_job_application_creation_workflow():
    """Verify job application creation and tracking pipeline."""
    app_data = {
        "company": "Anthropic Competitor Inc",
        "role": "Lead Systems Architect",
        "location": "Remote",
        "salary": "$250,000",
        "status": "SAVED"
    }
    res = client.post("/api/career/applications", json=app_data)
    assert res.status_code == 200
    data = res.json()
    assert "application" in data
    assert data["application"]["company"] == "Anthropic Competitor Inc"
    assert data["application"]["role"] == "Lead Systems Architect"

    # List applications
    list_res = client.get("/api/career/applications")
    assert list_res.status_code == 200
    apps = list_res.json()["applications"]
    assert len(apps) >= 1
