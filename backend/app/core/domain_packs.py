from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class DomainPack(BaseModel):
    id: str
    name: str
    category: str
    description: str
    minimum_plan: str
    capabilities: List[str]
    tools: List[str]
    icon: str
    is_active: bool = False
    is_installed: bool = False

DOMAIN_PACKS: Dict[str, DomainPack] = {
    "domain.career": DomainPack(
        id="domain.career",
        name="Career Operating Workspace",
        category="Career & Professional",
        description="Master resume facts, truthful tailoring, ATS alignment, interview prep, STAR drills, and salary coaching.",
        minimum_plan="free",
        capabilities=[
            "career.master_resume", "career.resume_import", "career.jd_analysis",
            "career.resume_tailoring", "career.ats", "career.application_tracker",
            "career.interview_prep", "career.star", "career.salary_coach",
            "career.goals", "career.trajectory"
        ],
        tools=["tools.files", "tools.search", "documents.export.pdf", "documents.export.docx"],
        icon="Briefcase",
        is_active=True,
        is_installed=True
    ),
    "domain.education": DomainPack(
        id="domain.education",
        name="Education & Study Companion",
        category="Learning & Academia",
        description="Flashcards, course notes, paper summaries, problem solving, and guided study workflows.",
        minimum_plan="student",
        capabilities=["domain.education", "research.basic", "workspace.projects"],
        tools=["tools.files", "tools.search", "documents.import.pdf"],
        icon="GraduationCap",
        is_active=False,
        is_installed=False
    ),
    "domain.writing": DomainPack(
        id="domain.writing",
        name="Writing & Content Studio",
        category="Creative & Communication",
        description="Long-form writing, technical documentation, essay drafting, tone transformation, and proofreading.",
        minimum_plan="personal",
        capabilities=["domain.writing", "core.chat.long_context"],
        tools=["tools.files", "documents.analysis"],
        icon="PenTool",
        is_active=False,
        is_installed=False
    ),
    "domain.general": DomainPack(
        id="domain.general",
        name="General Personal Assistant",
        category="Productivity",
        description="General conversation, daily planning, quick Q&A, and basic file management.",
        minimum_plan="free",
        capabilities=["domain.general", "core.chat.basic", "memory.session"],
        tools=["tools.search"],
        icon="Compass",
        is_active=True,
        is_installed=True
    ),
    "domain.business": DomainPack(
        id="domain.business",
        name="Business & Entrepreneurship",
        category="Business & Finance",
        description="Market research, business plan drafting, financial model analysis, and strategy formulation.",
        minimum_plan="power",
        capabilities=["domain.business", "research.deep", "tools.data_analysis"],
        tools=["tools.search", "tools.browser"],
        icon="TrendingUp",
        is_active=False,
        is_installed=False
    ),
    "domain.engineering": DomainPack(
        id="domain.engineering",
        name="Engineering & Systems Workbench",
        category="Engineering",
        description="CAD data inspection, systems design specs, architectural diagrams, and math calculation.",
        minimum_plan="power",
        capabilities=["domain.engineering", "core.chat.advanced_reasoning"],
        tools=["tools.code_execution", "tools.terminal"],
        icon="Cpu",
        is_active=False,
        is_installed=False
    ),
    "domain.software": DomainPack(
        id="domain.software",
        name="Software Engineering IDE Pack",
        category="Development",
        description="Code generation, refactoring, Git operations, bug fixing, test suite automation, and CI/CD.",
        minimum_plan="power",
        capabilities=["domain.software", "tools.code_execution", "tools.terminal", "tools.git", "tools.github"],
        tools=["tools.terminal", "tools.files", "tools.git"],
        icon="Code",
        is_active=False,
        is_installed=False
    ),
    "domain.cybersecurity": DomainPack(
        id="domain.cybersecurity",
        name="Cybersecurity & Vulnerability Suite",
        category="Security",
        description="PCAP analysis, threat triage, vulnerability scanning scripts, OWASP audits, and incident response.",
        minimum_plan="power",
        capabilities=["domain.cybersecurity", "tools.terminal", "tools.code_execution"],
        tools=["tools.terminal", "tools.files"],
        icon="ShieldCheck",
        is_active=False,
        is_installed=False
    ),
    "domain.science": DomainPack(
        id="domain.science",
        name="Biomedical & Life Sciences Suite",
        category="Science & Medicine",
        description="PubMed query workflows, protein sequence inspection, clinical trial search, and literature synthesis.",
        minimum_plan="power",
        capabilities=["domain.science", "research.paper_analysis"],
        tools=["research.multi_source", "tools.search"],
        icon="Dna",
        is_active=False,
        is_installed=False
    ),
    "domain.research": DomainPack(
        id="domain.research",
        name="Academic & Deep Research Pack",
        category="Research",
        description="arXiv/EuropePMC paper search, multi-source literature synthesis, citation manager, and LaTeX.",
        minimum_plan="power",
        capabilities=["domain.research", "research.deep", "research.multi_source", "research.paper_analysis"],
        tools=["tools.search", "tools.browser"],
        icon="BookOpen",
        is_active=False,
        is_installed=False
    )
}

class DomainPackService:
    @staticmethod
    def list_domain_packs() -> List[Dict[str, Any]]:
        return [pack.model_dump() for pack in DOMAIN_PACKS.values()]

    @staticmethod
    def get_domain_pack(pack_id: str) -> Optional[Dict[str, Any]]:
        pack = DOMAIN_PACKS.get(pack_id)
        return pack.model_dump() if pack else None
