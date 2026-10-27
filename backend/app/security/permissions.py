from enum import Enum
from app.security.paths import is_path_allowed
from app.config.settings import settings
import uuid
import datetime
from typing import Dict, Any, List

class PermissionLevel(str, Enum):
    READ_ONLY = "READ_ONLY"
    SAFE = "SAFE"
    USER_CONFIRMATION = "USER_CONFIRMATION"
    PRIVILEGED = "PRIVILEGED"

class SecurityManager:
    def validate_path(self, path: str) -> str:
        """Validate the given path against allowed roots.
        Returns the normalized path if allowed, otherwise raises SandboxViolationError.
        """
        if not is_path_allowed(path, settings.ALLOWED_ROOTS):
            raise SandboxViolationError(f"Path {path} is not allowed")
        # Return normalized path for convenience
        return path
    def __init__(self, default_level: PermissionLevel = PermissionLevel.USER_CONFIRMATION):
        self.current_safety_level = default_level

    def is_allowed(self, required_level: PermissionLevel) -> bool:
        # Simplistic hierarchy mapping
        levels = [
            PermissionLevel.READ_ONLY,
            PermissionLevel.SAFE,
            PermissionLevel.USER_CONFIRMATION,
            PermissionLevel.PRIVILEGED,
        ]
        
        try:
            req_idx = levels.index(required_level)
            curr_idx = levels.index(self.current_safety_level)
            return curr_idx >= req_idx
        except ValueError:
            return False

class PermissionRequest:
    def __init__(self, tool_name: str, arguments: dict, permission_level: str, risk_level: str, session_id: str):
        self.request_id = f"req-{uuid.uuid4().hex[:8]}"
        self.tool_name = tool_name
        self.arguments = arguments
        self.permission_level = permission_level
        self.risk_level = risk_level
        self.session_id = session_id
        self.created_timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
        self.status = "pending"  # pending, approved, denied
        
        # Action description
        if tool_name == "terminal":
            self.action_description = f"Run PowerShell command: {arguments.get('command')}"
        else:
            self.action_description = f"Execute tool {tool_name} with arguments {arguments}"

    def to_dict(self) -> dict:
        return {
            "request_id": self.request_id,
            "tool_name": self.tool_name,
            "action_description": self.action_description,
            "arguments": self.arguments,
            "permission_level": self.permission_level,
            "risk_level": self.risk_level,
            "created_timestamp": self.created_timestamp,
            "status": self.status,
            "session_id": self.session_id
        }

class PermissionStore:
    def __init__(self):
        self._requests: Dict[str, PermissionRequest] = {}

    def create_request(self, tool_name: str, arguments: dict, permission_level: str, risk_level: str, session_id: str) -> PermissionRequest:
        req = PermissionRequest(tool_name, arguments, permission_level, risk_level, session_id)
        self._requests[req.request_id] = req
        return req

    def get_request(self, request_id: str) -> PermissionRequest:
        return self._requests.get(request_id)

    def get_pending(self) -> List[PermissionRequest]:
        return [req for req in self._requests.values() if req.status == "pending"]

    def clear(self):
        self._requests.clear()

permission_store = PermissionStore()

class SandboxViolationError(Exception):
    """Raised when a path is outside allowed sandbox roots."""

class PermissionRequiredException(Exception):
    def __init__(self, permission_request: PermissionRequest):
        self.permission_request = permission_request
        super().__init__(f"Permission required for tool {permission_request.tool_name}")
