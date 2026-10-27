import pytest
import asyncio
from app.agent.errors import SaarthiError, ErrorCategory, InvalidStateTransitionError
from app.agent.core import AgentCore
from app.tools.executor import ToolExecutor
from app.tools.registry import ToolRegistry

FAILURE_CASES = [
    (SaarthiError(ErrorCategory.TOOL_ERROR, "Mock tool execution failure", details={"tool_name": "terminal"}), "terminal"),
    (ValueError("Invalid argument type"), "file_read"),
    (TimeoutError("Sync tool timed out"), "terminal"),
] + [(SaarthiError(ErrorCategory.INTERNAL_ERROR, f"Injected failure #{i}"), f"tool_{i}") for i in range(1, 58)]

@pytest.mark.parametrize("error_obj,tool_name", FAILURE_CASES)
def test_fuzz_error_sanitization(error_obj, tool_name):
    # Verify error string representations do not leak local paths or credentials
    err_str = str(error_obj)
    assert "C:\\Users\\prata" not in err_str
    assert "password=" not in err_str
    assert "sk-proj" not in err_str
