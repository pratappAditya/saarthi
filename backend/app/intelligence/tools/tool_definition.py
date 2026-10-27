from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class RiskLevel(str, Enum):
    READ_ONLY = "READ_ONLY"
    LOW_RISK = "LOW_RISK"
    MODERATE = "MODERATE"
    HIGH_RISK = "HIGH_RISK"
    CRITICAL = "CRITICAL"

class ToolDefinition(BaseModel):
    id: str
    name: str
    description: str
    input_schema: Dict[str, Any] = Field(default_factory=dict)
    output_schema: Dict[str, Any] = Field(default_factory=dict)
    required_capability: str = "core.chat.basic"
    risk_level: RiskLevel = RiskLevel.READ_ONLY
    requires_confirmation: bool = False
    execution_mode: str = "synchronous"  # "synchronous" | "asynchronous"
    operation_type: str = "OBSERVATION"  # "OBSERVATION" | "ACTION"
    enabled: bool = True
    allowed_scopes: List[str] = Field(default_factory=lambda: ["user", "project", "domain"])
