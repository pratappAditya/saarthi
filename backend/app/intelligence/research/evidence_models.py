"""
Saarthi Universal Research & Evidence Model (Phase 7).
Defines standard schemas for evidence classification, source metadata,
citations, conflicts, research plans, and synthesis outputs.
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class EvidenceClass(str, Enum):
    FACT = "FACT"                     # Direct physical observation, verified empirical measurement, official statute/standard
    SOURCE_DERIVED = "SOURCE-DERIVED" # Directly asserted in an authoritative institutional, academic, or reputable secondary source
    INFERENCE = "INFERENCE"           # Derived conclusion or analytical hypothesis synthesized from multiple claims
    UNCERTAIN = "UNCERTAIN"           # Insufficient evidence, disputed claim, or high measurement variance


class SourceType(str, Enum):
    PRIMARY = "PRIMARY"               # Primary source (raw data, excavation record, statutory law, direct observation)
    INSTITUTIONAL = "INSTITUTIONAL"   # Official government, standard body (NIST/IEEE/ISO), academic institution
    SECONDARY = "SECONDARY"           # Peer-reviewed journal, academic survey, textbook, reputable publication
    TERTIARY = "TERTIARY"             # Encyclopedia, compendium, general reference
    USER_PROVIDED = "USER-PROVIDED"   # Uploaded document, screenshot, or prompt-provided snippet


class RecencyCategory(str, Enum):
    CURRENT = "CURRENT"       # Current year or within active operational window (< 12 months)
    RECENT = "RECENT"         # Within last 1-3 years
    HISTORICAL = "HISTORICAL" # > 3-5 years old, or inherently archival/historical topic
    UNDATED = "UNDATED"       # Publication or revision date could not be established


class ScientificConfidenceTier(str, Enum):
    ESTABLISHED_EVIDENCE = "ESTABLISHED_EVIDENCE"
    PLAUSIBLE_INTERPRETATION = "PLAUSIBLE_INTERPRETATION"
    UNRESOLVED_QUESTION = "UNRESOLVED_QUESTION"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class HistoricalConfidenceTier(str, Enum):
    PRIMARY_EVIDENCE = "PRIMARY_EVIDENCE"
    SCHOLARLY_INTERPRETATION = "SCHOLARLY_INTERPRETATION"
    HYPOTHESIS = "HYPOTHESIS"
    UNCERTAINTY = "UNCERTAINTY"


class ResearchOutputMode(str, Enum):
    CONCISE_ANSWER = "concise_answer"
    DETAILED_EXPLANATION = "detailed_explanation"
    EVIDENCE_SUMMARY = "evidence_summary"
    LITERATURE_REVIEW = "literature_review"
    COMPARISON = "comparison"
    TIMELINE = "timeline"
    TECHNICAL_REPORT = "technical_report"
    RESEARCH_BRIEF = "research_brief"
    SOURCE_TABLE = "source_table"
    DECISION_SUPPORT = "decision_support"


class SupportingPassage(BaseModel):
    text: str
    section_name: Optional[str] = None
    page_number: Optional[int] = None
    verified_in_source: bool = True


class SourceMetadata(BaseModel):
    source_id: str
    url: Optional[str] = None
    title: str
    publisher: Optional[str] = None
    author: Optional[str] = None
    publication_date: Optional[str] = None
    accessed_date: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source_type: SourceType = SourceType.SECONDARY
    recency: RecencyCategory = RecencyCategory.UNDATED
    methodological_transparency: Optional[str] = None # e.g. "Peer-reviewed methodology", "Official standard spec"
    reliability_notes: Optional[str] = None
    content_hash: Optional[str] = None
    is_untrusted_input: bool = True
    staleness_warning: Optional[str] = None


class EvidenceItem(BaseModel):
    evidence_id: str
    statement: str
    classification: EvidenceClass
    source_ids: List[str] = Field(default_factory=list)
    supporting_passages: List[SupportingPassage] = Field(default_factory=list)
    confidence: float = 0.90
    domain: str = "research"
    limitations: Optional[str] = None
    domain_confidence_tier: Optional[str] = None # ScientificConfidenceTier or HistoricalConfidenceTier
    provenance: Dict[str, Any] = Field(default_factory=dict)


class SourceConflict(BaseModel):
    conflict_id: str
    topic: str
    source_a_id: str
    source_a_claim: str
    source_b_id: str
    source_b_claim: str
    disagreement_type: str # "methodological" | "temporal" | "contextual" | "factual"
    explanation: str
    resolution_caveats: str


class Citation(BaseModel):
    citation_id: str
    source_id: str
    title: str
    url: Optional[str] = None
    publisher: Optional[str] = None
    author: Optional[str] = None
    publication_date: Optional[str] = None
    accessed_date: Optional[str] = None
    supporting_passage: Optional[str] = None


class ResearchPlan(BaseModel):
    plan_id: str
    primary_question: str
    is_complex: bool = False
    research_dimensions: List[str] = Field(default_factory=list)
    subquestions: List[Dict[str, Any]] = Field(default_factory=list) # [{subquery: str, domain: str, dimension: str}]
    required_evidence_types: List[EvidenceClass] = Field(default_factory=list)
    target_source_types: List[SourceType] = Field(default_factory=list)
    relevant_domains: List[str] = Field(default_factory=list)
    time_constraints: Optional[str] = None
    geographic_constraints: Optional[str] = None
    output_mode: ResearchOutputMode = ResearchOutputMode.EVIDENCE_SUMMARY
    max_sources: int = 10
    max_iterations: int = 3
    stopping_criteria: str = "Target evidence acquired or maximum sources reached"


class ResearchSynthesisResult(BaseModel):
    research_id: str
    question: str
    plan: ResearchPlan
    sources: List[SourceMetadata] = Field(default_factory=list)
    evidence_items: List[EvidenceItem] = Field(default_factory=list)
    conflicts: List[SourceConflict] = Field(default_factory=list)
    citations: List[Citation] = Field(default_factory=list)
    synthesis_summary: str = ""
    output_mode: ResearchOutputMode = ResearchOutputMode.EVIDENCE_SUMMARY
    uncertainty_analysis: str = ""
    domain_id: str = "research"
    subdomains: List[str] = Field(default_factory=list)
    verification_status: str = "VERIFIED" # "VERIFIED" | "PARTIAL" | "UNVERIFIED"
    verification_notes: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
