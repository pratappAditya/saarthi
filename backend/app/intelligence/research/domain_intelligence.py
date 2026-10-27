"""
Domain Intelligence 2.0 (Phase 7).
Deepens the 17 universal domain packs with specialized terminology, common research tasks,
relevant source types, research patterns, reasoning considerations, common uncertainties,
recommended tools, and appropriate output structures.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class DomainIntelligenceSpec(BaseModel):
    domain_id: str
    name: str
    terminology: Dict[str, str] = Field(default_factory=dict)
    common_research_tasks: List[str] = Field(default_factory=list)
    relevant_source_types: List[str] = Field(default_factory=list)
    research_patterns: List[str] = Field(default_factory=list)
    reasoning_considerations: List[str] = Field(default_factory=list)
    common_uncertainty: List[str] = Field(default_factory=list)
    useful_tools: List[str] = Field(default_factory=list)
    appropriate_output_structures: List[str] = Field(default_factory=list)

# Comprehensive deep specification for all 17 domains
ALL_17_DOMAIN_INTELLIGENCE: Dict[str, DomainIntelligenceSpec] = {
    "general": DomainIntelligenceSpec(
        domain_id="general",
        name="General Companion",
        terminology={
            "provenance": "The chronology of the ownership, custody or source of a piece of information.",
            "grounding": "Binding generated responses to verified real-world facts and evidence."
        },
        common_research_tasks=[
            "Everyday factual verification", "Product and specification comparison", "Event timeline cross-checking"
        ],
        relevant_source_types=["PRIMARY", "INSTITUTIONAL", "SECONDARY", "TERTIARY"],
        research_patterns=["Query -> Verify Source -> Fact check -> Synthesize concise summary"],
        reasoning_considerations=["Maintain clarity, avoid unsubstantiated claims, distinguish opinions from facts"],
        common_uncertainty=["Colloquial ambiguities", "Conflicting consumer reviews", "Fast-changing real-time facts"],
        useful_tools=["browser.search", "file.read"],
        appropriate_output_structures=["concise_answer", "evidence_summary"]
    ),
    "career": DomainIntelligenceSpec(
        domain_id="career",
        name="Career Workspace",
        terminology={
            "ATS": "Applicant Tracking System filtering algorithm.",
            "STAR": "Situation, Task, Action, Result structured interview framework.",
            "LCOS": "Levelized Cost of Skills acquisition vs market compensation yield."
        },
        common_research_tasks=[
            "Job market salary benchmarking", "Skills gap analysis against job descriptions", "Company culture & interview signal synthesis"
        ],
        relevant_source_types=["INSTITUTIONAL", "PRIMARY", "SECONDARY"],
        research_patterns=["JD Extraction -> Competency Matrix -> Grounded Evidence Alignment -> Compensation Modeling"],
        reasoning_considerations=["Do not fabricate candidate experience or credentials", "Acknowledge variance across geography"],
        common_uncertainty=["Salary range self-reporting bias", "Hidden job market requirements", "Dynamic hiring freezes"],
        useful_tools=["career.analyze_jd", "career.tailor_resume", "career.prepare_interview", "career.salary_analysis"],
        appropriate_output_structures=["decision_support", "comparison", "technical_report"]
    ),
    "education": DomainIntelligenceSpec(
        domain_id="education",
        name="Education & Study",
        terminology={
            "Pedagogy": "Method and practice of teaching especially as an academic subject.",
            "Spaced Repetition": "Evidence-based learning technique using increasing intervals between review.",
            "Blooms Taxonomy": "Hierarchical classification of educational learning objectives."
        },
        common_research_tasks=[
            "Curriculum benchmark comparison", "Textbook syllabus breakdown", "Formative assessment design"
        ],
        relevant_source_types=["INSTITUTIONAL", "SECONDARY"],
        research_patterns=["Prerequisite Mapping -> Concept Decomposition -> Active Recall Formulation -> Synthesis"],
        reasoning_considerations=["Adapt conceptual depth to learner background", "Provide explicit worked examples"],
        common_uncertainty=["Variable curriculum standards across jurisdictions", "Divergent grading criteria"],
        useful_tools=["file.read", "browser.search"],
        appropriate_output_structures=["detailed_explanation", "timeline", "evidence_summary"]
    ),
    "writing": DomainIntelligenceSpec(
        domain_id="writing",
        name="Writing & Communications",
        terminology={
            "Voice": "The distinct personality and style of a piece of writing.",
            "Provenance Attribution": "Explicit citation of source material embedded in prose.",
            "Copyediting": "Improving formatting, style, and accuracy without altering substantive intent."
        },
        common_research_tasks=[
            "Style guide compliance review", "Literature review prose synthesis", "Editorial tone calibration"
        ],
        relevant_source_types=["PRIMARY", "SECONDARY"],
        research_patterns=["Source Synthesis -> Tone Alignment -> Draft Generation -> Attribution Audit"],
        reasoning_considerations=["Preserve authorial intent", "Never invent quotes or misattribute paraphrases"],
        common_uncertainty=["Subjective stylistic preferences", "Ambiguous editorial conventions"],
        useful_tools=["file.read", "email.draft"],
        appropriate_output_structures=["literature_review", "research_brief", "detailed_explanation"]
    ),
    "research": DomainIntelligenceSpec(
        domain_id="research",
        name="Academic Research & Synthesis",
        terminology={
            "Peer Review": "Evaluation of work by one or more people of similar competence.",
            "Systematic Review": "Structured literature review that collects and critically analyzes multiple research studies.",
            "Meta-Analysis": "Statistical analysis that combines the results of multiple scientific studies."
        },
        common_research_tasks=[
            "Systematic literature review", "Citation graph mapping", "Conflicting study methodology comparison"
        ],
        relevant_source_types=["PRIMARY", "INSTITUTIONAL", "SECONDARY"],
        research_patterns=["Question Decomposition -> Search -> Quality Filter -> Evidence Extraction -> Conflict Resolution -> Citation Mapping"],
        reasoning_considerations=["Strictly separate empirical facts from model inferences", "State search limitations and caveats"],
        common_uncertainty=["Publication bias toward positive results", "Replication crisis in specific subfields"],
        useful_tools=["browser.search", "file.read"],
        appropriate_output_structures=["literature_review", "comparison", "source_table", "technical_report"]
    ),
    "business": DomainIntelligenceSpec(
        domain_id="business",
        name="Business & Operations",
        terminology={
            "LTV/CAC": "Lifetime Value to Customer Acquisition Cost ratio.",
            "TAM": "Total Addressable Market.",
            "Moat": "Sustainable competitive advantage shielding market share."
        },
        common_research_tasks=[
            "Market size and growth rate estimation", "Competitive matrix benchmarking", "Unit economics analysis"
        ],
        relevant_source_types=["PRIMARY", "INSTITUTIONAL", "SECONDARY"],
        research_patterns=["Industry Report Gathering -> SEC/Regulatory Filing Analysis -> Financial Model Calibration"],
        reasoning_considerations=["Discount forward-looking promotional claims", "Prioritize audited financial statements"],
        common_uncertainty=["Private company financials opacity", "Macroeconomic volatility", "Survey sampling error"],
        useful_tools=["file.read", "browser.search"],
        appropriate_output_structures=["decision_support", "comparison", "research_brief"]
    ),
    "software": DomainIntelligenceSpec(
        domain_id="software",
        name="Software Engineering",
        terminology={
            "Idempotency": "An operation that can be applied multiple times without changing the result beyond initial application.",
            "Concurrency": "Execution of multiple instruction sequences simultaneously.",
            "SSRF": "Server-Side Request Forgery vulnerability."
        },
        common_research_tasks=[
            "API documentation and breaking change verification", "Architecture trade-off evaluation (monolith vs microservices)", "Bug root-cause analysis"
        ],
        relevant_source_types=["PRIMARY", "INSTITUTIONAL", "SECONDARY"],
        research_patterns=["Spec Inspection -> Version Compatibility Check -> Security Review -> Performance Benchmark"],
        reasoning_considerations=["Check framework versions strictly; APIs change rapidly across minor releases"],
        common_uncertainty=["Undocumented edge cases in third-party libraries", "OS-specific runtime divergence"],
        useful_tools=["code.execute", "terminal.execute", "file.read", "browser.search"],
        appropriate_output_structures=["technical_report", "comparison", "detailed_explanation"]
    ),
    "cybersecurity": DomainIntelligenceSpec(
        domain_id="cybersecurity",
        name="Cybersecurity & Audit",
        terminology={
            "CVE": "Common Vulnerabilities and Exposures dictionary identifier.",
            "CVSS": "Common Vulnerability Scoring System.",
            "Zero-Day": "Vulnerability that is undisclosed or has no vendor patch available."
        },
        common_research_tasks=[
            "Vulnerability impact analysis for CVE disclosures", "Threat vector modeling (STRIDE)", "Security policy compliance audit"
        ],
        relevant_source_types=["PRIMARY", "INSTITUTIONAL"],
        research_patterns=["NVD/Advisory Ingestion -> Exploit Precondition Analysis -> Blast Radius Assessment -> Remediation Synthesis"],
        reasoning_considerations=["Verify exact package versions affected", "Prioritize vendor advisories over unverified blogs"],
        common_uncertainty=["Active exploitation in the wild statistics", "Workaround efficacy under novel attack variants"],
        useful_tools=["terminal.execute", "file.read", "browser.search"],
        appropriate_output_structures=["technical_report", "decision_support", "evidence_summary"]
    ),
    "cs": DomainIntelligenceSpec(
        domain_id="cs",
        name="Computer Science & Theory",
        terminology={
            "NP-Complete": "Class of decision problems that are in NP and to which any problem in NP can be reduced in polynomial time.",
            "Asymptotic Complexity": "Limiting behavior of execution time or space as input size approaches infinity.",
            "CAP Theorem": "Distributed data store can provide only two of Consistency, Availability, and Partition tolerance."
        },
        common_research_tasks=[
            "Algorithm complexity proofs and comparisons", "Formal automata and language analysis", "Distributed consensus protocol review"
        ],
        relevant_source_types=["PRIMARY", "INSTITUTIONAL", "SECONDARY"],
        research_patterns=["Formal Definition -> Invariant Proof -> Lower Bound Analysis -> Concrete Implementation Mapping"],
        reasoning_considerations=["Distinguish worst-case, average-case, and amortized bounds explicitly"],
        common_uncertainty=["Open theoretical problems (P vs NP)", "Constant factor variations in physical hardware"],
        useful_tools=["code.execute", "file.read"],
        appropriate_output_structures=["technical_report", "detailed_explanation", "comparison"]
    ),
    "mechanical": DomainIntelligenceSpec(
        domain_id="mechanical",
        name="Mechanical Engineering",
        terminology={
            "Yield Strength": "Stress at which a material begins to deform plastically.",
            "Fatigue Limit": "Stress level below which a material can withstand an infinite number of cycles.",
            "Thermal Dissipation": "Transfer of heat from a system to its surroundings."
        },
        common_research_tasks=[
            "Material selection for cyclic fatigue", "Thermodynamic heat exchanger sizing", "Gear train kinematics analysis"
        ],
        relevant_source_types=["PRIMARY", "INSTITUTIONAL", "SECONDARY"],
        research_patterns=["Operating Boundary Definition -> Governing Equation Formulation -> Material Property Extraction -> Safety Factor Sizing"],
        reasoning_considerations=["State all boundary assumptions and safety margins clearly (e.g. Factor of Safety >= 1.5)"],
        common_uncertainty=["Environmental corrosion rates", "Weld joint defect tolerances in field conditions"],
        useful_tools=["file.read", "browser.search"],
        appropriate_output_structures=["technical_report", "comparison", "decision_support"]
    ),
    "civil": DomainIntelligenceSpec(
        domain_id="civil",
        name="Civil & Structural Engineering",
        terminology={
            "Bending Moment": "Reaction induced in a structural element when an external force is applied causing bending.",
            "Limit State Design": "Structural engineering method ensuring structures satisfy safety and serviceability limits.",
            "Seismic Base Shear": "Total expected lateral force on a structure's base due to earthquake shaking."
        },
        common_research_tasks=[
            "Reinforced concrete beam load calculations", "Foundation bearing capacity estimation", "Building code regulatory compliance (IS 456 / Eurocode / ACI 318)"
        ],
        relevant_source_types=["PRIMARY", "INSTITUTIONAL"],
        research_patterns=["Code Selection -> Dead/Live Load Combination -> Section Analysis -> Deflection Verification"],
        reasoning_considerations=["Always cite governing statutory building codes; do not blend national codes haphazardly"],
        common_uncertainty=["Subsurface geotechnical heterogeneity", "Extreme 100-year seismic and flood return periods"],
        useful_tools=["file.read", "browser.search"],
        appropriate_output_structures=["technical_report", "decision_support", "source_table"]
    ),
    "electrical": DomainIntelligenceSpec(
        domain_id="electrical",
        name="Electrical Engineering",
        terminology={
            "Impedance Matching": "Designing input/output impedance to maximize power transfer or minimize signal reflection.",
            "Bode Plot": "Graph of the frequency response of a system (magnitude and phase).",
            "Harmonic Distortion (THD)": "Measurement of the harmonic distortion present in a signal."
        },
        common_research_tasks=[
            "Switch-mode power supply (SMPS) design", "High-speed transmission line signal integrity", "Motor drive inverter topology selection"
        ],
        relevant_source_types=["INSTITUTIONAL", "PRIMARY", "SECONDARY"],
        research_patterns=["Circuit Topology Selection -> Frequency Domain Modeling -> Component Derating -> EMI/EMC Standard Compliance"],
        reasoning_considerations=["Include parasitic inductances and capacitances for frequencies above 10 MHz"],
        common_uncertainty=["Thermal runaway in power semiconductors under surge", "Electromagnetic interference (EMI) cross-talk"],
        useful_tools=["file.read", "browser.search"],
        appropriate_output_structures=["technical_report", "comparison", "detailed_explanation"]
    ),
    "biology": DomainIntelligenceSpec(
        domain_id="biology",
        name="Biology & Life Sciences",
        terminology={
            "Transcription Factor": "Protein that controls the rate of transcription of genetic information from DNA to messenger RNA.",
            "Epigenetics": "Heritable phenotype changes that do not involve alterations in the DNA sequence.",
            "CRISPR-Cas9": "Targeted genome editing technology derived from bacterial antiviral defenses."
        },
        common_research_tasks=[
            "Gene expression pathway analysis", "Protein structure and folding prediction comparison", "Pharmacokinetic clearance literature review"
        ],
        relevant_source_types=["PRIMARY", "INSTITUTIONAL", "SECONDARY"],
        research_patterns=["Genomic Identifier Resolution -> Pathway Mapping -> In Vitro vs In Vivo Evaluation -> Clinical Evidence Synthesis"],
        reasoning_considerations=["Distinguish in vitro cell assay observations from in vivo clinical outcomes"],
        common_uncertainty=["Biological model organism translation variance", "Post-translational modification complexities"],
        useful_tools=["file.read", "browser.search"],
        appropriate_output_structures=["literature_review", "evidence_summary", "technical_report"]
    ),
    "chemistry": DomainIntelligenceSpec(
        domain_id="chemistry",
        name="Chemistry & Materials",
        terminology={
            "Enthalpy": "Property of a thermodynamic system equal to internal energy plus product of pressure and volume.",
            "Catalysis": "Process of increasing the rate of a chemical reaction by adding a substance not consumed by the reaction.",
            "Electrochemical Potential": "Thermodynamic measure of chemical potential and electrostatic potential."
        },
        common_research_tasks=[
            "Reaction mechanism and pathway synthesis", "Battery cathode phase transition thermodynamics", "Polymer degradation kinetics review"
        ],
        relevant_source_types=["PRIMARY", "INSTITUTIONAL", "SECONDARY"],
        research_patterns=["Reaction Stoichiometry -> Thermodynamic Feasibility -> Kinetic Barrier Analysis -> Safety & Waste Review"],
        reasoning_considerations=["Check solvent compatibility and exothermic runaway risks for all reaction proposals"],
        common_uncertainty=["Trace catalyst poisoning", "Scalability from milligram batch to pilot synthesis"],
        useful_tools=["file.read", "browser.search"],
        appropriate_output_structures=["technical_report", "comparison", "evidence_summary"]
    ),
    "physics": DomainIntelligenceSpec(
        domain_id="physics",
        name="Physics & Applied Mechanics",
        terminology={
            "Quantum Superposition": "Fundamental principle of quantum mechanics where physical system exists partly in all states simultaneously.",
            "No-Cloning Theorem": "States that it is impossible to create an independent and identical copy of an arbitrary unknown quantum state.",
            "Entropy": "Measure of the number of possible microscopic states of a system in thermodynamic equilibrium."
        },
        common_research_tasks=[
            "Quantum key distribution security proof analysis", "Electromagnetic wave propagation in plasma", "Relativistic frame coordinate transformations"
        ],
        relevant_source_types=["PRIMARY", "INSTITUTIONAL", "SECONDARY"],
        research_patterns=["Conservation Law Identification -> Boundary Condition Formulation -> Hamiltonian/Lagrangian Derivation -> Experimental Verification"],
        reasoning_considerations=["Verify conservation of energy, momentum, and charge in all derivations"],
        common_uncertainty=["Quantum decoherence in thermal environments", "Non-perturbative regime approximations"],
        useful_tools=["file.read", "browser.search"],
        appropriate_output_structures=["technical_report", "detailed_explanation", "timeline"]
    ),
    "archaeology": DomainIntelligenceSpec(
        domain_id="archaeology",
        name="Archaeology & Field Research",
        terminology={
            "Stratigraphy": "Branch of geology concerned with the study of rock layers (strata) and layering (stratification) applied to archaeological deposits.",
            "Seriation": "Relative dating method in which assemblages or artifacts from numerous sites are placed in chronological order.",
            "Radiocarbon Dating (AMS)": "Method for determining age by using the decay properties of carbon-14 via Accelerator Mass Spectrometry."
        },
        common_research_tasks=[
            "Excavation site report analysis", "Ceramic and lithic typology classification", "Chronological alignment of cultural phases (e.g. Harappan phases)"
        ],
        relevant_source_types=["PRIMARY", "INSTITUTIONAL", "SECONDARY"],
        research_patterns=["Site Stratigraphy Verification -> Material Typology Sorting -> Radiocarbon Calibration -> Cultural Synthesis"],
        reasoning_considerations=["Strictly separate direct physical observations (soil layer, burnt brick size) from historical interpretation"],
        common_uncertainty=["Disturbed stratigraphic contexts (intrusive pits)", "Marine reservoir effects in radiocarbon dating"],
        useful_tools=["file.read", "browser.search"],
        appropriate_output_structures=["timeline", "evidence_summary", "technical_report"]
    ),
    "history": DomainIntelligenceSpec(
        domain_id="history",
        name="History & Historiography",
        terminology={
            "Historiography": "The study of the methods of historians in developing history as an academic discipline.",
            "Primary Source": "Immediate, first-hand accounts of a topic, from people who had a direct connection with it.",
            "Epigraphy": "The study of inscriptions, or epigraphs, as writing and literature."
        },
        common_research_tasks=[
            "Comparative archival source analysis", "Cross-checking historical chronicles against epigraphic inscriptions", "Historiographical debate synthesis"
        ],
        relevant_source_types=["PRIMARY", "INSTITUTIONAL", "SECONDARY"],
        research_patterns=["Source Provenance Check -> Author Bias Assessment -> Corroboration with Contemporary Records -> Historiographical Synthesis"],
        reasoning_considerations=["Contextualize authorial bias and patronage (e.g. royal court chronicles)", "Distinguish myth from corroborated chronicle"],
        common_uncertainty=["Lost archives and textual corruption over manuscript copies", "Partisan or selective recording by ancient scribes"],
        useful_tools=["file.read", "browser.search"],
        appropriate_output_structures=["timeline", "literature_review", "comparison", "evidence_summary"]
    )
}

class DomainIntelligenceManager:
    @staticmethod
    def get_domain_spec(domain_id: str) -> Optional[DomainIntelligenceSpec]:
        return ALL_17_DOMAIN_INTELLIGENCE.get(domain_id.lower())

    @staticmethod
    def list_all_specs() -> List[DomainIntelligenceSpec]:
        return list(ALL_17_DOMAIN_INTELLIGENCE.values())


domain_intelligence_manager = DomainIntelligenceManager()
