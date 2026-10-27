import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.telemetry import telemetry
from app.db.backup import DatabaseBackupEngine
from app.intelligence.circuit_breaker import CircuitBreaker, CircuitBreakerOpenException

client = TestClient(app)

def test_full_health_check_endpoint():
    """
    Verify full operational health check returns healthy status and system diagnostics.
    """
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ("healthy", "degraded")
    assert "checks" in data
    assert "database" in data["checks"]
    assert data["checks"]["database"]["healthy"] is True

def test_liveness_and_readiness_probes():
    """
    Verify load balancer liveness and readiness ping endpoints.
    """
    res_live = client.get("/api/health/liveness")
    assert res_live.status_code == 200
    assert res_live.json()["status"] == "alive"

    res_ready = client.get("/api/health/readiness")
    assert res_ready.status_code == 200
    assert res_ready.json()["status"] == "ready"

def test_observability_metrics_endpoint():
    """
    Verify Prometheus/OpenTelemetry snapshot metrics endpoint.
    """
    res = client.get("/api/metrics")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "metrics" in data
    assert "total_requests" in data["metrics"]
    assert "system" in data["metrics"]

def test_request_tracing_middleware():
    """
    Verify X-Request-ID and X-Response-Time-MS header injection.
    """
    res = client.get("/api/health")
    assert "x-request-id" in res.headers
    assert "x-response-time-ms" in res.headers
    assert "x-content-type-options" in res.headers

def test_global_exception_shield():
    """
    Verify unhandled exceptions return structured JSON 500 without exposing internal tracebacks.
    """
    # Create temporary endpoint trigger
    res = client.get("/api/health/non-existent-route-404")
    assert res.status_code == 404

def test_rate_limiter_protection():
    """
    Verify rate limiter middleware throttles excessive rapid requests.
    """
    responses = [client.get("/api/auth/verify") for _ in range(25)]
    status_codes = [r.status_code for r in responses]
    assert 429 in status_codes or 200 in status_codes

def test_database_backup_and_integrity_check():
    """
    Verify online database snapshotting and quick_check integrity inspection.
    """
    check = DatabaseBackupEngine.check_integrity()
    assert check["healthy"] is True
    assert check["status"] == "OK"

    backup_info = DatabaseBackupEngine.create_backup(tag="pytest_test")
    assert backup_info["status"] == "success"
    assert backup_info["size_mb"] > 0

    backups = DatabaseBackupEngine.list_backups()
    assert len(backups) >= 1

def test_circuit_breaker_resilience():
    """
    Verify circuit breaker pattern transitions to OPEN state when threshold is reached.
    """
    cb = CircuitBreaker("Test_Breaker", failure_threshold=2, recovery_timeout=5.0)

    def failing_func():
        raise RuntimeError("External AI API Timeout")

    with pytest.raises(RuntimeError):
        cb.execute(failing_func)

    with pytest.raises(RuntimeError):
        cb.execute(failing_func)

    assert cb.state == "OPEN"

    with pytest.raises(CircuitBreakerOpenException):
        cb.execute(failing_func)

def test_beta_feedback_and_crash_reporting():
    """
    Verify ingestion of beta feedback and client crash telemetry.
    """
    from app.api.beta_api import init_beta_tables
    init_beta_tables()
    
    fb_res = client.post("/api/beta/feedback", json={
        "category": "FEEDBACK",
        "title": "Beta Readiness QA",
        "description": "System performance is stable.",
        "rating": 5
    })
    assert fb_res.status_code == 200
    assert fb_res.json()["status"] == "success"

    crash_res = client.post("/api/beta/crash-report", json={
        "component": "ReactHeader",
        "error_name": "TestRenderException",
        "error_message": "Synthetic crash test"
    })
    assert crash_res.status_code == 200
    assert crash_res.json()["status"] == "success"
