import os
import sqlite3
import uuid
import secrets
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional

from app.licensing.models import (
    LicenseStatus, LicensePlan, Customer, LicenseRecord, DeviceActivation, AuditLogEntry
)
from app.licensing.crypto import (
    generate_keypair, sign_payload, public_key_to_pem, private_key_to_pem,
    private_key_from_pem, public_key_from_pem
)

from app.db.connection import get_db_connection
from app.config.settings import settings

class VendorServer:
    def __init__(self, db_path: Optional[str] = ":memory:", private_key_pem: Optional[bytes] = None):
        self._db_path = db_path
        self._shared_conn = None
        if db_path == ":memory:":
            self._shared_conn = sqlite3.connect(":memory:", check_same_thread=False)
            self._shared_conn.row_factory = sqlite3.Row
        self._init_db()
        
        if private_key_pem:
            self.private_key = private_key_from_pem(private_key_pem)
        else:
            self.private_key, _ = generate_keypair()
            
        self.public_key = self.private_key.public_key()
        self.public_key_pem = public_key_to_pem(self.public_key).decode('utf-8')

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
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS licenses (
                    license_id TEXT PRIMARY KEY,
                    license_key TEXT UNIQUE NOT NULL,
                    customer_id TEXT NOT NULL,
                    plan TEXT NOT NULL,
                    status TEXT NOT NULL,
                    max_devices INTEGER DEFAULT 2,
                    issued_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS device_activations (
                    activation_id TEXT PRIMARY KEY,
                    license_id TEXT NOT NULL,
                    device_fingerprint TEXT NOT NULL,
                    device_name TEXT,
                    activated_at TEXT NOT NULL,
                    last_seen_at TEXT NOT NULL,
                    FOREIGN KEY(license_id) REFERENCES licenses(license_id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vendor_audit_logs (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT NOT NULL,
                    target_type TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    details TEXT,
                    timestamp TEXT NOT NULL
                )
            """)
            conn.commit()

    def _log_audit(self, action: str, target_type: str, target_id: str, actor: str, details: Optional[str] = None):
        now_str = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            conn.cursor().execute("""
                INSERT INTO vendor_audit_logs (action, target_type, target_id, actor, details, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (action, target_type, target_id, actor, details, now_str))
            conn.commit()

    def create_customer(self, name: str, email: str, actor: str = "admin") -> Customer:
        cust_id = f"CUST-{uuid.uuid4().hex[:8].upper()}"
        now_str = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            try:
                conn.cursor().execute("""
                    INSERT INTO customers (customer_id, name, email, created_at)
                    VALUES (?, ?, ?, ?)
                """, (cust_id, name, email, now_str))
                conn.commit()
            except sqlite3.IntegrityError:
                raise ValueError(f"Customer with email '{email}' already exists.")

        self._log_audit("CREATE_CUSTOMER", "CUSTOMER", cust_id, actor, f"Created customer {name} ({email})")
        return Customer(customer_id=cust_id, name=name, email=email, created_at=now_str)

    def get_customer(self, customer_id: str) -> Optional[Customer]:
        with self._get_connection() as conn:
            row = conn.cursor().execute("SELECT * FROM customers WHERE customer_id = ?", (customer_id,)).fetchone()
            if row:
                return Customer(customer_id=row["customer_id"], name=row["name"], email=row["email"], created_at=row["created_at"])
        return None

    def list_customers(self) -> List[Customer]:
        with self._get_connection() as conn:
            rows = conn.cursor().execute("SELECT * FROM customers ORDER BY created_at DESC").fetchall()
            return [Customer(customer_id=r["customer_id"], name=r["name"], email=r["email"], created_at=r["created_at"]) for r in rows]

    def create_license(
        self,
        customer_id: str,
        plan: LicensePlan,
        duration_days: int = 30,
        max_devices: int = 2,
        actor: str = "admin"
    ) -> LicenseRecord:
        cust = self.get_customer(customer_id)
        if not cust:
            raise ValueError(f"Customer '{customer_id}' does not exist.")

        lic_id = f"LIC-{uuid.uuid4().hex[:8].upper()}"
        lic_key = f"SAARTHI-{plan.value[:3]}-{secrets.token_hex(6).upper()}"
        now = datetime.now(timezone.utc)
        expires = now + timedelta(days=duration_days)

        now_str = now.isoformat()
        exp_str = expires.isoformat()

        with self._get_connection() as conn:
            conn.cursor().execute("""
                INSERT INTO licenses (license_id, license_key, customer_id, plan, status, max_devices, issued_at, expires_at, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (lic_id, lic_key, customer_id, plan.value, LicenseStatus.ACTIVE.value, max_devices, now_str, exp_str, now_str))
            conn.commit()

        self._log_audit("CREATE_LICENSE", "LICENSE", lic_id, actor, f"Created {plan.value} license for {customer_id}")
        return LicenseRecord(
            license_id=lic_id,
            license_key=lic_key,
            customer_id=customer_id,
            plan=plan,
            status=LicenseStatus.ACTIVE,
            max_devices=max_devices,
            issued_at=now_str,
            expires_at=exp_str,
            created_at=now_str
        )

    def get_license_by_key(self, license_key: str) -> Optional[LicenseRecord]:
        with self._get_connection() as conn:
            row = conn.cursor().execute("SELECT * FROM licenses WHERE license_key = ?", (license_key,)).fetchone()
            if row:
                return LicenseRecord(
                    license_id=row["license_id"],
                    license_key=row["license_key"],
                    customer_id=row["customer_id"],
                    plan=LicensePlan(row["plan"]),
                    status=LicenseStatus(row["status"]),
                    max_devices=row["max_devices"],
                    issued_at=row["issued_at"],
                    expires_at=row["expires_at"],
                    created_at=row["created_at"]
                )
        return None

    def get_license(self, license_id: str) -> Optional[LicenseRecord]:
        with self._get_connection() as conn:
            row = conn.cursor().execute("SELECT * FROM licenses WHERE license_id = ?", (license_id,)).fetchone()
            if row:
                return LicenseRecord(
                    license_id=row["license_id"],
                    license_key=row["license_key"],
                    customer_id=row["customer_id"],
                    plan=LicensePlan(row["plan"]),
                    status=LicenseStatus(row["status"]),
                    max_devices=row["max_devices"],
                    issued_at=row["issued_at"],
                    expires_at=row["expires_at"],
                    created_at=row["created_at"]
                )
        return None

    def activate_license(self, license_key: str, device_fingerprint: str, device_name: Optional[str] = "Desktop") -> str:
        lic = self.get_license_by_key(license_key)
        if not lic:
            raise ValueError("Invalid license key.")

        if lic.status == LicenseStatus.REVOKED:
            raise ValueError("License has been permanently revoked by vendor.")
        if lic.status == LicenseStatus.SUSPENDED:
            raise ValueError("License is currently suspended by vendor.")
        if lic.status == LicenseStatus.CANCELLED:
            raise ValueError("License has been cancelled by vendor.")

        now = datetime.now(timezone.utc)
        exp_dt = datetime.fromisoformat(lic.expires_at)
        if exp_dt < now:
            raise ValueError("License has expired.")

        with self._get_connection() as conn:
            # Check existing device activations
            dev_rows = conn.cursor().execute(
                "SELECT * FROM device_activations WHERE license_id = ?", (lic.license_id,)
            ).fetchall()
            
            matching = [d for d in dev_rows if d["device_fingerprint"] == device_fingerprint]
            if not matching:
                if len(dev_rows) >= lic.max_devices:
                    raise ValueError(f"Device limit exceeded ({len(dev_rows)}/{lic.max_devices} devices registered).")
                
                act_id = f"ACT-{uuid.uuid4().hex[:8].upper()}"
                now_str = now.isoformat()
                conn.cursor().execute("""
                    INSERT INTO device_activations (activation_id, license_id, device_fingerprint, device_name, activated_at, last_seen_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (act_id, lic.license_id, device_fingerprint, device_name, now_str, now_str))
                conn.commit()
            else:
                now_str = now.isoformat()
                conn.cursor().execute("""
                    UPDATE device_activations SET last_seen_at = ? WHERE activation_id = ?
                """, (now_str, matching[0]["activation_id"]))
                conn.commit()

        # Generate Ed25519 Signed Activation Token
        payload = {
            "license_id": lic.license_id,
            "customer_id": lic.customer_id,
            "plan": lic.plan.value,
            "status": lic.status.value,
            "device_fingerprint": device_fingerprint,
            "issued_at": lic.issued_at,
            "expires_at": lic.expires_at,
            "grace_period_days": 7,
            "nonce": secrets.token_hex(8)
        }
        
        token = sign_payload(payload, self.private_key)
        self._log_audit("ACTIVATE_LICENSE", "LICENSE", lic.license_id, "client", f"Activated device {device_fingerprint[:8]}")
        return token

    def suspend_license(self, license_id: str, actor: str = "admin", reason: str = "Payment issue") -> bool:
        lic = self.get_license(license_id)
        if not lic:
            return False
        with self._get_connection() as conn:
            conn.cursor().execute("UPDATE licenses SET status = ? WHERE license_id = ?", (LicenseStatus.SUSPENDED.value, license_id))
            conn.commit()
        self._log_audit("SUSPEND_LICENSE", "LICENSE", license_id, actor, reason)
        return True

    def revoke_license(self, license_id: str, actor: str = "admin", reason: str = "Refund / Breach") -> bool:
        lic = self.get_license(license_id)
        if not lic:
            return False
        with self._get_connection() as conn:
            conn.cursor().execute("UPDATE licenses SET status = ? WHERE license_id = ?", (LicenseStatus.REVOKED.value, license_id))
            conn.commit()
        self._log_audit("REVOKE_LICENSE", "LICENSE", license_id, actor, reason)
        return True

    def cancel_license(self, license_id: str, actor: str = "admin", reason: str = "Customer subscription cancelled") -> bool:
        lic = self.get_license(license_id)
        if not lic:
            return False
        with self._get_connection() as conn:
            conn.cursor().execute("UPDATE licenses SET status = ? WHERE license_id = ?", (LicenseStatus.CANCELLED.value, license_id))
            conn.commit()
        self._log_audit("CANCEL_LICENSE", "LICENSE", license_id, actor, reason)
        return True

    def restore_license(self, license_id: str, actor: str = "admin") -> bool:
        lic = self.get_license(license_id)
        if not lic or lic.status == LicenseStatus.REVOKED:
            return False
        with self._get_connection() as conn:
            conn.cursor().execute("UPDATE licenses SET status = ? WHERE license_id = ?", (LicenseStatus.ACTIVE.value, license_id))
            conn.commit()
        self._log_audit("RESTORE_LICENSE", "LICENSE", license_id, actor, "Restored active status")
        return True

    def renew_license(self, license_id: str, extension_days: int = 30, actor: str = "admin") -> Optional[LicenseRecord]:
        lic = self.get_license(license_id)
        if not lic or lic.status == LicenseStatus.REVOKED:
            return None
        
        current_exp = datetime.fromisoformat(lic.expires_at)
        now = datetime.now(timezone.utc)
        base_time = max(current_exp, now)
        new_exp = (base_time + timedelta(days=extension_days)).isoformat()
        
        with self._get_connection() as conn:
            conn.cursor().execute("UPDATE licenses SET expires_at = ?, status = ? WHERE license_id = ?", (new_exp, LicenseStatus.ACTIVE.value, license_id))
            conn.commit()
            
        self._log_audit("RENEW_LICENSE", "LICENSE", license_id, actor, f"Extended by {extension_days} days")
        return self.get_license(license_id)

    def change_entitlement(self, license_id: str, new_plan: LicensePlan, actor: str = "admin") -> Optional[LicenseRecord]:
        lic = self.get_license(license_id)
        if not lic or lic.status == LicenseStatus.REVOKED:
            return None
            
        with self._get_connection() as conn:
            conn.cursor().execute("UPDATE licenses SET plan = ? WHERE license_id = ?", (new_plan.value, license_id))
            conn.commit()
            
        self._log_audit("CHANGE_ENTITLEMENT", "LICENSE", license_id, actor, f"Changed plan to {new_plan.value}")
        return self.get_license(license_id)

    def get_crl(self) -> List[Dict[str, str]]:
        with self._get_connection() as conn:
            rows = conn.cursor().execute(
                "SELECT license_id, status FROM licenses WHERE status IN (?, ?, ?)",
                (LicenseStatus.REVOKED.value, LicenseStatus.SUSPENDED.value, LicenseStatus.CANCELLED.value)
            ).fetchall()
            return [{"license_id": r["license_id"], "status": r["status"]} for r in rows]

    def sync_license(self, license_id: str, device_fingerprint: str) -> Dict[str, Any]:
        lic = self.get_license(license_id)
        if not lic:
            return {"status": LicenseStatus.REVOKED.value, "valid": False, "crl": self.get_crl()}

        if lic.status in (LicenseStatus.SUSPENDED.value, LicenseStatus.REVOKED.value, LicenseStatus.CANCELLED.value):
            return {"status": lic.status.value, "valid": False, "crl": self.get_crl()}

        now = datetime.now(timezone.utc)
        exp_dt = datetime.fromisoformat(lic.expires_at)
        if exp_dt < now:
            return {"status": LicenseStatus.EXPIRED.value, "valid": False, "crl": self.get_crl()}

        # Re-issue active token
        new_token = self.activate_license(lic.license_key, device_fingerprint)
        return {
            "status": LicenseStatus.ACTIVE.value,
            "valid": True,
            "activation_token": new_token,
            "crl": self.get_crl()
        }

    def get_audit_logs(self, target_id: Optional[str] = None) -> List[AuditLogEntry]:
        with self._get_connection() as conn:
            if target_id:
                rows = conn.cursor().execute("SELECT * FROM vendor_audit_logs WHERE target_id = ? ORDER BY log_id DESC", (target_id,)).fetchall()
            else:
                rows = conn.cursor().execute("SELECT * FROM vendor_audit_logs ORDER BY log_id DESC").fetchall()
            return [
                AuditLogEntry(
                    log_id=r["log_id"],
                    action=r["action"],
                    target_type=r["target_type"],
                    target_id=r["target_id"],
                    actor=r["actor"],
                    details=r["details"],
                    timestamp=r["timestamp"]
                ) for r in rows
            ]
