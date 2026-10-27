import os
import sys
import json
import asyncio
import pytest
import tempfile
import shutil
from typing import Dict, Any
from unittest.mock import AsyncMock, patch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app"))

from app.config.settings import settings
from app.agent.core import AgentCore, AgentState
from app.models.base import ModelProvider
from app.tools.base import BaseTool
from app.security.permissions import PermissionLevel, PermissionRequiredException, permission_store


class RecordingMockModelProvider(ModelProvider):
    def __init__(self, responses=None, delay: float = 0.0, model_name="mock-recording-model"):
        self.model_name = model_name
        self.responses = list(responses) if responses else []
        self.call_count = 0
        self.calls = []
        self.delay = delay

    async def generate_response(self, prompt: str, history=None, system_prompt: str = None) -> str:
        self.call_count += 1
        self.calls.append({
            "prompt": prompt,
            "history": history,
            "system_prompt": system_prompt
        })
        if self.delay > 0:
            await asyncio.sleep(self.delay)
        if self.responses:
            return self.responses.pop(0)
        return "Default mock response"


class SlowTool(BaseTool):
    @property
    def name(self) -> str:
        return "slow_tool"

    @property
    def description(self) -> str:
        return "Tool that sleeps to simulate long operation."

    @property
    def permission_level(self) -> PermissionLevel:
        return PermissionLevel.SAFE

    @property
    def risk_classification(self) -> str:
        return "LOW"

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "duration": {"type": "number"}
            },
            "required": ["duration"]
        }

    @property
    def output_schema(self) -> Dict[str, Any]:
        return {"type": "object"}

    async def execute(self, duration: float = 0.5, **kwargs) -> dict:
        await asyncio.sleep(duration)
        return {"slept": duration}


class PermTool(BaseTool):
    @property
    def name(self) -> str:
        return "perm_tool"

    @property
    def description(self) -> str:
        return "Permission confirmation required tool."

    @property
    def permission_level(self) -> PermissionLevel:
        return PermissionLevel.USER_CONFIRMATION

    @property
    def risk_classification(self) -> str:
        return "MEDIUM"

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "item": {"type": "string"}
            },
            "required": ["item"]
        }

    @property
    def output_schema(self) -> Dict[str, Any]:
        return {"type": "object"}

    async def execute(self, item: str = "default", **kwargs) -> dict:
        return {"done": item}


@pytest.fixture(autouse=True)
def setup_test_env():
    temp_dir = tempfile.mkdtemp()
    temp_db_path = os.path.join(temp_dir, "test_reliability.db")
    
    original_db = settings.DATABASE_PATH
    settings.DATABASE_PATH = temp_db_path
    
    from app.memory.sqlite_store import SQLiteMemoryStore
    from app.memory.manager import MemoryManager
    import app.memory.manager
    
    old_store = app.memory.manager.sqlite_store
    old_mgr = app.memory.manager.memory_manager
    
    new_store = SQLiteMemoryStore(temp_db_path)
    app.memory.manager.sqlite_store = new_store
    app.memory.manager.memory_manager = MemoryManager(new_store)
    permission_store.clear()
    
    yield temp_db_path
    
    app.memory.manager.sqlite_store = old_store
    app.memory.manager.memory_manager = old_mgr
    settings.DATABASE_PATH = original_db
    permission_store.clear()
    
    import gc
    gc.collect()
    try:
        shutil.rmtree(temp_dir)
    except Exception:
        pass


# 1. Single tool backward compatibility
@pytest.mark.anyio
async def test_single_tool_backward_compatibility():
    mock_model = RecordingMockModelProvider(responses=[
        '[TOOL_CALL]\n{"tool": "file_list", "arguments": {"path": "."}}\n[/TOOL_CALL]',
        "Done listing files."
    ])
    agent = AgentCore()
    agent.model = mock_model

    mock_executor = AsyncMock()
    mock_executor.execute_tool.return_value = {"success": True, "data": ["a.txt"]}
    agent.executor = mock_executor

    res_json = await agent.handle_message("sess-single-compat", "List files")
    res = json.loads(res_json)
    assert res["content"] == "Done listing files."
    assert mock_model.call_count == 2
    assert mock_executor.execute_tool.call_count == 1


# 2. Multiple tool calls
@pytest.mark.anyio
async def test_multiple_tool_calls():
    mock_model = RecordingMockModelProvider(responses=[
        '[TOOL_CALL]\n{"tool": "file_list", "arguments": {"path": "."}}\n[/TOOL_CALL]\n'
        '[TOOL_CALL]\n{"tool": "system_info", "arguments": {}}\n[/TOOL_CALL]',
        "Extracted both file list and system info."
    ])
    agent = AgentCore()
    agent.model = mock_model

    mock_executor = AsyncMock()
    mock_executor.execute_tool.side_effect = [
        {"success": True, "data": ["file1.py"]},
        {"success": True, "data": {"os": "Windows 11"}}
    ]
    agent.executor = mock_executor

    res_json = await agent.handle_message("sess-multi-tools", "Get workspace and system info")
    res = json.loads(res_json)
    assert res["content"] == "Extracted both file list and system info."
    assert mock_model.call_count == 2
    assert mock_executor.execute_tool.call_count == 2


# 3. Multiple tool call failure (partial failure)
@pytest.mark.anyio
async def test_multiple_tool_call_failure():
    mock_model = RecordingMockModelProvider(responses=[
        '[TOOL_CALL]\n{"tool": "file_list", "arguments": {"path": "."}}\n[/TOOL_CALL]\n'
        '[TOOL_CALL]\n{"tool": "nonexistent_tool", "arguments": {}}\n[/TOOL_CALL]',
        "Processed partial failure."
    ])
    agent = AgentCore()
    agent.model = mock_model

    mock_executor = AsyncMock()
    mock_executor.execute_tool.return_value = {"success": True, "data": ["f1"]}
    agent.executor = mock_executor

    res_json = await agent.handle_message("sess-multi-fail", "Run multi tools with one bad")
    res = json.loads(res_json)

    history = await agent.memory.get_messages("sess-multi-fail")
    tool_results = [json.loads(m["message"]) for m in history if "tool_result" in m.get("message", "")]
    assert len(tool_results) == 2
    assert tool_results[0]["success"] is True
    assert tool_results[1]["success"] is False
    assert tool_results[1]["error"]["type"] == "UNKNOWN_TOOL"


# 4. Tool timeout
@pytest.mark.anyio
async def test_tool_timeout():
    agent = AgentCore()
    agent.tools.register(SlowTool())
    agent.executor.timeout = 0.05

    result = await agent.executor.execute_tool("slow_tool", {"duration": 0.2})
    assert result["success"] is False
    assert result["error"]["code"] == "TOOL_TIMEOUT"
    assert "timed out after 0.05 seconds" in result["error"]["message"]


# 5. Tool timeout recovery
@pytest.mark.anyio
async def test_tool_timeout_recovery():
    mock_model = RecordingMockModelProvider(responses=[
        '[TOOL_CALL]\n{"tool": "slow_tool", "arguments": {"duration": 0.2}}\n[/TOOL_CALL]',
        "I recovered after the tool timed out."
    ])
    agent = AgentCore()
    agent.model = mock_model
    agent.tools.register(SlowTool())
    agent.executor.timeout = 0.05

    res_json = await agent.handle_message("sess-timeout-rec", "Run slow tool")
    res = json.loads(res_json)

    assert mock_model.call_count == 2
    assert res["content"] == "I recovered after the tool timed out."


# 6. Tool timeout termination
@pytest.mark.anyio
async def test_tool_timeout_termination():
    mock_model = RecordingMockModelProvider(responses=[
        '[TOOL_CALL]\n{"tool": "slow_tool", "arguments": {"duration": 0.2}}\n[/TOOL_CALL]' for _ in range(10)
    ])
    agent = AgentCore()
    agent.model = mock_model
    agent.tools.register(SlowTool())
    agent.executor.timeout = 0.05

    with patch.object(settings, "MAX_AGENT_ITERATIONS", 2):
        res_json = await agent.handle_message("sess-timeout-term", "Keep timing out")
        res = json.loads(res_json)

    assert mock_model.call_count == 2
    assert "maximum tool iteration limit of 2" in res["content"]


# 7. Permission tool timeout
@pytest.mark.anyio
async def test_permission_tool_timeout():
    mock_model = RecordingMockModelProvider(responses=[
        '[TOOL_CALL]\n{"tool": "perm_tool", "arguments": {"item": "delete_all"}}\n[/TOOL_CALL]'
    ])
    agent = AgentCore()
    agent.model = mock_model
    agent.tools.register(PermTool())
    agent.executor.timeout = 0.05

    with pytest.raises(PermissionRequiredException) as exc_info:
        await agent.handle_message("sess-perm-timeout", "Delete all")

    req = exc_info.value.permission_request
    assert req.tool_name == "perm_tool"
    assert req.status == "pending"


# 8. Cancel before model
@pytest.mark.anyio
async def test_cancel_before_model():
    mock_model = RecordingMockModelProvider(responses=["Should not reach here"])
    agent = AgentCore()
    agent.model = mock_model

    session_id = "sess-cancel-before"
    agent.cancel_session(session_id)

    res_json = await agent.handle_message(session_id, "Hello")
    res = json.loads(res_json)
    assert res["type"] == "text"
    assert "cancelled" in res["content"].lower()
    assert mock_model.call_count == 0


# 9. Cancel during model
@pytest.mark.anyio
async def test_cancel_during_model():
    mock_model = RecordingMockModelProvider(responses=["Delayed answer"], delay=0.2)
    agent = AgentCore()
    agent.model = mock_model

    session_id = "sess-cancel-during-model"

    async def run_task():
        return await agent.handle_message(session_id, "Heavy question")

    task = asyncio.create_task(run_task())
    await asyncio.sleep(0.05)
    agent.cancel_session(session_id)

    res_json = await task
    res = json.loads(res_json)
    assert "cancelled" in res["content"].lower()


# 10. Cancel during tool
@pytest.mark.anyio
async def test_cancel_during_tool():
    mock_model = RecordingMockModelProvider(responses=[
        '[TOOL_CALL]\n{"tool": "slow_tool", "arguments": {"duration": 0.5}}\n[/TOOL_CALL]',
        "Done"
    ])
    agent = AgentCore()
    agent.model = mock_model
    agent.tools.register(SlowTool())
    agent.executor.timeout = 5.0

    session_id = "sess-cancel-during-tool"

    async def run_task():
        return await agent.handle_message(session_id, "Run long tool")

    task = asyncio.create_task(run_task())
    await asyncio.sleep(0.1)
    agent.cancel_session(session_id)

    res_json = await task
    res = json.loads(res_json)
    assert "cancelled" in res["content"].lower()


# 11. Cancel between iterations
@pytest.mark.anyio
async def test_cancel_between_iterations():
    mock_model = RecordingMockModelProvider(responses=[
        '[TOOL_CALL]\n{"tool": "file_list", "arguments": {"path": "."}}\n[/TOOL_CALL]',
        '[TOOL_CALL]\n{"tool": "system_info", "arguments": {}}\n[/TOOL_CALL]',
        "Done"
    ])
    agent = AgentCore()
    agent.model = mock_model

    session_id = "sess-cancel-between"

    # We mock execute_tool to cancel session when first tool finishes
    orig_exec = agent.executor.execute_tool
    async def mock_exec(*args, **kwargs):
        agent.cancel_session(session_id)
        return {"success": True, "data": ["ok"]}

    agent.executor.execute_tool = mock_exec

    res_json = await agent.handle_message(session_id, "Run two tools")
    res = json.loads(res_json)
    assert "cancelled" in res["content"].lower()


# 12. Cross session cancellation isolation
@pytest.mark.anyio
async def test_cross_session_cancellation_isolation():
    mock_model_a = RecordingMockModelProvider(responses=["Delayed answer A"], delay=0.2)
    mock_model_b = RecordingMockModelProvider(responses=["Instant answer B"])

    agent = AgentCore()

    # Session A
    agent.model = mock_model_a
    task_a = asyncio.create_task(agent.handle_message("session-A", "Question A"))
    await asyncio.sleep(0.05)

    # Cancel Session A only
    agent.cancel_session("session-A")

    # Session B should run cleanly
    agent.model = mock_model_b
    res_b_json = await agent.handle_message("session-B", "Question B")
    res_b = json.loads(res_b_json)
    assert res_b["content"] == "Instant answer B"

    res_a_json = await task_a
    res_a = json.loads(res_a_json)
    assert "cancelled" in res_a["content"].lower()


# 13. Cancel after completion
@pytest.mark.anyio
async def test_cancel_after_completion():
    mock_model = RecordingMockModelProvider(responses=["Done answer"])
    agent = AgentCore()
    agent.model = mock_model

    session_id = "sess-cancel-after"
    await agent.handle_message(session_id, "Fast question")

    # Cancelling completed session returns False (not active)
    cancelled = agent.cancel_session(session_id)
    assert cancelled is False

    history = await agent.memory.get_messages(session_id)
    assert len(history) == 2
    assert "Done answer" in history[1]["message"]


# 14. Repeated cancellation
@pytest.mark.anyio
async def test_repeated_cancellation():
    agent = AgentCore()
    session_id = "sess-repeated-cancel"

    c1 = agent.cancel_session(session_id)
    c2 = agent.cancel_session(session_id)
    assert c1 is False
    assert c2 is False
    assert session_id in agent._canceled_sessions


# 15. No stuck agent state
@pytest.mark.anyio
async def test_no_stuck_agent_state():
    mock_model = RecordingMockModelProvider(responses=["Clean end"])
    agent = AgentCore()
    agent.model = mock_model

    session_id = "sess-no-stuck"
    state = AgentState(session_id=session_id, request_id="req-1", user_request="Hello")

    await agent._run_agent_loop(state)
    assert state.completion_state in ("success", "error", "pending_permission", "cancelled")
    assert state.completion_state != "running"
