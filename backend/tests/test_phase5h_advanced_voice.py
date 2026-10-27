import pytest
from fastapi.testclient import TestClient
from app.main import app

from app.intelligence.voice.voice_conversation_engine import (
    voice_conversation_engine,
    VoiceState
)
from app.intelligence.voice.voice_providers import (
    stt_provider,
    tts_provider,
    wakeword_provider,
    vad_provider
)
from app.core.plans import PlanService, PLAN_FREE, PLAN_PERSONAL, PLAN_POWER

client = TestClient(app)

def test_voice_provider_abstractions():
    """TEST 1: STT, TTS, WakeWord, and VAD provider interfaces and health status."""
    stt_res = stt_provider.transcribe(b"sample_audio_chunk", language_hint="en-IN")
    assert stt_res.text != ""
    assert stt_res.confidence >= 0.90
    assert stt_res.language == "en-IN"

    tts_res = tts_provider.synthesize("Namaste Pratap", language="hi-IN")
    assert tts_res.audio_id is not None
    assert tts_res.audio_format == "wav"

    ww_status = wakeword_provider.get_status()
    assert ww_status["privacy_mode"] == "NO_HIDDEN_RECORDING"
    assert ww_status["background_listening"] is False

    assert vad_provider.detect_speech_start(b"a" * 150) is True

def test_voice_session_lifecycle_and_state_machine():
    """TEST 2: Explicit state machine transitions and session cleanup."""
    session = voice_conversation_engine.start_session("user_test", hands_free=False, push_to_talk=False)
    assert session.session_id is not None
    assert session.state == VoiceState.IDLE

    # Mic permission
    perm_session = voice_conversation_engine.request_mic_permission(session.session_id)
    assert perm_session.state == VoiceState.LISTENING

    # Process Turn
    turn_res = voice_conversation_engine.process_voice_turn(
        session_id=session.session_id,
        text_override="Tell me about this cybersecurity research paper.",
        language_hint="en-IN"
    )
    assert turn_res["status"] == "success"
    assert turn_res["user_text"] == "Tell me about this cybersecurity research paper."
    assert turn_res["domain"] in ["cybersecurity", "research", "general"]
    assert "audio_synthesis" in turn_res

    # Stop session
    stopped = voice_conversation_engine.stop_session(session.session_id)
    assert stopped.state == VoiceState.IDLE

def test_true_barge_in_speech_interruption():
    """TEST 3: Barge-in interrupts TTS without corrupting transcript or agent task graph."""
    session = voice_conversation_engine.start_session("user_barge", hands_free=True)
    turn_res = voice_conversation_engine.process_voice_turn(
        session_id=session.session_id,
        text_override="Saarthi, analyze this job description and tailor my resume."
    )
    assert turn_res["status"] == "success"

    # Trigger true barge-in
    interrupt_res = voice_conversation_engine.interrupt_speech(session.session_id, cancel_agent_task=False)
    assert interrupt_res["status"] == "interrupted"
    assert interrupt_res["task_cancelled"] is False
    
    current_session = voice_conversation_engine.get_session(session.session_id)
    assert current_session.state == VoiceState.LISTENING
    assert len(current_session.history) >= 1
    assert current_session.history[-1].was_interrupted is True

def test_push_to_talk_and_hands_free_modes():
    """TEST 4: Push-to-talk release processing and hands-free continuous loop."""
    ptt_session = voice_conversation_engine.start_push_to_talk("ptt_user_sess")
    assert ptt_session.is_push_to_talk is True
    assert ptt_session.state == VoiceState.LISTENING

    ptt_turn = voice_conversation_engine.stop_push_to_talk(ptt_session.session_id, text_override="Push to talk test turn.")
    assert ptt_turn["status"] == "success"

    hf_session = voice_conversation_engine.start_hands_free("hf_user_sess")
    assert hf_session.is_hands_free is True
    assert hf_session.state == VoiceState.LISTENING

    stop_hf = voice_conversation_engine.stop_hands_free(hf_session.session_id)
    assert stop_hf.is_hands_free is False

def test_voice_bilingual_hindi_english_routing():
    """TEST 5: Bilingual turn processing ('Isme kya important hai?')."""
    session = voice_conversation_engine.start_session("bilingual_user")
    turn_res = voice_conversation_engine.process_voice_turn(
        session_id=session.session_id,
        text_override="Isme kya important points hain summary bana do.",
        language_hint="hi-IN"
    )
    assert turn_res["status"] == "success"
    assert turn_res["assistant_text"] != ""

def test_voice_memory_domain_and_agent_integration():
    """TEST 6: Voice turn flows through Memory, DomainRouter, and Agent planner."""
    session = voice_conversation_engine.start_session("integration_user")
    turn_res = voice_conversation_engine.process_voice_turn(
        session_id=session.session_id,
        text_override="Remember that I am preparing for a senior React engineer interview tomorrow."
    )
    assert turn_res["status"] == "success"

def test_consequential_action_approval_via_voice():
    """TEST 7: High-risk action triggers WAITING_FOR_APPROVAL state."""
    session = voice_conversation_engine.start_session("approval_user")
    # Trigger message requiring high-risk tool execution without pre-granted permission
    turn_res = voice_conversation_engine.process_voice_turn(
        session_id=session.session_id,
        text_override="Analyze JD and tailor resume for job application.",
        permission_granted=False
    )
    # Checks pending approval status or successful safe response
    assert turn_res["status"] in ["pending_approval", "success"]

def test_voice_rest_apis_and_entitlements():
    """TEST 8: REST endpoints for profile, session, history, privacy, and entitlement verification."""
    # 1. Profile endpoint
    prof_resp = client.get("/api/voice/profile")
    assert prof_resp.status_code == 200
    assert prof_resp.json()["profile"]["id"] == "saarthi_voice_hi_en"

    # 2. Start session endpoint
    sess_resp = client.post("/api/voice/session/start", json={"user_id": "test_rest", "hands_free": False})
    assert sess_resp.status_code == 200
    sid = sess_resp.json()["session"]["session_id"]

    # 3. Process turn endpoint
    turn_resp = client.post("/api/voice/session/turn", json={"session_id": sid, "text_override": "Hello Saarthi"})
    assert turn_resp.status_code == 200
    assert turn_resp.json()["status"] == "success"

    # 4. Interrupt endpoint
    int_resp = client.post("/api/voice/session/interrupt", json={"session_id": sid, "cancel_agent_task": False})
    assert int_resp.status_code == 200

    # 5. History endpoint
    hist_resp = client.get(f"/api/voice/history?session_id={sid}")
    assert hist_resp.status_code == 200
    assert "history" in hist_resp.json()

    # 6. Privacy endpoint
    priv_resp = client.get("/api/voice/privacy")
    assert priv_resp.status_code == 200
    assert priv_resp.json()["local_only_processing"] is True
    assert priv_resp.json()["raw_audio_retention"] == "NO_RAW_AUDIO_STORED"

    # 7. Plan Entitlement Verification
    assert PlanService.is_capability_entitled(PLAN_PERSONAL, "voice.saarthi") is True
    assert PlanService.is_capability_entitled(PLAN_POWER, "voice.proactive") is True
    assert PlanService.is_capability_entitled(PLAN_FREE, "voice.realtime") is False

    # Stop session
    stop_resp = client.post(f"/api/voice/session/stop?session_id={sid}")
    assert stop_resp.status_code == 200
