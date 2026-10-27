import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from app.intelligence.voice.voice_providers import (
    stt_provider,
    tts_provider,
    wakeword_provider,
    LocalSTTProvider,
    LocalTTSProvider,
    WakeWordProvider,
    WakeWordConfig
)
from app.intelligence.voice.voice_conversation_engine import (
    voice_conversation_engine,
    VoiceConversationEngine,
    VoiceState,
    VoiceConversationSessionState
)

logger = logging.getLogger("app.intelligence.voice_engine")

class VoiceProfile(BaseModel):
    id: str = "saarthi_voice_hi_en"
    name: str = "Saarthi AI Identity Voice"
    language: str = "en-IN"
    secondary_language: str = "hi-IN"
    accent: str = "Indian English + Hindi"
    gender: str = "Neutral Professional"
    provider: str = "Local Saarthi Voice Synthesizer"
    is_available: bool = True

class VoiceSession(BaseModel):
    session_id: str
    is_listening: bool = False
    wake_word_enabled: bool = False
    active_profile: VoiceProfile = Field(default_factory=VoiceProfile)
    state: str = "IDLE"

class WakeWordDetector:
    """Wake-word detector interface. Inactive by policy (No background listening without permission)."""
    @staticmethod
    def is_active() -> bool:
        return wakeword_provider.config.enabled

    @staticmethod
    def detect_wake_word(audio_chunk: bytes) -> bool:
        return wakeword_provider.detect_wake_word(audio_chunk)

class VoiceEngine:
    @staticmethod
    def get_voice_profile() -> VoiceProfile:
        return VoiceProfile()

    @staticmethod
    def synthesize_speech(text: str, language: str = "en-IN") -> Dict[str, Any]:
        """Synthesizes speech output using the TTS provider."""
        res = tts_provider.synthesize(text=text, language=language)
        return {
            "status": "synthesized",
            "voice_id": res.voice_id,
            "audio_format": res.audio_format,
            "text": text,
            "audio_id": res.audio_id,
            "duration_seconds": res.duration_seconds,
            "simulated": False
        }

voice_engine = VoiceEngine()
