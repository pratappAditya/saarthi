import os
import pytest
from app.db.connection import PostgresRowWrapper, PostgresCursorWrapper, get_db_connection
from app.config.settings import settings
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_postgres_row_wrapper():
    """Verify PostgresRowWrapper supports both dict key access and tuple index access."""
    row = PostgresRowWrapper({"user_id": "usr_123", "email": "test@example.com", "plan": "POWER"})
    assert row["user_id"] == "usr_123"
    assert row["email"] == "test@example.com"
    assert row[0] == "usr_123"
    assert row[1] == "test@example.com"
    assert dict(row) == {"user_id": "usr_123", "email": "test@example.com", "plan": "POWER"}

def test_postgres_sql_translation():
    """Verify SQL translation replaces SQLite ? placeholders, PRAGMA, AUTOINCREMENT, and LIKE for PostgreSQL."""
    class DummyCursor:
        def __init__(self):
            self.last_sql = ""
        def execute(self, sql, params):
            self.last_sql = sql
        def fetchone(self):
            return {"id": 42}

    dummy = DummyCursor()
    wrapper = PostgresCursorWrapper(dummy)

    # 1. Test placeholder translation
    wrapper.execute("SELECT * FROM users WHERE email = ? AND role = ?", ("test@example.com", "USER"))
    assert "%s" in dummy.last_sql
    assert "?" not in dummy.last_sql

    # 2. Test PRAGMA stripping
    wrapper.execute("PRAGMA journal_mode=WAL;")
    assert dummy.last_sql == "SELECT 1;"

    # 3. Test PRAGMA table_info translation
    wrapper.execute("PRAGMA table_info(users)")
    assert "information_schema.columns" in dummy.last_sql
    assert "table_name = 'users'" in dummy.last_sql

    # 4. Test PRAGMA integrity_check translation
    wrapper.execute("PRAGMA integrity_check;")
    assert "SELECT 'ok' AS integrity_check;" in dummy.last_sql

    # 5. Test datetime translation
    wrapper.execute("INSERT INTO users (created_at) VALUES (datetime('now'))")
    assert "CURRENT_TIMESTAMP" in dummy.last_sql

    # 6. Test AUTOINCREMENT translation
    wrapper.execute("CREATE TABLE test_tbl (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT);")
    assert "SERIAL PRIMARY KEY" in dummy.last_sql
    assert "AUTOINCREMENT" not in dummy.last_sql

    # 7. Test INSERT OR IGNORE translation
    wrapper.execute("INSERT OR IGNORE INTO users (email) VALUES (?)", ("test@example.com",))
    assert "ON CONFLICT DO NOTHING" in dummy.last_sql
    assert "OR IGNORE" not in dummy.last_sql

    # 8. Test LIKE to ILIKE translation
    wrapper.execute("SELECT * FROM users WHERE name LIKE ? AND status = 'ACTIVE'", ("%john%",))
    assert " ILIKE " in dummy.last_sql
    assert " LIKE " not in dummy.last_sql

    # 9. Test RETURNING id auto-append and lastrowid
    wrapper.execute("INSERT INTO resumes (title, raw_content) VALUES (?, ?)", ("Test", "Content"))
    assert "RETURNING id" in dummy.last_sql
    assert wrapper.lastrowid == 42

    # 10. Test table without id does NOT get RETURNING id
    wrapper.execute("INSERT INTO feature_flags (key, name) VALUES (?, ?)", ("TEST", "Test"))
    assert "RETURNING id" not in dummy.last_sql

def test_devices_upsert_syntax_sqlite_and_postgres_compatible():
    """Verify device registration query is portable and valid with foreign-key compliance."""
    conn = get_db_connection()
    try:
        conn.execute("""
            INSERT INTO users (user_id, email, password_hash, salt, role, created_at, updated_at)
            VALUES (?, ?, 'hash', 'salt', 'USER', '2026-09-24T00:00:00', '2026-09-24T00:00:00')
            ON CONFLICT (user_id) DO NOTHING
        """, ("usr_test_1", "usr_test_1@example.com"))
        conn.execute("""
            INSERT INTO devices (device_id, user_id, device_fingerprint, device_name, os_info, first_seen, last_seen, status)
            VALUES (?, ?, ?, ?, 'Windows Desktop', ?, ?, 'ACTIVE')
            ON CONFLICT (device_id) DO UPDATE SET
                user_id = excluded.user_id,
                device_fingerprint = excluded.device_fingerprint,
                device_name = excluded.device_name,
                last_seen = excluded.last_seen,
                status = excluded.status
        """, ("dev_test_1", "usr_test_1", "fp_1", "Laptop", "2026-09-24T00:00:00", "2026-09-24T00:00:00"))
        conn.commit()
        row = conn.execute("SELECT * FROM devices WHERE device_id = ?", ("dev_test_1",)).fetchone()
        assert row is not None
        assert row["device_name"] == "Laptop"
    finally:
        conn.close()

def test_production_postgresql_fail_closed(monkeypatch):
    """Verify production mode fails closed if PostgreSQL connection fails."""
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("DATABASE_URL", "postgresql://invalid_user:invalid_pass@127.0.0.1:54329/invalid_db")

    with pytest.raises(RuntimeError) as exc_info:
        get_db_connection()

    assert "Production PostgreSQL connection failed" in str(exc_info.value) or "psycopg2" in str(exc_info.value)

def test_health_endpoint_detects_db_type():
    """Verify /api/health endpoint returns database connectivity and engine type."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert "checks" in data
    assert "database" in data["checks"]
    assert data["checks"]["database"]["healthy"] is True
    assert "type" in data["checks"]["database"]
