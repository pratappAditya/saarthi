import pytest
import asyncio
import json
from app.agent.core import AgentCore

class DelayedMockModel:
    def __init__(self, text):
        self.text = text
        self.model_name = "mock-model"

    async def generate_response(self, prompt: str, history: list = None, system_prompt: str = None) -> str:
        await asyncio.sleep(0.05)
        return self.text

@pytest.mark.anyio
async def test_concurrent_sessions_execution():
    agent = AgentCore()
    agent.model = DelayedMockModel("Response completed")

    sess_1 = "concurrent-sess-1"
    sess_2 = "concurrent-sess-2"

    await agent.memory.clear_session(sess_1)
    await agent.memory.clear_session(sess_2)

    # Run Session 1 and Session 2 concurrently
    res1, res2 = await asyncio.gather(
        agent.handle_message(sess_1, "Query Session 1"),
        agent.handle_message(sess_2, "Query Session 2")
    )

    data1 = json.loads(res1)
    data2 = json.loads(res2)

    assert data1["content"] == "Response completed"
    assert data2["content"] == "Response completed"

    hist1 = await agent.memory.get_messages(sess_1)
    hist2 = await agent.memory.get_messages(sess_2)

    msg1_text = [m["message"] for m in hist1]
    msg2_text = [m["message"] for m in hist2]

    assert any("Query Session 1" in t for t in msg1_text)
    assert not any("Query Session 2" in t for t in msg1_text)

    assert any("Query Session 2" in t for t in msg2_text)
    assert not any("Query Session 1" in t for t in msg2_text)
