import sys
import os
# Ensure both backend/app and backend are in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app"))

import json
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.config.settings import settings
from app.security.permissions import PermissionLevel, SecurityManager, PermissionRequiredException, permission_store
from app.security.paths import is_path_allowed
from app.tools.registry import ToolRegistry
from app.tools.executor import ToolExecutor
from app.tools.base import BaseTool
from app.tools.file_list import FileListTool
from app.tools.file_read import FileReadTool
from app.tools.file_search import FileSearchTool
from app.tools.system_info import SystemInfoTool
from app.tools.terminal import TerminalTool
from app.agent.core import AgentCore
from app.main import app

# --- Mock Tool for Registry Testing ---
class MockDummyTool(BaseTool):
    @property
    def name(self) -> str:
        return "dummy_tool"
    @property
    def description(self) -> str:
        return "A dummy testing tool."
    @property
    def permission_level(self) -> PermissionLevel:
        return PermissionLevel.SAFE
    @property
    def risk_classification(self) -> str:
        return "LOW"
    @property
    def input_schema(self) -> dict:
        return {"type": "object", "properties": {}}
    @property
    def output_schema(self) -> dict:
        return {"type": "object", "properties": {}}
    async def execute(self, **kwargs):
        return {"status": "ok"}

# --- 1. Test Registry ---
def test_tool_registry():
    registry = ToolRegistry()
    tool = MockDummyTool()
    
    # Register and lookup
    registry.register(tool)
    assert registry.has("dummy_tool") is True
    assert registry.exists("dummy_tool") is True
    assert registry.get("dummy_tool") == tool
    
    # Duplicate registration should raise ValueError
    with pytest.raises(ValueError):
        registry.register(tool)
        
    # List tools
    tools_list = registry.list_tools()
    assert "dummy_tool" in tools_list
    assert tools_list["dummy_tool"]["risk_classification"] == "LOW"
    
    # Unregister
    registry.unregister("dummy_tool")
    assert registry.has("dummy_tool") is False

# --- 2. Test Filesystem Security ---
def test_path_boundary_resolution():
    allowed_roots = ["E:\\Saarthi", "E:\\Saarthi\\data"]
    
    # Standard paths
    assert is_path_allowed("E:\\Saarthi\\README.md", allowed_roots) is True
    assert is_path_allowed("E:\\Saarthi\\backend\\main.py", allowed_roots) is True
    
    # Directory boundary and prefix check
    assert is_path_allowed("E:\\SaarthiProject", allowed_roots) is False
    
    # Case insensitivity on Windows
    if os.name == 'nt':
        assert is_path_allowed("e:\\saarthi\\readme.md", allowed_roots) is True
        
    # Traversal escape
    assert is_path_allowed("E:\\Saarthi\\..\\Windows", allowed_roots) is False
    assert is_path_allowed("E:\\Saarthi\\..\\..\\Users", allowed_roots) is False
    assert is_path_allowed("C:\\Windows", allowed_roots) is False

# --- 3. Test Permissions ---
@pytest.mark.anyio
async def test_permission_logic_and_executor(tmp_path):
    registry = ToolRegistry()
    registry.register(MockDummyTool())
    
    # Tool requiring User Confirmation
    class ConfTool(BaseTool):
        @property
        def name(self) -> str:
            return "conf_tool"
        @property
        def description(self) -> str:
            return "Requires confirmation."
        @property
        def permission_level(self) -> PermissionLevel:
            return PermissionLevel.USER_CONFIRMATION
        @property
        def risk_classification(self) -> str:
            return "HIGH"
        @property
        def input_schema(self) -> dict:
            return {"type": "object", "properties": {}}
        @property
        def output_schema(self) -> dict:
            return {"type": "object", "properties": {}}
        async def execute(self, **kwargs):
            return {"confirmed": True}

    registry.register(ConfTool())
    
    # Tool requiring Privileged
    class PrivTool(BaseTool):
        @property
        def name(self) -> str:
            return "priv_tool"
        @property
        def description(self) -> str:
            return "Requires privileged."
        @property
        def permission_level(self) -> PermissionLevel:
            return PermissionLevel.PRIVILEGED
        @property
        def risk_classification(self) -> str:
            return "HIGH"
        @property
        def input_schema(self) -> dict:
            return {"type": "object", "properties": {}}
        @property
        def output_schema(self) -> dict:
            return {"type": "object", "properties": {}}
        async def execute(self, **kwargs):
            return {"status": "privileged"}

    registry.register(PrivTool())

    security_manager = SecurityManager(PermissionLevel.USER_CONFIRMATION)
    log_file = os.path.join(tmp_path, "tools.log")
    executor = ToolExecutor(
        registry=registry,
        security_manager=security_manager,
        allowed_roots=[str(tmp_path)],
        log_path=log_file
    )
    
    # READ_ONLY/SAFE automatically executes
    res_safe = await executor.execute_tool("dummy_tool", {})
    assert res_safe["success"] is True
    
    # USER_CONFIRMATION without confirmation triggers confirmation error
    res_conf = await executor.execute_tool("conf_tool", {})
    assert res_conf["success"] is False
    assert res_conf["status"] == "pending_confirmation"
    assert res_conf["error"]["code"] == "CONFIRMATION_REQUIRED"
    
    # USER_CONFIRMATION with confirmation executes
    res_conf_ok = await executor.execute_tool("conf_tool", {}, confirmed=True)
    assert res_conf_ok["success"] is True
    assert res_conf_ok["data"]["confirmed"] is True
    
    # PRIVILEGED is immediately rejected
    res_priv = await executor.execute_tool("priv_tool", {})
    assert res_priv["success"] is False
    assert "PRIVILEGED" in res_priv["error"]["message"]

# --- 4. Test Terminal ---
@pytest.mark.anyio
async def test_terminal_tool(tmp_path):
    tool = TerminalTool()
    
    # Override settings for testing
    original_root = settings.TOOL_ROOT_PATH
    original_roots = settings.ALLOWED_ROOTS
    settings.TOOL_ROOT_PATH = str(tmp_path)
    settings.ALLOWED_ROOTS = [str(tmp_path)]
    
    try:
        # Run safe command
        res = await tool.execute(command="Write-Output 'Hello from terminal'")
        assert res["exit_code"] == 0
        assert "Hello from terminal" in res["stdout"]
        
        # Test command chaining rejection
        with pytest.raises(PermissionError) as exc_info:
            await tool.execute(command="Write-Output 'hi' ; dir")
        assert "chaining" in str(exc_info.value)
        
        # Test destructive command rejection
        with pytest.raises(PermissionError) as exc_info:
            await tool.execute(command="Remove-Item test.txt")
        assert "File deletion is not currently enabled in Saarthi..." in str(exc_info.value)

        
        # Test timeout (using sleep command)
        settings.TERMINAL_TIMEOUT_SECONDS = 1
        res_timeout = await tool.execute(command="Start-Sleep -s 5")
        assert res_timeout["exit_code"] == -1
        assert "timed out" in res_timeout["stderr"]
        
    finally:
        # Restore settings
        settings.TOOL_ROOT_PATH = original_root
        settings.ALLOWED_ROOTS = original_roots
        settings.TERMINAL_TIMEOUT_SECONDS = 30

# --- 5. Test AgentCore Tool Iterations and Resumptions ---
@pytest.mark.anyio
async def test_agent_core_orchestration():
    agent = AgentCore()
    
    # Mock the LLM provider
    mock_model = AsyncMock()
    agent.model = mock_model
    
    # A. Test no tool requested
    mock_model.generate_response.return_value = "Hello user, how can I help you today?"
    res_no_tool = await agent.handle_message("sess_1", "Hello")
    assert "Hello user" in res_no_tool
    
    # B. Test valid tool requested (system_info)
    mock_model.generate_response.side_effect = [
        "Let me check system specs: [TOOL_CALL] {\"tool\": \"system_info\", \"arguments\": {}} [/TOOL_CALL]",
        "Your system is running Windows."
    ]
    res_tool = await agent.handle_message("sess_2", "Specs?")
    assert "running Windows" in res_tool
    
    # C. Test permission request (terminal)
    mock_model.generate_response.side_effect = [
        "Let me run npm test: [TOOL_CALL] {\"tool\": \"terminal\", \"arguments\": {\"command\": \"npm test\"}} [/TOOL_CALL]"
    ]
    permission_store.clear()
    with pytest.raises(PermissionRequiredException) as exc_info:
        await agent.handle_message("sess_3", "Run test")
    
    req = exc_info.value.permission_request
    assert req.tool_name == "terminal"
    assert req.arguments["command"] == "npm test"
    
    # D. Test approved tool resumption
    # Set mock response for model when continuing after tool execution
    mock_model.generate_response.side_effect = [
        "The tests passed successfully."
    ]
    # We patch executor's execute_tool to avoid actually launching powershell in this test
    with patch.object(agent.executor, "execute_tool", AsyncMock(return_value={"stdout": "PASS", "stderr": "", "exit_code": 0})):
        res_approved = await agent.resume_with_permission(req, approved=True)
        assert "passed successfully" in res_approved
        
    # E. Test denied tool resumption
    mock_model.generate_response.side_effect = [
        "I could not run the tests because you denied permission."
    ]
    res_denied = await agent.resume_with_permission(req, approved=False)
    assert "denied permission" in res_denied
    
    # F. Test iteration limit
    mock_model.generate_response.side_effect = [
        "Let me list: [TOOL_CALL] {\"tool\": \"system_info\", \"arguments\": {}} [/TOOL_CALL]"
    ] * 10
    
    # Set max iterations to 3 for testing
    original_iter = settings.MAX_TOOL_ITERATIONS
    settings.MAX_TOOL_ITERATIONS = 3
    try:
        res_limit = await agent.handle_message("sess_4", "Infinite loop please")
        assert "iteration limit" in res_limit
    finally:
        settings.MAX_TOOL_ITERATIONS = original_iter

# --- 6. Test API Endpoints ---
def test_api_endpoints():
    client = TestClient(app)
    permission_store.clear()
    
    # A. GET /api/tools
    res_tools = client.get("/api/tools")
    assert res_tools.status_code == 200
    data = res_tools.json()
    assert "terminal" in data["tools"]
    
    # B. Create a pending request manually for API test
    req = permission_store.create_request("terminal", {"command": "dir"}, "USER_CONFIRMATION", "HIGH", "sess_api")
    
    # GET /api/permissions/pending
    res_pending = client.get("/api/permissions/pending")
    assert res_pending.status_code == 200
    pending_list = res_pending.json()
    assert len(pending_list) == 1
    assert pending_list[0]["request_id"] == req.request_id
    
    # C. POST /api/permissions/{request_id}/approve
    # Patch agent's resume_with_permission to avoid LLM calls
    with patch("app.api.routes.agent.resume_with_permission", AsyncMock(return_value="Resumed and finished")):
        res_approve = client.post(f"/api/permissions/{req.request_id}/approve")
        assert res_approve.status_code == 200
        assert res_approve.json()["response"] == "Resumed and finished"
        assert req.status == "approved"
        
    # D. Test Deny with a new request
    req2 = permission_store.create_request("terminal", {"command": "dir"}, "USER_CONFIRMATION", "HIGH", "sess_api2")
    with patch("app.api.routes.agent.resume_with_permission", AsyncMock(return_value="Denied and resumed")):
        res_deny = client.post(f"/api/permissions/{req2.request_id}/deny")
        assert res_deny.status_code == 200
        assert res_deny.json()["response"] == "Denied and resumed"
        assert req2.status == "denied"
