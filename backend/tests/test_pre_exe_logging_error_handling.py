"""
Phase 14 & 15 — Automated Tests for Logging Safety and Error Handling.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_invalid_endpoint_returns_structured_404():
    """Verify missing endpoints return structured JSON 404 instead of unhandled crash."""
    res = client.get("/api/nonexistent-endpoint-xyz")
    assert res.status_code == 404
    assert "detail" in res.json()


def test_invalid_json_payload_returns_structured_422():
    """Verify malformed JSON payload returns structured validation error."""
    res = client.post("/api/profile", data="invalid json text", headers={"Content-Type": "application/json"})
    assert res.status_code == 422
    assert "detail" in res.json()


def test_invalid_application_id_returns_404():
    """Verify querying non-existent application ID returns clean 404."""
    res = client.get("/api/career/applications/999999")
    assert res.status_code == 404
    assert res.json()["detail"] == "Job application not found."
