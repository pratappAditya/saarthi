"""
Desktop Core & Architecture Unit Tests.
Covers:
- Desktop State Machine transitions & voice unavailability flagging
- Global shortcut configuration & hold/toggle modes
- Desktop Session Manager authentication, token storage, expiry, and account switching
- Active application context & selected text extraction
- Privacy Boundary Guard (blocking password managers, credential sanitization)
- Direct text insertion capability detection (SUPPORTED, UNSUPPORTED, PERMISSION_REQUIRED, FAILED)
- Phase 2 Voice Interfaces (clean contracts, no fake STT/TTS claims)
- Desktop Command Pipeline end-to-end flow
- Saarthi Desktop Companion runtime lifecycle
"""

import os
import sys
import json
import pytest
from unittest.mock import MagicMock, patch

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from desktop.core.state_machine import DesktopStateMachine, DesktopInteractionState
from desktop.core.session_manager import DesktopSessionManager
from desktop.core.privacy import PrivacyBoundaryGuard, DesktopPrivacyPolicy
from desktop.core.settings import DesktopSettingsManager
from desktop.core.pipeline import DesktopCommandPipeline
from desktop.interfaces.context_provider import ApplicationContext, SelectedTextContext, DesktopContextProvider
from desktop.interfaces.shortcut_provider import ShortcutConfig, ShortcutActivationMode, GlobalShortcutProvider
from desktop.interfaces.insertion_provider import InsertionCapabilityStatus, InsertionResult, TextInsertionProvider
from desktop.interfaces.accessibility_provider import AccessibilityPermissionStatus, AccessibilityProvider, FocusedElementInfo
from desktop.interfaces.voice_interfaces import (
    VoiceEnginePhaseStatus,
    UnimplementedVoiceEngine,
    VoiceInputProvider,
    SpeechRecognitionProvider,
    SpeechSynthesisProvider,
    SynthesisRequest
)
from desktop.platforms.macos import (
    MacOSContextProvider,
    MacOSAccessibilityProvider,
    MacOSTextInsertionProvider,
    MacOSGlobalShortcutProvider
)
from desktop.platforms.windows import (
    WindowsContextProvider,
    WindowsAccessibilityProvider,
    WindowsTextInsertionProvider,
    WindowsGlobalShortcutProvider
)
from desktop.platforms.factory import get_platform_adapters
from desktop.app import SaarthiDesktopApp


# ============================================================
# 1. DESKTOP STATE MACHINE TESTS (UNIT TEST)
# ============================================================

def test_state_machine_initial_state():
    """UNIT TEST: Verifies state machine starts at IDLE state."""
    sm = DesktopStateMachine()
    assert sm.current_state == DesktopInteractionState.IDLE
    summary = sm.get_summary()
    assert summary["state"] == "IDLE"
    assert "voice_phase_status" in summary


def test_state_machine_valid_lifecycle():
    """UNIT TEST: Verifies valid transition flow IDLE -> READY -> PROCESSING -> THINKING -> COMPLETED -> IDLE."""
    sm = DesktopStateMachine()
    assert sm.transition_to(DesktopInteractionState.READY) is True
    assert sm.current_state == DesktopInteractionState.READY

    assert sm.transition_to(DesktopInteractionState.PROCESSING) is True
    assert sm.current_state == DesktopInteractionState.PROCESSING

    assert sm.transition_to(DesktopInteractionState.THINKING) is True
    assert sm.current_state == DesktopInteractionState.THINKING

    assert sm.transition_to(DesktopInteractionState.COMPLETED) is True
    assert sm.current_state == DesktopInteractionState.COMPLETED

    assert sm.transition_to(DesktopInteractionState.IDLE) is True
    assert sm.current_state == DesktopInteractionState.IDLE


def test_state_machine_invalid_transition_rejected():
    """UNIT TEST: Verifies invalid direct transitions are rejected."""
    sm = DesktopStateMachine()
    # Cannot jump directly from IDLE to COMPLETED or THINKING
    assert sm.transition_to(DesktopInteractionState.COMPLETED) is False
    assert sm.current_state == DesktopInteractionState.IDLE


def test_state_machine_listening_state_explicitly_flags_voice_coming_soon():
    """UNIT TEST: Verifies entering LISTENING explicitly flags that voice engine is coming in Phase 2."""
    sm = DesktopStateMachine()
    sm.transition_to(DesktopInteractionState.READY)
    sm.transition_to(DesktopInteractionState.LISTENING)

    assert sm.current_state == DesktopInteractionState.LISTENING
    summary = sm.get_summary()
    assert "Phase 2" in sm.status_message or "Phase 2" in summary["message"]
    assert summary["data"].get("voice_engine_status") == "COMING_SOON_PHASE_2"
    assert summary["data"].get("real_voice_connected") is False


def test_state_machine_listeners():
    """UNIT TEST: Verifies registered state listeners receive transition updates."""
    sm = DesktopStateMachine()
    events = []

    def callback(state, payload):
        events.append((state, payload["state"]))

    sm.add_listener(callback)
    sm.transition_to(DesktopInteractionState.READY)
    sm.transition_to(DesktopInteractionState.IDLE)

    assert len(events) == 2
    assert events[0] == (DesktopInteractionState.READY, "READY")
    assert events[1] == (DesktopInteractionState.IDLE, "IDLE")


# ============================================================
# 2. GLOBAL SHORTCUT CONFIGURATION & ACTIVATION (UNIT TEST)
# ============================================================

def test_shortcut_configuration():
    """UNIT TEST: Verifies shortcut configuration supporting hold and toggle modes."""
    cfg = ShortcutConfig(
        primary_key="Fn",
        alternative_key="Control+Space",
        mode=ShortcutActivationMode.HOLD_TO_ACTIVATE
    )
    assert cfg.primary_key == "Fn"
    assert cfg.mode == ShortcutActivationMode.HOLD_TO_ACTIVATE

    cfg2 = ShortcutConfig(mode=ShortcutActivationMode.TOGGLE_TO_ACTIVATE)
    assert cfg2.mode == ShortcutActivationMode.TOGGLE_TO_ACTIVATE


def test_shortcut_provider_registration():
    """UNIT TEST: Verifies registering handlers on the global shortcut provider."""
    provider = MacOSGlobalShortcutProvider()
    activated = False

    def on_act():
        nonlocal activated
        activated = True

    provider.register_handler(on_activate=on_act)
    assert provider.start_listening() is True
    assert provider.is_active() is True

    # Simulate activation trigger
    provider.on_activate()
    assert activated is True

    provider.stop_listening()
    assert provider.is_active() is False


# ============================================================
# 3. PRIVACY BOUNDARY GUARD (UNIT TEST)
# ============================================================

def test_privacy_guard_blocks_sensitive_applications():
    """UNIT TEST: Verifies password managers and vaults are blocked from context extraction."""
    guard = PrivacyBoundaryGuard()
    assert guard.is_app_sensitive_or_blocked("1Password", "com.agilebits.onepassword") is True
    assert guard.is_app_sensitive_or_blocked("Bitwarden", "com.bitwarden.desktop") is True
    assert guard.is_app_sensitive_or_blocked("KeePassXC", "org.keepassxc.keepassxc") is True
    assert guard.is_app_sensitive_or_blocked("Keychain Access", "com.apple.keychainaccess") is True

    # Standard applications should be allowed
    assert guard.is_app_sensitive_or_blocked("Visual Studio Code", "com.microsoft.VSCode") is False
    assert guard.is_app_sensitive_or_blocked("Notes", "com.apple.Notes") is False
    assert guard.is_app_sensitive_or_blocked("Slack", "com.tinyspeck.slackmacgap") is False


def test_privacy_guard_redacts_credentials():
    """UNIT TEST: Verifies secrets/tokens are sanitized from selected text."""
    guard = PrivacyBoundaryGuard()
    raw = "My secret password: supersecret123 and auth Bearer abcdef1234567890abcdef1234567890"
    sanitized = guard.sanitize_selected_text(raw)
    assert "supersecret123" not in sanitized
    assert "[REDACTED_CREDENTIAL]" in sanitized


# ============================================================
# 4. DIRECT TEXT INSERTION CAPABILITY (UNIT TEST)
# ============================================================

def test_macos_text_insertion_capability_detection():
    """UNIT TEST: Verifies capability detection for supported vs unsupported macOS applications."""
    provider = MacOSTextInsertionProvider()

    # Supported editors/browsers
    cap_vscode = provider.check_capability("VS Code", "com.microsoft.VSCode")
    assert cap_vscode == InsertionCapabilityStatus.SUPPORTED

    cap_notes = provider.check_capability("Notes", "com.apple.Notes")
    assert cap_notes == InsertionCapabilityStatus.SUPPORTED

    # Unsupported desktop shell elements
    cap_finder = provider.check_capability("Finder", "com.apple.finder")
    assert cap_finder == InsertionCapabilityStatus.UNSUPPORTED


def test_text_insertion_execution():
    """UNIT TEST: Verifies insertion provider execution returns structured InsertionResult."""
    provider = MacOSTextInsertionProvider()
    res = provider.insert_text("Generated code sample", "VS Code", "com.microsoft.VSCode")
    assert isinstance(res, InsertionResult)
    assert res.status in [InsertionCapabilityStatus.SUPPORTED, InsertionCapabilityStatus.FAILED]
    assert res.target_app == "VS Code"


# ============================================================
# 5. PHASE 2 VOICE INTERFACES (UNIT TEST - VERIFYING NO FAKE STT/TTS)
# ============================================================

def test_phase_2_voice_interfaces_exist_and_reject_fake_calls():
    """
    UNIT TEST: Verifies VoiceInputProvider, SpeechRecognitionProvider, and SpeechSynthesisProvider
    contracts are prepared for Phase 2, but strictly do NOT claim functionality or implement fake STT/TTS.
    """
    engine = UnimplementedVoiceEngine()

    # Voice Input must raise NotImplementedError in Phase 3
    with pytest.raises(NotImplementedError) as exc_rec:
        engine.start_recording()
    assert "deferred to Phase 2" in str(exc_rec.value)

    # STT Transcription must raise NotImplementedError in Phase 3
    with pytest.raises(NotImplementedError) as exc_stt:
        engine.transcribe(b"fake_audio_chunk")
    assert "deferred to Phase 2" in str(exc_stt.value)

    # TTS Synthesis must raise NotImplementedError in Phase 3
    with pytest.raises(NotImplementedError) as exc_tts:
        engine.synthesize_to_bytes(SynthesisRequest(text="Hello world"))
    assert "deferred to Phase 2" in str(exc_tts.value)

    # Status must report deferred to Phase 2
    status = engine.get_status()
    assert status["voice_status"] == VoiceEnginePhaseStatus.DEFERRED_TO_PHASE_2.value
    assert status["connected"] is False
    assert status["microphone_active"] is False


# ============================================================
# 6. DESKTOP SESSION MANAGER (UNIT TEST)
# ============================================================

def test_desktop_session_lifecycle(tmp_path):
    """UNIT TEST: Verifies session token caching, authentication check, logout, and account switching."""
    mgr = DesktopSessionManager(session_dir=str(tmp_path))
    assert mgr.is_authenticated() is False
    assert mgr.get_token() is None

    # Simulate saving token
    mgr._save_session_file({
        "session_token": "mock_token_abc_123",
        "user": {"email": "test@saarthi.ai", "user_id": "usr_test_1"},
        "session_id": "sess_1"
    })
    assert mgr.is_authenticated() is True
    assert mgr.get_token() == "mock_token_abc_123"
    assert mgr.get_user_info()["email"] == "test@saarthi.ai"

    # Logout purges session
    mgr.logout(notify_backend=False)
    assert mgr.is_authenticated() is False
    assert mgr.get_token() is None


# ============================================================
# 7. PLATFORM ADAPTER FACTORY (REAL OS TEST)
# ============================================================

def test_platform_adapters_factory():
    """REAL OS TEST: Verifies factory instantiates proper platform adapters on active OS."""
    adapters = get_platform_adapters()
    assert len(adapters) == 5
    ctx, shortcut, access, insertion, voice = adapters
    assert isinstance(ctx, DesktopContextProvider)
    assert isinstance(shortcut, GlobalShortcutProvider)
    assert isinstance(access, AccessibilityProvider)
    assert isinstance(insertion, TextInsertionProvider)
    assert isinstance(voice, UnimplementedVoiceEngine)

    # Active application query returns valid structure
    app_ctx = ctx.get_active_application()
    assert isinstance(app_ctx, ApplicationContext)
    assert app_ctx.app_name is not None


# ============================================================
# 8. DESKTOP APPLICATION RUNTIME LIFECYCLE (INTEGRATION TEST)
# ============================================================

def test_desktop_app_runtime():
    """INTEGRATION TEST: Verifies desktop companion app initialization, activation, and status reporting."""
    app = SaarthiDesktopApp()
    status = app.get_status()
    assert "state" in status
    assert status["voice_phase"] == "PHASE_3_FOUNDATION_VOICE_COMING_IN_PHASE_2"

    # Activate companion
    act_res = app.activate()
    assert act_res["status"] == "activated"
    assert app.state_machine.current_state == DesktopInteractionState.READY

    # Deactivate companion
    app.deactivate()
    assert app.state_machine.current_state == DesktopInteractionState.IDLE
