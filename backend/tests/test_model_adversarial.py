import pytest
import json
from app.agent.core import AgentCore

class MockAdversarialModel:
    def __init__(self, outputs):
        self.outputs = outputs
        self.idx = 0
        self.model_name = "mock-model"

    async def generate_response(self, prompt: str, history: list = None, system_prompt: str = None) -> str:
        res = self.outputs[self.idx % len(self.outputs)]
        self.idx += 1
        return res

@pytest.mark.anyio
async def test_model_adversarial_malformed_json_handling():
    # Model returns invalid JSON inside tool call tag
    mock_model = MockAdversarialModel([
        '[TOOL_CALL]\n{"tool": "file_list", "arguments": {invalid_json_here}}\n[/TOOL_CALL]',
        "Recovered from malformed JSON."
    ])
    agent = AgentCore()
    agent.model = mock_model

    session_id = "sess-adv-json"
    res_json = await agent.handle_message(session_id, "Do action")
    
    history = await agent.memory.get_messages(session_id)
    tool_results = [json.loads(m["message"]) for m in history if "tool_result" in m.get("message", "")]

    assert len(tool_results) > 0
    assert tool_results[0]["success"] is False
    assert "MALFORMED_TOOL_CALL" in tool_results[0]["error"]["type"]

@pytest.mark.anyio
async def test_model_adversarial_unclosed_think_tag_stripped():
    mock_model = MockAdversarialModel([
        "Hello from assistant!<think>Internal thoughts trying to leak..."
    ])
    agent = AgentCore()
    agent.model = mock_model

    session_id = "sess-adv-think"
    res_json = await agent.handle_message(session_id, "Hello")
    res = json.loads(res_json)

    # <think> content must be stripped
    assert "<think>" not in res["content"]
    assert "Internal thoughts" not in res["content"]
    assert "Hello from assistant!" in res["content"]
