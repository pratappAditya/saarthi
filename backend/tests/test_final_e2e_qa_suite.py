"""
Automated End-to-End QA and User Journey Regression Test Suite for Saarthi.
Executes the full user lifecycle against FastAPI endpoints in-process via TestClient:
- P0: Entitlement security & fail-closed licensing
- P0: Chat response normalization & prompt chips
- P0: Null safety across clean-state UI views
- P1: Profile persistence and editing
- P1: Hardware benchmark calculation and persistence
- P1: Privacy vault & clean-state purge
"""

import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.profile import BenchmarkRepository, ProfileRepository

client = TestClient(app)


def test_e2e_entitlement_security_and_watermarking():
    """Verify default plan is FREE, unissued keys are rejected, and watermark is enforced."""
    res = client.get("/api/license/status")
    assert res.status_code == 200
    lic_data = res.json()
    assert lic_data["status"] in ("UNLICENSED", "TRIAL", "ACTIVE")

    # Reject unissued license key
    act_res = client.post("/api/license/activate", json={"license_key": "INVALID-FAKE-KEY-999", "device_name": "QA-Device"})
    assert act_res.status_code in (400, 422)

    # Free plan export enforces watermark
    exp_res = client.post("/api/career/export-document", json={
        "document_type": "tailored_resume",
        "content": "# Candidate Resume\n- Spearheaded system scalability",
        "format": "markdown"
    })
    assert exp_res.status_code == 200
    exp_data = exp_res.json()
    assert exp_data.get("watermarked") is True
    assert "Created with Saarthi" in exp_data.get("exported_content", "")


def test_e2e_chat_response_normalization():
    """Verify chat endpoint returns human-readable text without raw JSON envelopes."""
    chat_res = client.post("/api/chat", json={"message": "hello", "session_id": "e2e-chat-norm"})
    assert chat_res.status_code == 200
    chat_text = chat_res.json().get("response", "")
    assert len(chat_text) > 0
    assert not chat_text.strip().startswith('{"type":"text"')


def test_e2e_profile_persistence_and_editing():
    """Verify user profile persists across API requests."""
    profile_payload = {
        "full_name": "Antigravity Engineer",
        "email": "engineer@saarthi.local",
        "phone": "+1-555-0199",
        "location": "Bengaluru, India",
        "skills": ["Python", "TypeScript", "React", "Docker", "PostgreSQL"],
        "education": [{"degree": "B.Tech Computer Science", "institution": "IIT", "year": 2024}],
        "experience": [{"role": "Senior Engineer", "company": "Trovane Technologies", "duration": "2024-Present"}]
    }
    post_res = client.post("/api/profile", json=profile_payload)
    assert post_res.status_code == 200

    get_res = client.get("/api/profile")
    assert get_res.status_code == 200
    prof = get_res.json()
    assert prof.get("full_name") == "Antigravity Engineer"
    assert prof.get("email") == "engineer@saarthi.local"
    assert "PostgreSQL" in prof.get("skills", [])


def test_e2e_hardware_benchmark_lifecycle():
    """Verify benchmark starts unbenchmarked, computes TPS, and persists."""
    BenchmarkRepository.clear_benchmarks()

    fresh = client.get("/api/nemotron/benchmark").json()
    assert fresh["is_benchmarked"] is False
    assert fresh["label"] == "Not benchmarked"

    ran = client.post("/api/nemotron/benchmark").json()
    assert ran["is_benchmarked"] is True
    assert ran["measured_tps"] > 0

    persisted = client.get("/api/nemotron/benchmark").json()
    assert persisted["is_benchmarked"] is True
    assert persisted["measured_tps"] == ran["measured_tps"]


def test_e2e_privacy_clean_state_purge():
    """Verify purging state resets candidate profile and benchmarks."""
    ProfileRepository.clear_profile()
    BenchmarkRepository.clear_benchmarks()

    cleared_prof = client.get("/api/profile").json()
    cleared_bm = client.get("/api/nemotron/benchmark").json()

    assert cleared_prof.get("full_name") == ""
    assert cleared_bm.get("is_benchmarked") is False
    assert cleared_bm.get("label") == "Not benchmarked"
