from typing import Dict, Any, List, Optional
from pydantic import BaseModel

# Internal Plan IDs
PLAN_FREE = "free"
PLAN_STUDENT = "student"
PLAN_PERSONAL = "personal"
PLAN_POWER = "power"
PLAN_TEAMS = "teams"
PLAN_ENTERPRISE = "enterprise"

ALL_PLANS = [
    PLAN_FREE,
    PLAN_STUDENT,
    PLAN_PERSONAL,
    PLAN_POWER,
    PLAN_TEAMS,
    PLAN_ENTERPRISE
]

# Capability Taxonomy
CAPABILITIES = {
    # CORE
    "core.chat.basic": "Basic conversational AI",
    "core.chat.long_context": "Long context window chat",
    "core.chat.multimodal": "Multimodal image/document chat",
    "core.chat.advanced_reasoning": "Advanced deep reasoning & chain-of-thought",

    # MEMORY
    "memory.session": "Per-session transient memory",
    "memory.profile": "Persistent user profile memory",
    "memory.persistent": "Long-term persistent memory across sessions",
    "memory.semantic": "Vector/semantic memory search",
    "memory.manage": "Memory inspector and controls",
    "memory.export": "Memory export and backup",

    # DOCUMENTS
    "documents.import.pdf": "PDF document import",
    "documents.import.docx": "DOCX document import",
    "documents.import.images": "Image document import",
    "documents.import.spreadsheets": "Spreadsheet document import",
    "documents.analysis": "Deep document analysis & summarization",
    "documents.export.pdf": "Export formatted PDF",
    "documents.export.docx": "Export formatted DOCX",
    "documents.versioning": "Document version history & diffs",
    "multimodal.documents": "Multimodal document & image analysis",

    # CAREER (Migrated Phase 1-4)
    "career.master_resume": "Master Resume builder & persistent facts",
    "career.resume_import": "Resume file upload & local parsing",
    "career.jd_analysis": "JD requirement extraction & evidence matching",
    "career.resume_tailoring": "Truthful resume tailoring & diff generation",
    "career.ats": "ATS alignment & match scoring",
    "career.application_tracker": "Job application pipeline tracker",
    "career.interview_prep": "Interview question generator",
    "career.star": "STAR interview builder & 8-dimension scorer",
    "career.salary_coach": "Salary compensation breakdown & counter-offer coach",
    "career.goals": "Career goals & milestone tracking",
    "career.trajectory": "Visual career trajectory timeline",

    # VOICE
    "voice.input": "Voice speech-to-text input",
    "voice.output": "Voice text-to-speech output",
    "voice.realtime": "Real-time bi-directional streaming voice",
    "voice.saarthi": "Custom Saarthi voice persona",
    "voice.wake_word": "Hands-free wake-word detection",
    "voice.proactive": "Proactive voice alerts and reminders",

    # TOOLS
    "tools.files": "Local file system operations",
    "tools.search": "Web search and grounding",
    "tools.browser": "Automated web browser interaction",
    "tools.data_analysis": "Data analysis and visualization",
    "tools.code_execution": "Local sandboxed code execution",
    "tools.terminal": "Interactive terminal & shell execution",
    "tools.git": "Local Git repository operations",
    "tools.github": "GitHub API integrations",
    "tools.calendar": "Calendar scheduling & reminders",
    "tools.email": "Email drafting & management",
    "tools.computer_control": "OS application & computer control",
    "tools.api": "Custom REST API orchestration",
    "tools.mcp": "Model Context Protocol (MCP) tool integrations",
    "tools.mcp.actions": "MCP actions and workspace modifications",

    # AGENTS & AUTOMATION
    "agents.guided": "Step-by-step guided task workflows",
    "agents.custom": "Custom user-built agents",
    "agents.multistep": "Multi-step autonomous agent execution",
    "agents.autonomous": "Fully autonomous agent loops",
    "agents.background": "Background scheduled agent daemons",
    "agents.proactive": "Proactive background task execution",
    "agents.routines": "Routine creation and execution",
    "agents.scheduled": "Scheduled time-based routines",
    "agents.conditional": "Condition-triggered automation routines",
    "agents.advanced_automation": "Advanced multi-action background automation",

    # RESEARCH
    "research.basic": "Basic web literature search",
    "research.deep": "Multi-source deep research synthesis",
    "research.multi_source": "Cross-reference multi-database research",
    "research.paper_analysis": "Academic PDF paper analysis & extraction",
    "research.domain_research": "Domain-specific research packs",

    # DOMAINS
    "domain.career": "Career Workspace Domain Pack",
    "domain.education": "Education & Study Domain Pack",
    "domain.writing": "Writing & Content Domain Pack",
    "domain.general": "General AI Companion Domain Pack",
    "domain.business": "Business & Entrepreneurship Domain Pack",
    "domain.engineering": "Engineering & Systems Domain Pack",
    "domain.software": "Software Development Domain Pack",
    "domain.cybersecurity": "Cybersecurity & Pentesting Domain Pack",
    "domain.science": "Biomedical & Life Sciences Domain Pack",
    "domain.research": "Academic Research Domain Pack",
    "domain.custom": "Custom Domain Pack",

    # WORKSPACES
    "workspace.projects": "Project workspaces",
    "workspace.knowledge": "Knowledge base vault",
    "workspace.agents": "Agent workspace",
    "workspace.domains": "Domain pack manager",
    "workspace.automation": "Automation & workflows hub",

    # TEAM
    "team.workspace": "Shared team workspace",
    "team.shared_memory": "Shared team memory",
    "team.shared_agents": "Shared team agents",
    "team.rbac": "Role-based access controls",
    "team.audit": "Audit logging",
    "team.sso": "SSO & enterprise authentication"
}

# Plan Configurations & Pricing Catalog (INR)
PLAN_CATALOG = {
    PLAN_FREE: {
        "id": PLAN_FREE,
        "name": "Saarthi Free",
        "price_inr": 0,
        "billing_period": "forever",
        "description": "Essential AI operating companion with basic chat and career tools.",
        "badge": "Free"
    },
    PLAN_STUDENT: {
        "id": PLAN_STUDENT,
        "name": "Saarthi Student",
        "price_inr": 99,
        "billing_period": "month",
        "description": "For students & learners with study workspaces and guided research.",
        "badge": "Student"
    },
    PLAN_PERSONAL: {
        "id": PLAN_PERSONAL,
        "name": "Saarthi Personal",
        "price_inr": 399,
        "billing_period": "month",
        "description": "Full personal AI companion with long-term memory, voice, and automations.",
        "badge": "Popular"
    },
    PLAN_POWER: {
        "id": PLAN_POWER,
        "name": "Saarthi Power",
        "price_inr": 799,
        "billing_period": "month",
        "description": "For developers, researchers, and power users with terminal, computer control, and custom agents.",
        "badge": "Pro"
    },
    PLAN_TEAMS: {
        "id": PLAN_TEAMS,
        "name": "Saarthi Teams",
        "price_inr": 699,
        "billing_period": "user/month",
        "description": "Shared workspace, team memory, RBAC, and collaborative agent workflows.",
        "badge": "Teams"
    },
    PLAN_ENTERPRISE: {
        "id": PLAN_ENTERPRISE,
        "name": "Saarthi Enterprise",
        "price_inr": 0,
        "billing_period": "custom",
        "description": "Dedicated infrastructure, SAML/SSO, audit logs, and custom domain packs.",
        "badge": "Enterprise"
    }
}

# Baseline capabilities per plan
FREE_CAPABILITIES = {
    "core.chat.basic",
    "memory.session",
    "documents.import.pdf",
    "documents.import.docx",
    "documents.analysis",
    "documents.export.pdf",
    "documents.export.docx",
    "career.master_resume",
    "career.resume_import",
    "career.jd_analysis",
    "career.resume_tailoring",
    "career.ats",
    "career.application_tracker",
    "career.interview_prep",
    "tools.files",
    "tools.search",
    "tools.mcp",
    "domain.career",
    "domain.general",
    "agents.routines",
    "multimodal.documents"
}

STUDENT_CAPABILITIES = FREE_CAPABILITIES | {
    "memory.profile",
    "documents.versioning",
    "career.star",
    "career.salary_coach",
    "career.goals",
    "career.trajectory",
    "voice.input",
    "voice.output",
    "agents.guided",
    "research.basic",
    "domain.education",
    "workspace.projects"
}

PERSONAL_CAPABILITIES = STUDENT_CAPABILITIES | {
    "core.chat.long_context",
    "memory.persistent",
    "memory.semantic",
    "memory.manage",
    "memory.export",
    "documents.import.images",
    "documents.import.spreadsheets",
    "voice.realtime",
    "voice.saarthi",
    "voice.wake_word",
    "tools.browser",
    "tools.calendar",
    "tools.email",
    "tools.code_execution",
    "tools.mcp.actions",
    "agents.custom",
    "agents.proactive",
    "agents.scheduled",
    "agents.conditional",
    "research.deep",
    "domain.writing",
    "workspace.knowledge",
    "workspace.automation"
}

POWER_CAPABILITIES = PERSONAL_CAPABILITIES | {
    "core.chat.multimodal",
    "core.chat.advanced_reasoning",
    "voice.proactive",
    "tools.data_analysis",
    "tools.terminal",
    "tools.git",
    "tools.github",
    "tools.computer_control",
    "tools.api",
    "agents.multistep",
    "agents.autonomous",
    "agents.background",
    "agents.advanced_automation",
    "research.multi_source",
    "research.paper_analysis",
    "research.domain_research",
    "domain.business",
    "domain.engineering",
    "domain.software",
    "domain.cybersecurity",
    "domain.science",
    "domain.research",
    "domain.custom",
    "workspace.agents",
    "workspace.domains"
}

TEAMS_CAPABILITIES = POWER_CAPABILITIES | {
    "team.workspace",
    "team.shared_memory",
    "team.shared_agents",
    "team.rbac",
    "team.audit"
}

ENTERPRISE_CAPABILITIES = TEAMS_CAPABILITIES | {
    "team.sso"
}

PLAN_CAPABILITIES_MAP = {
    PLAN_FREE: FREE_CAPABILITIES,
    PLAN_STUDENT: STUDENT_CAPABILITIES,
    PLAN_PERSONAL: PERSONAL_CAPABILITIES,
    PLAN_POWER: POWER_CAPABILITIES,
    PLAN_TEAMS: TEAMS_CAPABILITIES,
    PLAN_ENTERPRISE: ENTERPRISE_CAPABILITIES
}

# Limits Per Plan
PLAN_LIMITS_MAP = {
    PLAN_FREE: {
        "monthly_resume_tailorings": 10,
        "monthly_agent_tasks": 0,
        "monthly_deep_research": 0,
        "custom_agents": 0,
        "vault_storage_gb": 1
    },
    PLAN_STUDENT: {
        "monthly_resume_tailorings": 50,
        "monthly_agent_tasks": 30,
        "monthly_deep_research": 10,
        "custom_agents": 2,
        "vault_storage_gb": 10
    },
    PLAN_PERSONAL: {
        "monthly_resume_tailorings": 200,
        "monthly_agent_tasks": 150,
        "monthly_deep_research": 50,
        "custom_agents": 5,
        "vault_storage_gb": 50
    },
    PLAN_POWER: {
        "monthly_resume_tailorings": 1000,
        "monthly_agent_tasks": 1000,
        "monthly_deep_research": 300,
        "custom_agents": 50,
        "vault_storage_gb": 200
    },
    PLAN_TEAMS: {
        "monthly_resume_tailorings": 5000,
        "monthly_agent_tasks": 5000,
        "monthly_deep_research": 1500,
        "custom_agents": 200,
        "vault_storage_gb": 1000
    },
    PLAN_ENTERPRISE: {
        "monthly_resume_tailorings": -1, # Unlimited
        "monthly_agent_tasks": -1,
        "monthly_deep_research": -1,
        "custom_agents": -1,
        "vault_storage_gb": 5000
    }
}

class PlanService:
    PLANS = {
        p.upper(): {cap: (cap in PLAN_CAPABILITIES_MAP[p]) for cap in CAPABILITIES.keys()}
        for p in ALL_PLANS
    }

    @staticmethod
    def get_plan_catalog() -> Dict[str, Any]:
        return PLAN_CATALOG

    @staticmethod
    def get_capabilities_for_plan(plan_id: str) -> Dict[str, bool]:
        plan = plan_id.lower()
        if plan not in PLAN_CAPABILITIES_MAP:
            plan = PLAN_FREE
        
        enabled_set = PLAN_CAPABILITIES_MAP[plan]
        return {cap: (cap in enabled_set) for cap in CAPABILITIES.keys()}

    @staticmethod
    def get_limits_for_plan(plan_id: str) -> Dict[str, Any]:
        plan = plan_id.lower()
        return PLAN_LIMITS_MAP.get(plan, PLAN_LIMITS_MAP[PLAN_FREE])

    @staticmethod
    def is_capability_entitled(plan_id: str, capability_id: str) -> bool:
        plan = plan_id.lower()
        enabled_set = PLAN_CAPABILITIES_MAP.get(plan, FREE_CAPABILITIES)
        return capability_id in enabled_set
