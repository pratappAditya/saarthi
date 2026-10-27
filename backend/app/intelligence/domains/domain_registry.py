import logging
from typing import Dict, Any, List, Optional
from app.intelligence.domains.domain_pack import DomainPack, DomainCategory, DomainWorkflow, DomainOutputSchema

logger = logging.getLogger("app.intelligence.domain_registry")

class DomainRegistry:
    def __init__(self):
        self.packs: Dict[str, DomainPack] = {}
        self._register_default_packs()

    def register_pack(self, pack: DomainPack):
        try:
            from app.intelligence.research.domain_intelligence import domain_intelligence_manager
            spec = domain_intelligence_manager.get_domain_spec(pack.id)
            if spec:
                if not pack.terminology:
                    pack.terminology = spec.terminology
                if not pack.common_research_tasks:
                    pack.common_research_tasks = spec.common_research_tasks
                if not pack.relevant_source_types:
                    pack.relevant_source_types = spec.relevant_source_types
                if not pack.research_patterns:
                    pack.research_patterns = spec.research_patterns
                if not pack.reasoning_considerations:
                    pack.reasoning_considerations = spec.reasoning_considerations
                if not pack.common_uncertainty:
                    pack.common_uncertainty = spec.common_uncertainty
        except Exception as e:
            logger.warning(f"Could not load domain intelligence for {pack.id}: {e}")
        self.packs[pack.id] = pack

    def get_pack(self, pack_id: str) -> Optional[DomainPack]:
        return self.packs.get(pack_id)

    def list_packs(self) -> List[DomainPack]:
        return list(self.packs.values())

    def _register_default_packs(self):
        # 1. General
        self.register_pack(DomainPack(
            id="general",
            name="General Companion",
            description="Universal AI companion for everyday inquiries, planning, and task execution.",
            aliases=["default", "general_assistant"],
            category=DomainCategory.CORE,
            system_instructions="You are Saarthi, a universal personal AI operating companion.",
            allowed_tools=["file.read", "browser.search"],
            required_capability="domain.basic"
        ))

        # 2. Career
        self.register_pack(DomainPack(
            id="career",
            name="Career Workspace",
            description="Resume tailoring, job requirement extraction, interview prep, and salary coaching.",
            aliases=["resumes", "jobs", "interview"],
            category=DomainCategory.CORE,
            system_instructions="Act as a truthful Career Architect.",
            allowed_tools=["career.analyze_jd", "career.tailor_resume", "career.prepare_interview", "career.salary_analysis"],
            required_capability="domain.basic"
        ))

        # 3. Education
        self.register_pack(DomainPack(
            id="education",
            name="Education & Study",
            description="Curriculum breakdown, lesson planning, active recall, and study guides.",
            aliases=["study", "teaching", "learning"],
            category=DomainCategory.CORE,
            system_instructions="Structure concepts clearly for effective learning.",
            allowed_tools=["file.read", "browser.search"],
            required_capability="domain.basic"
        ))

        # 4. Writing
        self.register_pack(DomainPack(
            id="writing",
            name="Writing & Communications",
            description="Technical documentation, editorial refinement, copyediting, and email drafting.",
            aliases=["editor", "content", "docs"],
            category=DomainCategory.CORE,
            system_instructions="Refine prose for clarity, tone, and impact.",
            allowed_tools=["file.read", "email.draft"],
            required_capability="domain.basic"
        ))

        # 5. Research
        self.register_pack(DomainPack(
            id="research",
            name="Academic Research & Synthesis",
            description="Decomposes questions, maps citations, extracts evidence, and detects conflicting sources.",
            aliases=["literature", "academic", "papers"],
            category=DomainCategory.CORE,
            system_instructions="Perform evidence-backed research with explicit provenance.",
            allowed_tools=["file.read", "browser.search"],
            required_capability="domain.research"
        ))

        # 6. Business
        self.register_pack(DomainPack(
            id="business",
            name="Business & Operations",
            description="Market analysis, business model canvas, financial summary, and strategy.",
            aliases=["finance", "management", "strategy"],
            category=DomainCategory.CORE,
            system_instructions="Provide structured business insights.",
            allowed_tools=["file.read", "browser.search"],
            required_capability="domain.basic"
        ))

        # 7. Software Engineering
        self.register_pack(DomainPack(
            id="software",
            name="Software Engineering",
            description="Code debugging, system architecture design, refactoring, and code execution.",
            aliases=["coding", "dev", "programming", "swe"],
            category=DomainCategory.TECHNICAL,
            system_instructions="Analyze code structure, detect bugs, and write clean robust code.",
            allowed_tools=["code.execute", "terminal.execute", "file.read", "browser.search"],
            required_capability="domain.software"
        ))

        # 8. Cybersecurity
        self.register_pack(DomainPack(
            id="cybersecurity",
            name="Cybersecurity & Audit",
            description="Security log audit, threat modeling, vulnerability analysis, and network artifacts.",
            aliases=["security", "infosec", "pentest", "audit"],
            category=DomainCategory.TECHNICAL,
            system_instructions="Conduct security analysis, identify vulnerabilities, and suggest remediations.",
            allowed_tools=["terminal.execute", "file.read", "browser.search"],
            required_capability="domain.cybersecurity"
        ))

        # 9. Computer Science
        self.register_pack(DomainPack(
            id="cs",
            name="Computer Science & Theory",
            description="Algorithms, data structures, complexity analysis, and computational theory.",
            aliases=["algorithms", "comp_sci"],
            category=DomainCategory.TECHNICAL,
            system_instructions="Explain theoretical computer science concepts.",
            allowed_tools=["code.execute", "file.read"],
            required_capability="domain.software"
        ))

        # 10. Mechanical Engineering
        self.register_pack(DomainPack(
            id="mechanical",
            name="Mechanical Engineering",
            description="Thermodynamics, fluid mechanics, CAD design concepts, and materials science.",
            aliases=["mech", "cad"],
            category=DomainCategory.TECHNICAL,
            system_instructions="Apply engineering principles with explicit assumptions and equations.",
            allowed_tools=["file.read", "browser.search"],
            required_capability="domain.engineering"
        ))

        # 11. Civil Engineering
        self.register_pack(DomainPack(
            id="civil",
            name="Civil & Structural Engineering",
            description="Structural load calculations, beam design, concrete, and geotechnics.",
            aliases=["structural", "construction"],
            category=DomainCategory.TECHNICAL,
            system_instructions="Provide structural analysis showing explicit load conditions and safety factors.",
            allowed_tools=["file.read", "browser.search"],
            required_capability="domain.engineering"
        ))

        # 12. Electrical Engineering
        self.register_pack(DomainPack(
            id="electrical",
            name="Electrical Engineering",
            description="Circuit analysis, signal processing, power systems, and microelectronics.",
            aliases=["ee", "circuits"],
            category=DomainCategory.TECHNICAL,
            system_instructions="Analyze circuits and electrical signals with clear schematic breakdown.",
            allowed_tools=["file.read", "browser.search"],
            required_capability="domain.engineering"
        ))

        # 13. Biology
        self.register_pack(DomainPack(
            id="biology",
            name="Biology & Life Sciences",
            description="Genomics, protein expression, cellular biology, and bioinformatics.",
            aliases=["bio", "genomics"],
            category=DomainCategory.SCIENCE,
            system_instructions="Analyze biological mechanisms and laboratory observations.",
            allowed_tools=["file.read", "browser.search"],
            required_capability="domain.basic"
        ))

        # 14. Chemistry
        self.register_pack(DomainPack(
            id="chemistry",
            name="Chemistry & Materials",
            description="Organic synthesis, stoichiometry, reaction mechanisms, and thermodynamics.",
            aliases=["chem"],
            category=DomainCategory.SCIENCE,
            system_instructions="Provide molecular analysis and chemical reaction steps.",
            allowed_tools=["file.read", "browser.search"],
            required_capability="domain.basic"
        ))

        # 15. Physics
        self.register_pack(DomainPack(
            id="physics",
            name="Physics & Applied Mechanics",
            description="Quantum mechanics, electromagnetism, optics, and classical dynamics.",
            aliases=["phys"],
            category=DomainCategory.SCIENCE,
            system_instructions="Derive physical laws and present clear equations.",
            allowed_tools=["file.read", "browser.search"],
            required_capability="domain.basic"
        ))

        # 16. Archaeology
        self.register_pack(DomainPack(
            id="archaeology",
            name="Archaeology & Field Research",
            description="Excavation reports, artifact typology, site stratigraphy, and chronology.",
            aliases=["archaeo", "excavation"],
            category=DomainCategory.HUMANITIES,
            system_instructions="Separate direct physical observations from interpretative hypotheses.",
            allowed_tools=["file.read", "browser.search"],
            required_capability="domain.archaeology"
        ))

        # 17. History
        self.register_pack(DomainPack(
            id="history",
            name="History & Historiography",
            description="Archival source analysis, historical timelines, and historiographical synthesis.",
            aliases=["historical"],
            category=DomainCategory.HUMANITIES,
            system_instructions="Contextualize historical sources with provenance.",
            allowed_tools=["file.read", "browser.search"],
            required_capability="domain.basic"
        ))

domain_registry = DomainRegistry()
