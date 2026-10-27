"""
Saarthi Ops Subsystem Security and Diagnostic Verification Test Suite.
Verifies read-only monitoring, RBAC, secret redaction, input validation,
non-execution guarantees, and shared VPS protection boundaries.
"""

import os
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.config.settings import settings
from app.ops.config import ALLOWED_OPS_SERVICES, MAX_ERROR_LOGS_LIMIT
from app.ops.redactor import ops_redactor
from app.ops.collector import ops_collector
from app.ops.diagnostics import ops_diagnostic_engine, DISCLAIMER_TEXT
from app.tools.registry import ToolRegistry

client = TestClient(app)

VALID_TEST_ADMIN_KEY = "test_ops_secure_admin_key_2026_audit"

@pytest.fixture(autouse=True)
def setup_ops_env(monkeypatch):
    """Configures clean test environment with a valid, non-placeholder admin key."""
    monkeypatch.setenv("VENDOR_ADMIN_KEY", VALID_TEST_ADMIN_KEY)
    monkeypatch.setenv("ADMIN_SECRET_KEY", VALID_TEST_ADMIN_KEY)
    monkeypatch.setattr(settings, "VENDOR_ADMIN_KEY", VALID_TEST_ADMIN_KEY)
    monkeypatch.setattr(settings, "ADMIN_SECRET_KEY", VALID_TEST_ADMIN_KEY)

# ==============================================================================
# 1. AUTHENTICATION & ACCESS CONTROL TESTS
# ==============================================================================

def test_ops_endpoints_require_authentication():
    """All Ops monitoring endpoints must reject unauthenticated requests."""
    endpoints = [
        "/api/ops/health",
        "/api/ops/metrics",
        "/api/ops/services",
        "/api/ops/services/saarthi-backend",
        "/api/ops/errors",
        "/api/ops/containers",
        "/api/ops/snapshots",
        "/api/ops/incidents",
        "/api/ops/audit",
    ]
    for ep in endpoints:
        resp = client.get(ep)
        assert resp.status_code in (401, 403), f"Endpoint {ep} allowed unauthenticated access!"

def test_ops_endpoints_reject_invalid_and_placeholder_keys():
    """Ops endpoints must reject invalid, empty, or placeholder keys."""
    invalid_keys = [
        "wrong_admin_key",
        "dev_admin_key",
        "admin",
        "changeme",
        "saarthi_admin_secret_key_2026",
    ]
    for key in invalid_keys:
        headers = {"X-Admin-Key": key}
        resp = client.get("/api/ops/health", headers=headers)
        assert resp.status_code in (401, 403), f"Key '{key}' was incorrectly accepted!"

def test_ops_endpoints_allow_valid_admin_key():
    """Valid configured admin key must succeed on read endpoints."""
    headers = {"X-Admin-Key": VALID_TEST_ADMIN_KEY}
    resp = client.get("/api/ops/health", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert "services_count" in data

# ==============================================================================
# 2. RBAC & ROLE BOUNDARY TESTS
# ==============================================================================

def test_ops_analyst_role_has_read_access_but_not_diagnose():
    """
    ANALYST role can read monitoring data, but cannot trigger AI diagnostics.
    """
    from app.admin.repositories.admin_repository import AdminRepository
    from app.admin.auth.admin_auth import hash_password

    # Create analyst user
    analyst_email = "analyst_ops_test@saarthi.local"
    try:
        admin_rec = AdminRepository.create_admin_user(
            email=analyst_email,
            password_hash=hash_password("AnalystPass123!"),
            role="ANALYST",
            full_name="Ops Analyst"
        )
    except Exception:
        admin_rec = AdminRepository.get_admin_by_email(analyst_email)

    session = AdminRepository.create_session(admin_rec["admin_id"])
    analyst_headers = {"Authorization": f"Bearer {session['session_token']}"}

    # Read access must succeed
    read_resp = client.get("/api/ops/health", headers=analyst_headers)
    assert read_resp.status_code == 200

    metrics_resp = client.get("/api/ops/metrics", headers=analyst_headers)
    assert metrics_resp.status_code == 200

    # Diagnose endpoint requires SUPER_ADMIN or ADMIN -> ANALYST must receive 403
    diag_resp = client.post("/api/ops/diagnose", json={}, headers=analyst_headers)
    assert diag_resp.status_code == 403
    assert "not authorized" in diag_resp.json()["detail"].lower()

# ==============================================================================
# 3. SERVICE ALLOWLIST & PATH TRAVERSAL REJECTION
# ==============================================================================

def test_ops_service_allowlist_enforcement():
    """Probing allowlisted services succeeds; non-allowlisted services are rejected with 400."""
    headers = {"X-Admin-Key": VALID_TEST_ADMIN_KEY}

    # Permitted services
    for s_id in ALLOWED_OPS_SERVICES:
        resp = client.get(f"/api/ops/services/{s_id}", headers=headers)
        assert resp.status_code == 200, f"Allowed service {s_id} returned {resp.status_code}"
        data = resp.json()
        assert data["service_id"] == s_id

    # Forbidden / Unrelated services (such as co-located MKS ERP)
    forbidden_services = [
        "mks_erp",
        "mks-erp",
        "mks_db",
        "mks_backend",
        "../../etc/passwd",
        "docker_daemon",
        "nginx_root"
    ]
    for bad_service in forbidden_services:
        resp = client.get(f"/api/ops/services/{bad_service}", headers=headers)
        assert resp.status_code in (400, 404), f"Forbidden service '{bad_service}' was not rejected!"
        if resp.status_code == 400:
            assert "not an allowlisted" in resp.json()["detail"].lower() or "not in the permitted" in resp.json()["detail"].lower()

# ==============================================================================
# 4. SECRET & CREDENTIAL REDACTION TESTS
# ==============================================================================

def test_secret_redactor_patterns():
    """Verify regex patterns purge passwords, tokens, SSH keys, and paths."""
    raw_texts = [
        ("Database error: postgresql://postgres_user:SuperSecretPassword123!@127.0.0.1:5432/saarthi",
         "postgresql://postgres_user:[REDACTED]@127.0.0.1:5432/saarthi"),
        ("Request header: Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.doNotLeakThis",
         "Authorization: [REDACTED]"),
        ("SSH Key detected: ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC3... root@host",
         "[REDACTED_SSH_KEY] root@host"),
        ("Query string: /api/webhook?admin_key=my_super_secret_admin_key_123",
         "/api/webhook?admin_key=[REDACTED]"),
    ]

    for raw, expected_substr in raw_texts:
        redacted = ops_redactor.redact_text(raw)
        assert "SuperSecretPassword123!" not in redacted
        assert "doNotLeakThis" not in redacted
        assert "my_super_secret_admin_key_123" not in redacted
        assert "[REDACTED" in redacted

def test_error_buffer_redacts_on_ingestion():
    """Error entries logged to Ops collector must be redacted before storage."""
    raw_error = "Connection failed to mysql://root:MyPrivateDbPass@localhost:3306/db with key sk-1234567890abcdef"
    entry = ops_collector.record_error(
        message=raw_error,
        level="ERROR",
        source="test.service",
        details={"api_key": "raw_leaked_key_999", "safe_param": "hello"}
    )

    assert "MyPrivateDbPass" not in entry["message"]
    assert "raw_leaked_key_999" not in str(entry["details"])
    assert entry["details"]["api_key"] == "[REDACTED]"
    assert entry["details"]["safe_param"] == "hello"

# ==============================================================================
# 5. LIMIT ENFORCEMENT & QUERY WINDOW TESTS
# ==============================================================================

def test_error_logs_and_audit_limits():
    """Error logs limit must be clamped or rejected by query bounds."""
    headers = {"X-Admin-Key": VALID_TEST_ADMIN_KEY}

    # Querying with valid limit succeeds
    resp = client.get("/api/ops/errors?limit=5", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) <= 5

    # Querying with excessive limit (> MAX_ERROR_LOGS_LIMIT) must be rejected by FastAPI validation
    resp_overflow = client.get(f"/api/ops/errors?limit={MAX_ERROR_LOGS_LIMIT + 50}", headers=headers)
    assert resp_overflow.status_code == 422, "Excessive query limit was not rejected with 422 Unprocessable Entity"

# ==============================================================================
# 6. STALE & UNAVAILABLE METRICS HANDLING
# ==============================================================================

def test_container_status_unavailable_in_local_mvp():
    """In local development mode without Docker, containers endpoint reports 'unavailable'."""
    headers = {"X-Admin-Key": VALID_TEST_ADMIN_KEY}
    resp = client.get("/api/ops/containers", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ("available", "unavailable")
    if not os.path.exists("/.dockerenv"):
        assert data["status"] == "unavailable"
        assert "not attached" in data["reason"].lower()

# ==============================================================================
# 7. AI DIAGNOSTIC ENGINE VERIFICATION (READ-ONLY, NO MUTATION)
# ==============================================================================

def test_diagnostic_engine_structured_output():
    """
    Diagnostics must produce structured output distinguishing facts from hypotheses,
    providing safe steps, and explicitly warning about shared VPS/MKS ERP impact.
    """
    headers = {"X-Admin-Key": VALID_TEST_ADMIN_KEY}
    resp = client.post("/api/ops/diagnose", json={}, headers=headers)
    assert resp.status_code == 200
    diag = resp.json()

    assert "problem_summary" in diag
    assert "facts" in diag and isinstance(diag["facts"], list)
    assert "hypotheses" in diag and isinstance(diag["hypotheses"], list)
    assert "evidence" in diag and isinstance(diag["evidence"], list)
    assert "missing_evidence" in diag and isinstance(diag["missing_evidence"], list)
    assert "confidence" in diag
    assert "safe_investigation_steps" in diag and isinstance(diag["safe_investigation_steps"], list)
    assert "shared_infrastructure_impact" in diag and isinstance(diag["shared_infrastructure_impact"], list)
    assert "recommendations_disclaimer" in diag
    assert "strictly read-only" in diag["recommendations_disclaimer"].lower()

def test_tool_registry_has_no_ops_execution_tools():
    """
    Verify that ToolRegistry has zero Ops-execution tools, zero shell tools,
    and zero container restart/stop tools.
    """
    registry = ToolRegistry()
    tools = registry.list_tools()
    for tool_name in tools:
        assert "docker" not in tool_name.lower(), f"Unsafe docker tool found in registry: {tool_name}"
        assert "shell" not in tool_name.lower(), f"Unsafe shell tool found in registry: {tool_name}"
        assert "restart" not in tool_name.lower(), f"Unsafe restart tool found in registry: {tool_name}"
        assert "stop" not in tool_name.lower(), f"Unsafe stop tool found in registry: {tool_name}"

# ==============================================================================
# 8. PHASE 2 DESIGN CORRECTION TESTS (TELEMETRY SCOPING, HMAC, FRESHNESS)
# ==============================================================================

def test_explicit_scoping_and_measurement_types():
    """
    Verify that telemetry fields are explicitly labeled with scope and measurement type.
    Confirms hardcoded latencies and fabricated container states are eliminated.
    """
    headers = {"X-Admin-Key": VALID_TEST_ADMIN_KEY}

    # 1. System metrics scoping
    metrics_resp = client.get("/api/ops/metrics", headers=headers)
    assert metrics_resp.status_code == 200
    m = metrics_resp.json()
    assert m["scope"] in ("host_and_process", "host")
    assert "measurement_type" in m
    assert m["ram"]["scope"] == "host"
    assert m["disk"]["scope"] == "host"

    # 2. Service checks scoping and unmeasured typing
    services_resp = client.get("/api/ops/services", headers=headers)
    assert services_resp.status_code == 200
    services = {s["service_id"]: s for s in services_resp.json()}

    # saarthi-backend is in-process
    assert services["saarthi-backend"]["measurement_type"] == "in_process"
    assert services["saarthi-backend"]["latency_ms"] is None

    # static assets (frontend/admin) are labeled unmeasured
    assert services["saarthi-frontend"]["measurement_type"] == "unmeasured"
    assert services["saarthi-frontend"]["status"] == "UNMEASURED"
    assert services["saarthi-frontend"]["latency_ms"] is None
    assert services["saarthi-frontend"]["is_verified"] is False

    assert services["saarthi-admin"]["measurement_type"] == "unmeasured"
    assert services["saarthi-admin"]["status"] == "UNMEASURED"
    assert services["saarthi-admin"]["latency_ms"] is None
    assert services["saarthi-admin"]["is_verified"] is False

    # saarthi-db is a live probe
    assert services["saarthi-db"]["measurement_type"] == "live_probe"
    assert services["saarthi-db"]["is_verified"] is True
    assert services["saarthi-db"]["latency_ms"] is not None

def test_unavailable_metrics_fail_closed_to_degraded(monkeypatch):
    """
    Unavailable hardware metrics must fail closed: overall health cannot be healthy.
    """
    monkeypatch.setattr(
        ops_collector,
        "get_system_metrics",
        lambda: {"status": "unavailable", "scope": "host", "reason": "Hardware probe failure"}
    )
    headers = {"X-Admin-Key": VALID_TEST_ADMIN_KEY}
    resp = client.get("/api/ops/health", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] != "healthy", "Unavailable metrics silently produced a healthy status!"
    assert data["status"] == "degraded"

def test_snapshot_hmac_authenticity_and_tamper_rejection():
    """
    Snapshot envelopes must be authenticated via HMAC-SHA256.
    Tampered payloads or invalid signatures must be rejected by the verify endpoint.
    """
    headers = {"X-Admin-Key": VALID_TEST_ADMIN_KEY}
    from app.ops.authenticity import snapshot_authenticity_service

    # Create signed snapshot
    test_payload = {"test_metric": 42, "snapshot_id": "test_snap_1"}
    envelope = snapshot_authenticity_service.sign_snapshot(test_payload, source_id="test-source")

    # Valid envelope passes verification
    resp_valid = client.post("/api/ops/snapshots/verify", json={"envelope": envelope}, headers=headers)
    assert resp_valid.status_code == 200
    assert resp_valid.json()["status"] == "verified"

    # Tampered envelope (altering payload) is rejected
    tampered_envelope = dict(envelope)
    tampered_envelope["payload"] = {"test_metric": 999, "snapshot_id": "test_snap_1"}
    resp_tampered = client.post("/api/ops/snapshots/verify", json={"envelope": tampered_envelope}, headers=headers)
    assert resp_tampered.status_code == 400
    assert "digest mismatch" in resp_tampered.json()["detail"].lower()

    # Tampered signature is rejected
    forged_envelope = dict(envelope)
    forged_envelope["signature"] = "0" * 64
    resp_forged = client.post("/api/ops/snapshots/verify", json={"envelope": forged_envelope}, headers=headers)
    assert resp_forged.status_code == 400
    assert "invalid envelope signature" in resp_forged.json()["detail"].lower()

def test_snapshot_freshness_policy_and_expiration():
    """
    Snapshots within 60s are fresh.
    Snapshots older than 180s are expired and rejected.
    """
    from datetime import datetime, timezone, timedelta
    from app.ops.authenticity import snapshot_authenticity_service

    now = datetime.now(timezone.utc)

    # 1. Fresh snapshot (< 60s)
    fresh_envelope = snapshot_authenticity_service.sign_snapshot({"test": "fresh"})
    is_valid, reason, meta = snapshot_authenticity_service.verify_envelope(fresh_envelope)
    assert is_valid is True
    assert meta["freshness"] == "fresh"
    assert meta["is_stale"] is False

    # 2. Expired snapshot (> 180s)
    expired_time = (now - timedelta(seconds=200)).isoformat()
    expired_envelope = snapshot_authenticity_service.sign_snapshot({"test": "expired"})
    expired_envelope["timestamp"] = expired_time
    # Re-sign to isolate the timestamp expiration check
    key = snapshot_authenticity_service.get_hmac_key()
    import hmac, json
    canonical_json = json.dumps(expired_envelope["payload"], sort_keys=True, separators=(',', ':'))
    payload_hmac = hmac.new(key, canonical_json.encode("utf-8"), "sha256").hexdigest()
    expired_envelope["payload_hmac"] = payload_hmac
    sig_mat = f"{expired_envelope['source_id']}:{expired_time}:{expired_envelope['nonce']}:{payload_hmac}".encode("utf-8")
    expired_envelope["signature"] = hmac.new(key, sig_mat, "sha256").hexdigest()

    is_valid_exp, reason_exp, meta_exp = snapshot_authenticity_service.verify_envelope(expired_envelope)
    assert is_valid_exp is False
    assert "expired" in reason_exp.lower()

def test_snapshot_future_timestamp_rejection():
    """Snapshots with future timestamps (> 15s ahead) must be rejected for clock skew / spoofing."""
    from datetime import datetime, timezone, timedelta
    import hmac, json
    from app.ops.authenticity import snapshot_authenticity_service

    now = datetime.now(timezone.utc)
    future_time = (now + timedelta(seconds=60)).isoformat()
    envelope = snapshot_authenticity_service.sign_snapshot({"test": "future"})
    envelope["timestamp"] = future_time

    key = snapshot_authenticity_service.get_hmac_key()
    canonical_json = json.dumps(envelope["payload"], sort_keys=True, separators=(',', ':'))
    payload_hmac = hmac.new(key, canonical_json.encode("utf-8"), "sha256").hexdigest()
    envelope["payload_hmac"] = payload_hmac
    sig_mat = f"{envelope['source_id']}:{future_time}:{envelope['nonce']}:{payload_hmac}".encode("utf-8")
    envelope["signature"] = hmac.new(key, sig_mat, "sha256").hexdigest()

    is_valid, reason, meta = snapshot_authenticity_service.verify_envelope(envelope)
    assert is_valid is False
    assert "future timestamp" in reason.lower()

def test_snapshot_replay_attack_prevention():
    """Submitting the exact same snapshot envelope twice within the window must be rejected as a replay."""
    from app.ops.authenticity import snapshot_authenticity_service

    envelope = snapshot_authenticity_service.sign_snapshot({"test": "replay_check"})
    # First verification succeeds
    is_valid_1, _, _ = snapshot_authenticity_service.verify_envelope(envelope)
    assert is_valid_1 is True

    # Immediate second verification with same nonce fails
    is_valid_2, reason_2, _ = snapshot_authenticity_service.verify_envelope(envelope)
    assert is_valid_2 is False
    assert "replay attack detected" in reason_2.lower()

def test_untrusted_snapshot_rejected_in_diagnosis():
    """Diagnose endpoint must reject forged or unverified snapshot envelopes."""
    headers = {"X-Admin-Key": VALID_TEST_ADMIN_KEY}

    forged_envelope = {
        "version": "1.0",
        "source_id": "malicious-source",
        "timestamp": "2026-10-19T14:00:00Z",
        "nonce": "fake_nonce",
        "payload_hmac": "fake_hmac",
        "signature": "fake_signature",
        "payload": {"fake": "state"}
    }

    resp = client.post(
        "/api/ops/diagnose",
        json={"snapshot_envelope": forged_envelope},
        headers=headers
    )
    assert resp.status_code == 400
    assert "untrusted snapshot rejected" in resp.json()["detail"].lower()

def test_api_health_endpoint_schema_contract():
    """
    Verify exact contract of /api/health:
    Returns status: 'healthy' | 'degraded', not string 'ok'.
    """
    resp = client.get("/api/health")
    assert resp.status_code in (200, 503)
    data = resp.json()
    assert "status" in data
    assert data["status"] in ("healthy", "degraded")
    assert "checks" in data
    assert "database" in data["checks"]
    assert "service" in data

def test_ed25519_asymmetric_signing_and_verification(monkeypatch, tmp_path):
    """
    Verify Ed25519 asymmetric signing:
    Collector signs with private key; backend verifies with public key only.
    """
    from app.ops.authenticity import SnapshotAuthenticityService, ReplayProtectionStore
    
    priv_hex, pub_hex = SnapshotAuthenticityService.generate_ed25519_keypair()
    monkeypatch.setenv("OPS_SNAPSHOT_SIGNING_KEY", priv_hex)
    monkeypatch.setenv("OPS_SNAPSHOT_VERIFY_KEY", pub_hex)
    
    store = ReplayProtectionStore(db_path=str(tmp_path / "replay_test.db"))
    svc = SnapshotAuthenticityService(replay_store=store)
    
    payload = {"service": "saarthi-backend", "status": "ONLINE", "healthy": True}
    envelope = svc.sign_snapshot(payload, source_id="saarthi-ops-collector", algorithm="ed25519")
    
    assert envelope["algorithm"] == "ed25519"
    assert envelope["version"] == "2.0"
    assert "payload_hash" in envelope
    
    is_valid, reason, meta = svc.verify_envelope(envelope)
    assert is_valid is True
    assert "verified authentic" in reason.lower()
    assert meta["algorithm"] == "ed25519"

def test_ed25519_wrong_key_rejection(monkeypatch, tmp_path):
    """Sign with private key A; attempt verification with unrelated public key B -> must fail."""
    from app.ops.authenticity import SnapshotAuthenticityService, ReplayProtectionStore
    
    priv_a, _ = SnapshotAuthenticityService.generate_ed25519_keypair()
    _, pub_b = SnapshotAuthenticityService.generate_ed25519_keypair()
    
    monkeypatch.setenv("OPS_SNAPSHOT_SIGNING_KEY", priv_a)
    monkeypatch.setenv("OPS_SNAPSHOT_VERIFY_KEY", pub_b)
    
    store = ReplayProtectionStore(db_path=str(tmp_path / "replay_test_wrong_key.db"))
    svc = SnapshotAuthenticityService(replay_store=store)
    
    envelope = svc.sign_snapshot({"test": "data"}, algorithm="ed25519")
    is_valid, reason, _ = svc.verify_envelope(envelope)
    assert is_valid is False
    assert "cryptographic authenticity check failed" in reason.lower()

def test_ed25519_tampered_payload_and_metadata_rejection(monkeypatch, tmp_path):
    """Altering payload or any metadata element in an Ed25519 envelope must fail verification."""
    from app.ops.authenticity import SnapshotAuthenticityService, ReplayProtectionStore
    
    priv_hex, pub_hex = SnapshotAuthenticityService.generate_ed25519_keypair()
    monkeypatch.setenv("OPS_SNAPSHOT_SIGNING_KEY", priv_hex)
    monkeypatch.setenv("OPS_SNAPSHOT_VERIFY_KEY", pub_hex)
    
    store = ReplayProtectionStore(db_path=str(tmp_path / "replay_test_tamper.db"))
    svc = SnapshotAuthenticityService(replay_store=store)
    
    # 1. Tamper payload content
    env1 = svc.sign_snapshot({"original": "clean"}, algorithm="ed25519")
    env1["payload"]["original"] = "tampered"
    is_valid1, reason1, _ = svc.verify_envelope(env1)
    assert is_valid1 is False
    assert "payload hash mismatch" in reason1.lower()
    
    # 2. Tamper source_id
    env2 = svc.sign_snapshot({"original": "clean"}, algorithm="ed25519")
    env2["source_id"] = "forged-collector-id"
    is_valid2, reason2, _ = svc.verify_envelope(env2)
    assert is_valid2 is False
    assert "authenticity check failed" in reason2.lower()
    
    # 3. Tamper signature bytes
    env3 = svc.sign_snapshot({"original": "clean"}, algorithm="ed25519")
    env3["signature"] = "a" * 128
    is_valid3, reason3, _ = svc.verify_envelope(env3)
    assert is_valid3 is False
    assert "authenticity check failed" in reason3.lower()

def test_concurrent_replay_prevention(monkeypatch, tmp_path):
    """Multiple concurrent worker threads attempting to submit identical envelope -> exactly 1 succeeds."""
    import concurrent.futures
    from app.ops.authenticity import SnapshotAuthenticityService, ReplayProtectionStore
    
    store = ReplayProtectionStore(db_path=str(tmp_path / "replay_concurrent.db"))
    svc = SnapshotAuthenticityService(replay_store=store)
    
    envelope = svc.sign_snapshot({"concurrency": "test"})
    
    results = []
    def attempt_verify():
        valid, reason, _ = svc.verify_envelope(envelope)
        return valid, reason
        
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(attempt_verify) for _ in range(8)]
        for f in concurrent.futures.as_completed(futures):
            results.append(f.result())
            
    successes = [r for r in results if r[0] is True]
    replays = [r for r in results if r[0] is False and "replay attack detected" in r[1].lower()]
    
    assert len(successes) == 1, f"Expected exactly 1 success, got {len(successes)}"
    assert len(replays) == 7, f"Expected 7 replays prevented, got {len(replays)}"

def test_backend_restart_replay_persistence(tmp_path):
    """Consuming a nonce in process 1 persists across backend restart (new instance, same db)."""
    from app.ops.authenticity import SnapshotAuthenticityService, ReplayProtectionStore
    
    db_file = str(tmp_path / "persistent_replay.db")
    
    # Backend instance 1
    store1 = ReplayProtectionStore(db_path=db_file)
    svc1 = SnapshotAuthenticityService(replay_store=store1)
    envelope = svc1.sign_snapshot({"restart": "test"})
    
    is_valid1, _, _ = svc1.verify_envelope(envelope)
    assert is_valid1 is True
    
    # Simulate backend reboot / restart by creating instance 2 attached to same persistent store
    store2 = ReplayProtectionStore(db_path=db_file)
    svc2 = SnapshotAuthenticityService(replay_store=store2)
    
    # Instance 2 must immediately reject envelope as replayed
    is_valid2, reason2, _ = svc2.verify_envelope(envelope)
    assert is_valid2 is False
    assert "replay attack detected" in reason2.lower()

def test_out_of_order_snapshot_rejection(tmp_path):
    """Older snapshot arriving after a newer snapshot must be rejected to prevent masking outages."""
    from datetime import datetime, timezone, timedelta
    from app.ops.authenticity import SnapshotAuthenticityService, ReplayProtectionStore
    
    store = ReplayProtectionStore(db_path=str(tmp_path / "out_of_order.db"))
    svc = SnapshotAuthenticityService(replay_store=store)
    
    # Snapshot 1 at current time
    env1 = svc.sign_snapshot({"status": "OFFLINE"})
    is_valid1, _, _ = svc.verify_envelope(env1)
    assert is_valid1 is True
    
    # Snapshot 2 crafted with an older timestamp (e.g. 25s earlier when service was 'healthy')
    now = datetime.now(timezone.utc)
    old_time = (now - timedelta(seconds=25)).isoformat()
    env2 = svc.sign_snapshot({"status": "ONLINE"})
    env2["timestamp"] = old_time
    
    # Re-sign with old timestamp so crypto is valid
    key = svc.get_hmac_key()
    import hmac, json
    c_json = json.dumps(env2["payload"], sort_keys=True, separators=(',', ':'))
    p_hmac = hmac.new(key, c_json.encode("utf-8"), "sha256").hexdigest()
    env2["payload_hmac"] = p_hmac
    sig_mat = f"{env2['source_id']}:{old_time}:{env2['nonce']}:{p_hmac}".encode("utf-8")
    env2["signature"] = hmac.new(key, sig_mat, "sha256").hexdigest()
    
    is_valid2, reason2, meta2 = svc.verify_envelope(env2)
    assert is_valid2 is False
    assert "out-of-order replay detected" in reason2.lower()

def test_oversized_payload_rejection():
    """Payloads exceeding MAX_SNAPSHOT_PAYLOAD_BYTES (64 KB) must fail closed."""
    from app.ops.authenticity import snapshot_authenticity_service, MAX_SNAPSHOT_PAYLOAD_BYTES
    import pytest
    
    huge_payload = {"junk": "x" * (MAX_SNAPSHOT_PAYLOAD_BYTES + 1024)}
    
    # Signing throws ValueError
    with pytest.raises(ValueError, match="exceeds maximum size limit"):
        snapshot_authenticity_service.sign_snapshot(huge_payload)
        
    # Verifying a forged oversized envelope fails closed
    oversized_env = {
        "version": "1.0",
        "source_id": "attacker",
        "timestamp": "2026-10-19T14:00:00Z",
        "nonce": "test_nonce",
        "payload_hmac": "fake",
        "signature": "fake",
        "payload": huge_payload
    }
    is_valid, reason, _ = snapshot_authenticity_service.verify_envelope(oversized_env)
    assert is_valid is False
    assert "oversized" in reason.lower()

def test_saarthi_collector_mks_isolation(monkeypatch):
    """
    Test host collector container filtering:
    Saarthi containers are captured; MKS ERP containers and foreign workloads are dropped.
    """
    import sys, os
    workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    if workspace_root not in sys.path:
        sys.path.insert(0, workspace_root)

    from deploy.collector.saarthi_collector import collect_allowlisted_containers
    
    # Simulated Docker engine /containers/json response containing both Saarthi & MKS ERP
    mock_docker_containers = [
        {"Names": ["/saarthi-staging-backend"], "State": "running", "Status": "Up 2 hours (healthy)", "Created": 1700000000},
        {"Names": ["/saarthi-staging-db"], "State": "running", "Status": "Up 2 hours (healthy)", "Created": 1700000000},
        {"Names": ["/mks-erp-web"], "State": "running", "Status": "Up 30 days", "Created": 1690000000},
        {"Names": ["/mks-erp-postgres"], "State": "running", "Status": "Up 30 days", "Created": 1690000000},
        {"Names": ["/host-monitoring-daemon"], "State": "running", "Status": "Up 50 days", "Created": 1680000000}
    ]
    
    monkeypatch.setattr("deploy.collector.saarthi_collector.query_docker_unix_socket", lambda _: mock_docker_containers)
    
    result = collect_allowlisted_containers()
    captured_names = [c["name"] for c in result]
    
    # Only Saarthi containers must be returned
    assert "saarthi-staging-backend" in captured_names
    assert "saarthi-staging-db" in captured_names
    
    # MKS ERP and host daemons must NEVER be present
    assert "mks-erp-web" not in captured_names
    assert "mks-erp-postgres" not in captured_names
    assert "host-monitoring-daemon" not in captured_names
    assert len(captured_names) == 2

def test_metric_scoping_and_cgroup_awareness():
    """Verify collector inspects cgroup and scopes metrics conservatively."""
    from app.ops.collector import ops_collector
    
    metrics = ops_collector.get_system_metrics()
    assert "scope" in metrics
    assert "cpu" in metrics
    assert "ram" in metrics
    assert "disk" in metrics
    assert "is_containerized" in metrics
    assert "scope" in metrics["ram"]
    assert "scope" in metrics["disk"]

# ==============================================================================
# 10. END-TO-END OPS INGESTION, REPLAY, CONCURRENCY & PERSISTENCE TESTS
# ==============================================================================

def test_ops_e2e_collector_to_dashboard_and_diagnostics(monkeypatch, tmp_path):
    """
    Complete E2E Path:
    Signed collector fixture -> Authenticated ingestion -> Persistent trusted snapshot ->
    Dashboard reads (/containers, /health) -> AI Diagnostics.
    """
    import json
    from datetime import datetime, timezone
    from app.ops.authenticity import SnapshotAuthenticityService, ReplayProtectionStore
    from app.ops.collector import OpsCollector

    priv_hex, pub_hex = SnapshotAuthenticityService.generate_ed25519_keypair()
    monkeypatch.setenv("OPS_SNAPSHOT_SIGNING_KEY", priv_hex)
    monkeypatch.setenv("OPS_SNAPSHOT_VERIFY_KEY", pub_hex)

    db_path = str(tmp_path / "e2e_replay.db")
    snap_path = str(tmp_path / "live_snapshot.json")
    monkeypatch.setenv("SAARTHI_HOST_SNAPSHOT_FILE", snap_path)

    store = ReplayProtectionStore(db_path=db_path)
    auth_svc = SnapshotAuthenticityService(replay_store=store)
    monkeypatch.setattr("app.ops.collector.snapshot_authenticity_service", auth_svc)

    collector = OpsCollector()
    monkeypatch.setattr("app.ops.router.ops_collector", collector)

    # 1. Collector fixture: create and sign host snapshot
    fixture_payload = {
        "host": {"status": "available", "cpu": {"percent_used": 15.0}},
        "containers": [
            {"name": "saarthi-staging-backend", "status": "Up 2 hours (healthy)", "state": "running"},
            {"name": "saarthi-staging-db", "status": "Up 2 hours (healthy)", "state": "running"}
        ],
        "generated_at": datetime.now(timezone.utc).isoformat()
    }
    envelope = auth_svc.sign_snapshot(fixture_payload, source_id="saarthi-ops-collector", algorithm="ed25519")

    with open(snap_path, "w", encoding="utf-8") as f:
        json.dump(envelope, f)

    # 2. Ingest via dashboard read: First read verifies & persists
    headers = {"X-Admin-Key": VALID_TEST_ADMIN_KEY}
    resp1 = client.get("/api/ops/containers", headers=headers)
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert data1["status"] == "available"
    assert data1["source"] == "host_collector"
    assert len(data1["containers"]) == 2
    assert data1["freshness"] == "fresh"

    # 3. Repeated GET reads: Must NOT trigger replay rejection
    for _ in range(5):
        resp_repeat = client.get("/api/ops/containers", headers=headers)
        assert resp_repeat.status_code == 200
        assert resp_repeat.json()["status"] == "available"
        assert len(resp_repeat.json()["containers"]) == 2

    # 4. Ops Health read: includes verified collector telemetry
    resp_health = client.get("/api/ops/health", headers=headers)
    assert resp_health.status_code == 200
    assert resp_health.json()["status"] in ("healthy", "degraded")

    # 5. AI Diagnostics: Analyzes trusted telemetry without mutation
    resp_diag = client.post("/api/ops/diagnose", json={}, headers=headers)
    assert resp_diag.status_code == 200
    diag = resp_diag.json()
    assert "facts" in diag
    assert "hypotheses" in diag
    assert "recommendations_disclaimer" in diag


def test_ops_concurrent_dashboard_and_diagnostic_reads(monkeypatch, tmp_path):
    """
    Multiple concurrent API requests (containers, health, diagnose) reading the same
    verified snapshot must all succeed without replay collision.
    """
    import json
    import concurrent.futures
    from app.ops.authenticity import SnapshotAuthenticityService, ReplayProtectionStore
    from app.ops.collector import OpsCollector

    priv_hex, pub_hex = SnapshotAuthenticityService.generate_ed25519_keypair()
    monkeypatch.setenv("OPS_SNAPSHOT_SIGNING_KEY", priv_hex)
    monkeypatch.setenv("OPS_SNAPSHOT_VERIFY_KEY", pub_hex)

    db_path = str(tmp_path / "concurrent_ops.db")
    snap_path = str(tmp_path / "live_snapshot.json")
    monkeypatch.setenv("SAARTHI_HOST_SNAPSHOT_FILE", snap_path)

    store = ReplayProtectionStore(db_path=db_path)
    auth_svc = SnapshotAuthenticityService(replay_store=store)
    monkeypatch.setattr("app.ops.collector.snapshot_authenticity_service", auth_svc)

    collector = OpsCollector()
    monkeypatch.setattr("app.ops.router.ops_collector", collector)

    envelope = auth_svc.sign_snapshot({
        "containers": [{"name": "saarthi-staging-backend", "status": "healthy", "state": "running"}]
    }, source_id="saarthi-ops-collector", algorithm="ed25519")

    with open(snap_path, "w", encoding="utf-8") as f:
        json.dump(envelope, f)

    headers = {"X-Admin-Key": VALID_TEST_ADMIN_KEY}

    def read_containers():
        return client.get("/api/ops/containers", headers=headers)

    def read_health():
        return client.get("/api/ops/health", headers=headers)

    def read_diagnose():
        return client.post("/api/ops/diagnose", json={}, headers=headers)

    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        f_containers = [executor.submit(read_containers) for _ in range(8)]
        f_health = [executor.submit(read_health) for _ in range(4)]
        f_diag = [executor.submit(read_diagnose) for _ in range(4)]

        for f in concurrent.futures.as_completed(f_containers + f_health + f_diag):
            resp = f.result()
            assert resp.status_code == 200, f"Concurrent request failed: {resp.text}"


def test_ops_duplicate_delivery_and_replay_rejection(monkeypatch, tmp_path):
    """
    Duplicate delivery of the exact same snapshot envelope to POST /api/ops/snapshots/verify
    must accept the first and reject the second with HTTP 400 (replay attack detected).
    """
    from app.ops.authenticity import SnapshotAuthenticityService, ReplayProtectionStore
    from app.ops.collector import OpsCollector

    priv_hex, pub_hex = SnapshotAuthenticityService.generate_ed25519_keypair()
    monkeypatch.setenv("OPS_SNAPSHOT_SIGNING_KEY", priv_hex)
    monkeypatch.setenv("OPS_SNAPSHOT_VERIFY_KEY", pub_hex)

    store = ReplayProtectionStore(db_path=str(tmp_path / "dup_replay.db"))
    auth_svc = SnapshotAuthenticityService(replay_store=store)
    monkeypatch.setattr("app.ops.router.snapshot_authenticity_service", auth_svc)
    monkeypatch.setattr("app.ops.collector.snapshot_authenticity_service", auth_svc)

    collector = OpsCollector()
    monkeypatch.setattr("app.ops.router.ops_collector", collector)

    envelope = auth_svc.sign_snapshot({"test": "duplicate_check"}, algorithm="ed25519")
    headers = {"X-Admin-Key": VALID_TEST_ADMIN_KEY}

    # First delivery: verified and ingested
    resp1 = client.post("/api/ops/snapshots/verify", json={"envelope": envelope}, headers=headers)
    assert resp1.status_code == 200
    assert resp1.json()["status"] == "verified"

    # Second delivery of duplicate envelope: must fail closed with 400 replay error
    resp2 = client.post("/api/ops/snapshots/verify", json={"envelope": envelope}, headers=headers)
    assert resp2.status_code == 400
    assert "replay attack detected" in resp2.json()["detail"].lower()


def test_ops_backend_restart_and_persistence(monkeypatch, tmp_path):
    """
    Backend restart simulation:
    - Snapshot ingested in process 1
    - Process 2 boots up attached to the same persistent store
    - Dashboard reads in process 2 serve the verified snapshot without replay error
    - Re-delivery of old envelope to process 2 is rejected
    """
    import json
    from app.ops.authenticity import SnapshotAuthenticityService, ReplayProtectionStore
    from app.ops.collector import OpsCollector

    priv_hex, pub_hex = SnapshotAuthenticityService.generate_ed25519_keypair()
    monkeypatch.setenv("OPS_SNAPSHOT_SIGNING_KEY", priv_hex)
    monkeypatch.setenv("OPS_SNAPSHOT_VERIFY_KEY", pub_hex)

    db_path = str(tmp_path / "restart_test.db")
    snap_path = str(tmp_path / "live_snapshot.json")
    monkeypatch.setenv("SAARTHI_HOST_SNAPSHOT_FILE", snap_path)

    # 1. Process 1: Ingest snapshot
    store1 = ReplayProtectionStore(db_path=db_path)
    auth1 = SnapshotAuthenticityService(replay_store=store1)
    monkeypatch.setattr("app.ops.collector.snapshot_authenticity_service", auth1)
    monkeypatch.setattr("app.ops.router.snapshot_authenticity_service", auth1)

    collector1 = OpsCollector()
    monkeypatch.setattr("app.ops.router.ops_collector", collector1)

    envelope = auth1.sign_snapshot({
        "containers": [{"name": "saarthi-staging-backend", "status": "healthy", "state": "running"}]
    }, algorithm="ed25519")

    with open(snap_path, "w", encoding="utf-8") as f:
        json.dump(envelope, f)

    headers = {"X-Admin-Key": VALID_TEST_ADMIN_KEY}
    resp1 = client.get("/api/ops/containers", headers=headers)
    assert resp1.status_code == 200
    assert len(resp1.json()["containers"]) == 1

    # 2. Simulate Backend Restart (Instance 2 attached to same persistent store)
    store2 = ReplayProtectionStore(db_path=db_path)
    auth2 = SnapshotAuthenticityService(replay_store=store2)
    monkeypatch.setattr("app.ops.collector.snapshot_authenticity_service", auth2)
    monkeypatch.setattr("app.ops.router.snapshot_authenticity_service", auth2)

    collector2 = OpsCollector()
    monkeypatch.setattr("app.ops.router.ops_collector", collector2)

    # Reading containers on restarted backend must succeed (recognized as already-accepted)
    resp2 = client.get("/api/ops/containers", headers=headers)
    assert resp2.status_code == 200
    assert len(resp2.json()["containers"]) == 1

    # Submitting same envelope via API to restarted backend is rejected as replayed
    resp_replayed = client.post("/api/ops/snapshots/verify", json={"envelope": envelope}, headers=headers)
    assert resp_replayed.status_code == 400
    assert "replay attack detected" in resp_replayed.json()["detail"].lower()


def test_ops_collector_update_replaces_state(monkeypatch, tmp_path):
    """
    Collector update:
    When the collector writes a newer snapshot, backend ingests it and dashboard serves the updated state.
    """
    import json
    import time
    from app.ops.authenticity import SnapshotAuthenticityService, ReplayProtectionStore
    from app.ops.collector import OpsCollector

    priv_hex, pub_hex = SnapshotAuthenticityService.generate_ed25519_keypair()
    monkeypatch.setenv("OPS_SNAPSHOT_SIGNING_KEY", priv_hex)
    monkeypatch.setenv("OPS_SNAPSHOT_VERIFY_KEY", pub_hex)

    db_path = str(tmp_path / "update_test.db")
    snap_path = str(tmp_path / "live_snapshot.json")
    monkeypatch.setenv("SAARTHI_HOST_SNAPSHOT_FILE", snap_path)

    store = ReplayProtectionStore(db_path=db_path)
    auth = SnapshotAuthenticityService(replay_store=store)
    monkeypatch.setattr("app.ops.collector.snapshot_authenticity_service", auth)
    monkeypatch.setattr("app.ops.router.snapshot_authenticity_service", auth)

    collector = OpsCollector()
    monkeypatch.setattr("app.ops.router.ops_collector", collector)

    # Snapshot 1: 1 container
    env1 = auth.sign_snapshot({
        "containers": [{"name": "saarthi-staging-backend", "status": "healthy", "state": "running"}]
    }, algorithm="ed25519")
    with open(snap_path, "w", encoding="utf-8") as f:
        json.dump(env1, f)

    headers = {"X-Admin-Key": VALID_TEST_ADMIN_KEY}
    resp1 = client.get("/api/ops/containers", headers=headers)
    assert resp1.status_code == 200
    assert len(resp1.json()["containers"]) == 1

    # Snapshot 2 (newer timestamp): 2 containers
    time.sleep(0.05)
    env2 = auth.sign_snapshot({
        "containers": [
            {"name": "saarthi-staging-backend", "status": "healthy", "state": "running"},
            {"name": "saarthi-staging-db", "status": "healthy", "state": "running"}
        ]
    }, algorithm="ed25519")
    with open(snap_path, "w", encoding="utf-8") as f:
        json.dump(env2, f)

    # Dashboard read picks up the new snapshot
    resp2 = client.get("/api/ops/containers", headers=headers)
    assert resp2.status_code == 200
    assert len(resp2.json()["containers"]) == 2


def test_ops_rollback_to_older_snapshot_rejected(monkeypatch, tmp_path):
    """
    Rollback / downgrade attack:
    An older snapshot cannot overwrite newer accepted state.
    """
    import json
    import hashlib
    from datetime import datetime, timezone, timedelta
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from app.ops.authenticity import SnapshotAuthenticityService, ReplayProtectionStore
    from app.ops.collector import OpsCollector

    priv_hex, pub_hex = SnapshotAuthenticityService.generate_ed25519_keypair()
    monkeypatch.setenv("OPS_SNAPSHOT_SIGNING_KEY", priv_hex)
    monkeypatch.setenv("OPS_SNAPSHOT_VERIFY_KEY", pub_hex)

    db_path = str(tmp_path / "rollback_test.db")
    snap_path = str(tmp_path / "live_snapshot.json")
    monkeypatch.setenv("SAARTHI_HOST_SNAPSHOT_FILE", snap_path)

    store = ReplayProtectionStore(db_path=db_path)
    auth = SnapshotAuthenticityService(replay_store=store)
    monkeypatch.setattr("app.ops.collector.snapshot_authenticity_service", auth)
    monkeypatch.setattr("app.ops.router.snapshot_authenticity_service", auth)

    collector = OpsCollector()
    monkeypatch.setattr("app.ops.router.ops_collector", collector)

    # 1. Accepted newer snapshot
    now = datetime.now(timezone.utc)
    env_new = auth.sign_snapshot({
        "containers": [
            {"name": "saarthi-staging-backend", "status": "unhealthy", "state": "failing"}
        ]
    }, algorithm="ed25519")
    with open(snap_path, "w", encoding="utf-8") as f:
        json.dump(env_new, f)

    headers = {"X-Admin-Key": VALID_TEST_ADMIN_KEY}
    resp_new = client.get("/api/ops/containers", headers=headers)
    assert resp_new.status_code == 200
    assert resp_new.json()["containers"][0]["status"] == "unhealthy"

    # 2. Craft older snapshot (20s earlier) claiming everything is "healthy"
    priv_key = ed25519.Ed25519PrivateKey.from_private_bytes(bytes.fromhex(priv_hex))
    old_time = (now - timedelta(seconds=20)).isoformat()
    old_nonce = "old_nonce_12345"
    old_payload = {
        "containers": [
            {"name": "saarthi-staging-backend", "status": "healthy", "state": "running"}
        ]
    }
    canonical_json = json.dumps(old_payload, sort_keys=True, separators=(',', ':'))
    payload_hash = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
    sig_mat = f"ed25519:saarthi-ops-collector:{old_time}:{old_nonce}:{payload_hash}".encode("utf-8")
    sig_hex = priv_key.sign(sig_mat).hex()

    env_old = {
        "version": "2.0",
        "algorithm": "ed25519",
        "source_id": "saarthi-ops-collector",
        "timestamp": old_time,
        "nonce": old_nonce,
        "payload_hash": payload_hash,
        "signature": sig_hex,
        "payload": old_payload
    }

    # Replace file with old snapshot
    with open(snap_path, "w", encoding="utf-8") as f:
        json.dump(env_old, f)

    # Dashboard read must REJECT the older snapshot and preserve newer "unhealthy" state
    resp_check = client.get("/api/ops/containers", headers=headers)
    assert resp_check.status_code == 200
    assert resp_check.json()["containers"][0]["status"] == "unhealthy"


def test_ops_missing_and_malformed_collector_file_safety(monkeypatch, tmp_path):
    """
    Missing or malformed collector files fail safely without crashing.
    """
    from app.ops.collector import OpsCollector

    # 1. Missing file
    missing_path = str(tmp_path / "nonexistent_snapshot.json")
    monkeypatch.setenv("SAARTHI_HOST_SNAPSHOT_FILE", missing_path)

    collector = OpsCollector()
    status = collector.get_container_status()
    assert status["status"] == "unavailable"

    # 2. Malformed JSON file
    malformed_path = str(tmp_path / "malformed.json")
    with open(malformed_path, "w", encoding="utf-8") as f:
        f.write("{invalid json content---")
    monkeypatch.setenv("SAARTHI_HOST_SNAPSHOT_FILE", malformed_path)

    status_malformed = collector.get_container_status()
    assert status_malformed["status"] == "unavailable"


def test_ops_expired_telemetry_cannot_produce_healthy(monkeypatch, tmp_path):
    """
    Expired telemetry (> 180s) cannot produce a healthy result:
    - Container status reports unavailable / expired
    - Overall Ops health reports degraded or unavailable
    """
    from datetime import datetime, timezone, timedelta
    from app.ops.authenticity import SnapshotAuthenticityService, ReplayProtectionStore
    from app.ops.collector import OpsCollector

    priv_hex, pub_hex = SnapshotAuthenticityService.generate_ed25519_keypair()
    monkeypatch.setenv("OPS_SNAPSHOT_SIGNING_KEY", priv_hex)
    monkeypatch.setenv("OPS_SNAPSHOT_VERIFY_KEY", pub_hex)

    db_path = str(tmp_path / "expired_test.db")
    store = ReplayProtectionStore(db_path=db_path)
    auth = SnapshotAuthenticityService(replay_store=store)
    monkeypatch.setattr("app.ops.collector.snapshot_authenticity_service", auth)
    monkeypatch.setattr("app.ops.router.snapshot_authenticity_service", auth)

    collector = OpsCollector()
    monkeypatch.setattr("app.ops.router.ops_collector", collector)

    # Set trusted host snapshot directly with an expired timestamp (200s ago)
    now = datetime.now(timezone.utc)
    expired_time = (now - timedelta(seconds=200)).isoformat()
    expired_envelope = {
        "version": "2.0",
        "algorithm": "ed25519",
        "source_id": "saarthi-ops-collector",
        "timestamp": expired_time,
        "nonce": "expired_nonce_123",
        "payload_hash": "dummy_hash",
        "signature": "dummy_sig",
        "payload": {
            "containers": [{"name": "saarthi-staging-backend", "status": "healthy", "state": "running"}]
        }
    }
    collector._trusted_host_snapshot = expired_envelope

    # Container status must report expired / unavailable
    c_status = collector.get_container_status()
    assert c_status["freshness"] == "expired"
    assert c_status["status"] == "unavailable"

    # Overall health must NOT be healthy
    health = collector.get_overall_ops_health()
    assert health["freshness"] == "expired"
    assert health["status"] in ("degraded", "unavailable")
    assert health["status"] != "healthy"



