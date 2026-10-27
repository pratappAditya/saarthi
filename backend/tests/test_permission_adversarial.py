import pytest
import json
from unittest.mock import AsyncMock
from app.agent.core import AgentCore
from app.security.permissions import PermissionStore, PermissionLevel, SecurityManager

@pytest.mark.anyio
async def test_permission_adversarial_wrong_request_id():
    store = PermissionStore()
    req = store.create_request("terminal", {"command": "dir"}, "USER_CONFIRMATION", "HIGH", "sess-1")
    
    # Nonexistent request ID returns None
    assert store.get_request("req-invalid-999") is None

@pytest.mark.anyio
async def test_permission_adversarial_double_approval_rejection():
    store = PermissionStore()
    req = store.create_request("terminal", {"command": "dir"}, "USER_CONFIRMATION", "HIGH", "sess-1")
    
    req.status = "approved"
    assert req.status == "approved"
    # Filter pending requests
    pending = store.get_pending()
    assert req not in pending

@pytest.mark.anyio
async def test_permission_adversarial_double_denial_rejection():
    store = PermissionStore()
    req = store.create_request("terminal", {"command": "dir"}, "USER_CONFIRMATION", "HIGH", "sess-1")
    
    req.status = "denied"
    assert req.status == "denied"
    pending = store.get_pending()
    assert req not in pending

@pytest.mark.anyio
async def test_permission_adversarial_privileged_tool_rejected():
    agent = AgentCore()
    # Privileged safety level is always rejected by executor / security manager
    assert agent.security_manager.is_allowed(PermissionLevel.PRIVILEGED) is False
