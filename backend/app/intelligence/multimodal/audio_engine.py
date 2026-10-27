import logging
import uuid
import time
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("app.intelligence.audio_engine")

class TranscriptionResult(BaseModel):
    text: str
    confidence: float = 0.95
    language: str = "en-IN"
    duration_seconds: float = 2.5
    timestamps: List[Dict[str, Any]] = Field(default_factory=list)

class AudioSynthesisResult(BaseModel):
    audio_id: str
    text: str
    voice_id: str = "saarthi_voice_hi_en"
    audio_format: str = "wav"
    audio_bytes: bytes = b""
    duration_seconds: float = 2.0

class VoiceSessionState(BaseModel):
    session_id: str
    is_active: bool = False
    is_listening: bool = False
    is_speaking: bool = False
    mic_permission_granted: bool = True
    active_transcript: str = ""
    last_user_speech: str = ""

class VoiceSessionManager:
    def __init__(self):
        self.active_sessions: Dict[str, VoiceSessionState] = {}

    def start_session(self, user_id: str = "default_user") -> VoiceSessionState:
        session_id = f"vsession_{uuid.uuid4().hex[:8]}"
        state = VoiceSessionState(
            session_id=session_id,
            is_active=True,
            is_listening=True,
            is_speaking=False,
            mic_permission_granted=True
        )
        self.active_sessions[session_id] = state
        return state

    def stop_session(self, session_id: str) -> Optional[VoiceSessionState]:
        state = self.active_sessions.get(session_id)
        if state:
            state.is_active = False
            state.is_listening = False
            state.is_speaking = False
        return state

    def interrupt_speech(self, session_id: str) -> Optional[VoiceSessionState]:
        """Barge-in architecture: stops TTS playback when user starts speaking."""
        state = self.active_sessions.get(session_id)
        if state:
            state.is_speaking = False
            state.is_listening = True
        return state

class LocalSTTProvider:
    def transcribe(self, audio_bytes: bytes) -> TranscriptionResult:
        if not audio_bytes:
            return TranscriptionResult(text="", confidence=0.0, duration_seconds=0.0)

        return TranscriptionResult(
            text="Transcribed user speech input from audio stream.",
            confidence=0.96,
            language="en-IN",
            duration_seconds=3.2,
            timestamps=[{"word": "Transcribed", "start": 0.0, "end": 0.5}]
        )

class LocalTTSProvider:
    def synthesize(self, text: str, voice_id: str = "saarthi_voice_hi_en") -> AudioSynthesisResult:
        audio_id = f"tts_{uuid.uuid4().hex[:8]}"
        return AudioSynthesisResult(
            audio_id=audio_id,
            text=text,
            voice_id=voice_id,
            audio_format="wav",
            audio_bytes=b"RIFF_SAMPLE_WAV_HEADER_DATA",
            duration_seconds=2.5
        )

stt_engine = LocalSTTProvider()
tts_engine = LocalTTSProvider()
voice_session_manager = VoiceSessionManager()
