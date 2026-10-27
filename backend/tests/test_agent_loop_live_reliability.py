import os
import sys
import json
import time
import asyncio
import pytest
import tempfile
import shutil
import urllib.request
from typing import Dict, Any

from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app"))

from app.main import app
from app.config.settings import settings
from app.agent.core import AgentCore
from app.models.base import ModelProvider
from app.tools.base import BaseTool
from app.security.permissions import PermissionLevel, permission_store

client = TestClient(app)

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


class AsyncSlowTool(BaseTool):
    @property
    def name(self) -> str:
        return "async_slow_tool"

    @property
    def description(self) -> str:
        return "Natively async tool using await asyncio.sleep."

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
            "properties": {"delay": {"type": "number"}},
            "required": ["delay"]
        }

    @property
    def output_schema(self) -> Dict[str, Any]:
        return {"type": "object"}

    async def execute(self, delay: float = 0.2, **kwargs) -> dict:
        await asyncio.sleep(delay)
        return {"status": "async_complete", "slept": delay}


class SyncBlockingTool(BaseTool):
    @property
    def name(self) -> str:
        return "sync_blocking_tool"

    @property
    def description(self) -> str:
        return "Synchronous blocking tool using time.sleep."

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
            "properties": {"delay": {"type": "number"}},
            "required": ["delay"]
        }

    @property
    def output_schema(self) -> Dict[str, Any]:
        return {"type": "object"}

    async def execute(self, delay: float = 0.2, **kwargs) -> dict:
        time.sleep(delay)
        return {"status": "sync_complete", "slept": delay}


@pytest.fixture(autouse=True)
def setup_test_env():
    temp_dir = tempfile.mkdtemp()
    temp_db_path = os.path.join(temp_dir, "test_live_reliability.db")
    
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


def is_ollama_available() -> bool:
    try:
        req = urllib.request.urlopen("http://localhost:11434/api/tags", timeout=1.0)
        if req.status == 200:
            data = json.loads(req.read().decode("utf-8"))
            models = [m.get("name", "") for m in data.get("models", [])]
            return any(settings.MODEL_NAME in m or "nemotron" in m for m in models)
        return False
    except Exception:
        return False


# ==============================================================================
# 1. MULTI-TOOL LIVE VERIFICATION WITH PRODUCTION TOOLS
# ==============================================================================

@pytest.mark.anyio
async def test_multi_tool_production_tools_execution():
    """
    Tests sequential execution of 3 production read-only tools:
    file_list, file_search, system_info
    """
    mock_model = RecordingMockModelProvider(responses=[
        '[TOOL_CALL]\n{"tool": "file_list", "arguments": {"path": "."}}\n[/TOOL_CALL]\n'
        '[TOOL_CALL]\n{"tool": "file_search", "arguments": {"query": "settings", "path": "."}}\n[/TOOL_CALL]\n'
        '[TOOL_CALL]\n{"tool": "system_info", "arguments": {}}\n[/TOOL_CALL]',
        "Successfully retrieved workspace files, searched for settings, and gathered system information."
    ])
    agent = AgentCore()
    agent.model = mock_model

    session_id = "sess-prod-multi-tool"
    res_json = await agent.handle_message(session_id, "Analyze workspace and system")
    res = json.loads(res_json)

    assert res["content"] == "Successfully retrieved workspace files, searched for settings, and gathered system information."
    assert mock_model.call_count == 2

    history = await agent.memory.get_messages(session_id)
    tool_results = [json.loads(m["message"]) for m in history if "tool_result" in m.get("message", "")]

    assert len(tool_results) == 3
    assert tool_results[0]["tool"] == "file_list"
    assert tool_results[0]["success"] is True
    assert tool_results[1]["tool"] == "file_search"
    assert tool_results[1]["success"] is True
    assert tool_results[2]["tool"] == "system_info"
    assert tool_results[2]["success"] is True


@pytest.mark.anyio
async def test_multi_tool_production_failure_handling():
    """
    Tests that a failure in Tool 1 does not retry Tool 1, allows Tool 2 to execute,
    and records both results distinctly in history.
    """
    mock_model = RecordingMockModelProvider(responses=[
        '[TOOL_CALL]\n{"tool": "file_list", "arguments": {"path": "./nonexistent_path_xyz_123"}}\n[/TOOL_CALL]\n'
        '[TOOL_CALL]\n{"tool": "system_info", "arguments": {}}\n[/TOOL_CALL]',
        "Handled bad path in file_list and reported system info."
    ])
    agent = AgentCore()
    agent.model = mock_model

    session_id = "sess-prod-multi-fail"
    res_json = await agent.handle_message(session_id, "Test bad path + system info")
    res = json.loads(res_json)

    assert res["content"] == "Handled bad path in file_list and reported system info."
    
    history = await agent.memory.get_messages(session_id)
    tool_results = [json.loads(m["message"]) for m in history if "tool_result" in m.get("message", "")]

    assert len(tool_results) == 2
    # Tool 1 failed due to non-existent directory, but did not crash or duplicate
    assert tool_results[0]["tool"] == "file_list"
    assert tool_results[0]["success"] is False
    # Tool 2 succeeded
    assert tool_results[1]["tool"] == "system_info"
    assert tool_results[1]["success"] is True


# ==============================================================================
# 2. REAL TOOL TIMEOUT VERIFICATION
# ==============================================================================

@pytest.mark.anyio
async def test_timeout_async_tool():
    """
    Async tool with await asyncio.sleep:
    - asyncio.wait_for cancels coroutine upon timeout.
    - Operation terminates cleanly, returns TOOL_TIMEOUT.
    - Agent handles error and can recover.
    """
    agent = AgentCore()
    agent.tools.register(AsyncSlowTool())
    agent.executor.timeout = 0.05

    start = time.perf_counter()
    result = await agent.executor.execute_tool("async_slow_tool", {"delay": 0.3})
    duration = time.perf_counter() - start

    assert result["success"] is False
    assert result["error"]["code"] == "TOOL_TIMEOUT"
    assert duration < 0.15


@pytest.mark.anyio
async def test_timeout_sync_blocking_behavior():
    """
    Synchronous blocking tool with time.sleep:
    - Main event loop thread is blocked during synchronous time.sleep execution.
    - Demonstrates that sync blocking operations do not hit await points until finished.
    """
    agent = AgentCore()
    agent.tools.register(SyncBlockingTool())
    agent.executor.timeout = 0.05

    start = time.perf_counter()
    result = await agent.executor.execute_tool("sync_blocking_tool", {"delay": 0.10})
    duration = time.perf_counter() - start

    # Synchronous time.sleep completes without hit of await point, returning output after delay
    assert duration >= 0.09
    assert "status" in result.get("data", {}) or result.get("error", {}).get("code") == "TOOL_TIMEOUT"


# ==============================================================================
# 3. REAL CANCELLATION API VERIFICATION VIA FASTAPI ENDPOINT
# ==============================================================================

def test_cancel_api_endpoint_before_model():
    """
    Cancelling a session via POST /api/chat/cancel/{session_id} before message sending.
    """
    session_id = "sess-api-cancel-before"
    # Pre-cancel session
    resp = client.post(f"/api/chat/cancel/{session_id}")
    assert resp.status_code == 200
    assert resp.json()["session_id"] == session_id

    # Post message
    chat_resp = client.post("/api/chat", json={"session_id": session_id, "message": "Hello"})
    assert chat_resp.status_code == 200
    data = chat_resp.json()
    assert "cancelled" in data["response"].lower()


def test_cancel_api_endpoint_unknown_session():
    """
    Cancelling a non-existent/inactive session returns HTTP 200 with cancelled: False.
    """
    resp = client.post("/api/chat/cancel/nonexistent-session-999")
    assert resp.status_code == 200
    assert resp.json() == {"session_id": "nonexistent-session-999", "cancelled": False}


@pytest.mark.anyio
async def test_cancel_api_endpoint_cross_session_isolation():
    """
    Cancelling session A via HTTP does not affect session B.
    """
    from app.api.routes import agent

    mock_model_a = RecordingMockModelProvider(responses=["Answer A"], delay=0.2)
    mock_model_b = RecordingMockModelProvider(responses=["Answer B"])

    agent.model = mock_model_a
    task_a = asyncio.create_task(agent.handle_message("sess-iso-A", "Question A"))
    await asyncio.sleep(0.05)

    # Cancel session A via API endpoint
    resp = client.post("/api/chat/cancel/sess-iso-A")
    assert resp.status_code == 200

    # Execute session B
    agent.model = mock_model_b
    res_b_json = await agent.handle_message("sess-iso-B", "Question B")
    res_b = json.loads(res_b_json)
    assert res_b["content"] == "Answer B"

    res_a_json = await task_a
    res_a = json.loads(res_a_json)
    assert "cancelled" in res_a["content"].lower()


# ==============================================================================
# 4. SECURITY CHECK VERIFICATION
# ==============================================================================

@pytest.mark.anyio
async def test_cancellation_security_permissions():
    """
    Verifies that cancellation cannot approve permissions or execute privileged tools.
    """
    agent = AgentCore()
    session_id = "sess-sec-cancel"
    agent.cancel_session(session_id)

    # Sending a message to cancelled session should return cancelled status, not grant permissions
    res_json = await agent.handle_message(session_id, "Run privileged tool")
    res = json.loads(res_json)
    assert "cancelled" in res["content"].lower()
    assert len(permission_store.get_pending()) == 0


@pytest.mark.anyio
async def test_cancellation_stale_state_cleanup():
    """
    Verifies that subsequent request on same session ID after cancellation cleans stale state.
    """
    mock_model = RecordingMockModelProvider(responses=["Fresh response after cancellation"])
    agent = AgentCore()
    agent.model = mock_model

    session_id = "sess-stale-clean"
    # First turn: cancelled before run
    agent.cancel_session(session_id)
    res1_json = await agent.handle_message(session_id, "Message 1")
    res1 = json.loads(res1_json)
    assert "cancelled" in res1["content"].lower()

    # Second turn: new user message should execute cleanly
    res2_json = await agent.handle_message(session_id, "Message 2")
    res2 = json.loads(res2_json)
    assert res2["content"] == "Fresh response after cancellation"


# ==============================================================================
# 5. OLLAMA LIVE INTEGRATION (CONDITIONAL/SKIPPED WHEN OFFLINE)
# ==============================================================================

@pytest.mark.skipif(not is_ollama_available(), reason="Ollama local server is not running on http://localhost:11434")
@pytest.mark.anyio
async def test_ollama_live_integration():
    """
    Live test against local Ollama server if active.
    Skipped when Ollama server is offline.
    """
    from app.models.ollama import NemotronProvider
    provider = NemotronProvider(model_name="nemotron-3-nano:4b")
    response = await provider.generate_response(prompt="Reply with 'OK'")
    assert response is not None
