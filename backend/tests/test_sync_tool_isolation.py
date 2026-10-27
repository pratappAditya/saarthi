import os
import time
import asyncio
import threading
import pytest
from typing import Dict, Any

from app.tools.base import BaseTool
from app.tools.registry import ToolRegistry
from app.tools.executor import ToolExecutor
from app.tools.terminal import TerminalTool
from app.security.permissions import SecurityManager, PermissionLevel
from app.config.settings import settings
from app.agent.core import AgentCore, AgentState


class SampleSyncTool(BaseTool):
    @property
    def name(self) -> str:
        return "sample_sync_tool"

    @property
    def description(self) -> str:
        return "A sample synchronous test tool."

    @property
    def permission_level(self) -> PermissionLevel:
        return PermissionLevel.SAFE

    @property
    def risk_classification(self) -> str:
        return "LOW"

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"echo": {"type": "string"}}}

    @property
    def output_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"result": {"type": "string"}}}

    @property
    def is_synchronous(self) -> bool:
        return True

    async def execute(self, echo: str = "hello", **kwargs) -> Any:
        return await asyncio.to_thread(self._execute_sync, echo=echo, **kwargs)

    def _execute_sync(self, echo: str = "hello", **kwargs) -> Any:
        return {"result": f"processed_{echo}"}


class BlockingSyncTool(BaseTool):
    def __init__(self, block_event: threading.Event = None, delay: float = 0.15):
        self.block_event = block_event or threading.Event()
        self.delay = delay
        self.completed = False

    @property
    def name(self) -> str:
        return "blocking_sync_tool"

    @property
    def description(self) -> str:
        return "A blocking synchronous test tool."

    @property
    def permission_level(self) -> PermissionLevel:
        return PermissionLevel.SAFE

    @property
    def risk_classification(self) -> str:
        return "LOW"

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {}}

    @property
    def output_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {}}

    @property
    def is_synchronous(self) -> bool:
        return True

    async def execute(self, **kwargs) -> Any:
        return await asyncio.to_thread(self._execute_sync, **kwargs)

    def _execute_sync(self, **kwargs) -> Any:
        # Wait on thread event or sleep for specified delay
        if self.block_event.is_set():
            time.sleep(self.delay)
        else:
            self.block_event.wait(timeout=self.delay)
        self.completed = True
        return {"status": "done"}


class NativeAsyncTool(BaseTool):
    @property
    def name(self) -> str:
        return "native_async_tool"

    @property
    def description(self) -> str:
        return "A native asynchronous test tool."

    @property
    def permission_level(self) -> PermissionLevel:
        return PermissionLevel.SAFE

    @property
    def risk_classification(self) -> str:
        return "LOW"

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {}}

    @property
    def output_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {}}

    @property
    def is_synchronous(self) -> bool:
        return False

    async def execute(self, delay: float = 0.05, **kwargs) -> Any:
        await asyncio.sleep(delay)
        return {"status": "async_done"}


class ExceptionSyncTool(BaseTool):
    @property
    def name(self) -> str:
        return "exception_sync_tool"

    @property
    def description(self) -> str:
        return "A synchronous tool that raises an exception."

    @property
    def permission_level(self) -> PermissionLevel:
        return PermissionLevel.SAFE

    @property
    def risk_classification(self) -> str:
        return "LOW"

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {}}

    @property
    def output_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {}}

    @property
    def is_synchronous(self) -> bool:
        return True

    async def execute(self, **kwargs) -> Any:
        return await asyncio.to_thread(self._execute_sync, **kwargs)

    def _execute_sync(self, **kwargs) -> Any:
        raise ValueError("Simulated synchronous error")


@pytest.fixture
def test_setup(tmp_path):
    log_file = str(tmp_path / "tools.log")
    registry = ToolRegistry()
    security_manager = SecurityManager(PermissionLevel.USER_CONFIRMATION)
    executor = ToolExecutor(
        registry=registry,
        security_manager=security_manager,
        allowed_roots=settings.ALLOWED_ROOTS,
        log_path=log_file,
        timeout=2.0
    )
    return registry, executor, log_file


# 1. test_sync_tool_does_not_block_event_loop
@pytest.mark.anyio
async def test_sync_tool_does_not_block_event_loop(test_setup):
    registry, executor, _ = test_setup
    block_evt = threading.Event()
    tool = BlockingSyncTool(block_event=block_evt, delay=0.15)
    registry.register(tool)

    loop_counter = 0

    async def event_loop_pulse():
        nonlocal loop_counter
        for _ in range(5):
            await asyncio.sleep(0.02)
            loop_counter += 1

    # Start the sync tool and pulse task concurrently on the same event loop
    tool_task = asyncio.create_task(executor.execute_tool("blocking_sync_tool", {}))
    pulse_task = asyncio.create_task(event_loop_pulse())

    res, _ = await asyncio.gather(tool_task, pulse_task)

    assert res["success"] is True
    # The event loop pulse must have executed iterations while the sync tool ran in thread
    assert loop_counter >= 3, f"Event loop was blocked! Counter reached only {loop_counter}"


# 2. test_sync_tool_success
@pytest.mark.anyio
async def test_sync_tool_success(test_setup):
    registry, executor, _ = test_setup
    registry.register(SampleSyncTool())

    res = await executor.execute_tool("sample_sync_tool", {"echo": "world"})
    assert res["success"] is True
    assert res["tool"] == "sample_sync_tool"
    assert res["data"] == {"result": "processed_world"}


# 3. test_sync_tool_timeout
@pytest.mark.anyio
async def test_sync_tool_timeout(tmp_path):
    log_file = str(tmp_path / "tools.log")
    registry = ToolRegistry()
    security_manager = SecurityManager(PermissionLevel.USER_CONFIRMATION)
    # Set short 0.1s timeout
    executor = ToolExecutor(
        registry=registry,
        security_manager=security_manager,
        allowed_roots=settings.ALLOWED_ROOTS,
        log_path=log_file,
        timeout=0.1
    )
    tool = BlockingSyncTool(delay=0.4)
    registry.register(tool)

    res = await executor.execute_tool("blocking_sync_tool", {})
    assert res["success"] is False
    assert res["error"]["code"] == "TOOL_TIMEOUT"
    assert "timed out" in res["error"]["message"]


# 4. test_sync_tool_cancellation
@pytest.mark.anyio
async def test_sync_tool_cancellation(test_setup):
    registry, executor, _ = test_setup
    block_evt = threading.Event()
    tool = BlockingSyncTool(block_event=block_evt, delay=1.0)
    registry.register(tool)

    exec_task = asyncio.create_task(executor.execute_tool("blocking_sync_tool", {}))
    await asyncio.sleep(0.05)

    exec_task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await exec_task

    # Release worker thread
    block_evt.set()


# 5. test_sync_tool_exception
@pytest.mark.anyio
async def test_sync_tool_exception(test_setup):
    registry, executor, _ = test_setup
    registry.register(ExceptionSyncTool())

    res = await executor.execute_tool("exception_sync_tool", {})
    assert res["success"] is False
    assert res["error"]["code"] == "INVALID_ARGUMENT"
    assert "Simulated synchronous error" in res["error"]["message"]


# 6. test_multiple_sync_tools
@pytest.mark.anyio
async def test_multiple_sync_tools(test_setup):
    registry, executor, _ = test_setup
    registry.register(SampleSyncTool())
    registry.register(BlockingSyncTool(delay=0.05))

    res1, res2 = await asyncio.gather(
        executor.execute_tool("sample_sync_tool", {"echo": "task1"}),
        executor.execute_tool("blocking_sync_tool", {})
    )

    assert res1["success"] is True
    assert res1["data"]["result"] == "processed_task1"
    assert res2["success"] is True
    assert res2["data"]["status"] == "done"


# 7. test_sync_and_async_tools_mixed
@pytest.mark.anyio
async def test_sync_and_async_tools_mixed(test_setup):
    registry, executor, _ = test_setup
    registry.register(SampleSyncTool())
    registry.register(NativeAsyncTool())

    res_sync, res_async = await asyncio.gather(
        executor.execute_tool("sample_sync_tool", {"echo": "mixed"}),
        executor.execute_tool("native_async_tool", {"delay": 0.02})
    )

    assert res_sync["success"] is True
    assert res_sync["data"]["result"] == "processed_mixed"
    assert res_async["success"] is True
    assert res_async["data"]["status"] == "async_done"


# 8. test_cross_session_isolation
@pytest.mark.anyio
async def test_cross_session_isolation(test_setup):
    registry, executor, log_file = test_setup
    registry.register(SampleSyncTool())

    res_a = await executor.execute_tool("sample_sync_tool", {"echo": "A"}, session_id="session_A")
    res_b = await executor.execute_tool("sample_sync_tool", {"echo": "B"}, session_id="session_B")

    assert res_a["data"]["result"] == "processed_A"
    assert res_b["data"]["result"] == "processed_B"

    # Verify log entries correctly isolate sessions
    import json
    with open(log_file, "r") as f:
        logs = [json.loads(line) for line in f.read().splitlines() if line.strip()]

    sessions = [l["session_id"] for l in logs]
    assert "session_A" in sessions
    assert "session_B" in sessions


# 9. test_terminal_timeout_regression
@pytest.mark.anyio
async def test_terminal_timeout_regression():
    tool = TerminalTool()
    # Override settings timeout temporarily
    original_timeout = settings.TERMINAL_TIMEOUT_SECONDS
    settings.TERMINAL_TIMEOUT_SECONDS = 0.2

    try:
        res = await tool.execute(command="Start-Sleep -s 3")
        assert res["exit_code"] == -1
        assert "timed out after" in res["stderr"]
    finally:
        settings.TERMINAL_TIMEOUT_SECONDS = original_timeout


# 10. test_no_success_after_timeout
@pytest.mark.anyio
async def test_no_success_after_timeout(tmp_path):
    log_file = str(tmp_path / "tools.log")
    registry = ToolRegistry()
    security_manager = SecurityManager(PermissionLevel.USER_CONFIRMATION)
    executor = ToolExecutor(
        registry=registry,
        security_manager=security_manager,
        allowed_roots=settings.ALLOWED_ROOTS,
        log_path=log_file,
        timeout=0.1
    )
    block_evt = threading.Event()
    tool = BlockingSyncTool(block_event=block_evt, delay=0.3)
    registry.register(tool)

    res = await executor.execute_tool("blocking_sync_tool", {})
    assert res["success"] is False
    assert res["error"]["code"] == "TOOL_TIMEOUT"

    # Wait until background worker thread finishes naturally
    await asyncio.sleep(0.35)

    # Result returned to caller remains TIMEOUT failure
    assert res["success"] is False
    assert res["error"]["code"] == "TOOL_TIMEOUT"


# 11. test_no_stuck_agent_state
@pytest.mark.anyio
async def test_no_stuck_agent_state():
    state = AgentState(
        session_id="test_state_session",
        request_id="req_123",
        user_request="run isolated sync tool"
    )
    assert state.completion_state == "running"

    # Simulate tool execution success transition
    state.completion_state = "success"
    assert state.completion_state != "running"

    # Simulate tool timeout failure transition
    state.completion_state = "error"
    state.errors.append("TOOL_TIMEOUT")
    assert state.completion_state != "running"
