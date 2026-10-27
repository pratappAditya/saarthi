from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class AdminRoleEnum(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    SUPPORT = "SUPPORT"
    ANALYST = "ANALYST"

class AdminUser(BaseModel):
    admin_id: str
    email: str
    role: AdminRoleEnum
    full_name: Optional[str] = ""
    status: str = "ACTIVE"
    created_at: str
    updated_at: str

class AdminSession(BaseModel):
    session_token: str
    admin_id: str
    expires_at: str
    ip_address: str = "127.0.0.1"
    created_at: str

class AdminPermission(BaseModel):
    permission_code: str
    module: str
    action: str

class AdminAuditEvent(BaseModel):
    id: Optional[int] = None
    admin_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    action: str
    target: Optional[str] = ""
    reason: Optional[str] = ""
    previous_state: Optional[Dict[str, Any]] = Field(default_factory=dict)
    resulting_state: Optional[Dict[str, Any]] = Field(default_factory=dict)
    request_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    status: str = "SUCCESS"
