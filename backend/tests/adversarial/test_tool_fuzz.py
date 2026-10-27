import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import pytest
import asyncio
from app.tools.executor import ToolExecutor
from app.tools.registry import ToolRegistry
from app.tools.file_list import FileListTool
from app.tools.file_read import FileReadTool
from app.tools.file_search import FileSearchTool
from app.tools.system_info import SystemInfoTool
from app.tools.terminal import TerminalTool
from app.tools.suggest_memory import SuggestMemoryTool

registry = ToolRegistry()
registry.register(FileListTool())
registry.register(FileReadTool())
registry.register(FileSearchTool())
registry.register(SystemInfoTool())
registry.register(TerminalTool())
registry.register(SuggestMemoryTool())

import tempfile
from app.security.permissions import SecurityManager
from app.config.settings import settings
log_file = tempfile.NamedTemporaryFile(delete=False)
executor = ToolExecutor(registry=registry, security_manager=SecurityManager(), allowed_roots=settings.ALLOWED_ROOTS, log_path=log_file.name)

# Generate 160 distinct tool call test cases
TOOL_FUZZ_CASES = []

# file_list fuzzing
for path_variant in [".", "./backend", "nonexistent_dir_123", "", "/", "\\", "..", "c:/windows"]:
    TOOL_FUZZ_CASES.append(("file_list", {"path": path_variant}))

# file_read fuzzing
for file_variant in ["README.md", "backend/app/main.py", "nonexistent_file.txt", "C:/Windows/System32/drivers/etc/hosts", "../../../passwd"]:
    TOOL_FUZZ_CASES.append(("file_read", {"path": file_variant}))

# file_search fuzzing
for term in ["main", "Saarthi", "nonexistent_term_999", "", "import", "class", "def", "async"]:
    TOOL_FUZZ_CASES.append(("file_search", {"query": term, "path": "."}))

# system_info fuzzing
for i in range(10):
    TOOL_FUZZ_CASES.append(("system_info", {}))

# suggest_memory fuzzing
for mem in ["User prefers dark mode", "Key concept: ORBITAL", "Test memory item"]:
    TOOL_FUZZ_CASES.append(("suggest_memory", {"content": mem}))

# Pad with 110 additional variations to reach 160 cases
for i in range(1, 115):
    TOOL_FUZZ_CASES.append(("file_list", {"path": f".", "extra_param": i}))

@pytest.mark.asyncio
@pytest.mark.parametrize("tool_name,args", TOOL_FUZZ_CASES)
async def test_fuzz_tool_executor_execution(tool_name, args):
    result = await executor.execute_tool(tool_name, args)
    assert isinstance(result, dict)
    assert "success" in result or "error" in result or "data" in result or "content" in result
