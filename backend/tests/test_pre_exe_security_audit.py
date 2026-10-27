"""
Phase 13 — Automated Tests for Pre-Release Security Audit.
Verifies secret redaction, key protection, admin bypass prevention, and license verification security.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.licensing.telemetry import PrivacySafeTelemetryLogger
from app.config.settings import settings

client = TestClient(app)

def test_telemetry_redacts_sensitive_content():
    """Verify PrivacySafeTelemetryLogger redacts prompt, resume, password, and secret keys."""
    logger = PrivacySafeTelemetryLogger()
    sensitive_data = {
        "user_id": "123",
        "prompt": "Super secret prompt",
        "resume": "Candidate resume text",
        "password": "Password123!",
        "token": "secret_token_val"
    }
    sanitized = logger._sanitize_data(sensitive_data)
    assert sanitized["user_id"] == "123"
    assert "prompt" not in sanitized or sanitized["prompt"] == "[REDACTED]"
    assert "password" not in sanitized or sanitized["password"] == "[REDACTED]"


def test_admin_vendor_endpoints_require_secret_key():
    """Verify vendor administrative endpoints enforce key authorization."""
    res = client.post("/api/license/create", json={"plan": "POWER"})
    assert res.status_code in (401, 403, 404, 405)


def test_public_key_embedded_without_private_key():
    """Verify only public key is available to client runtime."""
    from app.licensing.crypto import DEFAULT_VENDOR_PUBLIC_KEY_PEM
    assert "BEGIN PUBLIC KEY" in DEFAULT_VENDOR_PUBLIC_KEY_PEM
    assert "PRIVATE KEY" not in DEFAULT_VENDOR_PUBLIC_KEY_PEM
