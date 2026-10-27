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
from app.memory.sqlite_store import SQLiteMemoryStore
from app.memory.manager import MemoryManager, memory_manager, memory_request_store, MemoryApprovalRequiredException
from app.memory.commands import MemoryCommandProcessor
from app.tools.suggest_memory import SuggestMemoryTool
from app.agent.core import AgentCore
from app.main import app

client = TestClient(app)

@pytest.fixture
def temp_db(tmp_path):
    db_file = os.path.join(tmp_path, "test_saarthi.db")
    store = SQLiteMemoryStore(db_file)
    manager = MemoryManager(store)
    return manager

# --- 1. Test Store and Manager CRUD ---
def test_memory_crud(temp_db):
    # Create USER memory
    m1 = temp_db.create_memory("USER", "pref_lang", "I prefer Python.")
    assert m1["id"] is not None
    assert m1["category"] == "USER"
    assert m1["key"] == "pref_lang"
    assert m1["content"] == "I prefer Python."
    assert m1["status"] == "ACTIVE"
    
    # Get memory
    m1_get = temp_db.get_memory(m1["id"])
    assert m1_get is not None
    assert m1_get["content"] == "I prefer Python."
    
    # List memories
    all_mems = temp_db.list_memories(category="USER")
    assert len(all_mems) == 1
    
    # Search memories
    search_res = temp_db.search_memory("Python")
    assert len(search_res) == 1
    assert search_res[0]["id"] == m1["id"]
    
    # Update memory
    updated = temp_db.update_memory(m1["id"], content="I prefer Python and Go.")
    assert updated["content"] == "I prefer Python and Go."
    
    # Delete memory
    temp_db.delete_memory(m1["id"])
    assert temp_db.get_memory(m1["id"])["status"] == "DELETED"
    assert len(temp_db.list_memories(status="ACTIVE")) == 0


# --- 2. Test Commands Parser ---
@pytest.mark.anyio
async def test_memory_commands(temp_db):
    with patch("app.memory.commands.memory_manager", temp_db):
        # A. Remember USER preferences
        with pytest.raises(MemoryApprovalRequiredException) as exc_info:
            await MemoryCommandProcessor.process("Remember that I prefer TypeScript.", "sess_cmd")
        req = exc_info.value.memory_request
        assert req.action == "create"
        assert req.category == "USER"
        
        # Simulate approval and creation
        mems_created = temp_db.create_memory(
            category=req.category,
            key=req.key,
            content=req.content,
            project_id=req.project_id,
            source="user"
        )
        
        mems = temp_db.list_memories(category="USER", status="ACTIVE")
        assert len(mems) == 1
        assert "TypeScript" in mems[0]["content"]
        
        # B. What do you remember about me?
        resp_what = await MemoryCommandProcessor.process("What do you remember about me?", "sess_cmd")
        assert "TypeScript" in resp_what
        
        # C. Remember PROJECT details
        with pytest.raises(MemoryApprovalRequiredException) as exc_info:
            await MemoryCommandProcessor.process("Remember this: Saarthi's source code is on E:\\Saarthi.", "sess_cmd")
        req_proj = exc_info.value.memory_request
        assert req_proj.action == "create"
        assert req_proj.category == "PROJECT"
        
        # Simulate approval and creation
        temp_db.create_memory(
            category=req_proj.category,
            key=req_proj.key,
            content=req_proj.content,
            project_id=req_proj.project_id,
            source="user"
        )
        
        mems_proj = temp_db.list_memories(category="PROJECT", status="ACTIVE")
        assert len(mems_proj) == 1
        assert mems_proj[0]["project_id"] == "Saarthi"
        
        # D. What do you remember about Saarthi?
        resp_about_saarthi = await MemoryCommandProcessor.process("What do you remember about Saarthi?", "sess_cmd")
        assert "Saarthi's source code" in resp_about_saarthi
        
        # E. Show my project memories
        resp_all_proj = await MemoryCommandProcessor.process("Show my project memories.", "sess_cmd")
        assert "Saarthi" in resp_all_proj
        
        # F. Forget that...
        with pytest.raises(MemoryApprovalRequiredException) as exc_info:
            await MemoryCommandProcessor.process("Forget that I prefer TypeScript.", "sess_cmd")
        req_forget = exc_info.value.memory_request
        assert req_forget.action == "delete"
        assert req_forget.category == "USER"
        
        # Simulating approval by manually deleting from temp_db
        temp_db.delete_memory(mems[0]["id"])
        
        # G. Forget everything about...
        with pytest.raises(MemoryApprovalRequiredException) as exc_info:
            await MemoryCommandProcessor.process("Forget everything about Saarthi.", "sess_cmd")
        req_forget_all = exc_info.value.memory_request
        assert req_forget_all.action == "delete"
        assert req_forget_all.category == "PROJECT"
        
        # Simulating approval by manually deleting project memory
        temp_db.delete_memory(mems_proj[0]["id"])


# --- 3. Test Suggest Memory Tool ---
@pytest.mark.anyio
async def test_suggest_memory_tool():
    tool = SuggestMemoryTool()
    memory_request_store.clear()
    
    with pytest.raises(MemoryApprovalRequiredException) as exc_info:
        await tool.execute(
            category="USER",
            key="preferred_ide",
            content="Prefers VS Code",
            question="Would you like me to remember that you prefer VS Code?",
            session_id="sess_tool"
        )
        
    req = exc_info.value.memory_request
    assert req.category == "USER"
    assert req.key == "preferred_ide"
    assert req.content == "Prefers VS Code"
    assert req.session_id == "sess_tool"
    assert req.status == "pending"


# --- 4. Test Endpoints Integration ---
@pytest.mark.anyio
async def test_memory_endpoints(temp_db):
    memory_request_store.clear()
    
    with patch("app.api.routes.agent.memory.add_message", AsyncMock()):
        with patch("app.memory.commands.memory_manager", temp_db):
            with patch("app.api.routes.agent.resume_with_memory_approval") as mock_resume:
                # Create a pending memory request in the store
                req = memory_request_store.create_request(
                    category="USER",
                    key="pref_ide",
                    content="Prefers PyCharm",
                    project_id=None,
                    session_id="sess_api"
                )
                
                # Test approve endpoint
                mock_resume.return_value = json.dumps({"type": "text", "content": "I have remembered..."})
                resp_app = client.post(f"/api/memory/approve/{req.request_id}")
                assert resp_app.status_code == 200
                assert resp_app.json()["status"] == "success"
                mock_resume.assert_called_once_with(req, approved=True)
                
                # Test deny endpoint
                req_deny = memory_request_store.create_request(
                    category="USER",
                    key="pref_ide",
                    content="Prefers PyCharm",
                    project_id=None,
                    session_id="sess_api"
                )
                mock_resume.reset_mock()
                mock_resume.return_value = json.dumps({"type": "text", "content": "Understood..."})
                resp_deny = client.post(f"/api/memory/deny/{req_deny.request_id}")
                assert resp_deny.status_code == 200
                assert resp_deny.json()["status"] == "success"
                mock_resume.assert_called_once_with(req_deny, approved=False)
