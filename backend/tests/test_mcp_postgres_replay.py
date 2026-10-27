"""
PostgreSQL 16 Durable Replay Protection Integration Test Suite.
===============================================================
Strict Fail-Closed Verification Gate for MCP Consequential RequestState.

INVARIANTS:
1. Requires POSTGRES_TEST_URL to be set to a local test database.
2. Directly verifies that the connected server is PostgreSQL 16 via SELECT version().
3. Prohibits silent fallback to SQLite: any attempt to use SQLite triggers an immediate RuntimeError.
4. Validates:
   - Schema creation and primary key constraint on token_id.
   - Replay rejection across independent manager instances.
   - Replay rejection across simulated process restarts.
   - Exactly one success and nine rejections under 10 concurrent requests.
   - Expired, tampered, cross-user, cross-method, and modified-parameter tokens cause zero execution side effects and zero database writes.
   - Database failure fails closed.
   - Retention pruning purges expired records while preserving active tokens.
"""

import os
import time
import pytest
import concurrent.futures
from urllib.parse import urlparse

import psycopg2
import psycopg2.extras

from app.mcp.request_state import RequestStateManager, init_request_state_table
from app.db.connection import get_db_connection, HAS_PSYCOPG2, PostgresConnectionAdapter
from app.db.postgres_schema import init_postgres_tables


@pytest.fixture(scope="session", autouse=True)
def verify_postgres_16_prerequisites():
    """
    Validates PostgreSQL 16 availability and configuration.
    Fails closed immediately if POSTGRES_TEST_URL is not set or server is unreachable.
    Never falls back to SQLite.
    """
    pg_url = os.getenv("POSTGRES_TEST_URL")
    if not pg_url:
        pytest.fail(
            "BLOCKED: POSTGRES_TEST_URL environment variable is not set. "
            "A verified PostgreSQL 16 test instance is required for this gate. "
            "SQLite fallback is strictly prohibited."
        )

    if not HAS_PSYCOPG2:
        pytest.fail("BLOCKED: psycopg2-binary driver is not available.")

    parsed = urlparse(pg_url)
    if parsed.hostname not in ("127.0.0.1", "localhost"):
        pytest.fail(
            f"BLOCKED: Security violation: POSTGRES_TEST_URL must target 127.0.0.1 or localhost, got '{parsed.hostname}'"
        )
    if not parsed.path or ("test" not in parsed.path.lower() and parsed.path.strip("/") != "saarthi_test_db"):
        pytest.fail(
            f"BLOCKED: Security violation: POSTGRES_TEST_URL must target a dedicated test database, got '{parsed.path}'"
        )

    # Direct driver probe to verify PostgreSQL 16
    try:
        direct_conn = psycopg2.connect(pg_url, connect_timeout=3)
        cur = direct_conn.cursor()
        cur.execute("SELECT version();")
        row = cur.fetchone()
        version_str = row[0] if row else ""
        cur.close()
        direct_conn.close()
    except Exception as e:
        pytest.fail(
            f"BLOCKED: Failed to connect directly to PostgreSQL test server at {pg_url}: {e}"
        )

    if "PostgreSQL 16" not in version_str and "Postgres 16" not in version_str:
        pytest.fail(
            f"BLOCKED: Target server is not PostgreSQL 16. Server version string: {version_str}"
        )


@pytest.fixture(autouse=True)
def enforce_strict_postgresql_adapter(monkeypatch):
    """
    Enforces that all database operations in this suite strictly use PostgreSQL.
    Sets ENVIRONMENT=production and DATABASE_URL=POSTGRES_TEST_URL.
    Intercepts get_db_connection to guarantee that any silent fallback to SQLite raises RuntimeError.
    """
    pg_url = os.getenv("POSTGRES_TEST_URL")
    monkeypatch.setenv("DATABASE_URL", pg_url or "")
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("MCP_STATE_SECRET", "test_mcp_secure_signing_key_4a7b9c1d2e3f4a5b6c7d8e9f")

    from app.db import connection as db_conn_mod
    orig_get_db = db_conn_mod.get_db_connection

    def strict_get_db_connection(db_path=None):
        conn = orig_get_db(db_path)
        if not isinstance(conn, PostgresConnectionAdapter):
            raise RuntimeError(
                f"FATAL: Application attempted silent fallback to {type(conn)}! "
                "SQLite is strictly prohibited in this PostgreSQL gate."
            )
        return conn

    monkeypatch.setattr(db_conn_mod, "get_db_connection", strict_get_db_connection)
    import app.mcp.request_state as req_state_mod
    monkeypatch.setattr(req_state_mod, "get_db_connection", strict_get_db_connection)

    # Apply PostgreSQL schema and reset test table
    init_postgres_tables()
    init_request_state_table()
    mgr = RequestStateManager()
    mgr.reset_consumed_tokens()
    yield mgr
    mgr.reset_consumed_tokens()


def test_postgres_16_version_and_endpoint_verified():
    """Verify that the test suite is connected to a genuine PostgreSQL 16 server."""
    with get_db_connection() as conn:
        assert isinstance(conn, PostgresConnectionAdapter)
        cur = conn.cursor()
        cur.execute("SELECT version();")
        row = cur.fetchone()
        version_str = row["version"] if isinstance(row, dict) else row[0]
        assert "PostgreSQL 16" in version_str or "Postgres 16" in version_str


def test_postgres_mcp_schema_and_pk_constraint():
    """Verify table structure and PRIMARY KEY constraint on token_id in PostgreSQL."""
    with get_db_connection() as conn:
        assert isinstance(conn, PostgresConnectionAdapter)
        cur = conn.cursor()

        # Check column types
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'mcp_consumed_tokens'
            ORDER BY ordinal_position;
        """)
        columns = {row["column_name"]: row for row in cur.fetchall()}
        assert "token_id" in columns
        assert "principal" in columns
        assert "method" in columns
        assert "params_hash" in columns
        assert "consumed_at" in columns
        assert "expires_at" in columns

        # Check PRIMARY KEY constraint
        cur.execute("""
            SELECT c.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.constraint_column_usage ccu ON tc.constraint_name = ccu.constraint_name
            JOIN information_schema.columns c ON c.table_name = tc.table_name AND c.column_name = ccu.column_name
            WHERE tc.constraint_type = 'PRIMARY KEY' AND tc.table_name = 'mcp_consumed_tokens';
        """)
        pk_cols = [r["column_name"] for r in cur.fetchall()]
        assert "token_id" in pk_cols


def test_postgres_multi_process_replay_rejection():
    """Two separate RequestStateManager instances against PostgreSQL: replay is rejected."""
    mgr_1 = RequestStateManager()
    mgr_2 = RequestStateManager()

    token = mgr_1.issue_state(
        principal="pg_ops_user",
        method="saarthi_interactive_deploy",
        originating_request_id="pg-multi-inst-1",
        salient_params={"target": "staging"},
        ttl_seconds=300
    )

    valid_1, err_1, _ = mgr_1.verify_and_consume_state(
        token=token, principal="pg_ops_user", method="saarthi_interactive_deploy", salient_params={"target": "staging"}, consume=True
    )
    assert valid_1 is True
    assert err_1 is None

    # Instance 2 presentation must fail with replay rejection
    valid_2, err_2, _ = mgr_2.verify_and_consume_state(
        token=token, principal="pg_ops_user", method="saarthi_interactive_deploy", salient_params={"target": "staging"}, consume=True
    )
    assert valid_2 is False
    assert "Replayed requestState token" in err_2


def test_postgres_simulated_process_restart_replay_rejection():
    """Replay following simulated worker/process restart against PostgreSQL."""
    mgr_initial = RequestStateManager()
    token = mgr_initial.issue_state(
        principal="pg_ops_user",
        method="saarthi_interactive_deploy",
        originating_request_id="pg-restart-1",
        salient_params={"target": "staging"},
        ttl_seconds=300
    )

    v1, err1, _ = mgr_initial.verify_and_consume_state(
        token=token, principal="pg_ops_user", method="saarthi_interactive_deploy", salient_params={"target": "staging"}, consume=True
    )
    assert v1 is True
    assert err1 is None

    # Simulate worker restart: instantiate a new manager pointing to the same PostgreSQL store
    del mgr_initial
    mgr_restarted = RequestStateManager()

    v2, err2, _ = mgr_restarted.verify_and_consume_state(
        token=token, principal="pg_ops_user", method="saarthi_interactive_deploy", salient_params={"target": "staging"}, consume=True
    )
    assert v2 is False
    assert "Replayed requestState token" in err2


def test_postgres_concurrent_10_submissions_exactly_one_success():
    """10 simultaneous threads using same token against PostgreSQL: exactly 1 succeeds, 9 fail."""
    mgr = RequestStateManager()
    token = mgr.issue_state(
        principal="pg_ops_user",
        method="saarthi_interactive_deploy",
        originating_request_id="pg-concurrent-1",
        salient_params={"target": "staging"},
        ttl_seconds=300
    )

    def worker():
        local_mgr = RequestStateManager()
        return local_mgr.verify_and_consume_state(
            token=token, principal="pg_ops_user", method="saarthi_interactive_deploy", salient_params={"target": "staging"}, consume=True
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(worker) for _ in range(10)]
        results = [f.result() for f in futures]

    successes = [r for r in results if r[0] is True]
    failures = [r for r in results if r[0] is False]

    assert len(successes) == 1, f"Expected exactly 1 success, got {len(successes)}"
    assert len(failures) == 9
    for f in failures:
        assert "already been consumed" in f[1]


def test_postgres_negative_tokens_cause_zero_side_effects():
    """Expired, tampered, cross-user, cross-method, and modified-parameter tokens cause zero writes in PostgreSQL."""
    mgr = RequestStateManager()

    # 1. Expired token
    expired_tok = mgr.issue_state("pg_ops_user", "saarthi_interactive_deploy", 1, {"target": "staging"}, ttl_seconds=-10)
    v_exp, err_exp, _ = mgr.verify_and_consume_state(expired_tok, "pg_ops_user", "saarthi_interactive_deploy", {"target": "staging"})
    assert not v_exp
    assert "Expired" in err_exp

    # 2. Tampered signature
    legit = mgr.issue_state("pg_ops_user", "saarthi_interactive_deploy", 2, {"target": "staging"}, ttl_seconds=300)
    v_tamp, err_tamp, _ = mgr.verify_and_consume_state(legit[:-4] + "dead", "pg_ops_user", "saarthi_interactive_deploy", {"target": "staging"})
    assert not v_tamp
    assert "signature mismatch" in err_tamp

    # 3. Cross-principal
    v_cross, err_cross, _ = mgr.verify_and_consume_state(legit, "attacker", "saarthi_interactive_deploy", {"target": "staging"})
    assert not v_cross
    assert "Cross-user" in err_cross

    # 4. Cross-method
    v_mth, err_mth, _ = mgr.verify_and_consume_state(legit, "pg_ops_user", "saarthi_unauthorized_action", {"target": "staging"})
    assert not v_mth
    assert "Cross-method" in err_mth

    # 5. Modified parameter
    v_param, err_param, _ = mgr.verify_and_consume_state(legit, "pg_ops_user", "saarthi_interactive_deploy", {"target": "production"})
    assert not v_param
    assert "parameter tampering" in err_param

    # Verify zero rows written to PostgreSQL
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) AS count FROM mcp_consumed_tokens;")
        row = cur.fetchone()
        count = row["count"] if isinstance(row, dict) else row[0]
        assert count == 0, f"Expected 0 ledger rows for failed tokens, found {count}"


def test_postgres_database_failure_fails_closed(monkeypatch):
    """Verify that a database outage during token consumption fails closed in PostgreSQL mode."""
    mgr = RequestStateManager()
    token = mgr.issue_state("pg_ops_user", "saarthi_interactive_deploy", 3, {"target": "staging"}, ttl_seconds=300)

    from app.db import connection as db_conn_mod
    def mock_db_down(*args, **kwargs):
        raise RuntimeError("OperationalError: connection to PostgreSQL server lost")

    monkeypatch.setattr(db_conn_mod, "get_db_connection", mock_db_down)
    import app.mcp.request_state as req_state_mod
    monkeypatch.setattr(req_state_mod, "get_db_connection", mock_db_down)

    valid, err, payload = mgr.verify_and_consume_state(
        token=token, principal="pg_ops_user", method="saarthi_interactive_deploy", salient_params={"target": "staging"}, consume=True
    )
    assert valid is False
    assert payload is None
    assert "failing closed" in err.lower()


def test_postgres_retention_pruning_maintains_replay_window():
    """Verify retention cleanup deletes expired records while preserving active tokens in PostgreSQL."""
    mgr = RequestStateManager()

    tok_short = mgr.issue_state("pg_ops_user", "saarthi_interactive_deploy", "s-1", {"target": "staging"}, ttl_seconds=1)
    mgr.verify_and_consume_state(tok_short, "pg_ops_user", "saarthi_interactive_deploy", {"target": "staging"}, consume=True)

    tok_long = mgr.issue_state("pg_ops_user", "saarthi_interactive_deploy", "l-1", {"target": "staging"}, ttl_seconds=300)
    mgr.verify_and_consume_state(tok_long, "pg_ops_user", "saarthi_interactive_deploy", {"target": "staging"}, consume=True)

    time.sleep(1.2)
    deleted = mgr.purge_expired()
    assert deleted >= 1

    # Ensure tok_long is still recorded as consumed in PostgreSQL
    v_replay, err_replay, _ = mgr.verify_and_consume_state(tok_long, "pg_ops_user", "saarthi_interactive_deploy", {"target": "staging"}, consume=True)
    assert not v_replay
    assert "already been consumed" in err_replay
