"""
Voice API Router for Saarthi.
Provides REST endpoints for speech recognition, neural synthesis,
conversational sessions, barge-in interruption, dictionary management,
and voice personalization.
"""

import base64
import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Response
from pydantic import BaseModel

from app.core.entitlements import require_capability
from app.intelligence.voice.voice_engine import voice_engine, VoiceProfile
from app.intelligence.voice.voice_conversation_engine import voice_conversation_engine, VoiceState
from app.intelligence.voice.voice_providers import (
    stt_provider,
    tts_provider,
    wakeword_provider
)
from app.intelligence.voice.stt_provider import real_stt_provider
from app.intelligence.voice.tts_provider import real_tts_provider
from app.intelligence.voice.audio_capture import audio_capture
from app.intelligence.voice.voice_dictionary import voice_dictionary, VoiceDictionaryEntry
from app.intelligence.voice.voice_personalization import voice_personalization
from app.intelligence.voice.voice_history import voice_history_manager
from app.intelligence.voice.language_registry import language_registry

logger = logging.getLogger("app.api.voice_api")
router = APIRouter(prefix="/voice", tags=["voice"])


class VoiceStartSessionRequest(BaseModel):
    user_id: Optional[str] = "default_local_user"
    hands_free: Optional[bool] = False
    push_to_talk: Optional[bool] = False


class VoiceTurnRequest(BaseModel):
    session_id: str
    text_override: Optional[str] = None
    language_hint: Optional[str] = "en-IN"
    permission_granted: Optional[bool] = False
    attachment_id: Optional[str] = None
    application_name: Optional[str] = "Desktop"


class VoiceInterruptRequest(BaseModel):
    session_id: str
    cancel_agent_task: Optional[bool] = False


class WakeWordConfigRequest(BaseModel):
    enabled: bool
    sensitivity: Optional[float] = 0.8


class VoiceDictionaryCreateRequest(BaseModel):
    word: str
    preferred_spelling: str
    pronunciation_hint: Optional[str] = None
    replacement: Optional[str] = None
    domain: Optional[str] = "general"
    user_id: Optional[str] = "default_local_user"


class VoicePersonalizationUpdateRequest(BaseModel):
    user_id: Optional[str] = "default_local_user"
    preferred_language: Optional[str] = None
    preferred_response_language: Optional[str] = None
    speaking_rate: Optional[float] = None
    voice_gender: Optional[str] = None
    response_length: Optional[str] = None
    auto_punctuation: Optional[bool] = None
    spoken_confirmations: Optional[bool] = None
    save_raw_audio: Optional[bool] = None


@router.get("/profile")
def get_voice_profile_endpoint():
    return {
        "profile": voice_engine.get_voice_profile().model_dump(),
        "stt_status": stt_provider.get_status(),
        "tts_status": tts_provider.get_status(),
        "wakeword_status": wakeword_provider.get_status(),
        "supported_languages": [p.model_dump() for p in language_registry.list_active_languages()]
    }


@router.post("/synthesize")
def synthesize_voice_endpoint(text: str, language: Optional[str] = "en-IN", return_binary: Optional[bool] = False):
    res = voice_engine.synthesize_speech(text=text, language=language or "en-IN")
    if return_binary:
        real_syn = real_tts_provider.synthesize(text=text, language=language or "en-IN")
        return Response(content=real_syn.audio_bytes, media_type="audio/wav")
    return res


@router.post("/transcribe")
async def transcribe_audio_endpoint(
    language_hint: Optional[str] = Form("en-IN"),
    audio_file: UploadFile = File(...)
):
    """Direct Speech-to-Text endpoint for audio upload."""
    content = await audio_file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty audio file provided.")

    res = real_stt_provider.transcribe(content, language_hint=language_hint or "en-IN")
    return {
        "raw_transcript": res.raw_transcript,
        "normalized_transcript": res.normalized_transcript,
        "detected_language": res.detected_language,
        "confidence": res.confidence,
        "duration_seconds": res.duration_seconds,
        "latency_ms": res.latency_ms,
        "tokens": [t.model_dump() for t in res.tokens]
    }


@router.get("/devices")
def list_audio_devices_endpoint():
    """Lists available system microphone devices."""
    devices = audio_capture.list_input_devices()
    return {"devices": devices, "status": audio_capture.get_status()}


@router.post("/session/start", dependencies=[Depends(require_capability("voice.saarthi"))])
def start_voice_session_endpoint(req: VoiceStartSessionRequest):
    session = voice_conversation_engine.start_session(
        user_id=req.user_id or "default_local_user",
        hands_free=req.hands_free or False,
        push_to_talk=req.push_to_talk or False
    )
    return {
        "session": session.model_dump(),
        "message": f"Voice session '{session.session_id}' started."
    }


@router.post("/session/stop")
def stop_voice_session_endpoint(session_id: str):
    session = voice_conversation_engine.stop_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Voice session not found.")
    return {"session": session.model_dump(), "message": "Voice session stopped cleanly."}


@router.get("/session/state")
def get_voice_session_state_endpoint(session_id: str):
    session = voice_conversation_engine.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Voice session not found.")
    return {"session": session.model_dump()}


@router.post("/session/turn")
def process_voice_turn_endpoint(req: VoiceTurnRequest):
    res = voice_conversation_engine.process_voice_turn(
        session_id=req.session_id,
        text_override=req.text_override,
        language_hint=req.language_hint or "en-IN",
        permission_granted=req.permission_granted or False,
        attachment_id=req.attachment_id,
        application_name=req.application_name or "Desktop"
    )
    return res


@router.post("/session/upload-turn")
async def upload_voice_turn_endpoint(
    session_id: str = Form(...),
    language_hint: Optional[str] = Form("en-IN"),
    permission_granted: Optional[bool] = Form(False),
    attachment_id: Optional[str] = Form(None),
    application_name: Optional[str] = Form("Desktop"),
    audio_file: UploadFile = File(...)
):
    content = await audio_file.read()
    res = voice_conversation_engine.process_voice_turn(
        session_id=session_id,
        audio_bytes=content,
        language_hint=language_hint or "en-IN",
        permission_granted=permission_granted or False,
        attachment_id=attachment_id,
        application_name=application_name or "Desktop"
    )
    return res


@router.post("/session/interrupt")
def interrupt_voice_session_endpoint(req: VoiceInterruptRequest):
    res = voice_conversation_engine.interrupt_speech(
        session_id=req.session_id,
        cancel_agent_task=req.cancel_agent_task or False
    )
    return res


@router.post("/session/push-to-talk/start")
def start_push_to_talk_endpoint(session_id: str):
    session = voice_conversation_engine.start_push_to_talk(session_id)
    return {"session": session.model_dump(), "message": "Push-to-Talk active. Recording..."}


@router.post("/session/push-to-talk/stop")
def stop_push_to_talk_endpoint(session_id: str, text_override: Optional[str] = None):
    res = voice_conversation_engine.stop_push_to_talk(session_id=session_id, audio_bytes=None)
    if text_override:
        res = voice_conversation_engine.process_voice_turn(session_id=session_id, text_override=text_override)
    return res


@router.post("/session/hands-free/start", dependencies=[Depends(require_capability("voice.realtime"))])
def start_hands_free_endpoint(session_id: str):
    session = voice_conversation_engine.start_hands_free(session_id)
    return {"session": session.model_dump(), "message": "Hands-Free Mode enabled."}


@router.post("/session/hands-free/stop")
def stop_hands_free_endpoint(session_id: str):
    session = voice_conversation_engine.stop_hands_free(session_id)
    return {"session": session.model_dump() if session else None, "message": "Hands-Free Mode disabled."}


@router.get("/wakeword/config")
def get_wakeword_config_endpoint():
    return {"config": wakeword_provider.get_status()}


@router.post("/wakeword/config", dependencies=[Depends(require_capability("voice.wake_word"))])
def update_wakeword_config_endpoint(req: WakeWordConfigRequest):
    cfg = wakeword_provider.update_config(enabled=req.enabled, sensitivity=req.sensitivity or 0.8)
    return {"config": wakeword_provider.get_status(), "message": "Wake-word configuration updated."}


# --- Voice Dictionary CRUD Endpoints ---

@router.get("/dictionary")
def list_voice_dictionary_endpoint(user_id: Optional[str] = "default_local_user"):
    entries = voice_dictionary.list_entries(user_id=user_id or "default_local_user")
    return {"entries": [e.model_dump() for e in entries]}


@router.post("/dictionary")
def add_voice_dictionary_endpoint(req: VoiceDictionaryCreateRequest):
    entry = voice_dictionary.add_entry(
        word=req.word,
        preferred_spelling=req.preferred_spelling,
        user_id=req.user_id or "default_local_user",
        pronunciation_hint=req.pronunciation_hint,
        replacement=req.replacement,
        domain=req.domain or "general"
    )
    return {"entry": entry.model_dump(), "message": "Dictionary term saved."}


@router.delete("/dictionary/{entry_id}")
def delete_voice_dictionary_endpoint(entry_id: str, user_id: Optional[str] = "default_local_user"):
    deleted = voice_dictionary.delete_entry(entry_id, user_id=user_id or "default_local_user")
    if not deleted:
        raise HTTPException(status_code=404, detail="Dictionary entry not found.")
    return {"deleted": True, "message": "Entry removed."}


# --- Voice Personalization Endpoints ---

@router.get("/personalization")
def get_voice_personalization_endpoint(user_id: Optional[str] = "default_local_user"):
    settings = voice_personalization.get_settings(user_id or "default_local_user")
    return {"settings": settings.model_dump()}


@router.post("/personalization")
def update_voice_personalization_endpoint(req: VoicePersonalizationUpdateRequest):
    updated = voice_personalization.update_settings(
        user_id=req.user_id or "default_local_user",
        preferred_language=req.preferred_language,
        preferred_response_language=req.preferred_response_language,
        speaking_rate=req.speaking_rate,
        voice_gender=req.voice_gender,
        response_length=req.response_length,
        auto_punctuation=req.auto_punctuation,
        spoken_confirmations=req.spoken_confirmations,
        save_raw_audio=req.save_raw_audio
    )
    return {"settings": updated.model_dump(), "message": "Voice personalization preferences updated."}


# --- Voice History Endpoints ---

@router.get("/history")
def get_voice_history_endpoint(
    session_id: Optional[str] = None,
    search: Optional[str] = None,
    user_id: Optional[str] = "default_local_user"
):
    history = voice_history_manager.get_history(
        user_id=user_id or "default_local_user",
        session_id=session_id,
        search_query=search
    )
    return {"history": [h.model_dump() for h in history]}


@router.delete("/history/{turn_id}")
def delete_voice_turn_endpoint(turn_id: str, user_id: Optional[str] = "default_local_user"):
    deleted = voice_history_manager.delete_turn(turn_id, user_id=user_id or "default_local_user")
    if not deleted:
        raise HTTPException(status_code=404, detail="Turn record not found.")
    return {"deleted": True, "message": "Voice turn deleted."}


@router.delete("/history")
def clear_voice_history_endpoint(
    session_id: Optional[str] = None,
    user_id: Optional[str] = "default_local_user"
):
    cleared_count = voice_history_manager.clear_history(
        user_id=user_id or "default_local_user",
        session_id=session_id
    )
    return {"cleared": True, "count": cleared_count, "message": "Voice conversation history cleared."}


@router.get("/privacy")
def get_voice_privacy_endpoint():
    return {
        "microphone_permission": "GRANTED",
        "active_sessions_count": len(voice_conversation_engine.sessions),
        "raw_audio_retention": "NO_RAW_AUDIO_STORED",
        "stt_provider": stt_provider.get_status(),
        "tts_provider": tts_provider.get_status(),
        "wakeword_status": wakeword_provider.get_status(),
        "local_only_processing": True
    }
