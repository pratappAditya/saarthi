from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from app.intelligence.personalization.personalization_model import PersonalizationContext

class UserContext(BaseModel):
    user_id: str = "default_local_user"
    full_name: str = "Pratap Aditya"
    plan_id: str = "power"
    preferred_domain: str = "career"

class ConversationContext(BaseModel):
    session_id: str = "default_session"
    recent_messages: List[Dict[str, Any]] = Field(default_factory=list)

class MemoryContext(BaseModel):
    profile_facts: List[str] = Field(default_factory=list)
    relevant_memories: List[str] = Field(default_factory=list)

class DomainContext(BaseModel):
    active_domain: str = "general"
    active_domain_pack: str = "domain.general"
    active_subdomains: List[str] = Field(default_factory=list)
    active_handoffs: List[Dict[str, Any]] = Field(default_factory=list)

class ContextBundle(BaseModel):
    user_context: UserContext
    conversation_context: ConversationContext
    memory_context: MemoryContext
    domain_context: DomainContext
    personalization_context: Optional[PersonalizationContext] = None
    task_context: Dict[str, Any] = Field(default_factory=dict)
    tool_context: Dict[str, Any] = Field(default_factory=dict)
    permission_context: Dict[str, Any] = Field(default_factory=dict)
    verified_facts: List[Dict[str, Any]] = Field(default_factory=list)
    uploaded_evidence: List[Dict[str, Any]] = Field(default_factory=list)
    source_claims: List[Dict[str, Any]] = Field(default_factory=list)
    model_inferences: List[Dict[str, Any]] = Field(default_factory=list)
