import pytest
import json
from unittest.mock import AsyncMock
from app.agent.core import AgentCore

class CountingMockModel:
    def __init__(self, tool_response):
        self.tool_response = tool_response
        self.called = 0
        self.model_name = "mock-model"

    async def generate_response(self, prompt: str, history: list = None, system_prompt: str = None) -> str:
        self.called += 1
        if self.called == 1:
            return self.tool_response
        return "Final completion response."

@pytest.mark.anyio
async def test_single_tool_execution_idempotency():
    mock_model = CountingMockModel('[TOOL_CALL]\n{"tool": "file_list", "arguments": {"path": "."}}\n[/TOOL_CALL]')
    agent = AgentCore()
    agent.model = mock_model

    session_id = "sess-idempotency-1"
    await agent.memory.clear_session(session_id)

    res_json = await agent.handle_message(session_id, "List files once")
    
    history = await agent.memory.get_messages(session_id)
    tool_results = [json.loads(m["message"]) for m in history if m["sender"] == "user" and "tool_result" in m.get("message", "")]

    # Exactly 1 tool result produced for 1 tool call
    assert len(tool_results) == 1
    assert tool_results[0]["tool"] == "file_list"
    assert tool_results[0]["success"] is True
