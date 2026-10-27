import sys
import os
import json
import pytest
import tempfile
import shutil
from unittest.mock import AsyncMock, patch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app"))

from app.config.settings import settings
from app.agent.core import AgentCore, AgentState
import app.memory.manager

@pytest.fixture(autouse=True)
def setup_test_db():
    # Setup temporary database
    temp_dir = tempfile.mkdtemp()
    temp_db_path = os.path.join(temp_dir, "test_saarthi.db")
    
    # Save original settings
    original_db = settings.DATABASE_PATH
    settings.DATABASE_PATH = temp_db_path
    
    # Clear memory manager store to use new path
    from app.memory.sqlite_store import SQLiteMemoryStore
    from app.memory.manager import MemoryManager
    import app.memory.manager
    
    old_mgr = app.memory.manager.memory_manager
    app.memory.manager.memory_manager = MemoryManager(SQLiteMemoryStore(temp_db_path))
    
    yield temp_db_path
    
    # Cleanup
    app.memory.manager.memory_manager = old_mgr
    settings.DATABASE_PATH = original_db
    
    import gc
    gc.collect()
    try:
        shutil.rmtree(temp_dir)
    except Exception:
        # Ignore Windows file lock issues in test teardown
        pass

@pytest.mark.anyio
async def test_secret_screening():
    # Attempt to create memory containing a secret
    with pytest.raises(ValueError) as exc:
        app.memory.manager.memory_manager.create_memory(
            category="USER",
            key="test_password",
            content="my private password is admin123"
        )
    assert "Refusing to store potential secrets" in str(exc.value)

@pytest.mark.anyio
async def test_smart_tool_routing():
    agent = AgentCore()
    
    # Test file-related routing
    tools = agent._route_tools("Can you list all the files in my folder?", [])
    assert "file_list" in tools
    assert "file_read" in tools
    assert "file_search" in tools
    assert "terminal" not in tools
    
    # Test system-related routing
    tools = agent._route_tools("Show system info.", [])
    assert "system_info" in tools
    assert "file_list" not in tools
    
    # Test memory-related routing
    tools = agent._route_tools("Remember that my name is Alice.", [])
    assert "suggest_memory" in tools
    
    # Test general question (no tools)
    tools = agent._route_tools("What is the capital of India?", [])
    assert len(tools) == 0

@pytest.mark.anyio
async def test_memory_scoring_and_retrieval():
    # Let's create some memories
    app.memory.manager.memory_manager.create_memory(
        category="USER",
        key="my_preference",
        content="I prefer dark mode in all UI applications."
    )
    
    app.memory.manager.memory_manager.create_memory(
        category="PROJECT",
        key="saarthi_path",
        content="The Saarthi project is located at E:/Saarthi."
    )
    
    agent = AgentCore()
    
    # Search for user preference
    mems = agent._get_relevant_memories("What is my personal theme preference?")
    assert len(mems) > 0
    assert any(m["category"] == "USER" for m in mems)
    
    # Search for project location
    mems_project = agent._get_relevant_memories("Where is the project located?")
    assert len(mems_project) > 0
    assert any(m["category"] == "PROJECT" for m in mems_project)

@pytest.mark.anyio
async def test_iteration_limit():
    agent = AgentCore()
    
    # Mock model to return a tool call indefinitely
    mock_model = AsyncMock()
    mock_model.model_name = "mock-nemotron"
    mock_model.generate_response.return_value = (
        "[TOOL_CALL]\n"
        '{"tool": "file_list", "arguments": {"directory_path": "."}}\n'
        "[/TOOL_CALL]"
    )
    
    # Mock executor.execute_tool to return success
    mock_executor = AsyncMock()
    mock_executor.execute_tool.return_value = {
        "success": True,
        "data": ["file1.txt"]
    }
    
    with patch.object(agent, "model", mock_model), \
         patch.object(agent, "executor", mock_executor):
        
        session_id = "test-session-limit"
        res_json = await agent.handle_message(session_id, "Find files")
        
        # Verify it terminated and returned iteration limit error message
        res = json.loads(res_json)
        assert res["type"] == "text"
        assert "stopped because the maximum tool iteration limit" in res["content"]
        
        # Check diagnostics log was generated
        log_path = os.path.join(settings.SAARTHI_DATA_DIR, "logs", "agent_diagnostics.log")
        assert os.path.exists(log_path)
        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            assert len(lines) > 0
            last_diag = json.loads(lines[-1])
            assert last_diag["session_id"] == session_id
            assert last_diag["iteration_count"] == settings.MAX_AGENT_ITERATIONS
            assert last_diag["error_status"] is True
