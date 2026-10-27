import os
import json
import logging
from typing import Dict, Any, Optional
from app.db.connection import get_db_connection, with_db_retry

logger = logging.getLogger("app.core.feature_flags")

DEFAULT_FEATURE_FLAGS = {
    "voice": True,
    "advanced_voice": True,
    "agents": True,
    "automation": True,
    "research": True,
    "multimodal": True,
    "domain_packs": True,
    "teams": True,
    "billing": False,  # Live billing disabled by default until funding
    "experimental_features": False,
}

class FeatureFlagManager:
    def __init__(self):
        self._initialized = False

    @with_db_retry()
    def _ensure_init(self):
        if self._initialized:
            return
        try:
            with get_db_connection() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS feature_flags (
                        key TEXT PRIMARY KEY,
                        enabled INTEGER NOT NULL DEFAULT 1,
                        rollout_percentage INTEGER NOT NULL DEFAULT 100,
                        description TEXT DEFAULT '',
                        updated_at TEXT NOT NULL
                    )
                """)
                conn.commit()
                
                # Seed defaults if empty
                for key, enabled in DEFAULT_FEATURE_FLAGS.items():
                    conn.execute("""
                        INSERT INTO feature_flags (key, name, enabled, rollout_percentage, description, updated_at)
                        VALUES (?, ?, ?, 100, ?, datetime('now'))
                        ON CONFLICT (key) DO NOTHING
                    """, (key, key.upper(), 1 if enabled else 0, f"System feature flag: {key}"))
                conn.commit()
            self._initialized = True
        except Exception as e:
            logger.warning(f"Feature flags lazy init warning: {e}")

    def is_enabled(self, key: str, default: bool = False) -> bool:
        self._ensure_init()
        try:
            with get_db_connection() as conn:
                row = conn.execute("SELECT enabled FROM feature_flags WHERE key = ?", (key,)).fetchone()
                if row:
                    return bool(row[0])
        except Exception as e:
            logger.error(f"Error reading feature flag {key}: {e}")
        return DEFAULT_FEATURE_FLAGS.get(key, default)

    def set_flag(self, key: str, enabled: bool, rollout_percentage: int = 100) -> bool:
        self._ensure_init()
        try:
            with get_db_connection() as conn:
                conn.execute("""
                    INSERT INTO feature_flags (key, name, enabled, rollout_percentage, updated_at)
                    VALUES (?, ?, ?, ?, datetime('now'))
                    ON CONFLICT(key) DO UPDATE SET
                        enabled = excluded.enabled,
                        rollout_percentage = excluded.rollout_percentage,
                        updated_at = datetime('now')
                """, (key, key.upper(), 1 if enabled else 0, rollout_percentage))
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error setting feature flag {key}: {e}")
            return False

    def get_all_flags(self) -> Dict[str, Any]:
        self._ensure_init()
        flags = dict(DEFAULT_FEATURE_FLAGS)
        try:
            with get_db_connection() as conn:
                rows = conn.execute("SELECT key, enabled, rollout_percentage, updated_at FROM feature_flags").fetchall()
                for row in rows:
                    flags[row["key"]] = {
                        "enabled": bool(row["enabled"]),
                        "rollout_percentage": row["rollout_percentage"],
                        "updated_at": row["updated_at"]
                    }
        except Exception as e:
            logger.error(f"Error fetching all feature flags: {e}")
        return flags

feature_flag_manager = FeatureFlagManager()
