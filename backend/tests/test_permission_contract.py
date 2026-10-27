import pytest
from app.security.permissions import PermissionStore, PermissionLevel, SecurityManager

def test_permission_store_request_creation_and_lookup():
    store = PermissionStore()
    req = store.create_request(
        tool_name="terminal",
        arguments={"command": "dir"},
        permission_level="USER_CONFIRMATION",
        risk_level="HIGH",
        session_id="sess-perm-1"
    )
    assert req.request_id.startswith("req-")
    assert req.status == "pending"
    assert req.session_id == "sess-perm-1"
    assert req.tool_name == "terminal"

    fetched = store.get_request(req.request_id)
    assert fetched is req

def test_permission_request_status_immutability():
    store = PermissionStore()
    req = store.create_request(
        tool_name="terminal",
        arguments={"command": "dir"},
        permission_level="USER_CONFIRMATION",
        risk_level="HIGH",
        session_id="sess-perm-1"
    )
    assert req.status == "pending"
    req.status = "approved"
    assert req.status == "approved"

    # Once approved, pending requests list should not include it
    pending = store.get_pending()
    assert req not in pending

def test_security_manager_hierarchy():
    sm = SecurityManager(default_level=PermissionLevel.USER_CONFIRMATION)
    assert sm.is_allowed(PermissionLevel.READ_ONLY) is True
    assert sm.is_allowed(PermissionLevel.SAFE) is True
    assert sm.is_allowed(PermissionLevel.USER_CONFIRMATION) is True
    assert sm.is_allowed(PermissionLevel.PRIVILEGED) is False
