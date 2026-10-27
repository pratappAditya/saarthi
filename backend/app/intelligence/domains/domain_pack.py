from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class DomainCategory(str, Enum):
    CORE = "core"
    TECHNICAL = "technical"
    SCIENCE = "science"
    HUMANITIES = "humanities"

class DomainWorkflow(BaseModel):
    id: str
    name: str
    description: str
    steps: List[str] = Field(default_factory=list)

class DomainOutputSchema(BaseModel):
    name: str
    required_fields: List[str] = Field(default_factory=list)
    format_template: str = ""

class DomainPack(BaseModel):
    id: str
    name: str
    description: str
    aliases: List[str] = Field(default_factory=list)
    category: DomainCategory = DomainCategory.CORE
    system_instructions: str
    terminology: Dict[str, str] = Field(default_factory=dict)
    workflows: List[DomainWorkflow] = Field(default_factory=list)
    allowed_tools: List[str] = Field(default_factory=list)
    knowledge_providers: List[str] = Field(default_factory=list)
    supported_file_types: List[str] = Field(default_factory=list)
    required_capability: str = "domain.basic"
    prompt_templates: Dict[str, str] = Field(default_factory=dict)
    example_tasks: List[str] = Field(default_factory=list)
    output_schemas: List[DomainOutputSchema] = Field(default_factory=list)
    # Phase 7 Deep Domain Intelligence 2.0
    common_research_tasks: List[str] = Field(default_factory=list)
    relevant_source_types: List[str] = Field(default_factory=list)
    research_patterns: List[str] = Field(default_factory=list)
    reasoning_considerations: List[str] = Field(default_factory=list)
    common_uncertainty: List[str] = Field(default_factory=list)
