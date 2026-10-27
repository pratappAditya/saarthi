import os
import sqlite3
import hashlib
import secrets
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
from app.config.settings import settings

from app.db.connection import get_db_connection, with_db_retry

DATABASE_PATH = settings.DATABASE_PATH

def init_auth_tables():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                full_name TEXT NOT NULL DEFAULT '',
                is_verified INTEGER NOT NULL DEFAULT 0,
                verification_token TEXT,
                reset_token TEXT,
                reset_token_expires TEXT,
                role TEXT NOT NULL DEFAULT 'USER',
                subscription_plan TEXT NOT NULL DEFAULT 'FREE',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_token TEXT UNIQUE NOT NULL,
                user_id TEXT NOT NULL,
                device_id TEXT NOT NULL,
                device_name TEXT NOT NULL DEFAULT 'Desktop Workstation',
                ip_address TEXT DEFAULT '127.0.0.1',
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                last_active_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT UNIQUE NOT NULL,
                user_id TEXT NOT NULL,
                device_fingerprint TEXT NOT NULL,
                device_name TEXT NOT NULL DEFAULT 'Desktop Workstation',
                os_info TEXT DEFAULT '',
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'ACTIVE',
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS free_usage_quota (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id_or_device TEXT UNIQUE NOT NULL,
                request_count INTEGER NOT NULL DEFAULT 0,
                token_count INTEGER NOT NULL DEFAULT 0,
                daily_limit INTEGER NOT NULL DEFAULT 30,
                cooldown_until TEXT,
                last_request_at TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id TEXT NOT NULL,
                action TEXT NOT NULL,
                target_user TEXT,
                details TEXT,
                timestamp TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS login_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0,
                locked_until TEXT,
                updated_at TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_verifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                verification_id TEXT UNIQUE NOT NULL,
                user_id TEXT NOT NULL,
                email TEXT NOT NULL,
                token TEXT UNIQUE NOT NULL,
                expires_at TEXT NOT NULL,
                is_used INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reset_id TEXT UNIQUE NOT NULL,
                user_id TEXT NOT NULL,
                token TEXT UNIQUE NOT NULL,
                expires_at TEXT NOT NULL,
                is_used INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()

init_auth_tables()

def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    if not salt:
        salt = secrets.token_hex(16)
    pw_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()
    return pw_hash, salt

class AuthRepository:
    @staticmethod
    def check_rate_limit(key: str, max_attempts: int = 5, lock_minutes: int = 15) -> tuple[bool, Optional[str]]:
        now = datetime.now(timezone.utc)
        now_str = now.isoformat()
        with get_db_connection() as conn:
            row = conn.execute("SELECT * FROM login_attempts WHERE key = ?", (key,)).fetchone()
            if not row:
                return True, None
            d = dict(row)
            if d.get("locked_until"):
                lu_raw = d["locked_until"]
                if isinstance(lu_raw, datetime):
                    locked_until_dt = lu_raw if lu_raw.tzinfo else lu_raw.replace(tzinfo=timezone.utc)
                else:
                    locked_until_dt = datetime.fromisoformat(str(lu_raw))
                    if locked_until_dt.tzinfo is None:
                        locked_until_dt = locked_until_dt.replace(tzinfo=timezone.utc)
                if now < locked_until_dt:
                    return False, f"Too many failed attempts. Account temporarily locked until {d['locked_until']}"
                else:
                    conn.execute("DELETE FROM login_attempts WHERE key = ?", (key,))
                    conn.commit()
            return True, None

    @staticmethod
    @with_db_retry()
    def record_login_attempt(key: str, success: bool, max_attempts: int = 5, lock_minutes: int = 15):
        now = datetime.now(timezone.utc)
        now_str = now.isoformat()
        with get_db_connection() as conn:
            if success:
                conn.execute("DELETE FROM login_attempts WHERE key = ?", (key,))
            else:
                row = conn.execute("SELECT * FROM login_attempts WHERE key = ?", (key,)).fetchone()
                if not row:
                    conn.execute("INSERT INTO login_attempts (key, attempts, updated_at) VALUES (?, 1, ?)", (key, now_str))
                else:
                    new_count = row["attempts"] + 1
                    locked_until = (now + timedelta(minutes=lock_minutes)).isoformat() if new_count >= max_attempts else None
                    conn.execute("UPDATE login_attempts SET attempts = ?, locked_until = ?, updated_at = ? WHERE key = ?",
                                 (new_count, locked_until, now_str, key))
            conn.commit()

    @staticmethod
    @with_db_retry()
    def create_user(email: str, password: str, full_name: str = "", role: str = "USER") -> Dict[str, Any]:
        email = email.strip().lower()
        if not email or "@" not in email:
            raise ValueError("Invalid email address.")
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters long.")
            
        pw_hash, salt = hash_password(password)
        user_id = f"usr_{secrets.token_hex(8)}"
        verification_token = secrets.token_urlsafe(16)
        now_str = datetime.now(timezone.utc).isoformat()
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            existing = cursor.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
            if existing:
                raise ValueError("An account with this email address already exists.")
                
            cursor.execute("""
                INSERT INTO users (user_id, email, password_hash, salt, full_name, is_verified, verification_token, role, subscription_plan, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, 0, ?, ?, 'FREE', ?, ?)
            """, (user_id, email, pw_hash, salt, full_name, verification_token, role, now_str, now_str))
            conn.commit()
            
        return AuthRepository.get_user_by_id(user_id)

    @staticmethod
    @with_db_retry()
    def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        with get_db_connection() as conn:
            row = conn.execute("SELECT user_id, email, full_name, is_verified, verification_token, role, subscription_plan, created_at, updated_at FROM users WHERE user_id = ?", (user_id,)).fetchone()
            if row:
                return dict(row)
        return None

    @staticmethod
    @with_db_retry()
    def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        email = email.strip().lower()
        with get_db_connection() as conn:
            row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
            if row:
                return dict(row)
        return None

    @staticmethod
    @with_db_retry()
    def authenticate(email: str, password: str) -> Optional[Dict[str, Any]]:
        allowed, err_msg = AuthRepository.check_rate_limit(email)
        if not allowed:
            raise ValueError(err_msg)

        user = AuthRepository.get_user_by_email(email)
        if not user:
            AuthRepository.record_login_attempt(email, success=False)
            return None

        pw_hash, _ = hash_password(password, user["salt"])
        if pw_hash == user["password_hash"]:
            AuthRepository.record_login_attempt(email, success=True)
            return {
                "user_id": user["user_id"],
                "email": user["email"],
                "full_name": user["full_name"],
                "is_verified": bool(user["is_verified"]),
                "role": user["role"],
                "subscription_plan": user["subscription_plan"]
            }
        
        AuthRepository.record_login_attempt(email, success=False)
        return None

    @staticmethod
    def verify_email(token: str) -> bool:
        now_str = datetime.now(timezone.utc).isoformat()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            user = cursor.execute("SELECT user_id FROM users WHERE verification_token = ?", (token,)).fetchone()
            if user:
                cursor.execute("UPDATE users SET is_verified = 1, verification_token = NULL, updated_at = ? WHERE user_id = ?",
                               (now_str, user["user_id"]))
                conn.commit()
                return True
        return False

    @staticmethod
    def create_password_reset_token(email: str) -> Optional[str]:
        user = AuthRepository.get_user_by_email(email)
        if not user:
            return None
        reset_token = secrets.token_urlsafe(24)
        reset_id = f"prst_{secrets.token_hex(8)}"
        expires_at = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        now_str = datetime.now(timezone.utc).isoformat()
        
        with get_db_connection() as conn:
            conn.execute("UPDATE users SET reset_token = ?, reset_token_expires = ?, updated_at = ? WHERE email = ?",
                         (reset_token, expires_at, now_str, email.lower().strip()))
            conn.execute("""
                INSERT INTO password_reset_tokens (reset_id, user_id, token, expires_at, is_used, created_at)
                VALUES (?, ?, ?, ?, 0, ?)
            """, (reset_id, user["user_id"], reset_token, expires_at, now_str))
            conn.commit()
        return reset_token

    @staticmethod
    def reset_password(reset_token: str, new_password: str) -> bool:
        if len(new_password) < 6:
            raise ValueError("Password must be at least 6 characters long.")
            
        now = datetime.now(timezone.utc)
        now_str = now.isoformat()
        
        with get_db_connection() as conn:
            user = conn.execute("SELECT * FROM users WHERE reset_token = ?", (reset_token,)).fetchone()
            if not user:
                # Also check password_reset_tokens table for consistency
                tok_row = conn.execute("SELECT * FROM password_reset_tokens WHERE token = ? AND is_used = 0", (reset_token,)).fetchone()
                if tok_row:
                    tok_d = dict(tok_row)
                    if tok_d["expires_at"] >= now_str:
                        user = conn.execute("SELECT * FROM users WHERE user_id = ?", (tok_d["user_id"],)).fetchone()
            
            if not user:
                return False
                
            exp_str = user.get("reset_token_expires") if isinstance(user, dict) else user["reset_token_expires"]
            if exp_str:
                try:
                    exp_dt = datetime.fromisoformat(exp_str)
                    if now > exp_dt:
                        return False # Token expired
                except Exception:
                    pass
                    
            pw_hash, salt = hash_password(new_password)
            u_id = user["user_id"]
            conn.execute("""
                UPDATE users SET password_hash = ?, salt = ?, reset_token = NULL, reset_token_expires = NULL, updated_at = ?
                WHERE user_id = ?
            """, (pw_hash, salt, now_str, u_id))
            conn.execute("UPDATE password_reset_tokens SET is_used = 1 WHERE token = ?", (reset_token,))
            conn.commit()
            return True

    @staticmethod
    def create_session(user_id: str, device_id: str = "default_device", device_name: str = "Desktop Workstation") -> Dict[str, Any]:
        token = f"sess_{secrets.token_urlsafe(32)}"
        now = datetime.now(timezone.utc)
        expires_at = (now + timedelta(days=30)).isoformat()
        now_str = now.isoformat()
        
        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO sessions (session_token, user_id, device_id, device_name, created_at, expires_at, last_active_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (token, user_id, device_id, device_name, now_str, expires_at, now_str))
            
            # Register device binding
            conn.execute("""
                INSERT INTO devices (device_id, user_id, device_fingerprint, device_name, os_info, first_seen, last_seen, status)
                VALUES (?, ?, ?, ?, 'Windows Desktop', ?, ?, 'ACTIVE')
                ON CONFLICT (device_id) DO UPDATE SET
                    user_id = excluded.user_id,
                    device_fingerprint = excluded.device_fingerprint,
                    device_name = excluded.device_name,
                    last_seen = excluded.last_seen,
                    status = excluded.status
            """, (device_id, user_id, device_id, device_name, now_str, now_str))
            conn.commit()
            
        return {"session_token": token, "expires_at": expires_at}

    @staticmethod
    def get_session(session_token: str) -> Optional[Dict[str, Any]]:
        with get_db_connection() as conn:
            row = conn.execute("""
                SELECT s.*, u.email, u.full_name, u.role, u.subscription_plan, u.is_verified
                FROM sessions s
                JOIN users u ON s.user_id = u.user_id
                WHERE s.session_token = ?
            """, (session_token,)).fetchone()
            if not row:
                return None
            s_dict = dict(row)
            exp_raw = s_dict["expires_at"]
            if isinstance(exp_raw, datetime):
                expires_dt = exp_raw if exp_raw.tzinfo else exp_raw.replace(tzinfo=timezone.utc)
            else:
                expires_dt = datetime.fromisoformat(str(exp_raw))
                if expires_dt.tzinfo is None:
                    expires_dt = expires_dt.replace(tzinfo=timezone.utc)
            if expires_dt < datetime.now(timezone.utc):
                return None # Expired
            s_dict["expires_at"] = expires_dt.isoformat()
            return s_dict

    @staticmethod
    def list_user_devices(user_id: str) -> List[Dict[str, Any]]:
        with get_db_connection() as conn:
            rows = conn.execute("SELECT * FROM devices WHERE user_id = ?", (user_id,)).fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def revoke_device(user_id: str, device_id: str):
        with get_db_connection() as conn:
            conn.execute("UPDATE devices SET status = 'REVOKED' WHERE user_id = ? AND device_id = ?", (user_id, device_id))
            conn.execute("DELETE FROM sessions WHERE user_id = ? AND device_id = ?", (user_id, device_id))
            conn.commit()

    @staticmethod
    def revoke_session(session_token: str):
        with get_db_connection() as conn:
            conn.execute("DELETE FROM sessions WHERE session_token = ?", (session_token,))
            conn.commit()

    @staticmethod
    def revoke_all_user_sessions(user_id: str):
        with get_db_connection() as conn:
            conn.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
            conn.commit()

    @staticmethod
    def update_user_plan(user_id: str, plan: str):
        with get_db_connection() as conn:
            conn.execute("UPDATE users SET subscription_plan = ?, updated_at = ? WHERE user_id = ?",
                         (plan, datetime.now(timezone.utc).isoformat(), user_id))
            conn.commit()

    @staticmethod
    def delete_account(user_id: str):
        with get_db_connection() as conn:
            conn.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
            conn.execute("DELETE FROM devices WHERE user_id = ?", (user_id,))
            conn.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            conn.commit()
