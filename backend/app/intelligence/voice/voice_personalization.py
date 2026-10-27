"""
Saarthi Voice Personalization Engine.
Manages user voice preferences (rate, pitch, response length, auto-punctuation)
and enforces resolution precedence:
Task -> Project -> Domain -> Global -> System.
"""

from typing import Dict, Any, Optional
from app.intelligence.voice.models import VoicePersonalizationSettings, VoiceLanguageCode


class VoicePersonalizationManager:
    """Manages voice personalization settings with multi-tier precedence."""

    def __init__(self):
        self._user_settings: Dict[str, VoicePersonalizationSettings] = {}

    def get_settings(self, user_id: str = "default_local_user") -> VoicePersonalizationSettings:
        if user_id not in self._user_settings:
            self._user_settings[user_id] = VoicePersonalizationSettings(user_id=user_id)
        return self._user_settings[user_id]

    def update_settings(
        self,
        user_id: str,
        preferred_language: Optional[str] = None,
        preferred_response_language: Optional[str] = None,
        speaking_rate: Optional[float] = None,
        voice_gender: Optional[str] = None,
        response_length: Optional[str] = None,
        auto_punctuation: Optional[bool] = None,
        spoken_confirmations: Optional[bool] = None,
        save_raw_audio: Optional[bool] = None
    ) -> VoicePersonalizationSettings:
        settings = self.get_settings(user_id)

        if preferred_language is not None:
            settings.preferred_language = preferred_language
        if preferred_response_language is not None:
            settings.preferred_response_language = preferred_response_language
        if speaking_rate is not None:
            settings.speaking_rate = max(0.5, min(2.0, speaking_rate))
        if voice_gender is not None:
            settings.voice_gender = voice_gender
        if response_length is not None:
            settings.response_length = response_length
        if auto_punctuation is not None:
            settings.auto_punctuation = auto_punctuation
        if spoken_confirmations is not None:
            settings.spoken_confirmations = spoken_confirmations
        if save_raw_audio is not None:
            settings.save_raw_audio = save_raw_audio

        self._user_settings[user_id] = settings
        return settings

    def resolve_effective_settings(
        self,
        user_id: str = "default_local_user",
        domain: Optional[str] = None,
        task_overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Resolves effective settings respecting precedence:
        Task -> Domain -> Global User -> System Default.
        """
        base = self.get_settings(user_id).model_dump()

        # Domain overrides
        if domain == "software":
            base["response_length"] = "concise"
        elif domain in ("education", "research"):
            base["response_length"] = "detailed"

        # Task overrides
        if task_overrides:
            for k, v in task_overrides.items():
                if v is not None and k in base:
                    base[k] = v

        return base


voice_personalization = VoicePersonalizationManager()
