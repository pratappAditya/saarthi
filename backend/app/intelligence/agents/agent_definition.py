from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.intelligence.agents.agent_state import AgentStatus

class AgentDefinition(BaseModel):
    id: str
    name: str
    description: str
    system_prompt: str
    allowed_tools: List[str] = Field(default_factory=list)
    required_capabilities: List[str] = Field(default_factory=list)
    max_steps: int = 10
    risk_policy: str = "MODERATE"
    memory_scope: str = "user"
    domain: str = "general"
    enabled: bool = True

AGENT_CATALOG: Dict[str, AgentDefinition] = {
    "career_architect": AgentDefinition(
        id="career_architect",
        name="Career Architect Agent",
        description="Specialized agent for resume facts, truthful tailoring, ATS audits, and interview drills.",
        system_prompt="You are Saarthi Career Architect. Help the user optimize job applications and prepare for interviews using verified candidate facts.",
        allowed_tools=["career.analyze_jd", "career.tailor_resume", "career.prepare_interview", "career.salary_analysis"],
        required_capabilities=["career.master_resume"],
        max_steps=10,
        domain="career"
    ),
    "research_assistant": AgentDefinition(
        id="research_assistant",
        name="Deep Research Assistant Agent",
        description="Specialized agent for multi-source paper search, document synthesis, and academic literature analysis.",
        system_prompt="You are Saarthi Deep Research Assistant. Help the user synthesize complex papers and gather research notes.",
        allowed_tools=["browser.search", "file.read", "file.search"],
        required_capabilities=["research.deep"],
        max_steps=15,
        domain="research"
    ),
    "software_engineer": AgentDefinition(
        id="software_engineer",
        name="Software Engineering Agent",
        description="Specialized agent for code analysis, refactoring, test execution, and Git workflows.",
        system_prompt="You are Saarthi Software Engineering Agent. Help the user analyze codebase structure, generate tests, and refactor code.",
        allowed_tools=["code.execute", "terminal.execute", "file.read", "file.search"],
        required_capabilities=["tools.code_execution"],
        max_steps=10,
        domain="software"
    )
}
