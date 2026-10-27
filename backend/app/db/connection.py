import os
import sqlite3
import time
import functools
import logging
import asyncio
import inspect
import re
from typing import Callable, Any, Optional, Dict, Union

try:
    import psycopg2
    import psycopg2.extras
    import psycopg2.pool
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False

from app.config.settings import settings

logger = logging.getLogger("app.db.connection")

_pg_pool: Optional[Any] = None

TABLES_WITHOUT_ID = {
    "usage_records",
    "user_subscription",
    "user_personalization_profile",
    "feature_flags",
    "local_revocation_cache",
    "mcp_consumed_tokens",
}

TABLE_PKS = {
    "multimodal_attachments": "id",
    "agent_routines": "id",
    "agent_goals": "id",
    "agent_tasks": "task_id",
    "local_revocation_cache": "license_id",
    "user_personalization_profile": "user_id",
    "personalization_preferences": "user_id",
    "domain_expertise": "user_id, domain",
    "project_personalization_overrides": "user_id, project_name",
    "unified_automations": "automation_id",
    "automation_checkpoints": "checkpoint_id",
    "payments": "id",
    "subscriptions": "id",
    "invoices": "id",
    "refunds": "id",
    "payment_events": "id",
    "subscription_events": "id",
    "billing_audit_events": "id",
    "billing_customers": "id",
    "mcp_consumed_tokens": "token_id",
}

def get_pg_pool(db_url: str):
    global _pg_pool
    if _pg_pool is None and HAS_PSYCOPG2:
        try:
            _pg_pool = psycopg2.pool.ThreadedConnectionPool(1, 20, db_url)
            logger.info("Initialized PostgreSQL threaded connection pool (1-20 connections).")
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL connection pool: {e}")
            raise e
    return _pg_pool

def close_pg_pool():
    global _pg_pool
    if _pg_pool is not None:
        try:
            _pg_pool.closeall()
            logger.info("Closed all connections in PostgreSQL pool.")
        except Exception as e:
            logger.warning(f"Error closing PostgreSQL pool: {e}")
        finally:
            _pg_pool = None

class PostgresRowWrapper(dict):
    """
    Dict subclass supporting key access row['email'], tuple index access row[0], and dict(row).
    """
    def __init__(self, record: Dict[str, Any]):
        super().__init__(record or {})
        self._keys = list(self.keys())
        self._values = tuple(self.values())

    def __getitem__(self, item: Any) -> Any:
        if isinstance(item, int):
            return self._values[item]
        return super().__getitem__(item)

class PostgresCursorWrapper:
    def __init__(self, pg_cursor):
        self._cursor = pg_cursor
        self._lastrowid: Optional[int] = None
        self._returning_row: Optional[Any] = None

    def execute(self, sql: str, parameters: Any = ()):
        sql_translated, appended_returning = self._translate_sql(sql)
        self._returning_row = None
        self._cursor.execute(sql_translated, parameters or ())
        if appended_returning:
            try:
                row = self._cursor.fetchone()
                if row:
                    if isinstance(row, dict):
                        self._lastrowid = row.get("id")
                    elif hasattr(row, "__getitem__"):
                        self._lastrowid = row[0]
                    self._returning_row = row
            except Exception:
                self._lastrowid = None
        return self

    def executemany(self, sql: str, seq_of_parameters: Any = ()):
        sql_translated, _ = self._translate_sql(sql)
        self._cursor.executemany(sql_translated, seq_of_parameters or ())
        return self

    def fetchone(self) -> Optional[PostgresRowWrapper]:
        if self._returning_row is not None:
            row = self._returning_row
            self._returning_row = None
            if not row:
                return None
            return PostgresRowWrapper(dict(row))
        row = self._cursor.fetchone()
        if not row:
            return None
        return PostgresRowWrapper(dict(row))

    def fetchall(self) -> list:
        if self._returning_row is not None:
            row = self._returning_row
            self._returning_row = None
            return [PostgresRowWrapper(dict(row))]
        rows = self._cursor.fetchall()
        if not rows:
            return []
        return [PostgresRowWrapper(dict(r)) for r in rows]

    @property
    def rowcount(self) -> int:
        return self._cursor.rowcount

    @property
    def lastrowid(self) -> Optional[int]:
        return self._lastrowid

    @property
    def description(self):
        return self._cursor.description

    def _translate_sql(self, sql: str) -> tuple[str, bool]:
        appended_returning = False
        sql_trimmed = sql.strip()
        sql_upper = sql_trimmed.upper()

        # Handle PRAGMA statements
        if sql_upper.startswith("PRAGMA"):
            # Check PRAGMA table_info(...)
            m_info = re.match(r"^PRAGMA\s+table_info\s*\(\s*['\"]?([a-zA-Z0-9_]+)['\"]?\s*\)", sql_trimmed, re.IGNORECASE)
            if m_info:
                tbl_name = m_info.group(1).lower()
                translated_sql = (
                    "SELECT 0 AS cid, column_name AS name, data_type AS type, "
                    "(CASE WHEN is_nullable = 'NO' THEN 1 ELSE 0 END) AS notnull, "
                    "column_default AS dflt_value, 0 AS pk "
                    "FROM information_schema.columns "
                    f"WHERE table_name = '{tbl_name}' "
                    "ORDER BY ordinal_position;"
                )
                return translated_sql, False

            # Check PRAGMA integrity_check / quick_check
            if re.match(r"^PRAGMA\s+(?:integrity_check|quick_check)", sql_trimmed, re.IGNORECASE):
                return "SELECT 'ok' AS integrity_check;", False

            # Other PRAGMAs (WAL, busy_timeout, foreign_keys, synchronous)
            return "SELECT 1;", False

        # Translate AUTOINCREMENT to PostgreSQL SERIAL PRIMARY KEY
        sql = re.sub(r'\bINTEGER\s+PRIMARY\s+KEY\s+AUTOINCREMENT\b', 'SERIAL PRIMARY KEY', sql, flags=re.IGNORECASE)
        sql = re.sub(r'\bAUTOINCREMENT\b', '', sql, flags=re.IGNORECASE)

        # Translate datetime('now')
        sql = re.sub(r"\bdatetime\('now'\)", "CURRENT_TIMESTAMP", sql, flags=re.IGNORECASE)

        # Translate DATETIME column type to TIMESTAMP WITH TIME ZONE for PostgreSQL (excluding function calls)
        sql = re.sub(r'\bDATETIME\b(?!\s*\()', 'TIMESTAMP WITH TIME ZONE', sql, flags=re.IGNORECASE)

        # Translate INSERT OR REPLACE INTO to INSERT INTO ... ON CONFLICT (...) DO UPDATE SET ...
        m_replace = re.match(r"^INSERT\s+OR\s+REPLACE\s+INTO\s+([a-zA-Z0-9_]+)\s*\(([^)]+)\)\s*VALUES\s*(.*)", sql.strip(), re.IGNORECASE | re.DOTALL)
        if m_replace:
            tbl_name = m_replace.group(1).lower()
            cols_str = m_replace.group(2)
            values_str = m_replace.group(3).rstrip().rstrip(';')
            cols = [c.strip() for c in cols_str.split(",")]
            pk = TABLE_PKS.get(tbl_name, "id")
            pk_cols = [c.strip().lower() for c in pk.split(",")]
            update_cols = [c for c in cols if c.lower() not in pk_cols]
            if update_cols:
                update_clause = ", ".join([f"{c} = EXCLUDED.{c}" for c in update_cols])
                sql = f"INSERT INTO {tbl_name} ({cols_str}) VALUES {values_str} ON CONFLICT ({pk}) DO UPDATE SET {update_clause};"
            else:
                sql = f"INSERT INTO {tbl_name} ({cols_str}) VALUES {values_str} ON CONFLICT ({pk}) DO NOTHING;"

        # Translate INSERT OR IGNORE INTO to INSERT INTO ... ON CONFLICT DO NOTHING
        if re.search(r'\bINSERT\s+OR\s+IGNORE\s+INTO\b', sql, re.IGNORECASE):
            sql = re.sub(r'\bINSERT\s+OR\s+IGNORE\s+INTO\b', 'INSERT INTO', sql, flags=re.IGNORECASE)
            sql = sql.rstrip().rstrip(';') + " ON CONFLICT DO NOTHING;"

        # Translate SQLite ? placeholders and handle LIKE -> ILIKE outside quotes
        translated = []
        in_single_quote = False
        in_double_quote = False
        i = 0
        n = len(sql)
        while i < n:
            char = sql[i]
            if char == "'" and not in_double_quote:
                in_single_quote = not in_single_quote
                translated.append(char)
                i += 1
            elif char == '"' and not in_single_quote:
                in_double_quote = not in_double_quote
                translated.append(char)
                i += 1
            elif not in_single_quote and not in_double_quote:
                if char == '?':
                    translated.append('%s')
                    i += 1
                elif sql[i:i+6].upper() == " LIKE ":
                    translated.append(" ILIKE ")
                    i += 6
                elif sql[i:i+10].upper() == " NOT LIKE ":
                    translated.append(" NOT ILIKE ")
                    i += 10
                else:
                    translated.append(char)
                    i += 1
            else:
                translated.append(char)
                i += 1

        final_sql = "".join(translated)

        # Check for appending RETURNING id on INSERT
        final_upper = final_sql.strip().upper()
        if final_upper.startswith("INSERT INTO") and "RETURNING" not in final_upper and "SELECT" not in final_upper:
            m_table = re.match(r"^INSERT\s+INTO\s+([a-zA-Z0-9_]+)", final_sql.strip(), re.IGNORECASE)
            if m_table:
                target_table = m_table.group(1).lower()
                if target_table not in TABLES_WITHOUT_ID:
                    final_sql = final_sql.rstrip().rstrip(';') + " RETURNING id;"
                    appended_returning = True

        return final_sql, appended_returning

class PostgresConnectionAdapter:
    def __init__(self, pg_conn, pool=None):
        self._conn = pg_conn
        self._pool = pool
        self._closed = False

    def cursor(self):
        return PostgresCursorWrapper(self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor))

    def execute(self, sql: str, parameters: Any = ()):
        cursor = self.cursor()
        cursor.execute(sql, parameters)
        return cursor

    def executemany(self, sql: str, seq_of_parameters: Any = ()):
        cursor = self.cursor()
        cursor.executemany(sql, seq_of_parameters)
        return cursor

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        if not self._closed:
            if self._pool:
                self._pool.putconn(self._conn)
            else:
                self._conn.close()
            self._closed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self.close()

_configured_sqlite_paths = set()

def get_db_connection(db_path: Optional[str] = None) -> Union[sqlite3.Connection, PostgresConnectionAdapter]:
    """
    Unified database connection helper supporting PostgreSQL and SQLite.
    Automatically resolves PostgreSQL if DATABASE_URL or POSTGRES_URI is set.
    """
    db_url = settings.DATABASE_URL or os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URI", "")
    env_name = os.getenv("ENVIRONMENT", "development").lower()
    is_staging_or_prod = env_name in ("production", "staging")

    if is_staging_or_prod and (not db_url or not (db_url.startswith("postgresql://") or db_url.startswith("postgres://"))):
        raise RuntimeError(
            f"FATAL: DATABASE_URL / POSTGRES_URI is required and must target PostgreSQL in {env_name} environment. "
            "Silent fallback to SQLite is strictly prohibited."
        )

    if db_url and (db_url.startswith("postgresql://") or db_url.startswith("postgres://")):
        if not HAS_PSYCOPG2:
            raise RuntimeError("psycopg2-binary is required when DATABASE_URL is set to PostgreSQL.")
        try:
            pool = get_pg_pool(db_url)
            conn = pool.getconn()
            return PostgresConnectionAdapter(conn, pool=pool)
        except Exception as e:
            logger.error(f"PostgreSQL connection error: {e}")
            if is_staging_or_prod:
                raise RuntimeError(f"Production PostgreSQL connection failed ({env_name}): {e}")
            logger.warning("Falling back to SQLite in non-production mode...")

    # Fallback / Default: SQLite
    path = db_path or settings.DATABASE_PATH
    if path != ":memory:":
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        
    conn = sqlite3.connect(path, timeout=30.0)
    if path != ":memory:":
        try:
            conn.execute("PRAGMA busy_timeout=30000;")
            conn.execute("PRAGMA foreign_keys=ON;")
            if path not in _configured_sqlite_paths:
                conn.execute("PRAGMA journal_mode=WAL;")
                conn.execute("PRAGMA synchronous=NORMAL;")
                _configured_sqlite_paths.add(path)
        except Exception as e:
            logger.warning(f"Could not set WAL/busy_timeout pragmas: {e}")

    conn.row_factory = sqlite3.Row
    return conn

def with_db_retry(max_retries: int = 5, initial_delay: float = 0.1, backoff_factor: float = 2.0):
    """
    Decorator that retries database operations when encountering locking or transient network errors.
    Supports both sync and async functions.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        if inspect.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                delay = initial_delay
                last_err = None
                for attempt in range(1, max_retries + 1):
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        err_str = str(e).lower()
                        if "locked" in err_str or "busy" in err_str or "could not serialize" in err_str:
                            last_err = e
                            if attempt == max_retries:
                                logger.error(f"Database retry limit reached ({max_retries}) in {func.__name__}")
                                raise
                            logger.warning(f"Database lock/retry in {func.__name__} (attempt {attempt}/{max_retries}). Retrying in {delay:.2f}s...")
                            await asyncio.sleep(delay)
                            delay *= backoff_factor
                        else:
                            raise
                if last_err:
                    raise last_err
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                delay = initial_delay
                last_err = None
                for attempt in range(1, max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        err_str = str(e).lower()
                        if "locked" in err_str or "busy" in err_str or "could not serialize" in err_str:
                            last_err = e
                            if attempt == max_retries:
                                logger.error(f"Database retry limit reached ({max_retries}) in {func.__name__}")
                                raise
                            logger.warning(f"Database lock/retry in {func.__name__} (attempt {attempt}/{max_retries}). Retrying in {delay:.2f}s...")
                            time.sleep(delay)
                            delay *= backoff_factor
                        else:
                            raise
                if last_err:
                    raise last_err
            return sync_wrapper
    return decorator
