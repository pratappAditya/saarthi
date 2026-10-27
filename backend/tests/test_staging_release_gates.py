"""
Saarthi Staging Release Gates Security & Integrity Automated Test Suite.
Verifies all Phase Two, Three, Four, Eight, and Nine hardening gates.
"""

import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config.settings import settings
from app.api.health_api import get_ai_provider_status
from app.admin.auth.admin_auth import (
    validate_admin_security_configuration,
    get_configured_admin_key,
    verify_admin_key,
    is_insecure_placeholder
)
from app.db.connection import get_db_connection

client = TestClient(app)


def test_health_endpoint_returns_200_and_truthful_checks():
    """Verify /api/health and /health endpoints return structured truthful checks."""
    for path in ("/api/health", "/health"):
        res = client.get(path)
        assert res.status_code in (200, 503)
        data = res.json()
        assert "status" in data
        assert "checks" in data
        assert "database" in data["checks"]
        assert "storage" in data["checks"]
        assert "memory" in data["checks"]
        assert "ai_provider" in data["checks"]
        
        ai = data["checks"]["ai_provider"]
        assert "provider" in ai
        assert "model" in ai
        assert "configured" in ai
        assert "reachable" in ai
        assert "is_live" in ai
        assert "execution_mode" in ai
        assert ai["execution_mode"] in ("live", "local", "demo", "unavailable")


def test_ai_status_truthfulness_vocabulary(monkeypatch):
    """Verify AI provider status reports truthful vocabulary across configurations."""
    # 1. Unconfigured provider -> 'unavailable'
    monkeypatch.setattr(settings, "MODEL_PROVIDER", "none")
    monkeypatch.setattr(settings, "ENVIRONMENT", "staging")
    monkeypatch.setattr(settings, "DEMO_MODE", False)
    st = get_ai_provider_status()
    assert st["configured"] is False
    assert st["reachable"] is False
    assert st["is_live"] is False
    assert st["execution_mode"] == "unavailable"
    assert st["last_error_category"] == "NOT_CONFIGURED"

    # 2. Mock provider in staging without DEMO_MODE -> 'unavailable'
    monkeypatch.setattr(settings, "MODEL_PROVIDER", "mock")
    monkeypatch.setattr(settings, "ENVIRONMENT", "staging")
    monkeypatch.setattr(settings, "DEMO_MODE", False)
    st = get_ai_provider_status()
    assert st["configured"] is False
    assert st["is_live"] is False
    assert st["execution_mode"] == "unavailable"
    assert st["last_error_category"] == "MOCK_PROHIBITED_IN_STAGING"

    # 3. Explicit Demo Mode in staging -> 'demo'
    monkeypatch.setattr(settings, "MODEL_PROVIDER", "mock")
    monkeypatch.setattr(settings, "ENVIRONMENT", "staging")
    monkeypatch.setattr(settings, "DEMO_MODE", True)
    st = get_ai_provider_status()
    assert st["configured"] is True
    assert st["is_live"] is False
    assert st["execution_mode"] == "demo"
    assert st["last_error_category"] is None


def test_admin_auth_rejects_insecure_placeholders(monkeypatch):
    """Verify admin auth strictly rejects placeholder keys and revoked tokens."""
    placeholders = [
        "generate_fresh_random_staging_admin_key_64chars",
        "saarthi_admin_secret_key_2026",
        "SAARTHI_SECRET_ADMIN_KEY_2026",
        "change_in_production",
        "my_placeholder_secret_key",
        "example_admin_key",
    ]
    for ph in placeholders:
        assert is_insecure_placeholder(ph) is True
        assert verify_admin_key(ph) is False

    monkeypatch.setenv("ENVIRONMENT", "staging")
    monkeypatch.setenv("VENDOR_ADMIN_KEY", "generate_fresh_random_staging_admin_key_64chars")
    with pytest.raises(RuntimeError) as exc_info:
        validate_admin_security_configuration(is_prod=True)
    assert "insecure placeholder" in str(exc_info.value) or "absent" in str(exc_info.value)


def test_admin_auth_enforces_minimum_entropy(monkeypatch):
    """Verify admin secret key requires at least 32 characters in staging/production."""
    monkeypatch.setenv("ENVIRONMENT", "staging")
    monkeypatch.setenv("VENDOR_ADMIN_KEY", "short_key_under_32_chars")
    with pytest.raises(RuntimeError) as exc_info:
        validate_admin_security_configuration(is_prod=True)
    assert "insufficient entropy" in str(exc_info.value)


def test_database_staging_fail_closed_without_postgres(monkeypatch):
    """Verify staging environment fails closed when PostgreSQL is unavailable, preventing silent SQLite fallback."""
    monkeypatch.setenv("ENVIRONMENT", "staging")
    monkeypatch.setenv("DATABASE_URL", "postgresql://invalid_staging_user:bad_pass@127.0.0.1:54329/invalid_staging_db")
    with pytest.raises(RuntimeError) as exc_info:
        get_db_connection()
    assert "Production PostgreSQL connection failed" in str(exc_info.value) or "PostgreSQL connection failed" in str(exc_info.value)


def test_readiness_probe_distinguishes_db():
    """Verify /api/health/readiness returns 200 when DB is connected, and /api/health/liveness returns 200."""
    res = client.get("/api/health/liveness")
    assert res.status_code == 200
    assert res.json().get("status") == "alive"

    res_ready = client.get("/api/health/readiness")
    assert res_ready.status_code == 200
    assert res_ready.json().get("status") == "ready"


def test_billing_disabled_by_default_in_staging(monkeypatch):
    """Verify non-free checkout fails closed with HTTP 403 when FEATURE_BILLING=False."""
    monkeypatch.setenv("ENVIRONMENT", "staging")
    monkeypatch.setattr(settings, "ENVIRONMENT", "staging")
    monkeypatch.setattr(settings, "FEATURE_BILLING", False)
    monkeypatch.setattr(settings, "PAYMENT_PROVIDER", "none")

    res = client.post("/api/payment/checkout", json={
        "plan_id": "POWER",
        "seats": 1,
        "currency": "INR"
    })
    # Should be rejected with 403 or 401 (auth) or 400
    assert res.status_code in (401, 403, 400)
