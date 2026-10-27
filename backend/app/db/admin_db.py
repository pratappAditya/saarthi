import os
import sqlite3
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from app.config.settings import settings

from app.db.connection import get_db_connection

def init_admin_tables():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Admin Audit Log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id TEXT NOT NULL,
                action TEXT NOT NULL,
                target_user TEXT,
                details TEXT,
                ip_address TEXT DEFAULT '127.0.0.1',
                timestamp TEXT NOT NULL
            )
        """)
        try:
            cols = [row["name"] for row in cursor.execute("PRAGMA table_info(admin_audit_log)").fetchall()]
            if "ip_address" not in cols:
                cursor.execute("ALTER TABLE admin_audit_log ADD COLUMN ip_address TEXT DEFAULT '127.0.0.1'")
        except Exception:
            pass
        
        # 2. Feature Flags
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feature_flags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                enabled INTEGER NOT NULL DEFAULT 1,
                rollout_percentage INTEGER NOT NULL DEFAULT 100,
                description TEXT DEFAULT '',
                updated_by TEXT DEFAULT 'ADMIN',
                updated_at TEXT NOT NULL
            )
        """)
        
        # 3. Maintenance Mode
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS maintenance_mode (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                enabled INTEGER NOT NULL DEFAULT 0,
                message TEXT DEFAULT 'Saarthi is undergoing scheduled system maintenance.',
                bypass_whitelist TEXT DEFAULT '127.0.0.1',
                updated_by TEXT DEFAULT 'ADMIN',
                updated_at TEXT NOT NULL
            )
        """)
        
        # 4. Tool Policies
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tool_policies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_id TEXT UNIQUE NOT NULL,
                risk_classification TEXT NOT NULL DEFAULT 'LOW',
                permission_level TEXT NOT NULL DEFAULT 'AUTOMATIC',
                enabled INTEGER NOT NULL DEFAULT 1,
                updated_by TEXT DEFAULT 'ADMIN',
                updated_at TEXT NOT NULL
            )
        """)
        
        # 5. Support & User Feedback
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS support_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                feedback_type TEXT NOT NULL DEFAULT 'GENERAL',
                content TEXT NOT NULL,
                rating INTEGER,
                status TEXT NOT NULL DEFAULT 'OPEN',
                created_at TEXT NOT NULL
            )
        """)
        
        # 6. Organizations / Teams
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS organizations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                org_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                plan TEXT NOT NULL DEFAULT 'TEAMS',
                max_seats INTEGER NOT NULL DEFAULT 10,
                status TEXT NOT NULL DEFAULT 'ACTIVE',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # 7. IP & Device Ban List
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ip_bans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                identifier TEXT UNIQUE NOT NULL,
                ban_type TEXT NOT NULL DEFAULT 'IP',
                reason TEXT DEFAULT '',
                banned_by TEXT DEFAULT 'ADMIN',
                created_at TEXT NOT NULL
            )
        """)
        
                # 8. Entitlement Overrides
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entitlement_overrides (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE NOT NULL,
                plan_override TEXT,
                capabilities_json TEXT DEFAULT '{}',
                expires_at TEXT,
                created_by TEXT DEFAULT 'ADMIN',
                updated_at TEXT NOT NULL
            )
        """)

        # 9. Admin Users
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'ADMIN',
                full_name TEXT DEFAULT '',
                status TEXT NOT NULL DEFAULT 'ACTIVE',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # 10. Admin Roles
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role_name TEXT UNIQUE NOT NULL,
                permissions_json TEXT NOT NULL DEFAULT '[]',
                description TEXT DEFAULT ''
            )
        """)

        # 11. Admin Permissions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_permissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                permission_code TEXT UNIQUE NOT NULL,
                module TEXT NOT NULL,
                action TEXT NOT NULL
            )
        """)

        # 12. Admin Sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_token TEXT UNIQUE NOT NULL,
                admin_id TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                ip_address TEXT DEFAULT '127.0.0.1',
                created_at TEXT NOT NULL
            )
        """)

        # 13. Admin Audit Events (Immutable detailed operational audit)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                action TEXT NOT NULL,
                target TEXT DEFAULT '',
                reason TEXT DEFAULT '',
                previous_state TEXT DEFAULT '{}',
                resulting_state TEXT DEFAULT '{}',
                request_metadata TEXT DEFAULT '{}',
                status TEXT NOT NULL DEFAULT 'SUCCESS'
            )
        """)
        
        # Seed default feature flags if empty
        cursor.execute("SELECT COUNT(*) FROM feature_flags")
        if cursor.fetchone()[0] == 0:
            now_str = datetime.now(timezone.utc).isoformat()
            default_flags = [
                ("voice_barge_in", "Voice Barge-in Interruption", 1, 100, "Allows user voice barge-in during speech synthesis."),
                ("cross_domain_synthesis", "Cross-Domain Task Graphs", 1, 100, "Enables multi-domain task graph synthesis."),
                ("deep_personalization", "Deep Signal Learning", 1, 100, "Enables implicit preference signal learning."),
                ("proactive_jarvis", "Proactive Alert Engine", 1, 100, "Surfaces proactive goal and cross-domain suggestions."),
                ("experimental_nemotron_v3", "Nemotron 3 Ultra Tier", 0, 20, "Experimental 8B/14B Nemotron tier support.")
            ]
            for key, name, enabled, rollout, desc in default_flags:
                cursor.execute("""
                    INSERT INTO feature_flags (key, name, enabled, rollout_percentage, description, updated_by, updated_at)
                    VALUES (?, ?, ?, ?, ?, 'SYSTEM', ?)
                """, (key, name, enabled, rollout, desc, now_str))

        # Seed default admin roles if empty
        cursor.execute("SELECT COUNT(*) FROM admin_roles")
        if cursor.fetchone()[0] == 0:
            import json
            default_roles = [
                ("SUPER_ADMIN", json.dumps(["*"]), "Full operational control"),
                ("ADMIN", json.dumps(["users.*", "plans.*", "agents.*", "routines.*", "models.*", "domains.*", "diagnostics.*", "security.read"]), "Operations and management"),
                ("SUPPORT", json.dumps(["users.read", "users.diagnostics", "diagnostics.*", "security.read"]), "User support and read-only diagnostics"),
                ("ANALYST", json.dumps(["*.read", "dashboard.read", "metrics.read"]), "Read-only analytics and metrics")
            ]
            for r_name, p_json, desc in default_roles:
                cursor.execute("INSERT INTO admin_roles (role_name, permissions_json, description) VALUES (?, ?, ?)", (r_name, p_json, desc))
                
        conn.commit()
                
        # Seed default maintenance state if empty
        cursor.execute("SELECT COUNT(*) FROM maintenance_mode")
        if cursor.fetchone()[0] == 0:
            now_str = datetime.now(timezone.utc).isoformat()
            cursor.execute("""
                INSERT INTO maintenance_mode (enabled, message, bypass_whitelist, updated_by, updated_at)
                VALUES (0, 'Saarthi is undergoing scheduled system maintenance.', '127.0.0.1,admin@saarthi.ai', 'SYSTEM', ?)
            """, (now_str,))
            
        conn.commit()

class AdminRepository:
    @staticmethod
    def log_action(admin_id: str, action: str, target_user: Optional[str] = None, details: Optional[str] = None, ip_address: str = "127.0.0.1"):
        now_str = datetime.now(timezone.utc).isoformat()
        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO admin_audit_log (admin_id, action, target_user, details, ip_address, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (admin_id, action, target_user, details, ip_address, now_str))
            conn.commit()

    @staticmethod
    def list_audit_logs(limit: int = 100) -> List[Dict[str, Any]]:
        with get_db_connection() as conn:
            rows = conn.execute("SELECT * FROM admin_audit_log ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def list_feature_flags() -> List[Dict[str, Any]]:
        with get_db_connection() as conn:
            rows = conn.execute("SELECT * FROM feature_flags ORDER BY id ASC").fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def update_feature_flag(key: str, enabled: bool, rollout_percentage: int, admin_id: str = "ADMIN") -> Dict[str, Any]:
        now_str = datetime.now(timezone.utc).isoformat()
        with get_db_connection() as conn:
            conn.execute("""
                UPDATE feature_flags
                SET enabled = ?, rollout_percentage = ?, updated_by = ?, updated_at = ?
                WHERE key = ?
            """, (1 if enabled else 0, rollout_percentage, admin_id, now_str, key))
            conn.commit()
            row = conn.execute("SELECT * FROM feature_flags WHERE key = ?", (key,)).fetchone()
            return dict(row) if row else {}

    @staticmethod
    def get_maintenance_mode() -> Dict[str, Any]:
        with get_db_connection() as conn:
            row = conn.execute("SELECT * FROM maintenance_mode ORDER BY id DESC LIMIT 1").fetchone()
            return dict(row) if row else {"enabled": 0, "message": "", "bypass_whitelist": ""}

    @staticmethod
    def set_maintenance_mode(enabled: bool, message: str, bypass_whitelist: str, admin_id: str = "ADMIN") -> Dict[str, Any]:
        now_str = datetime.now(timezone.utc).isoformat()
        with get_db_connection() as conn:
            conn.execute("""
                UPDATE maintenance_mode
                SET enabled = ?, message = ?, bypass_whitelist = ?, updated_by = ?, updated_at = ?
            """, (1 if enabled else 0, message, bypass_whitelist, admin_id, now_str))
            conn.commit()
            return AdminRepository.get_maintenance_mode()

    @staticmethod
    def list_tool_policies() -> List[Dict[str, Any]]:
        with get_db_connection() as conn:
            rows = conn.execute("SELECT * FROM tool_policies ORDER BY tool_id ASC").fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def set_tool_policy(tool_id: str, risk_classification: str, permission_level: str, enabled: bool, admin_id: str = "ADMIN") -> Dict[str, Any]:
        now_str = datetime.now(timezone.utc).isoformat()
        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO tool_policies (tool_id, risk_classification, permission_level, enabled, updated_by, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(tool_id) DO UPDATE SET
                    risk_classification = excluded.risk_classification,
                    permission_level = excluded.permission_level,
                    enabled = excluded.enabled,
                    updated_by = excluded.updated_by,
                    updated_at = excluded.updated_at
            """, (tool_id, risk_classification, permission_level, 1 if enabled else 0, admin_id, now_str))
            conn.commit()
            row = conn.execute("SELECT * FROM tool_policies WHERE tool_id = ?", (tool_id,)).fetchone()
            return dict(row) if row else {}

    @staticmethod
    def list_support_feedback() -> List[Dict[str, Any]]:
        with get_db_connection() as conn:
            rows = conn.execute("SELECT * FROM support_feedback ORDER BY id DESC LIMIT 100").fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def submit_feedback(user_id: str, feedback_type: str, content: str, rating: Optional[int] = None) -> Dict[str, Any]:
        now_str = datetime.now(timezone.utc).isoformat()
        with get_db_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO support_feedback (user_id, feedback_type, content, rating, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, feedback_type, content, rating, now_str))
            conn.commit()
            row = conn.execute("SELECT * FROM support_feedback WHERE id = ?", (cursor.lastrowid,)).fetchone()
            return dict(row)

    @staticmethod
    def list_organizations() -> List[Dict[str, Any]]:
        with get_db_connection() as conn:
            rows = conn.execute("SELECT * FROM organizations ORDER BY id DESC").fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def create_organization(name: str, plan: str = "TEAMS", max_seats: int = 10) -> Dict[str, Any]:
        now_str = datetime.now(timezone.utc).isoformat()
        org_id = f"org_{int(datetime.now().timestamp() * 1000)}"
        with get_db_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO organizations (org_id, name, plan, max_seats, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (org_id, name, plan, max_seats, now_str, now_str))
            conn.commit()
            row = conn.execute("SELECT * FROM organizations WHERE org_id = ?", (org_id,)).fetchone()
            return dict(row)

    @staticmethod
    def list_ip_bans() -> List[Dict[str, Any]]:
        with get_db_connection() as conn:
            rows = conn.execute("SELECT * FROM ip_bans ORDER BY id DESC").fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def add_ip_ban(identifier: str, ban_type: str = "IP", reason: str = "", admin_id: str = "ADMIN") -> Dict[str, Any]:
        now_str = datetime.now(timezone.utc).isoformat()
        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO ip_bans (identifier, ban_type, reason, banned_by, created_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(identifier) DO UPDATE SET reason = excluded.reason
            """, (identifier, ban_type, reason, admin_id, now_str))
            conn.commit()
            row = conn.execute("SELECT * FROM ip_bans WHERE identifier = ?", (identifier,)).fetchone()
            return dict(row)

    @staticmethod
    def remove_ip_ban(identifier: str) -> bool:
        with get_db_connection() as conn:
            res = conn.execute("DELETE FROM ip_bans WHERE identifier = ?", (identifier,))
            conn.commit()
            return res.rowcount > 0

init_admin_tables()
