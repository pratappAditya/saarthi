import sqlite3
import os
import json
import time
import logging
from typing import Dict, Any, List, Optional
from app.intelligence.personalization.personalization_model import (
    UserPersonalizationProfile,
    PreferenceItem,
    PreferenceSource,
    DomainExpertise,
    ExpertiseLevel
)
from app.db.connection import get_db_connection
from app.config.settings import settings

logger = logging.getLogger("app.intelligence.personalization_store")

class PersonalizationStore:
    """
    Persistence Store for User Personalization Profiles, Explicit & Inferred Preferences,
    Domain Expertise Metrics, and Project-Scoped Overrides.
    """
    def __init__(self, db_path: Optional[str] = None):
        self._db_path = db_path
        self._init_tables()

    @property
    def db_path(self) -> str:
        return self._db_path or settings.DATABASE_PATH

    @db_path.setter
    def db_path(self, val: str):
        self._db_path = val

    def _get_connection(self):
        return get_db_connection(self.db_path)

    def _init_tables(self):
        conn = self._get_connection()
        try:
            with conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS user_personalization_profile (
                        user_id TEXT PRIMARY KEY,
                        communication_style TEXT NOT NULL,
                        preferred_response_length TEXT NOT NULL,
                        technical_depth TEXT NOT NULL,
                        preferred_languages TEXT NOT NULL,
                        preferred_tone TEXT NOT NULL,
                        preferred_formatting TEXT NOT NULL,
                        decision_making_style TEXT NOT NULL,
                        autonomy_preference TEXT NOT NULL,
                        confirmation_preference TEXT NOT NULL,
                        proactivity_preference TEXT NOT NULL,
                        preferred_working_hours TEXT NOT NULL,
                        preferred_tools TEXT NOT NULL,
                        preferred_workflows TEXT NOT NULL,
                        learning_interests TEXT NOT NULL,
                        recurring_objectives TEXT NOT NULL,
                        explicit_preferences TEXT NOT NULL,
                        personalization_enabled INTEGER NOT NULL DEFAULT 1,
                        learning_enabled INTEGER NOT NULL DEFAULT 1,
                        inference_enabled INTEGER NOT NULL DEFAULT 1,
                        proactive_learning_enabled INTEGER NOT NULL DEFAULT 1,
                        voice_personalization_enabled INTEGER NOT NULL DEFAULT 1,
                        updated_at REAL NOT NULL
                    );
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS personalization_preferences (
                        id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        key TEXT NOT NULL,
                        category TEXT NOT NULL,
                        value TEXT NOT NULL,
                        source TEXT NOT NULL,
                        confidence REAL NOT NULL,
                        evidence TEXT NOT NULL,
                        created_at REAL NOT NULL,
                        last_observed REAL NOT NULL,
                        decay_seconds REAL,
                        confirmed INTEGER NOT NULL DEFAULT 0,
                        rejected INTEGER NOT NULL DEFAULT 0,
                        affected_behavior TEXT NOT NULL,
                        UNIQUE(user_id, key)
                    );
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS domain_expertise (
                        id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        domain TEXT NOT NULL,
                        level TEXT NOT NULL,
                        confidence REAL NOT NULL,
                        evidence TEXT NOT NULL,
                        last_updated REAL NOT NULL,
                        explicit_override INTEGER NOT NULL DEFAULT 0,
                        UNIQUE(user_id, domain)
                    );
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS project_personalization_overrides (
                        id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        project_id TEXT NOT NULL,
                        key TEXT NOT NULL,
                        value TEXT NOT NULL,
                        updated_at REAL NOT NULL,
                        UNIQUE(user_id, project_id, key)
                    );
                """)
        finally:
            conn.close()

    def get_profile(self, user_id: str = "default_local_user") -> UserPersonalizationProfile:
        conn = self._get_connection()
        try:
            row = conn.execute("SELECT * FROM user_personalization_profile WHERE user_id = ?", (user_id,)).fetchone()
            if not row:
                # Initialize default profile
                default_prof = UserPersonalizationProfile(user_id=user_id)
                self.save_profile(default_prof)
                return default_prof

            d = dict(row)
            # Parse JSON fields
            d["preferred_languages"] = json.loads(d["preferred_languages"])
            d["preferred_tools"] = json.loads(d["preferred_tools"])
            d["preferred_workflows"] = json.loads(d["preferred_workflows"])
            d["learning_interests"] = json.loads(d["learning_interests"])
            d["recurring_objectives"] = json.loads(d["recurring_objectives"])
            d["explicit_preferences"] = json.loads(d["explicit_preferences"])

            # Map boolean toggles
            d["personalization_enabled"] = bool(d["personalization_enabled"])
            d["learning_enabled"] = bool(d["learning_enabled"])
            d["inference_enabled"] = bool(d["inference_enabled"])
            d["proactive_learning_enabled"] = bool(d["proactive_learning_enabled"])
            d["voice_personalization_enabled"] = bool(d["voice_personalization_enabled"])

            # Fetch domain expertise
            exp_rows = conn.execute("SELECT * FROM domain_expertise WHERE user_id = ?", (user_id,)).fetchall()
            domain_exp = {}
            for erow in exp_rows:
                ed = dict(erow)
                domain_exp[ed["domain"]] = DomainExpertise(
                    domain=ed["domain"],
                    level=ExpertiseLevel(ed["level"]),
                    confidence=ed["confidence"],
                    evidence=ed["evidence"],
                    last_updated=ed["last_updated"],
                    explicit_override=bool(ed["explicit_override"])
                )
            d["domain_expertise"] = domain_exp

            # Fetch inferred preferences
            pref_rows = conn.execute("SELECT * FROM personalization_preferences WHERE user_id = ? AND rejected = 0", (user_id,)).fetchall()
            inferred_prefs = {}
            for prow in pref_rows:
                pd = dict(prow)
                val = pd["value"]
                try:
                    val = json.loads(val)
                except Exception:
                    pass

                inferred_prefs[pd["key"]] = PreferenceItem(
                    key=pd["key"],
                    category=pd["category"],
                    value=val,
                    source=PreferenceSource(pd["source"]),
                    confidence=pd["confidence"],
                    evidence=pd["evidence"],
                    created_at=pd["created_at"],
                    last_observed=pd["last_observed"],
                    decay_seconds=pd["decay_seconds"],
                    confirmed=bool(pd["confirmed"]),
                    rejected=bool(pd["rejected"]),
                    affected_behavior=pd["affected_behavior"]
                )
            d["inferred_preferences"] = inferred_prefs

            return UserPersonalizationProfile(**d)
        finally:
            conn.close()

    def save_profile(self, profile: UserPersonalizationProfile):
        conn = self._get_connection()
        try:
            with conn:
                conn.execute("""
                    INSERT OR REPLACE INTO user_personalization_profile (
                        user_id, communication_style, preferred_response_length, technical_depth,
                        preferred_languages, preferred_tone, preferred_formatting, decision_making_style,
                        autonomy_preference, confirmation_preference, proactivity_preference,
                        preferred_working_hours, preferred_tools, preferred_workflows,
                        learning_interests, recurring_objectives, explicit_preferences,
                        personalization_enabled, learning_enabled, inference_enabled,
                        proactive_learning_enabled, voice_personalization_enabled, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    profile.user_id, profile.communication_style, profile.preferred_response_length,
                    profile.technical_depth, json.dumps(profile.preferred_languages), profile.preferred_tone,
                    profile.preferred_formatting, profile.decision_making_style, profile.autonomy_preference,
                    profile.confirmation_preference, profile.proactivity_preference, profile.preferred_working_hours,
                    json.dumps(profile.preferred_tools), json.dumps(profile.preferred_workflows),
                    json.dumps(profile.learning_interests), json.dumps(profile.recurring_objectives),
                    json.dumps(profile.explicit_preferences), int(profile.personalization_enabled),
                    int(profile.learning_enabled), int(profile.inference_enabled),
                    int(profile.proactive_learning_enabled), int(profile.voice_personalization_enabled),
                    time.time()
                ))
        finally:
            conn.close()

    def set_explicit_preference(self, user_id: str, key: str, value: Any, category: str = "general") -> PreferenceItem:
        profile = self.get_profile(user_id)
        profile.explicit_preferences[key] = value

        # Update profile attributes if matching
        if hasattr(profile, key):
            setattr(profile, key, value)

        self.save_profile(profile)

        # Also store in preference items table as USER_EXPLICIT
        item = PreferenceItem(
            key=key,
            category=category,
            value=value,
            source=PreferenceSource.USER_EXPLICIT,
            confidence=1.0,
            evidence="Explicitly set by user",
            confirmed=True,
            rejected=False
        )
        self.save_preference_item(user_id, item)
        return item

    def record_inferred_preference(
        self,
        user_id: str,
        key: str,
        category: str,
        value: Any,
        confidence: float,
        evidence: str,
        decay_seconds: Optional[float] = 30 * 86400
    ) -> Optional[PreferenceItem]:
        profile = self.get_profile(user_id)
        if not profile.learning_enabled or not profile.inference_enabled:
            logger.info(f"Learning/Inference disabled for user '{user_id}'. Ignored inferred preference '{key}'.")
            return None

        # Check if already explicit or rejected
        existing = profile.inferred_preferences.get(key)
        if existing and (existing.source == PreferenceSource.USER_EXPLICIT or existing.rejected):
            return existing

        item = PreferenceItem(
            key=key,
            category=category,
            value=value,
            source=PreferenceSource.MODEL_INFERRED,
            confidence=confidence,
            evidence=evidence,
            decay_seconds=decay_seconds,
            confirmed=False,
            rejected=False
        )
        self.save_preference_item(user_id, item)
        return item

    def save_preference_item(self, user_id: str, item: PreferenceItem):
        conn = self._get_connection()
        try:
            item_id = f"pref_{user_id}_{item.key}"
            val_str = json.dumps(item.value) if not isinstance(item.value, str) else item.value
            with conn:
                conn.execute("""
                    INSERT OR REPLACE INTO personalization_preferences (
                        id, user_id, key, category, value, source, confidence, evidence,
                        created_at, last_observed, decay_seconds, confirmed, rejected, affected_behavior
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    item_id, user_id, item.key, item.category, val_str, item.source.value,
                    item.confidence, item.evidence, item.created_at, item.last_observed,
                    item.decay_seconds, int(item.confirmed), int(item.rejected), item.affected_behavior
                ))
        finally:
            conn.close()

    def confirm_preference(self, user_id: str, key: str) -> bool:
        conn = self._get_connection()
        try:
            with conn:
                cur = conn.execute("""
                    UPDATE personalization_preferences
                    SET confirmed = 1, source = ?, confidence = 1.0, last_observed = ?
                    WHERE user_id = ? AND key = ?
                """, (PreferenceSource.USER_CONFIRMED.value, time.time(), user_id, key))
                return cur.rowcount > 0
        finally:
            conn.close()

    def reject_preference(self, user_id: str, key: str) -> bool:
        conn = self._get_connection()
        try:
            with conn:
                cur = conn.execute("""
                    UPDATE personalization_preferences
                    SET rejected = 1, confidence = 0.0, last_observed = ?
                    WHERE user_id = ? AND key = ?
                """, (time.time(), user_id, key))
                return cur.rowcount > 0
        finally:
            conn.close()

    def forget_preference(self, user_id: str, key: str) -> bool:
        conn = self._get_connection()
        try:
            with conn:
                cur = conn.execute("DELETE FROM personalization_preferences WHERE user_id = ? AND key = ?", (user_id, key))
                # Also remove from explicit_preferences
                profile = self.get_profile(user_id)
                if key in profile.explicit_preferences:
                    del profile.explicit_preferences[key]
                    self.save_profile(profile)
                return cur.rowcount > 0
        finally:
            conn.close()

    def set_domain_expertise(
        self,
        user_id: str,
        domain: str,
        level: ExpertiseLevel,
        confidence: float = 0.9,
        evidence: str = "Direct assessment or override",
        explicit_override: bool = False
    ) -> DomainExpertise:
        conn = self._get_connection()
        try:
            exp_id = f"exp_{user_id}_{domain}"
            now = time.time()
            with conn:
                conn.execute("""
                    INSERT OR REPLACE INTO domain_expertise (
                        id, user_id, domain, level, confidence, evidence, last_updated, explicit_override
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    exp_id, user_id, domain, level.value, confidence, evidence, now, int(explicit_override)
                ))
            return DomainExpertise(
                domain=domain,
                level=level,
                confidence=confidence,
                evidence=evidence,
                last_updated=now,
                explicit_override=explicit_override
            )
        finally:
            conn.close()

    def set_project_override(self, user_id: str, project_id: str, key: str, value: Any):
        conn = self._get_connection()
        try:
            ov_id = f"proj_ov_{user_id}_{project_id}_{key}"
            val_str = json.dumps(value) if not isinstance(value, str) else value
            with conn:
                conn.execute("""
                    INSERT OR REPLACE INTO project_personalization_overrides (
                        id, user_id, project_id, key, value, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (ov_id, user_id, project_id, key, val_str, time.time()))
        finally:
            conn.close()

    def get_project_overrides(self, user_id: str, project_id: str) -> Dict[str, Any]:
        conn = self._get_connection()
        try:
            rows = conn.execute(
                "SELECT key, value FROM project_personalization_overrides WHERE user_id = ? AND project_id = ?",
                (user_id, project_id)
            ).fetchall()
            res = {}
            for r in rows:
                k, v = r["key"], r["value"]
                try:
                    v = json.loads(v)
                except Exception:
                    pass
                res[k] = v
            return res
        finally:
            conn.close()

    def reset_category(self, user_id: str, category: str):
        conn = self._get_connection()
        try:
            with conn:
                conn.execute("DELETE FROM personalization_preferences WHERE user_id = ? AND category = ?", (user_id, category))
        finally:
            conn.close()

    def reset_all(self, user_id: str):
        conn = self._get_connection()
        try:
            with conn:
                conn.execute("DELETE FROM user_personalization_profile WHERE user_id = ?", (user_id,))
                conn.execute("DELETE FROM personalization_preferences WHERE user_id = ?", (user_id,))
                conn.execute("DELETE FROM domain_expertise WHERE user_id = ?", (user_id,))
                conn.execute("DELETE FROM project_personalization_overrides WHERE user_id = ?", (user_id,))
        finally:
            conn.close()

personalization_store = PersonalizationStore()
