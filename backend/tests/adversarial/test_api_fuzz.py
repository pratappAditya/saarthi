import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Generate 105 distinct payload cases for API inputs
API_INPUT_CASES = [
    "",
    "   ",
    "\t\n\r",
    "a",
    "Hello Saarthi",
    "सारथी एजेंट हिंदी परीक्षण",
    "🚀🤖🔥 Agent test with emoji!",
    "CJK text: 助手测试 🤖",
    "Control chars: \x00\x01\x02\x03\x04\x05",
    "Unclosed quote: ' ' ' \" \"",
    "Special XML/HTML: <script>alert(1)</script>",
    "Nested tags: <think><foo>bar</foo></think>",
    "A" * 1000,
    "B" * 5000,
] + [f"Parameterized chat input variation {i}: " + ("x" * (i * 10)) for i in range(1, 92)]

@pytest.mark.parametrize("message_input", API_INPUT_CASES)
def test_fuzz_api_chat_input_validation(message_input):
    payload = {
        "message": message_input,
        "session_id": "test_fuzz_session_1"
    }
    response = client.post("/api/chat", json=payload)
    # Should return either 200 (processed/handled) or 422 (validation error if empty/whitespace)
    assert response.status_code in (200, 422, 400)
    if response.status_code == 200:
        data = response.json()
        assert "response" in data or "session_id" in data or "state" in data

@pytest.mark.parametrize("session_id", [
    "valid_session_123",
    "session-with-dashes",
    "session_with_underscores",
    "session.with.dots",
    "1234567890",
    "a" * 100,
    "session/with/slashes",
    "session\\with\\backslashes",
    "session%20with%20spaces",
    "session;drop table users;",
] + [f"sess_{i}" for i in range(1, 11)])
def test_fuzz_api_session_id_variants(session_id):
    response = client.get(f"/api/history/{session_id}")
    assert response.status_code in (200, 400, 404, 422)
