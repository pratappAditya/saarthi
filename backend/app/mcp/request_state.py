"""
Cryptographic RequestState Management for Model Context Protocol (MCP) MRTR.
Protects integrity, principal binding, method/params binding, expiration,
and provides durable, persistent single-use replay protection for consequential
multi round-trip confirmation flows.
"""

import os
import hmac
import hashlib
import json
import base64
import time
import secrets
import logging
import datetime
from typing import Dict, Any, Optional, Tuple

from app.db.connection import get_db_connection

logger = logging.getLogger("app.mcp.request_state")


def init_request_state_table(db_path: Optional[str] = None) -> None:
    """
    Ensures the durable mcp_consumed_tokens ledger table exists.
    Supports both PostgreSQL and SQLite.
    """
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mcp_consumed_tokens (
                    token_id VARCHAR(64) PRIMARY KEY,
                    principal VARCHAR(255) NOT NULL,
                    method VARCHAR(255) NOT NULL,
                    params_hash VARCHAR(64) NOT NULL,
                    consumed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
                )
            """)
            try:
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_mcp_tokens_expires_at ON mcp_consumed_tokens(expires_at)")
            except Exception:
                pass
            if hasattr(conn, "commit"):
                conn.commit()
    except Exception as e:
        logger.error(f"Failed to initialize mcp_consumed_tokens table: {e}")


class RequestStateManager:
    """
    Manages cryptographically protected, principal-bound, single-use requestState tokens
    for MCP Multi Round-Trip Requests (MRTR) backed by a durable database ledger.
    """

    def __init__(
        self,
        secret_key: Optional[bytes] = None,
        default_ttl_seconds: int = 300,
        db_path: Optional[str] = None
    ):
        is_prod = os.getenv("ENVIRONMENT", "development").lower() in ("staging", "production")
        raw_secret = (
            secret_key
            or os.getenv("MCP_STATE_SECRET")
            or os.getenv("SECRET_KEY")
            or os.getenv("JWT_SECRET")
            or os.getenv("ADMIN_SECRET_KEY")
        )

        PLACEHOLDER_SECRETS = {
            "saarthi_mcp_secure_request_state_signing_key_default",
            "dev_key",
            "generate_fresh_random_staging_jwt_secret_64chars",
            "generate_fresh_random_staging_admin_key_64chars",
            "generate_fresh_random_staging_jwt_secret_64chars",
        }

        if is_prod and (not raw_secret or (isinstance(raw_secret, str) and raw_secret.strip() in PLACEHOLDER_SECRETS)):
            raise RuntimeError(
                "FATAL: MCP_STATE_SECRET, SECRET_KEY, or JWT_SECRET must be explicitly configured with a secure, "
                "non-placeholder secret in staging/production environments."
            )

        if not raw_secret:
            raw_secret = "saarthi_mcp_secure_request_state_signing_key_default"

        if isinstance(raw_secret, str):
            self.secret_key = raw_secret.encode("utf-8")
        else:
            self.secret_key = raw_secret

        self.default_ttl = default_ttl_seconds
        self.db_path = db_path
        self._op_counter = 0

        # Auto-ensure schema on initialization
        self._ensure_table()

    def _ensure_table(self, conn=None) -> None:
        """Internal helper to ensure the table is available."""
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mcp_consumed_tokens (
                    token_id VARCHAR(64) PRIMARY KEY,
                    principal VARCHAR(255) NOT NULL,
                    method VARCHAR(255) NOT NULL,
                    params_hash VARCHAR(64) NOT NULL,
                    consumed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
                )
            """)
            try:
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_mcp_tokens_expires_at ON mcp_consumed_tokens(expires_at)")
            except Exception:
                pass
            if hasattr(conn, "commit"):
                conn.commit()
        else:
            init_request_state_table(self.db_path)

    @staticmethod
    def _compute_params_hash(params: Optional[Dict[str, Any]]) -> str:
        """Computes deterministic SHA-256 hash of salient parameters."""
        if not params:
            return hashlib.sha256(b"{}").hexdigest()
        canonical_json = json.dumps(params, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

    def issue_state(
        self,
        principal: str,
        method: str,
        originating_request_id: Any,
        salient_params: Optional[Dict[str, Any]] = None,
        ttl_seconds: Optional[int] = None
    ) -> str:
        """
        Issues an HMAC-protected, principal- and request-bound opaque requestState token.
        """
        now = int(time.time())
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        token_id = secrets.token_hex(16)
        params_hash = self._compute_params_hash(salient_params)

        payload = {
            "tid": token_id,
            "sub": str(principal),
            "mth": str(method),
            "rid": str(originating_request_id),
            "phash": params_hash,
            "iat": now,
            "exp": now + ttl
        }
        payload_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        payload_b64 = base64.urlsafe_b64encode(payload_bytes).decode("ascii").rstrip("=")

        signature = hmac.new(self.secret_key, payload_b64.encode("ascii"), hashlib.sha256).digest()
        sig_b64 = base64.urlsafe_b64encode(signature).decode("ascii").rstrip("=")

        return f"{payload_b64}.{sig_b64}"

    def verify_and_consume_state(
        self,
        token: str,
        principal: str,
        method: str,
        salient_params: Optional[Dict[str, Any]] = None,
        consume: bool = True
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Validates token integrity, expiry, principal, method, parameters binding, and
        atomically consumes the token in the durable database ledger to prevent replay.

        Returns: (is_valid, error_reason, payload)
        Fails closed on database unavailability or verification failure.
        """
        if not token or not isinstance(token, str):
            return False, "Missing or invalid requestState token", None

        parts = token.split(".")
        if len(parts) != 2:
            return False, "Malformed requestState format", None

        payload_b64, sig_b64 = parts
        # 1. Verify HMAC signature
        expected_sig = hmac.new(self.secret_key, payload_b64.encode("ascii"), hashlib.sha256).digest()
        expected_sig_b64 = base64.urlsafe_b64encode(expected_sig).decode("ascii").rstrip("=")
        if not hmac.compare_digest(sig_b64, expected_sig_b64):
            return False, "Tampered requestState token signature mismatch", None

        # 2. Decode payload
        try:
            padded_b64 = payload_b64 + "=" * (-len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(padded_b64.encode("ascii"))
            payload = json.loads(payload_bytes.decode("utf-8"))
        except Exception:
            return False, "Invalid payload encoding in requestState", None

        # 3. Expiry check
        now = int(time.time())
        exp = payload.get("exp", 0)
        if now > exp:
            return False, "Expired requestState token", None

        # 4. Principal binding check
        token_principal = payload.get("sub")
        if token_principal != str(principal):
            return False, f"Cross-user requestState violation: issued to '{token_principal}', presented by '{principal}'", None

        # 5. Method binding check
        token_method = payload.get("mth")
        if token_method != str(method):
            return False, f"Cross-method requestState violation: issued for '{token_method}', presented for '{method}'", None

        # 6. Salient parameters binding check
        current_phash = self._compute_params_hash(salient_params)
        token_phash = payload.get("phash")
        if token_phash != current_phash:
            return False, "Cross-request parameter tampering detected in requestState", None

        # 7. Durable single-use replay protection backed by persistent database ledger
        token_id = payload.get("tid")
        if not token_id or not isinstance(token_id, str):
            return False, "Malformed requestState: missing token identifier", None

        now_iso = datetime.datetime.fromtimestamp(now, tz=datetime.timezone.utc).isoformat()
        exp_iso = datetime.datetime.fromtimestamp(exp, tz=datetime.timezone.utc).isoformat()

        try:
            with get_db_connection(self.db_path) as conn:
                self._ensure_table(conn)
                cursor = conn.cursor()
                if not consume:
                    cursor.execute("SELECT 1 FROM mcp_consumed_tokens WHERE token_id = ?", (token_id,))
                    row = cursor.fetchone()
                    if row:
                        return False, "Replayed requestState token: state has already been consumed", None
                    return True, None, payload

                # Atomic consumption via primary key insertion
                cursor.execute(
                    """
                    INSERT INTO mcp_consumed_tokens (token_id, principal, method, params_hash, consumed_at, expires_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
                    """,
                    (token_id, str(principal), str(method), current_phash, exp_iso)
                )
                if hasattr(conn, "commit"):
                    conn.commit()

                # Periodic retention pruning (1 in 20 consumptions)
                self._op_counter += 1
                if self._op_counter % 20 == 0:
                    try:
                        cursor.execute("DELETE FROM mcp_consumed_tokens WHERE expires_at < ?", (now_iso,))
                        if hasattr(conn, "commit"):
                            conn.commit()
                    except Exception:
                        pass
        except Exception as e:
            err_msg = str(e).lower()
            if any(k in err_msg for k in ("unique", "primary key", "integrityerror", "duplicate key")):
                return False, "Replayed requestState token: state has already been consumed", None
            logger.error(f"Database error during requestState verification/consumption: {e}")
            return False, "Database error during state consumption: failing closed", None

        return True, None, payload

    def purge_expired(self, now_ts: Optional[float] = None) -> int:
        """
        Purges expired token records from the durable consumed-token store.
        Returns the number of deleted records.
        """
        now = now_ts if now_ts is not None else time.time()
        now_iso = datetime.datetime.fromtimestamp(now, tz=datetime.timezone.utc).isoformat()
        try:
            with get_db_connection(self.db_path) as conn:
                self._ensure_table(conn)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM mcp_consumed_tokens WHERE expires_at < ?", (now_iso,))
                rowcount = cursor.rowcount if hasattr(cursor, "rowcount") else 0
                if hasattr(conn, "commit"):
                    conn.commit()
                return rowcount
        except Exception as e:
            logger.error(f"Failed to purge expired requestState tokens: {e}")
            return 0

    def reset_consumed_tokens(self) -> None:
        """Reset consumed token ledger in durable database (primarily for test environments)."""
        try:
            with get_db_connection(self.db_path) as conn:
                self._ensure_table(conn)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM mcp_consumed_tokens")
                if hasattr(conn, "commit"):
                    conn.commit()
        except Exception as e:
            logger.warning(f"Error resetting mcp_consumed_tokens: {e}")


request_state_manager = RequestStateManager()
