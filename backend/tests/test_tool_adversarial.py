import pytest
import os
import tempfile
from app.config.settings import settings
from app.tools.executor import ToolExecutor
from app.tools.registry import ToolRegistry
from app.tools.file_read import FileReadTool
from app.tools.file_list import FileListTool
from app.tools.terminal import TerminalTool
from app.security.permissions import SecurityManager, PermissionLevel

@pytest.fixture
def temp_env():
    temp_dir = os.path.realpath(tempfile.mkdtemp())
    log_path = os.path.join(temp_dir, "tools.log")
    roots = list(settings.ALLOWED_ROOTS) + [temp_dir]
    yield temp_dir, log_path, roots

@pytest.mark.anyio
async def test_tool_adversarial_path_traversal_blocked(temp_env):
    temp_dir, log_path, roots = temp_env
    registry = ToolRegistry()
    registry.register(FileReadTool())

    sm = SecurityManager(PermissionLevel.USER_CONFIRMATION)
    executor = ToolExecutor(registry=registry, security_manager=sm, allowed_roots=roots, log_path=log_path)

    # Attempting to read files outside allowed root must be rejected
    res = await executor.execute_tool("file_read", {"path": "C:\\Windows\\System32\\drivers\\etc\\hosts"}, session_id="test", confirmed=True)
    assert res["success"] is False
    assert "denied" in res["error"]["message"].lower() or "outside" in res["error"]["message"].lower()

@pytest.mark.anyio
async def test_tool_adversarial_nonexistent_file(temp_env):
    temp_dir, log_path, roots = temp_env
    registry = ToolRegistry()
    registry.register(FileReadTool())

    sm = SecurityManager(PermissionLevel.USER_CONFIRMATION)
    executor = ToolExecutor(registry=registry, security_manager=sm, allowed_roots=roots, log_path=log_path)

    nonexistent = os.path.join(settings.ALLOWED_ROOTS[0], "nonexistent_file_123.txt")
    res = await executor.execute_tool("file_read", {"path": nonexistent}, session_id="test", confirmed=True)
    assert res["success"] is False
    assert "does not exist" in res["error"]["message"].lower() or "not found" in res["error"]["message"].lower() or "denied" in res["error"]["message"].lower()

@pytest.mark.anyio
async def test_tool_adversarial_terminal_dangerous_command_blocked(temp_env):
    temp_dir, log_path, roots = temp_env
    registry = ToolRegistry()
    registry.register(TerminalTool())

    sm = SecurityManager(PermissionLevel.USER_CONFIRMATION)
    executor = ToolExecutor(registry=registry, security_manager=sm, allowed_roots=roots, log_path=log_path)

    # Deleting root directories should be blocked by TerminalTool safety filter
    res = await executor.execute_tool("terminal", {"command": "Remove-Item -Recurse -Force C:\\"}, session_id="test", confirmed=True)
    assert res["success"] is False
    assert "not currently enabled" in res["error"]["message"].lower() or "file deletion" in res["error"]["message"].lower()
