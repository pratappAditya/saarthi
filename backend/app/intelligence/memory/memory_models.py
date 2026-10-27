from typing import Dict, Any, List, Optional
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime, timezone

# ------------------ Canonical Memory Classes ------------------

class MemoryClass(str, Enum):
    SHORT_TERM_CONTEXT = "SHORT_TERM_CONTEXT"
    CONVERSATION_MEMORY = "CONVERSATION_MEMORY"
    USER_MEMORY = "USER_MEMORY"
    PROJECT_MEMORY = "PROJECT_MEMORY"
    GOAL_MEMORY = "GOAL_MEMORY"
    DOMAIN_EXPERTISE = "DOMAIN_EXPERTISE"
    WORKFLOW_MEMORY = "WORKFLOW_MEMORY"
    PREFERENCE_MEMORY = "PREFERENCE_MEMORY"
    VOICE_MEMORY = "VOICE_MEMORY"

# Backwards compatibility alias
MemoryType = MemoryClass


# ------------------ Canonical Memory Scopes ------------------

class MemoryScope(str, Enum):
    GLOBAL_USER = "global_user"
    PROJECT = "project"
    GOAL = "goal"
    DOMAIN = "domain"
    CONVERSATION = "conversation"
    TASK = "task"
    USER = "user"  # alias for backwards compatibility


# ------------------ Canonical Provenance Classes ------------------

class MemoryProvenance(str, Enum):
    USER_EXPLICIT = "USER_EXPLICIT"
    SOURCE_DERIVED = "SOURCE_DERIVED"
    OBSERVED = "OBSERVED"
    MODEL_INFERENCE = "MODEL_INFERENCE"

    # Lowercase aliases for existing DB records
    user_explicit = "user_explicit"
    uploaded_document = "uploaded_document"
    tool_observation = "tool_observation"
    model_inference = "model_inference"


# ------------------ Retention & Expiration States ------------------

class RetentionState(str, Enum):
    DURABLE = "durable"
    TEMPORARY = "temporary"
    EXPIRING = "expiring"
    ARCHIVED = "archived"


# ------------------ Memory Item Model ------------------

class MemoryItem(BaseModel):
    id: Optional[int] = None
    user_id: str = "default_local_user"
    memory_class: MemoryClass = MemoryClass.USER_MEMORY
    content: str
    provenance: MemoryProvenance = MemoryProvenance.USER_EXPLICIT
    confidence: float = 1.0
    importance: int = 5  # 1 to 10 scale
    scope: MemoryScope = MemoryScope.GLOBAL_USER
    domain: Optional[str] = "general"
    project_id: Optional[str] = None
    goal_id: Optional[str] = None
    workflow_id: Optional[str] = None
    conversation_id: Optional[str] = None
    task_id: Optional[str] = None
    retention_state: str = RetentionState.DURABLE.value
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    expires_at: Optional[str] = None
    last_accessed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    access_count: int = 0
    is_active: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # Backwards compatibility properties
    @property
    def type(self) -> MemoryClass:
        return self.memory_class

    @property
    def source(self) -> MemoryProvenance:
        return self.provenance
