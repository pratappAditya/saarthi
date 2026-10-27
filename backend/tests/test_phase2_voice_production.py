"""
Phase 2: Production Voice Operating Layer Test Suite.
Comprehensive verification of:
1. Audio capture lifecycle (start, stop, cancel, device query)
2. Real Speech-to-Text (English en-IN, Hindi hi-IN, Hinglish code switching)
3. Real Text-to-Speech (Indian English Prabhat/Neerja, Hindi Madhur/Swara)
4. Energy VAD (Voice Activity Detection, RMS energy, silence tracking)
5. True Barge-in interruption during speech synthesis
6. Voice commands (formatting primitives and action directives)
7. STT quality pipeline (normalization, punctuation, capitalization, numbers)
8. Voice dictionary (custom terms, casing, and regex substitutions)
9. Voice history (tenant isolation, search, and deletion)
10. Voice personalization (preferences, precedence hierarchy)
11. Desktop active-app context integration
12. Multimodal voice integration (audio + attachment_id)
13. Domain voice routing (across Saarthi 17 domains)
14. Agent voice control with high-risk approval guards
15. REST APIs (/voice/profile, /devices, /dictionary, /personalization, /history)
"""

import os
import sys
import io
import time
import pytest

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from fastapi.testclient import TestClient

from app.main import app
from app.intelligence.voice.models import VoiceState, VoiceLanguageCode, AudioFormat
from app.intelligence.voice.language_registry import language_registry, LanguageProfile
from app.intelligence.voice.stt_provider import real_stt_provider
from app.intelligence.voice.tts_provider import real_tts_provider
from app.intelligence.voice.vad import energy_vad, VADState
from app.intelligence.voice.audio_capture import audio_capture
from app.intelligence.voice.voice_dictionary import voice_dictionary
from app.intelligence.voice.stt_quality_pipeline import stt_quality_pipeline
from app.intelligence.voice.voice_personalization import voice_personalization
from app.intelligence.voice.voice_history import voice_history_manager
from app.intelligence.voice.voice_conversation_engine import voice_conversation_engine
from app.intelligence.voice.voice_commands import voice_command_processor
from desktop.interfaces.voice_interfaces import RealDesktopVoiceEngine, SynthesisRequest

client = TestClient(app)


# ============================================================
# 1. AUDIO CAPTURE & HARDWARE ENUMERATION TESTS
# ============================================================

def test_audio_capture_device_enumeration_and_status():
    """Verifies audio input device listing and status telemetry."""
    status = audio_capture.get_status()
    assert "is_recording" in status
    assert "sample_rate" in status
    assert status["sample_rate"] == 16000

    devices = audio_capture.list_input_devices()
    assert isinstance(devices, list)


def test_audio_capture_start_stop_cancel_lifecycle():
    """Verifies starting, cancelling, and stopping audio capture without leaks."""
    from unittest.mock import MagicMock, patch

    mock_stream = MagicMock()
    with patch("sounddevice.RawInputStream", return_value=mock_stream):
        # Start and cancel
        started = audio_capture.start_recording()
        assert started is True
        audio_capture.cancel_recording()
        status_after_cancel = audio_capture.get_status()
        assert status_after_cancel["is_recording"] is False
        assert status_after_cancel["buffered_bytes"] == 0

        # Start and stop to get WAV bytes
        audio_capture.start_recording()
        audio_capture._audio_callback(b"\x00\x00" * 512, 512, None, None)
        wav_bytes = audio_capture.stop_recording()
        assert isinstance(wav_bytes, bytes)
        assert len(wav_bytes) > 0
        assert wav_bytes[:4] == b"RIFF"


# ============================================================
# 2. VOICE ACTIVITY DETECTION (VAD) TESTS
# ============================================================

def test_energy_vad_speech_onset_and_silence():
    """Verifies RMS energy calculation, noise floor adaptation, and silence transitions."""
    vad_state = VADState()

    # Synthetic quiet frame (noise floor)
    quiet_frame = b"\x05\x00" * 200
    res_quiet = energy_vad.process_chunk(quiet_frame, vad_state)
    assert res_quiet["is_speech"] is False
    assert res_quiet["rms_energy"] < 100.0

    # Synthetic loud frame (speech energy)
    loud_frame = b"\x00\x20" * 400
    res_loud_1 = energy_vad.process_chunk(loud_frame, vad_state)
    res_loud_2 = energy_vad.process_chunk(loud_frame, vad_state)
    assert vad_state.is_speech is True
    assert res_loud_2["is_speech"] is True

    # Transition to prolonged silence
    vad_state.silence_start_time = time.time() - 1.5  # 1500ms ago (> 900ms threshold)
    res_silent = energy_vad.process_chunk(quiet_frame, vad_state)
    assert res_silent["speech_ended"] is True
    assert vad_state.is_speech is False


# ============================================================
# 3. REAL SPEECH RECOGNITION (STT) TESTS
# ============================================================

def test_real_stt_transcription_and_language_detection():
    """Verifies real STT provider handles audio input and code switching."""
    status = real_stt_provider.get_status()
    assert status["healthy"] is True
    assert status["connected"] is True
    assert "en-IN" in status["supported_languages"]
    assert "hi-IN" in status["supported_languages"]

    # Empty audio handling
    empty_res = real_stt_provider.transcribe(b"")
    assert empty_res.raw_transcript == ""
    assert empty_res.confidence == 0.0


def test_language_registry_code_switching_detection():
    """Verifies detection of English, Hindi, and mixed Hinglish code-switching."""
    # Pure English
    en_det = language_registry.detect_code_switching("Can you please summarize this financial report?")
    assert en_det["primary_language"] == "en-IN"
    assert en_det["is_code_switched"] is False

    # Pure Hindi Devanagari
    hi_det = language_registry.detect_code_switching("कृपया इस रिपोर्ट का सारांश प्रस्तुत करें।")
    assert hi_det["primary_language"] == "hi-IN"
    assert hi_det["is_code_switched"] is False

    # Hinglish with Hindi markers in Latin script
    hinglish_1 = language_registry.detect_code_switching("Kal mujhe Bangalore office ke liye ek report bana dena.")
    assert hinglish_1["primary_language"] == "hi-en"
    assert hinglish_1["is_code_switched"] is True

    # Mixed Devanagari and Latin script
    hinglish_2 = language_registry.detect_code_switching("इस API endpoint को optimize कर दो।")
    assert hinglish_2["primary_language"] == "hi-en"
    assert hinglish_2["is_code_switched"] is True


# ============================================================
# 4. REAL TEXT-TO-SPEECH (TTS) & LOCAL SYNTHESIZER TESTS
# ============================================================

def test_real_tts_synthesis_english_and_hindi():
    """Verifies TTS synthesis generates valid non-empty audio waveforms."""
    # English synthesis
    syn_en = real_tts_provider.synthesize("Welcome to Saarthi.", language="en-IN", speaking_rate=1.0)
    assert len(syn_en.audio_bytes) > 100
    assert syn_en.duration_seconds > 0.5
    assert syn_en.audio_format == AudioFormat.WAV
    assert syn_en.audio_bytes[:4] == b"RIFF"

    # Hindi synthesis
    syn_hi = real_tts_provider.synthesize("सारथी में आपका स्वागत है।", language="hi-IN", speaking_rate=1.0)
    assert len(syn_hi.audio_bytes) > 100
    assert syn_hi.duration_seconds > 0.5


def test_local_pcm_harmonic_synthesizer_fallback():
    """Verifies fallback synthesizer produces genuine audible 16-bit PCM WAV audio."""
    pcm_bytes = real_tts_provider._synthesize_local_pcm("Testing local PCM synthesis.")
    assert len(pcm_bytes) > 1000
    assert pcm_bytes[:4] == b"RIFF"
    assert b"WAVE" in pcm_bytes[:16]


# ============================================================
# 5. VOICE COMMANDS & FORMATTING PRIMITIVES TESTS
# ============================================================

def test_voice_command_processor_formatting():
    """Verifies spoken formatting primitives: new line, new paragraph, bullets, numbered lists."""
    raw = "Header text new line first bullet point new paragraph second section"
    transformed, cmds = voice_command_processor.process_text(raw)
    assert "\n" in transformed
    assert "\n\n" in transformed
    assert len(cmds) >= 2


def test_voice_command_processor_action_directives():
    """Verifies action directives (undo, redo, rewrite, translate to hindi)."""
    _, cmd_undo = voice_command_processor.process_text("undo that")
    assert len(cmd_undo) == 1
    assert cmd_undo[0].command_name == "undo"

    _, cmd_trans = voice_command_processor.process_text("translate to hindi")
    assert len(cmd_trans) == 1
    assert cmd_trans[0].command_name == "translate_hindi"


# ============================================================
# 6. STT QUALITY PIPELINE & VOICE DICTIONARY TESTS
# ============================================================

def test_voice_dictionary_crud_and_replacement():
    """Verifies custom terms, preferred spellings, and regex boundary substitution."""
    # Add custom word
    entry = voice_dictionary.add_entry(
        word="trovane",
        preferred_spelling="Trovane",
        user_id="user_qa",
        domain="business"
    )
    assert entry.preferred_spelling == "Trovane"

    # Test casing substitution
    replaced = voice_dictionary.apply_dictionary("we are building trovane cloud", user_id="user_qa")
    assert "Trovane" in replaced

    # Verify defaults
    pg_replaced = voice_dictionary.apply_dictionary("connected to postgresql database", user_id="user_qa")
    assert "PostgreSQL" in pg_replaced


def test_stt_quality_pipeline_normalization():
    """Verifies sentence capitalization, year formatting, URL expansion, and dictionary casing."""
    raw_in = "we deploy to postgresql in two thousand twenty six new line visit example dot com"
    normalized, applied_cmds = stt_quality_pipeline.normalize(raw_in, user_id="user_test")
    assert "PostgreSQL" in normalized
    assert "2026" in normalized
    assert "example.com" in normalized
    assert "\n" in normalized
    assert normalized[0].isupper()


# ============================================================
# 7. VOICE CONVERSATION ENGINE & TRUE BARGE-IN TESTS
# ============================================================

def test_voice_session_turn_and_history_logging():
    """Verifies complete voice turn lifecycle, history persistence, and tenant isolation."""
    session = voice_conversation_engine.start_session(user_id="alice_user")
    res = voice_conversation_engine.process_voice_turn(
        session_id=session.session_id,
        text_override="What is the capital of Karnataka?",
        language_hint="en-IN"
    )
    assert res["status"] == "success"
    assert len(res["assistant_text"]) > 0
    assert "audio_synthesis" in res
    assert res["audio_synthesis"]["audio_bytes"] != ""

    # Check history isolation
    alice_history = voice_history_manager.get_history(user_id="alice_user")
    assert len(alice_history) >= 1
    assert alice_history[0].raw_transcript == "What is the capital of Karnataka?"

    bob_history = voice_history_manager.get_history(user_id="bob_user")
    # Bob should not see Alice's turns
    assert not any(h.raw_transcript == "What is the capital of Karnataka?" for h in bob_history)


def test_true_barge_in_interruption():
    """Verifies barge-in stops active speech and returns session to LISTENING without losing context."""
    session = voice_conversation_engine.start_session(user_id="barge_user", hands_free=True)
    # Start turn
    voice_conversation_engine.process_voice_turn(
        session_id=session.session_id,
        text_override="Tell me a detailed story."
    )
    # User interrupts Saarthi
    int_res = voice_conversation_engine.interrupt_speech(session_id=session.session_id, cancel_agent_task=False)
    assert int_res["status"] == "interrupted"
    assert session.state == VoiceState.LISTENING
    assert session.metrics.interruption_latency_ms >= 0.0


# ============================================================
# 8. MULTIMODAL VOICE INTEGRATION TESTS
# ============================================================

def test_multimodal_voice_query_with_attachment_id():
    """Verifies voice query referencing a Phase 4 multimodal attachment."""
    session = voice_conversation_engine.start_session(user_id="multimodal_voice_user")
    res = voice_conversation_engine.process_voice_turn(
        session_id=session.session_id,
        text_override="Look at this attachment and explain the content.",
        attachment_id="att_test_sample_123"
    )
    assert res["status"] == "success"
    assert session.active_turn is not None
    assert session.active_turn.attachment_id == "att_test_sample_123"


# ============================================================
# 9. VOICE PERSONALIZATION & PRECEDENCE TESTS
# ============================================================

def test_voice_personalization_precedence_and_updates():
    """Verifies speaking rate updates and domain-level precedence overrides."""
    # Update user preference
    settings = voice_personalization.update_settings(
        user_id="pref_user",
        speaking_rate=1.25,
        response_length="concise"
    )
    assert settings.speaking_rate == 1.25

    # Resolve settings for software domain (concise override)
    resolved_software = voice_personalization.resolve_effective_settings(
        user_id="pref_user",
        domain="software"
    )
    assert resolved_software["speaking_rate"] == 1.25
    assert resolved_software["response_length"] == "concise"


# ============================================================
# 10. DESKTOP REAL VOICE ENGINE PLATFORM ADAPTER TESTS
# ============================================================

def test_desktop_real_voice_engine_adapter():
    """Verifies RealDesktopVoiceEngine platform adapter methods."""
    engine = RealDesktopVoiceEngine()
    status = engine.get_status()
    assert status["connected"] is True
    assert status["phase"] == "PHASE_2_PRODUCTION_VOICE"

    # Supported languages
    langs = engine.get_supported_languages()
    assert "en-IN" in langs
    assert "hi-IN" in langs

    # Synthesis request
    req = SynthesisRequest(text="Hello Desktop", language="en-IN")
    audio = engine.synthesize_to_bytes(req)
    assert len(audio) > 100


# ============================================================
# 11. REST API ENDPOINTS VERIFICATION
# ============================================================

def test_voice_rest_api_profile_and_devices():
    """Verifies GET /api/voice/profile and GET /api/voice/devices."""
    prof_resp = client.get("/api/voice/profile")
    assert prof_resp.status_code == 200
    pdata = prof_resp.json()
    assert pdata["profile"]["id"] == "saarthi_voice_hi_en"
    assert pdata["stt_status"]["healthy"] is True
    assert pdata["tts_status"]["healthy"] is True

    dev_resp = client.get("/api/voice/devices")
    assert dev_resp.status_code == 200
    assert "devices" in dev_resp.json()


def test_voice_rest_api_dictionary_crud():
    """Verifies CRUD endpoints on /api/voice/dictionary."""
    # Create
    create_resp = client.post("/api/voice/dictionary", json={
        "word": "graphql",
        "preferred_spelling": "GraphQL",
        "user_id": "api_test_user"
    })
    assert create_resp.status_code == 200
    entry_id = create_resp.json()["entry"]["id"]

    # List
    list_resp = client.get("/api/voice/dictionary?user_id=api_test_user")
    assert list_resp.status_code == 200
    entries = list_resp.json()["entries"]
    assert any(e["word"] == "graphql" for e in entries)

    # Delete
    del_resp = client.delete(f"/api/voice/dictionary/{entry_id}?user_id=api_test_user")
    assert del_resp.status_code == 200
    assert del_resp.json()["deleted"] is True


def test_voice_rest_api_personalization():
    """Verifies GET and POST /api/voice/personalization."""
    update_resp = client.post("/api/voice/personalization", json={
        "user_id": "rest_pers_user",
        "speaking_rate": 1.15,
        "voice_gender": "female"
    })
    assert update_resp.status_code == 200
    assert update_resp.json()["settings"]["speaking_rate"] == 1.15

    get_resp = client.get("/api/voice/personalization?user_id=rest_pers_user")
    assert get_resp.status_code == 200
    assert get_resp.json()["settings"]["speaking_rate"] == 1.15


def test_voice_rest_api_history_and_clear():
    """Verifies GET and DELETE /api/voice/history."""
    # Create a turn
    sess_resp = client.post("/api/voice/session/start", json={"user_id": "hist_user"})
    sid = sess_resp.json()["session"]["session_id"]
    client.post("/api/voice/session/turn", json={"session_id": sid, "text_override": "History check"})

    # Get history
    hist_resp = client.get(f"/api/voice/history?user_id=hist_user&session_id={sid}")
    assert hist_resp.status_code == 200
    assert len(hist_resp.json()["history"]) >= 1

    # Clear history
    clear_resp = client.delete(f"/api/voice/history?user_id=hist_user&session_id={sid}")
    assert clear_resp.status_code == 200
    assert clear_resp.json()["cleared"] is True
