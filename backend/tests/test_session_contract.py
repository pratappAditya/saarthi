import pytest
import asyncio
from unittest.mock import AsyncMock
from app.agent.core import AgentCore

class MockModelProvider:
    def __init__(self, response_map):
        self.response_map = response_map
        self.model_name = "mock-model"

    async def generate_response(self, prompt: str, history: list = None, system_prompt: str = None) -> str:
        last_msg = ""
        if history:
            last_msg = history[-1].get("message", "")
        for key, resp in self.response_map.items():
            if key in last_msg or key in prompt:
                return resp
        return "Default response"

@pytest.mark.anyio
async def test_session_isolation_history_and_state():
    model = MockModelProvider({
        "User A Query": "Response for Session A",
        "User B Query": "Response for Session B"
    })
    agent = AgentCore()
    agent.model = model

    sess_a = "session-iso-a"
    sess_b = "session-iso-b"

    await agent.memory.clear_session(sess_a)
    await agent.memory.clear_session(sess_b)

    res_a = await agent.handle_message(sess_a, "User A Query")
    res_b = await agent.handle_message(sess_b, "User B Query")

    hist_a = await agent.memory.get_messages(sess_a)
    hist_b = await agent.memory.get_messages(sess_b)

    # Verify Session A history contains only Session A messages
    messages_a_text = [m["message"] for m in hist_a]
    messages_b_text = [m["message"] for m in hist_b]

    assert any("User A Query" in t for t in messages_a_text)
    assert not any("User B Query" in t for t in messages_a_text)

    assert any("User B Query" in t for t in messages_b_text)
    assert not any("User A Query" in t for t in messages_b_text)

@pytest.mark.anyio
async def test_session_cancellation_isolation():
    agent = AgentCore()
    agent.cancel_session("session-cancel-only-a")

    assert "session-cancel-only-a" in agent._canceled_sessions
    assert "session-cancel-only-b" not in agent._canceled_sessions
