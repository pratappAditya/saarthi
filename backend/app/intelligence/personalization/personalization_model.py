import time
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class PreferenceSource(str, Enum):
    USER_EXPLICIT = "USER_EXPLICIT"
    USER_CONFIRMED = "USER_CONFIRMED"
    MODEL_INFERRED = "MODEL_INFERRED"
    SYSTEM_DERIVED = "SYSTEM_DERIVED"

class ExpertiseLevel(str, Enum):
    NOVICE = "novice"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class DomainExpertise(BaseModel):
    domain: str
    level: ExpertiseLevel = ExpertiseLevel.INTERMEDIATE
    confidence: float = 0.8
    evidence: str = "Default baseline estimate"
    last_updated: float = Field(default_factory=time.time)
    explicit_override: bool = False

class PreferenceItem(BaseModel):
    key: str
    category: str = "communication" # communication, work, domain, proactivity, voice
    value: Any
    source: PreferenceSource = PreferenceSource.MODEL_INFERRED
    confidence: float = 0.75
    evidence: str = "Inferred from interaction patterns"
    created_at: float = Field(default_factory=time.time)
    last_observed: float = Field(default_factory=time.time)
    decay_seconds: Optional[float] = 30 * 86400 # 30 days default decay for inferences
    confirmed: bool = False
    rejected: bool = False
    affected_behavior: str = "Adapts response synthesis"

class UserPersonalizationProfile(BaseModel):
    user_id: str = "default_local_user"
    communication_style: str = "direct" # direct, explanatory, conversational, executive
    preferred_response_length: str = "concise" # concise, balanced, detailed
    technical_depth: str = "adaptive" # novice, intermediate, advanced, expert, adaptive
    preferred_languages: List[str] = Field(default_factory=lambda: ["en-IN", "hi-IN"])
    preferred_tone: str = "intelligent, calm" # calm, casual, formal, technical
    preferred_formatting: str = "bullet_points" # bullet_points, prose, code_heavy, markdown
    decision_making_style: str = "action_oriented" # data_driven, intuitive, action_oriented
    autonomy_preference: str = "semi_autonomous" # guided, semi_autonomous, autonomous
    confirmation_preference: str = "risk_based" # strict, risk_based, minimal
    proactivity_preference: str = "moderate" # high, moderate, low, quiet
    preferred_working_hours: str = "09:00-18:00"
    preferred_tools: List[str] = Field(default_factory=lambda: ["browser", "code_execution", "terminal"])
    preferred_workflows: List[str] = Field(default_factory=lambda: ["resume_tailoring", "deep_research"])
    domain_expertise: Dict[str, DomainExpertise] = Field(default_factory=dict)
    learning_interests: List[str] = Field(default_factory=list)
    recurring_objectives: List[str] = Field(default_factory=list)
    explicit_preferences: Dict[str, Any] = Field(default_factory=dict)
    inferred_preferences: Dict[str, PreferenceItem] = Field(default_factory=dict)
    
    # Feature & Privacy Controls
    personalization_enabled: bool = True
    learning_enabled: bool = True
    inference_enabled: bool = True
    proactive_learning_enabled: bool = True
    voice_personalization_enabled: bool = True
    
    updated_at: float = Field(default_factory=time.time)

class PersonalizationContext(BaseModel):
    user_id: str = "default_local_user"
    effective_communication_style: str = "direct"
    effective_response_length: str = "concise"
    effective_technical_depth: str = "adaptive"
    effective_formatting: str = "bullet_points"
    effective_proactivity_level: str = "moderate"
    effective_voice_rate: float = 1.0
    effective_domain_expertise: str = "intermediate"
    precedence_scope: str = "Global" # Task > Project > Domain > Global
    active_overrides: List[str] = Field(default_factory=list)
    explanations: List[str] = Field(default_factory=list)
    personalization_enabled: bool = True
