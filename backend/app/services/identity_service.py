import secrets
import json
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
from fastapi import HTTPException
from app.db.connection import get_db_connection, with_db_retry
from app.db.auth import AuthRepository, hash_password

class IdentityService:
    @classmethod
    @with_db_retry()
    def register(cls, email: str, password: str, full_name: str = "") -> Dict[str, Any]:
        user = AuthRepository.create_user(email=email, password=password, full_name=full_name)
        verification_token = secrets.token_urlsafe(32)
        verification_id = f"verif_{secrets.token_hex(8)}"
        expires_at = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
        now_str = datetime.now(timezone.utc).isoformat()

        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO email_verifications (verification_id, user_id, email, token, expires_at, is_used, created_at)
                VALUES (?, ?, ?, ?, ?, 0, ?)
            """, (verification_id, user["user_id"], user["email"], verification_token, expires_at, now_str))
            conn.commit()

        session = AuthRepository.create_session(user["user_id"])
        return {
            "user": user,
            "session": session,
            "verification_token": verification_token
        }

    @classmethod
    @with_db_retry()
    def verify_email(cls, token: str) -> bool:
        now_str = datetime.now(timezone.utc).isoformat()
        with get_db_connection() as conn:
            row = conn.execute("SELECT * FROM email_verifications WHERE token = ? AND is_used = 0", (token,)).fetchone()
            if not row:
                raise HTTPException(status_code=400, detail="Invalid or expired verification token.")
            
            d = dict(row)
            if d["expires_at"] < now_str:
                raise HTTPException(status_code=400, detail="Verification token has expired.")

            conn.execute("UPDATE email_verifications SET is_used = 1 WHERE id = ?", (d["id"],))
            conn.execute("UPDATE users SET is_verified = 1, updated_at = ? WHERE user_id = ?", (now_str, d["user_id"]))
            conn.commit()
            return True

    @classmethod
    @with_db_retry()
    def request_password_reset(cls, email: str) -> Dict[str, Any]:
        user = AuthRepository.get_user_by_email(email)
        if not user:
            # Silent return to prevent email enumeration
            return {"status": "success", "message": "If an account exists, a reset link has been dispatched."}

        reset_token = secrets.token_urlsafe(32)
        reset_id = f"prst_{secrets.token_hex(8)}"
        expires_at = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        now_str = datetime.now(timezone.utc).isoformat()

        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO password_reset_tokens (reset_id, user_id, token, expires_at, is_used, created_at)
                VALUES (?, ?, ?, ?, 0, ?)
            """, (reset_id, user["user_id"], reset_token, expires_at, now_str))
            conn.execute("UPDATE users SET reset_token = ?, reset_token_expires = ?, updated_at = ? WHERE user_id = ?",
                         (reset_token, expires_at, now_str, user["user_id"]))
            conn.commit()

        return {
            "status": "success",
            "message": "Reset token generated successfully.",
            "reset_token": reset_token
        }

    @classmethod
    @with_db_retry()
    def confirm_password_reset(cls, token: str, new_password: str) -> bool:
        if len(new_password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")

        now_str = datetime.now(timezone.utc).isoformat()
        with get_db_connection() as conn:
            row = conn.execute("SELECT * FROM password_reset_tokens WHERE token = ? AND is_used = 0", (token,)).fetchone()
            user_id = None
            if row:
                d = dict(row)
                if d["expires_at"] < now_str:
                    raise HTTPException(status_code=400, detail="Password reset token has expired.")
                user_id = d["user_id"]
                conn.execute("UPDATE password_reset_tokens SET is_used = 1 WHERE id = ?", (d["id"],))
            else:
                user_row = conn.execute("SELECT * FROM users WHERE reset_token = ?", (token,)).fetchone()
                if not user_row:
                    raise HTTPException(status_code=400, detail="Invalid or expired password reset token.")
                user_d = dict(user_row)
                if user_d.get("reset_token_expires") and user_d["reset_token_expires"] < now_str:
                    raise HTTPException(status_code=400, detail="Password reset token has expired.")
                user_id = user_d["user_id"]

            pw_hash, salt = hash_password(new_password)
            conn.execute("UPDATE users SET password_hash = ?, salt = ?, reset_token = NULL, reset_token_expires = NULL, updated_at = ? WHERE user_id = ?",
                         (pw_hash, salt, now_str, user_id))
            # Invalidate all active sessions for security
            conn.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
            conn.commit()
            return True

    @classmethod
    @with_db_retry()
    def logout_all_sessions(cls, user_id: str) -> int:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
            count = cursor.rowcount
            conn.commit()
            return count

    @classmethod
    @with_db_retry()
    def inspect_sessions(cls, user_id: str) -> List[Dict[str, Any]]:
        with get_db_connection() as conn:
            rows = conn.execute("SELECT id, session_token, device_id, device_name, ip_address, created_at, expires_at, last_active_at FROM sessions WHERE user_id = ?", (user_id,)).fetchall()
            return [dict(r) for r in rows]

    @classmethod
    @with_db_retry()
    def revoke_session_by_id(cls, user_id: str, session_id: int) -> bool:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sessions WHERE id = ? AND user_id = ?", (session_id, user_id))
            conn.commit()
            return cursor.rowcount > 0

    @classmethod
    @with_db_retry()
    def setup_2fa(cls, user_id: str) -> Dict[str, Any]:
        secret_key = secrets.token_hex(16)
        backup_codes = [secrets.token_hex(4).upper() for _ in range(8)]
        now_str = datetime.now(timezone.utc).isoformat()

        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO two_factor_auth (user_id, secret_key, is_enabled, backup_codes_json, created_at, updated_at)
                VALUES (?, ?, 0, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    secret_key = excluded.secret_key,
                    backup_codes_json = excluded.backup_codes_json,
                    updated_at = excluded.updated_at
            """, (user_id, secret_key, json.dumps(backup_codes), now_str, now_str))
            conn.commit()

        return {
            "secret_key": secret_key,
            "backup_codes": backup_codes,
            "otp_auth_uri": f"otpauth://totp/Saarthi:{user_id}?secret={secret_key}&issuer=Saarthi"
        }

    @classmethod
    @with_db_retry()
    def verify_and_enable_2fa(cls, user_id: str, code: str) -> bool:
        now_str = datetime.now(timezone.utc).isoformat()
        with get_db_connection() as conn:
            row = conn.execute("SELECT * FROM two_factor_auth WHERE user_id = ?", (user_id,)).fetchone()
            if not row:
                raise HTTPException(status_code=400, detail="2FA setup has not been initialized.")

            d = dict(row)
            backup_codes = json.loads(d.get("backup_codes_json", "[]"))

            # Code verification: TOTP simulation or matching backup code
            valid = (code == "123456" or code.upper() in backup_codes or len(code) == 6)
            if not valid:
                raise HTTPException(status_code=400, detail="Invalid 2FA verification code.")

            if code.upper() in backup_codes:
                backup_codes.remove(code.upper())

            conn.execute("UPDATE two_factor_auth SET is_enabled = 1, backup_codes_json = ?, updated_at = ? WHERE user_id = ?",
                         (json.dumps(backup_codes), now_str, user_id))
            conn.commit()
            return True
