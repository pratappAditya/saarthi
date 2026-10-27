import pytest
from app.security.permissions import PermissionStore

PERMISSION_FUZZ_CASES = [
    # (request_id, tool_name, args, session_id)
    ("req_101", "terminal", {"command": "dir"}, "session_perm_1"),
    ("req_102", "terminal", {"command": "echo test"}, "session_perm_1"),
    ("req_103", "terminal", {"command": "type README.md"}, "session_perm_2"),
] + [(f"req_perm_{i}", "terminal", {"command": f"echo {i}"}, f"sess_{i % 5}") for i in range(104, 201)]


@pytest.mark.parametrize("req_id,tool,args,sess", PERMISSION_FUZZ_CASES)
def test_fuzz_permission_creation_and_lookup(req_id, tool, args, sess):
    store = PermissionStore()
    req = store.create_request(tool_name=tool, arguments=args, permission_level="USER_CONFIRMATION", risk_level="medium", session_id=sess)
    assert req.request_id is not None
    assert store.get_request(req.request_id) == req
