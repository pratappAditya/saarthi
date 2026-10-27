from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class PermissionScope(str, Enum):
    ONE_TIME = "one_time"
    SESSION = "session"
    TASK = "task"
    PERSISTENT = "persistent"

class PermissionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"
    REVOKED = "revoked"

class PermissionRequest(BaseModel):
    id: Optional[int] = None
    request_id: str
    user_id: str = "default_local_user"
    session_id: Optional[str] = "default_session"
    tool_id: str
    action_description: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    risk_level: str = "MODERATE"
    scope: PermissionScope = PermissionScope.ONE_TIME
    status: PermissionStatus = PermissionStatus.PENDING
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
