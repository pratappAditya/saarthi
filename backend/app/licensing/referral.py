"""
Saarthi Referral Engine & Anti-Abuse System
Privacy-safe referral tracking and fraud prevention.
"""

import sqlite3
import hashlib
import uuid
import datetime
from typing import Dict, Any, Optional, List
from app.config.settings import settings
from app.db.connection import get_db_connection

class ReferralManager:
    """
    Manages user referral codes, tracks referral activations,
    and enforces strict anti-abuse rules (self-referral prevention, device duplicate checks).
    """
    def __init__(self, db_path: str = None):
        self._db_path = db_path
        self._init_db()

    @property
    def db_path(self) -> str:
        return self._db_path or settings.DATABASE_PATH

    @db_path.setter
    def db_path(self, val: str):
        self._db_path = val

    def _get_connection(self):
        return get_db_connection(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS referral_codes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE NOT NULL,
                    code TEXT UNIQUE NOT NULL,
                    device_fingerprint TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS referral_redemptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    referral_code TEXT NOT NULL,
                    referrer_user_id TEXT NOT NULL,
                    referee_user_id TEXT NOT NULL,
                    referee_device_fingerprint TEXT NOT NULL,
                    status TEXT NOT NULL, -- PENDING, ACTIVATED, REJECTED
                    rejection_reason TEXT,
                    created_at TEXT NOT NULL,
                    activated_at TEXT
                )
            """)
            conn.commit()

    def get_or_create_referral_code(self, user_id: str = "default_user", device_fingerprint: str = "") -> str:
        """Retrieves or generates a unique referral code for a user."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT code FROM referral_codes WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return row[0]
            
            # Generate deterministic code prefix from user_id hash
            hash_suffix = hashlib.sha256(f"{user_id}_{uuid.uuid4().hex}".encode()).hexdigest()[:6].upper()
            code = f"REF-{hash_suffix}"
            now = datetime.datetime.now(datetime.timezone.utc).isoformat()
            
            cursor.execute("""
                INSERT INTO referral_codes (user_id, code, device_fingerprint, created_at)
                VALUES (?, ?, ?, ?)
            """, (user_id, code, device_fingerprint, now))
            conn.commit()
            return code

    def redeem_referral(
        self,
        code: str,
        referee_user_id: str,
        referee_device_fingerprint: str
    ) -> Dict[str, Any]:
        """
        Validates and processes a referral redemption with anti-abuse controls.
        """
        code = code.strip().upper()
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            # 1. Lookup code
            cursor.execute("SELECT user_id, device_fingerprint FROM referral_codes WHERE code = ?", (code,))
            row = cursor.fetchone()
            if not row:
                return {"success": False, "reason": "INVALID_CODE", "message": "Referral code does not exist."}

            referrer_user_id, referrer_fingerprint = row[0], row[1]

            # 2. Anti-abuse: Self-referral check (same user or same device fingerprint)
            if referrer_user_id == referee_user_id:
                return {"success": False, "reason": "SELF_REFERRAL", "message": "Self-referral is not permitted."}
                
            if referrer_fingerprint and referee_device_fingerprint and (referrer_fingerprint == referee_device_fingerprint):
                return {"success": False, "reason": "SAME_DEVICE", "message": "Referral attempted from same hardware device."}

            # 3. Anti-abuse: Check if referee already redeemed a referral
            cursor.execute("""
                SELECT id FROM referral_redemptions 
                WHERE referee_user_id = ? OR referee_device_fingerprint = ?
            """, (referee_user_id, referee_device_fingerprint))
            if cursor.fetchone():
                return {"success": False, "reason": "ALREADY_REDEEMED", "message": "This user or device has already redeemed a referral code."}

            # 4. Success: Record redemption
            cursor.execute("""
                INSERT INTO referral_redemptions (
                    referral_code, referrer_user_id, referee_user_id, referee_device_fingerprint, status, created_at, activated_at
                ) VALUES (?, ?, ?, ?, 'ACTIVATED', ?, ?)
            """, (code, referrer_user_id, referee_user_id, referee_device_fingerprint, now, now))
            conn.commit()

            return {
                "success": True,
                "status": "ACTIVATED",
                "message": "Referral code successfully redeemed! Welcome bonus applied.",
                "referrer_user_id": referrer_user_id
            }

    def get_referral_stats(self, user_id: str = "default_user") -> Dict[str, Any]:
        """Returns non-sensitive referral statistics for the user dashboard."""
        code = self.get_or_create_referral_code(user_id)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM referral_redemptions 
                WHERE referrer_user_id = ? AND status = 'ACTIVATED'
            """, (user_id,))
            successful_referrals = cursor.fetchone()[0]

            return {
                "referral_code": code,
                "successful_referrals": successful_referrals,
                "earned_rewards_description": f"{successful_referrals * 7} extra trial days earned",
                "privacy_guarantee": "Zero referred user personal content or identity is shared."
            }

default_referral_manager = ReferralManager()
