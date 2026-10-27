"""
Saarthi Voice 2.0 Models and Data Contracts.
Defines normalized structures for speech transcription, synthesis,
language identification, voice dictionary, personalization, and history.
"""

import time
import uuid
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class VoiceLanguageCode(str, Enum):
    ENGLISH_IN = "en-IN"
    HINDI_IN = "hi-IN"
    HINGLISH = "hi-en"
    ENGLISH_US = "en-US"
    BENGALI_IN = "bn-IN"
    TAMIL_IN = "ta-IN"
    TELUGU_IN = "te-IN"
    MARATHI_IN = "mr-IN"
    GUJARATI_IN = "gu-IN"


class VoiceState(str, Enum):
    IDLE = "IDLE"
    READY = "READY"
    REQUESTING_MIC_PERMISSION = "REQUESTING_MIC_PERMISSION"
    LISTENING = "LISTENING"
    TRANSCRIBING = "TRANSCRIBING"
    THINKING = "THINKING"
    WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL"
    EXECUTING = "EXECUTING"
    SPEAKING = "SPEAKING"
    INTERRUPTED = "INTERRUPTED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"


class AudioFormat(str, Enum):
    WAV = "wav"
    MP3 = "mp3"
    PCM = "pcm"


class VoiceDictionaryEntry(BaseModel):
    id: str = Field(default_factory=lambda: f"vdict_{uuid.uuid4().hex[:8]}")
    user_id: str = "default_local_user"
    word: str
    preferred_spelling: str
    pronunciation_hint: Optional[str] = None
    replacement: Optional[str] = None
    domain: Optional[str] = "general"
    created_at: float = Field(default_factory=time.time)


class VoicePersonalizationSettings(BaseModel):
    user_id: str = "default_local_user"
    preferred_language: str = VoiceLanguageCode.ENGLISH_IN.value
    preferred_response_language: str = "auto"  # auto, en-IN, hi-IN, hi-en
    speaking_rate: float = 1.0  # 0.75 to 1.5
    pitch: float = 1.0
    voice_gender: str = "neutral_professional"  # male, female, neutral_professional
    response_length: str = "balanced"  # concise, balanced, detailed
    auto_punctuation: bool = True
    paragraph_auto_split: bool = True
    spoken_confirmations: bool = True
    enable_voice_commands: bool = True
    save_raw_audio: bool = False  # Privacy default: do not retain raw audio


class SpeechToken(BaseModel):
    token: str
    start_time_s: float = 0.0
    end_time_s: float = 0.0
    confidence: float = 1.0


class RealTranscriptionResult(BaseModel):
    raw_transcript: str
    normalized_transcript: str
    detected_language: str = "en-IN"
    confidence: float = 0.95
    duration_seconds: float = 0.0
    is_partial: bool = False
    tokens: List[SpeechToken] = Field(default_factory=list)
    provider_name: str = "GoogleSpeechAPI"
    latency_ms: float = 0.0
    applied_commands: List[str] = Field(default_factory=list)


class RealAudioSynthesisResult(BaseModel):
    audio_id: str = Field(default_factory=lambda: f"tts_{uuid.uuid4().hex[:8]}")
    text: str
    voice_id: str
    language: str
    audio_format: AudioFormat = AudioFormat.WAV
    audio_bytes: bytes = b""
    duration_seconds: float = 0.0
    speaking_rate: float = 1.0
    provider_name: str = "EdgeTTSNeural"
    latency_ms: float = 0.0


class VoiceTurnRecord(BaseModel):
    turn_id: str = Field(default_factory=lambda: f"vturn_{uuid.uuid4().hex[:8]}")
    session_id: str
    user_id: str = "default_local_user"
    application_name: str = "Desktop"
    language: str = "en-IN"
    raw_transcript: str
    normalized_transcript: str
    assistant_response_text: str
    domain: str = "general"
    timestamp: float = Field(default_factory=time.time)
    duration_seconds: float = 0.0
    was_interrupted: bool = False
    status: str = "SUCCESS"  # SUCCESS, INTERRUPTED, CANCELLED, ERROR
    audio_retained: bool = False
    attachment_id: Optional[str] = None
    agent_task_id: Optional[str] = None
