"""
Desktop API Integration Tests.
Verifies backend endpoints for the native Saarthi Desktop Companion.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_desktop_status_endpoint():
    """INTEGRATION TEST: Verifies /api/desktop/status exposes Phase 3 operational status and flags Phase 2 voice as pending."""
    resp = client.get("/api/desktop/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "operational"
    assert data["version"] == "1.0.0-phase3"
    assert "darwin" in data["supported_platforms"]
    assert "win32" in data["supported_platforms"]
    assert data["phase_2_voice_engine"] == "PENDING_PHASE_2"
    assert "Voice engine (STT/TTS) is deferred to Phase 2" in data["voice_status_notice"]
    assert data["accessibility_api_supported"] is True
    assert data["direct_text_insertion_supported"] is True


def test_desktop_privacy_endpoint():
    """INTEGRATION TEST: Verifies /api/desktop/privacy declarations."""
    resp = client.get("/api/desktop/privacy")
    assert resp.status_code == 200
    data = resp.json()
    assert "what_saarthi_accesses" in data
    assert "what_requires_os_permissions" in data
    assert "what_is_transmitted_to_backend" in data
    assert "what_stays_local" in data
    assert "prohibited_actions" in data
    assert any("microphone" in item.lower() for item in data["prohibited_actions"])


def test_desktop_command_chat():
    """INTEGRATION TEST: Verifies basic desktop command execution with active application context."""
    payload = {
        "prompt": "Hello Saarthi, help me with this task.",
        "action": "chat",
        "active_application": {
            "app_name": "VS Code",
            "bundle_id": "com.microsoft.VSCode",
            "window_title": "app.py — Saarthi",
            "is_accessible": True,
            "focused_field_available": True
        },
        "session_id": "test_desktop_session_1"
    }
    resp = client.post("/api/desktop/command", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ["success", "pending_confirmation"]
    assert "desktop_metadata" in data
    assert data["desktop_metadata"]["active_app"] == "VS Code"
    assert data["desktop_metadata"]["voice_engine_phase"] == "DEFERRED_PHASE_2"


def test_desktop_command_rewrite_with_selected_text():
    """INTEGRATION TEST: Verifies contextual rewrite using selected text context."""
    payload = {
        "prompt": "Make this more professional.",
        "action": "rewrite",
        "selected_text": "Hey check out this cool thing we did yesterday.",
        "active_application": {
            "app_name": "Slack",
            "bundle_id": "com.tinyspeck.slackmacgap",
            "is_accessible": True
        },
        "session_id": "test_desktop_session_2"
    }
    resp = client.post("/api/desktop/command", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["desktop_metadata"]["had_selected_text"] is True
    assert data["desktop_metadata"]["action"] == "rewrite"


def test_desktop_text_insertion_authorization():
    """INTEGRATION TEST: Verifies authorization endpoint for direct text insertion."""
    payload = {
        "text": "Revised professional response text.",
        "target_app": "Notes",
        "target_bundle_id": "com.apple.Notes"
    }
    resp = client.post("/api/desktop/insert-text", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "APPROVED"
    assert data["insertion_authorized"] is True
    assert data["target_app"] == "Notes"
    assert data["char_count"] == len(payload["text"])


def test_desktop_text_insertion_blocks_sensitive_apps():
    """INTEGRATION TEST: Verifies text insertion into password managers is blocked by policy."""
    for sensitive_app in ["1Password", "Bitwarden", "KeePass"]:
        payload = {
            "text": "Sensitive data.",
            "target_app": sensitive_app
        }
        resp = client.post("/api/desktop/insert-text", json=payload)
        assert resp.status_code == 403
        assert "blocked by policy" in resp.json()["detail"].lower()
