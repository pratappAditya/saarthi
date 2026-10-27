import os
import sys
import json
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
from app.models.ollama import clean_reasoning
from app.tools.base import BaseTool
from app.security.permissions import PermissionLevel, PermissionRequiredException, permission_store
from app.memory.manager import MemoryRequest


class RecordingMockModelProvider(ModelProvider):
    """
    Controllable mocked model provider that records every invocation,
    captures prompts/history/system_prompt, and returns sequential responses or simulated errors.
    """
    def __init__(self, responses=None, model_name="mock-recording-model"):
        self.model_name = model_name
        self.responses = list(responses) if responses else []
        self.call_count = 0
        self.calls = []
        self.should_raise = None

    async def generate_response(self, prompt: str, history=None, system_prompt: str = None) -> str:
        self.call_count += 1
        self.calls.append({
            "prompt": prompt,
            "history": history,
            "system_prompt": system_prompt
        })
        if self.should_raise:
            raise self.should_raise
        if self.responses:
            return self.responses.pop(0)
        return "Default mock response"


class FailingTestTool(BaseTool):
    @property
    def name(self) -> str:
        return "failing_test_tool"

    @property
    def description(self) -> str:
        return "Test tool that raises an exception."

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
                "reason": {"type": "string"}
            },
            "required": ["reason"]
        }

    @property
    def output_schema(self) -> Dict[str, Any]:
        return {"type": "object"}

    async def execute(self, **kwargs) -> dict:
        raise RuntimeError(f"Simulated failure: {kwargs.get('reason', 'unknown')}")


class ConfirmationTestTool(BaseTool):
    @property
    def name(self) -> str:
        return "confirmation_test_tool"

    @property
    def description(self) -> str:
        return "Test tool requiring user confirmation."

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
                "action": {"type": "string"}
            },
            "required": ["action"]
        }

    @property
    def output_schema(self) -> Dict[str, Any]:
        return {"type": "object"}

    async def execute(self, **kwargs) -> dict:
        return {"status": "executed", "action": kwargs.get("action")}


@pytest.fixture(autouse=True)
def setup_test_environment():
    temp_dir = tempfile.mkdtemp()
    temp_db_path = os.path.join(temp_dir, "test_agent_audit.db")
    
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


# ==============================================================================
# 1. SIMPLE RESPONSE
# ==============================================================================
@pytest.mark.anyio
async def test_simple_response():
    mock_model = RecordingMockModelProvider(responses=["The capital of India is New Delhi."])
    agent = AgentCore()
    agent.model = mock_model

    session_id = "test-simple-session"
    res_json = await agent.handle_message(session_id, "What is the capital of India?")
    res = json.loads(res_json)

    assert res["type"] == "text"
    assert res["content"] == "The capital of India is New Delhi."
    assert mock_model.call_count == 1
    
    history = await agent.memory.get_messages(session_id)
    assert len(history) == 2
    assert history[0]["sender"] == "user"
    assert history[1]["sender"] == "assistant"


# ==============================================================================
# 2. TOOL LOOP
# ==============================================================================
@pytest.mark.anyio
async def test_tool_loop():
    responses = [
        '[TOOL_CALL]\n{"tool": "file_list", "arguments": {"path": "."}}\n[/TOOL_CALL]',
        "Found 2 files: main.py and README.md."
    ]
    mock_model = RecordingMockModelProvider(responses=responses)
    agent = AgentCore()
    agent.model = mock_model

    mock_executor = AsyncMock()
    mock_executor.execute_tool.return_value = {
        "success": True,
        "data": ["main.py", "README.md"]
    }
    agent.executor = mock_executor

    session_id = "test-tool-loop-session"
    res_json = await agent.handle_message(session_id, "List files in workspace")
    res = json.loads(res_json)

    assert mock_model.call_count == 2
    assert mock_executor.execute_tool.call_count == 1
    assert res["content"] == "Found 2 files: main.py and README.md."

    second_call_history = mock_model.calls[1]["history"]
    tool_result_msgs = [m for m in second_call_history if "main.py" in m.get("message", "")]
    assert len(tool_result_msgs) == 1
    assert "main.py" in tool_result_msgs[0]["message"]


# ==============================================================================
# 3. MULTIPLE TOOL CALLS (SEQUENTIAL MULTI-TOOL EXECUTION)
# ==============================================================================
@pytest.mark.anyio
async def test_multiple_tool_calls_supported():
    responses = [
        '[TOOL_CALL]\n{"tool": "file_list", "arguments": {"path": "."}}\n[/TOOL_CALL]\n'
        '[TOOL_CALL]\n{"tool": "system_info", "arguments": {}}\n[/TOOL_CALL]',
        "Recovery answer after tool format warning."
    ]
    mock_model = RecordingMockModelProvider(responses=responses)
    agent = AgentCore()
    agent.model = mock_model

    session_id = "test-multi-tool-session"
    await agent.handle_message(session_id, "Do multiple actions")

    history = await agent.memory.get_messages(session_id)
    tool_results = [json.loads(m["message"]) for m in history if m["sender"] == "user" and "tool_result" in m.get("message", "")]
    
    assert len(tool_results) == 2
    assert tool_results[0]["success"] is True
    assert tool_results[1]["success"] is True


# ==============================================================================
# 4. MALFORMED TOOL CALLS
# ==============================================================================
@pytest.mark.anyio
async def test_malformed_tool_calls():
    # 4a: Invalid JSON
    mock_model_1 = RecordingMockModelProvider(responses=[
        '[TOOL_CALL]\n{invalid_json_here}\n[/TOOL_CALL]',
        "Handled invalid JSON gracefully."
    ])
    agent_1 = AgentCore()
    agent_1.model = mock_model_1
    await agent_1.handle_message("session-malformed-1", "Test invalid json")
    hist_1 = await agent_1.memory.get_messages("session-malformed-1")
    res_1 = [json.loads(m["message"]) for m in hist_1 if "tool_result" in m.get("message", "")][0]
    assert res_1["error"]["type"] == "MALFORMED_TOOL_CALL"

    # 4b: Unknown tool
    mock_model_2 = RecordingMockModelProvider(responses=[
        '[TOOL_CALL]\n{"tool": "nonexistent_tool_xyz", "arguments": {}}\n[/TOOL_CALL]',
        "Handled unknown tool."
    ])
    agent_2 = AgentCore()
    agent_2.model = mock_model_2
    await agent_2.handle_message("session-malformed-2", "Test unknown tool")
    hist_2 = await agent_2.memory.get_messages("session-malformed-2")
    res_2 = [json.loads(m["message"]) for m in hist_2 if "tool_result" in m.get("message", "")][0]
    assert res_2["error"]["type"] == "UNKNOWN_TOOL"

    # 4c: Missing tool name
    mock_model_3 = RecordingMockModelProvider(responses=[
        '[TOOL_CALL]\n{"arguments": {"foo": "bar"}}\n[/TOOL_CALL]',
        "Handled missing tool name."
    ])
    agent_3 = AgentCore()
    agent_3.model = mock_model_3
    await agent_3.handle_message("session-malformed-3", "Test missing tool name")
    hist_3 = await agent_3.memory.get_messages("session-malformed-3")
    res_3 = [json.loads(m["message"]) for m in hist_3 if "tool_result" in m.get("message", "")][0]
    assert res_3["error"]["type"] == "MALFORMED_TOOL_CALL"

    # 4d: Mismatched markers
    mock_model_4 = RecordingMockModelProvider(responses=[
        '[TOOL_CALL]\n{"tool": "file_list", "arguments": {}}\n[/TOOL_FILE_LIST]',
        "Handled mismatched markers."
    ])
    agent_4 = AgentCore()
    agent_4.model = mock_model_4
    await agent_4.handle_message("session-malformed-4", "Test mismatched markers")
    hist_4 = await agent_4.memory.get_messages("session-malformed-4")
    res_4 = [json.loads(m["message"]) for m in hist_4 if "tool_result" in m.get("message", "")][0]
    assert res_4["error"]["type"] == "MALFORMED_TOOL_CALL"


# ==============================================================================
# 5. TOOL EXCEPTION
# ==============================================================================
@pytest.mark.anyio
async def test_tool_exception():
    mock_model = RecordingMockModelProvider(responses=[
        '[TOOL_CALL]\n{"tool": "failing_test_tool", "arguments": {"reason": "database unreachable"}}\n[/TOOL_CALL]',
        "I noticed the tool failed with an error."
    ])
    agent = AgentCore()
    agent.model = mock_model
    agent.tools.register(FailingTestTool())

    session_id = "test-tool-exception-session"
    res_json = await agent.handle_message(session_id, "Trigger failing tool")
    res = json.loads(res_json)

    assert mock_model.call_count == 2
    assert res["content"] == "I noticed the tool failed with an error."

    history = await agent.memory.get_messages(session_id)
    tool_results = [json.loads(m["message"]) for m in history if "tool_result" in m.get("message", "")]
    assert len(tool_results) == 1
    assert tool_results[0]["success"] is False
    assert tool_results[0]["error"]["code"] == "EXECUTION_ERROR"
    assert "database unreachable" in tool_results[0]["error"]["message"]


# ==============================================================================
# 6. TOOL TIMEOUT (PHASE A.2 IMPLEMENTATION)
# ==============================================================================
@pytest.mark.anyio
async def test_tool_timeout_implementation():
    agent = AgentCore()
    assert hasattr(agent.executor, "timeout")
    assert agent.executor.timeout == 30.0


# ==============================================================================
# 7. MAX ITERATIONS
# ==============================================================================
@pytest.mark.anyio
async def test_max_iterations():
    mock_model = RecordingMockModelProvider(responses=[
        '[TOOL_CALL]\n{"tool": "system_info", "arguments": {}}\n[/TOOL_CALL]' for _ in range(10)
    ])
    agent = AgentCore()
    agent.model = mock_model

    mock_executor = AsyncMock()
    mock_executor.execute_tool.return_value = {"success": True, "data": "sys info"}
    agent.executor = mock_executor

    session_id = "test-max-iter-session"
    with patch.object(settings, "MAX_AGENT_ITERATIONS", 3):
        res_json = await agent.handle_message(session_id, "Repeat system info")
        res = json.loads(res_json)

    assert mock_model.call_count == 3
    assert mock_executor.execute_tool.call_count == 3
    assert "maximum tool iteration limit of 3" in res["content"]


# ==============================================================================
# 8. EMPTY MODEL RESPONSE
# ==============================================================================
@pytest.mark.anyio
async def test_empty_model_response():
    mock_model = RecordingMockModelProvider(responses=["   \n  "])
    agent = AgentCore()
    agent.model = mock_model

    session_id = "test-empty-response-session"
    res_json = await agent.handle_message(session_id, "Hello")
    res = json.loads(res_json)

    assert res["type"] == "text"
    assert res["content"] == ""


# ==============================================================================
# 9. REASONING CLEANUP
# ==============================================================================
def test_reasoning_cleanup():
    t1 = "<think>internal thoughts</think>User visible content"
    assert clean_reasoning(t1) == "User visible content"

    t2 = "<thinking>internal thoughts</thinking>User visible content"
    assert clean_reasoning(t2) == "User visible content"

    t3 = "Thinking...internal thoughts...done thinking.User visible content"
    assert clean_reasoning(t3) == "User visible content"

    t4 = "<think>unclosed thought tag"
    assert clean_reasoning(t4) == ""

    t5 = "I am thinking about your request."
    assert clean_reasoning(t5) == "I am thinking about your request."


# ==============================================================================
# 10. PERMISSION FLOW
# ==============================================================================
@pytest.mark.anyio
async def test_permission_flow():
    mock_model = RecordingMockModelProvider(responses=[
        '[TOOL_CALL]\n{"tool": "confirmation_test_tool", "arguments": {"action": "delete_cache"}}\n[/TOOL_CALL]',
        "Action completed after approval."
    ])
    agent = AgentCore()
    agent.model = mock_model
    agent.tools.register(ConfirmationTestTool())

    session_id = "test-perm-session"
    
    # Step 1: Trigger permission request
    with pytest.raises(PermissionRequiredException) as exc_info:
        await agent.handle_message(session_id, "Delete cache")

    req = exc_info.value.permission_request
    assert req.tool_name == "confirmation_test_tool"
    assert req.status == "pending"

    # Step 2: Test Denial
    agent_denial = AgentCore()
    agent_denial.model = RecordingMockModelProvider(responses=["Understood, action was denied."])
    agent_denial.tools.register(ConfirmationTestTool())
    
    res_denied_json = await agent_denial.resume_with_permission(req, approved=False)
    res_denied = json.loads(res_denied_json)
    assert res_denied["type"] == "text"

    hist_denied = await agent_denial.memory.get_messages(session_id)
    denied_results = [json.loads(m["message"]) for m in hist_denied if "tool_result" in m.get("message", "")]
    assert len(denied_results) == 1
    assert denied_results[0]["error"]["type"] == "PERMISSION_DENIED"

    # Step 3: Test Approval
    agent_approval = AgentCore()
    agent_approval.model = RecordingMockModelProvider(responses=["Executed successfully after approval."])
    agent_approval.tools.register(ConfirmationTestTool())

    req2 = permission_store.create_request(
        tool_name="confirmation_test_tool",
        arguments={"action": "delete_cache"},
        permission_level="USER_CONFIRMATION",
        risk_level="MEDIUM",
        session_id="test-perm-session-2"
    )
    res_approved_json = await agent_approval.resume_with_permission(req2, approved=True)
    res_approved = json.loads(res_approved_json)
    assert res_approved["type"] == "text"

    hist_approved = await agent_approval.memory.get_messages("test-perm-session-2")
    approved_results = [json.loads(m["message"]) for m in hist_approved if "tool_result" in m.get("message", "")]
    assert len(approved_results) == 1
    assert approved_results[0]["success"] is True


# ==============================================================================
# 11. SESSION ISOLATION
# ==============================================================================
@pytest.mark.anyio
async def test_session_isolation():
    agent = AgentCore()
    agent.model = RecordingMockModelProvider(responses=["Response A", "Response B"])

    await agent.handle_message("session-A", "Secret message for A")
    await agent.handle_message("session-B", "Message for B")

    hist_a = await agent.memory.get_messages("session-A")
    hist_b = await agent.memory.get_messages("session-B")

    assert len(hist_a) == 2
    assert len(hist_b) == 2
    assert "Secret message for A" in hist_a[0]["message"]
    assert "Secret message for A" not in hist_b[0]["message"]


# ==============================================================================
# 12. MEMORY BEHAVIOR & SECRET SCREENING
# ==============================================================================
@pytest.mark.anyio
async def test_memory_behavior():
    from app.memory.manager import memory_manager
    # Exactly-once write and retrieval
    memory_manager.create_memory(
        category="USER",
        key="theme_pref",
        content="Prefers dark theme in all IDEs."
    )

    mems = memory_manager.list_memories(status="ACTIVE")
    assert len(mems) == 1
    assert mems[0]["content"] == "Prefers dark theme in all IDEs."

    # Secret screening prevention
    with pytest.raises(ValueError) as exc_info:
        memory_manager.create_memory(
            category="USER",
            key="api_token",
            content="my_secret_token_123456789"
        )
    assert "Refusing to store potential secrets" in str(exc_info.value)


# ==============================================================================
# 13. MODEL CALL COUNTING
# ==============================================================================
@pytest.mark.anyio
async def test_model_call_counting():
    # Simple response -> 1 call
    m1 = RecordingMockModelProvider(responses=["Hello"])
    a1 = AgentCore()
    a1.model = m1
    await a1.handle_message("s-count-1", "Hi")
    assert m1.call_count == 1

    # One tool call -> 2 calls
    m2 = RecordingMockModelProvider(responses=[
        '[TOOL_CALL]\n{"tool": "system_info", "arguments": {}}\n[/TOOL_CALL]',
        "System is Windows 11."
    ])
    a2 = AgentCore()
    a2.model = m2
    await a2.handle_message("s-count-2", "Check sys info")
    assert m2.call_count == 2

    # Permission required tool -> 1 call (paused before 2nd call)
    m3 = RecordingMockModelProvider(responses=[
        '[TOOL_CALL]\n{"tool": "confirmation_test_tool", "arguments": {"action": "run"}}\n[/TOOL_CALL]'
    ])
    a3 = AgentCore()
    a3.model = m3
    a3.tools.register(ConfirmationTestTool())
    with pytest.raises(PermissionRequiredException):
        await a3.handle_message("s-count-3", "Run action")
    assert m3.call_count == 1


# ==============================================================================
# 14. TERMINATION PATHS
# ==============================================================================
@pytest.mark.anyio
async def test_termination_paths():
    agent = AgentCore()

    # Path A: Normal answer
    agent.model = RecordingMockModelProvider(responses=["Direct answer"])
    res_a = await agent.handle_message("s-term-1", "Simple question")
    assert "Direct answer" in res_a

    # Path B: Memory command shortcut (0 model calls)
    agent.model = RecordingMockModelProvider(responses=["Not called"])
    res_b = await agent.handle_message("s-term-2", "What do you remember about me?")
    assert agent.model.call_count == 0

    # Path C: Model failure
    agent.model = RecordingMockModelProvider()
    agent.model.should_raise = RuntimeError("LLM connection failed")
    res_c = await agent.handle_message("s-term-3", "Fail model")
    assert "error communicating with the local AI model" in res_c


# ==============================================================================
# 15. CANCELLATION (PHASE A.2 IMPLEMENTATION)
# ==============================================================================
@pytest.mark.anyio
async def test_cancellation_implementation():
    agent = AgentCore()
    assert hasattr(agent, "cancel_session")
