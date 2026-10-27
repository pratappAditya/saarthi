import os
import sqlite3
from datetime import datetime, timezone, timedelta
from typing import Tuple, Optional, Dict, Any, List

from app.licensing.models import LicenseStatus, LicensePlan, Entitlements
from app.licensing.crypto import verify_token, public_key_from_pem, DEFAULT_VENDOR_PUBLIC_KEY_PEM
from app.licensing.device import get_device_fingerprint

from app.config.settings import settings
from app.db.connection import get_db_connection

class ClientLicenseManager:
    def __init__(self, db_path: str = None, public_key_pem: Optional[bytes] = None):
        self._db_path = db_path
        self._shared_conn = None
        if db_path == ":memory:":
            self._shared_conn = get_db_connection(":memory:")
            
        if public_key_pem:
            self.public_key = public_key_from_pem(public_key_pem)
        else:
            self.public_key = public_key_from_pem(DEFAULT_VENDOR_PUBLIC_KEY_PEM.encode('utf-8'))
            
        self._init_db()

    @property
    def db_path(self) -> str:
        return self._db_path or settings.DATABASE_PATH

    @db_path.setter
    def db_path(self, val: str):
        self._db_path = val

    def _get_connection(self):
        if self._shared_conn:
            return self._shared_conn
        return get_db_connection(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS client_license_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    license_key TEXT NOT NULL,
                    activation_token TEXT NOT NULL,
                    plan TEXT NOT NULL,
                    status TEXT NOT NULL,
                    device_fingerprint TEXT NOT NULL,
                    issued_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    last_verified_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clock_tamper_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    last_observed_timestamp TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS local_revocation_cache (
                    license_id TEXT PRIMARY KEY,
                    revoked_at TEXT NOT NULL,
                    reason TEXT
                )
            """)
            conn.commit()

    def update_clock_high_water_mark(self, current_dt: datetime) -> bool:
        """
        Logs current timestamp and verifies that current time is not prior to 
        the maximum previously recorded timestamp (Clock Rollback Guard).
        """
        now_str = current_dt.isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            row = cursor.execute("SELECT MAX(last_observed_timestamp) as max_ts FROM clock_tamper_log").fetchone()
            if row and row["max_ts"]:
                max_dt = datetime.fromisoformat(row["max_ts"])
                if current_dt < max_dt - timedelta(minutes=5): # Allow 5 min clock jitter tolerance
                    return False # Clock rollback detected!
                    
            cursor.execute("INSERT INTO clock_tamper_log (last_observed_timestamp, updated_at) VALUES (?, ?)", (now_str, now_str))
            conn.commit()
        return True

    def record_revocation(self, license_id: str, reason: str = "Revoked by vendor"):
        now_str = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            conn.cursor().execute(
                "INSERT OR REPLACE INTO local_revocation_cache (license_id, revoked_at, reason) VALUES (?, ?, ?)",
                (license_id, now_str, reason)
            )
            conn.commit()

    def is_revoked_locally(self, license_id: str) -> bool:
        with self._get_connection() as conn:
            row = conn.cursor().execute("SELECT 1 FROM local_revocation_cache WHERE license_id = ?", (license_id,)).fetchone()
            return row is not None

    def store_activation_token(self, license_key: str, activation_token: str, payload: Dict[str, Any]):
        now_str = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM client_license_cache")
            cursor.execute("""
                INSERT INTO client_license_cache 
                (license_key, activation_token, plan, status, device_fingerprint, issued_at, expires_at, last_verified_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                license_key,
                activation_token,
                payload.get("plan", LicensePlan.MONTHLY.value),
                payload.get("status", LicenseStatus.ACTIVE.value),
                payload.get("device_fingerprint", ""),
                payload.get("issued_at", now_str),
                payload.get("expires_at", now_str),
                now_str,
                now_str
            ))
            conn.commit()

    def get_cached_license(self) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            row = conn.cursor().execute("SELECT * FROM client_license_cache ORDER BY id DESC LIMIT 1").fetchone()
            if row:
                return dict(row)
        return None

    def evaluate_license(self, current_device_fingerprint: Optional[str] = None) -> Tuple[LicenseStatus, Optional[Entitlements], str]:
        now = datetime.now(timezone.utc)
        
        # 1. Check Clock Rollback Guard
        if not self.update_clock_high_water_mark(now):
            return LicenseStatus.CLOCK_TAMPERED, None, "Clock rollback detected. System clock was set back."

        cached = self.get_cached_license()
        if not cached:
            return LicenseStatus.UNLICENSED, None, "No active license found. Please activate a valid Saarthi license."

        token = cached.get("activation_token", "")
        
        # 2. Cryptographic Signature Verification
        try:
            payload = verify_token(token, self.public_key)
        except Exception as e:
            return LicenseStatus.REVOKED, None, f"License token verification failed: {str(e)}"

        license_id = payload.get("license_id", "")
        
        # 3. Check Local Revocation List
        if self.is_revoked_locally(license_id):
            return LicenseStatus.REVOKED, None, "This license has been revoked by the vendor."

        # 4. Check Status Flag in Payload
        token_status = payload.get("status", "")
        if token_status == LicenseStatus.SUSPENDED.value:
            return LicenseStatus.SUSPENDED, None, "License account is suspended by vendor."
        if token_status == LicenseStatus.CANCELLED.value:
            return LicenseStatus.CANCELLED, None, "License subscription has been cancelled."
        if token_status == LicenseStatus.REVOKED.value:
            self.record_revocation(license_id, "Revoked in token payload")
            return LicenseStatus.REVOKED, None, "License has been revoked by vendor."

        # 5. Check Device Hardware Fingerprint Match
        expected_fp = payload.get("device_fingerprint", "")
        actual_fp = current_device_fingerprint or get_device_fingerprint()
        if expected_fp != actual_fp:
            return LicenseStatus.UNLICENSED, None, "Device hardware fingerprint mismatch. License is bound to another machine."

        # 6. Check License Expiration Date
        exp_str = payload.get("expires_at", "")
        try:
            exp_dt = datetime.fromisoformat(exp_str)
            if exp_dt < now:
                return LicenseStatus.EXPIRED, None, "License has expired. Please renew your subscription."
        except Exception:
            return LicenseStatus.UNLICENSED, None, "Invalid license expiration date."

        # 7. Check Offline Grace Period (Max 7 Days)
        last_verified_str = cached.get("last_verified_at", "")
        try:
            last_verified_dt = datetime.fromisoformat(last_verified_str)
            grace_days = payload.get("grace_period_days", 7)
            if now - last_verified_dt > timedelta(days=grace_days, seconds=60):
                return LicenseStatus.GRACE_EXPIRED, None, f"Offline grace period ({grace_days} days) expired. Please connect to internet to sync license."
        except Exception:
            pass

        # 8. All Checks Passed -> Active State with Entitlements
        plan_str = payload.get("plan", LicensePlan.MONTHLY.value)
        try:
            plan = LicensePlan(plan_str)
        except Exception:
            plan = LicensePlan.MONTHLY
            
        entitlements = Entitlements.from_plan(plan)
        return LicenseStatus.ACTIVE, entitlements, "License active."

    def clear_license(self):
        with self._get_connection() as conn:
            conn.cursor().execute("DELETE FROM client_license_cache")
            conn.commit()
