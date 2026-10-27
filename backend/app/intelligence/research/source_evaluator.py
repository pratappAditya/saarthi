"""
Transparent Source Evaluation Framework (Phase 7).
Classifies sources into PRIMARY, INSTITUTIONAL, SECONDARY, TERTIARY, USER-PROVIDED.
Evaluates methodological transparency, institutional authority, corroboration,
and specificity without crude artificial 'truth scores'.
"""

import re
from typing import Dict, Any, List, Optional
from app.intelligence.research.evidence_models import SourceMetadata, SourceType, RecencyCategory

INSTITUTIONAL_DOMAINS = [
    ".gov", ".nic.in", ".gov.in", ".mil", ".edu", ".ac.uk", ".ac.in",
    "nist.gov", "fda.gov", "cdc.gov", "who.int", "ieee.org", "ietf.org",
    "iso.org", "w3.org", "arxiv.org", "nih.gov", "ncbi.nlm.nih.gov", "cern.ch"
]

PRIMARY_SOURCE_KEYWORDS = [
    "statute", "treaty", "census", "excavation report", "raw dataset", "transcript",
    "charter", "court judgment", "patent", "rfc", "direct observation", "laboratory notebook"
]

SECONDARY_KEYWORDS = [
    "journal", "proceedings", "systematic review", "peer-reviewed", "nature",
    "science", "springer", "elsevier", "ieee transactions", "acm"
]

TERTIARY_KEYWORDS = [
    "wikipedia", "britannica", "handbook", "summary", "encyclopedia", "digest"
]


class SourceEvaluator:
    @staticmethod
    def classify_source_type(
        url: Optional[str] = None,
        title: str = "",
        publisher: Optional[str] = None,
        raw_text: Optional[str] = None
    ) -> SourceType:
        """
        Classifies the source tier based on domain authority, publisher, and title content.
        """
        title_lower = title.lower()
        url_lower = (url or "").lower()
        pub_lower = (publisher or "").lower()

        # Check for user-provided markers
        if "user upload" in title_lower or "local workspace" in title_lower or "attachment" in url_lower:
            return SourceType.USER_PROVIDED

        # Check for primary legal/scientific records
        if any(k in title_lower or (raw_text and k in raw_text[:500].lower()) for k in PRIMARY_SOURCE_KEYWORDS):
            return SourceType.PRIMARY

        # Check institutional domains
        if any(dom in url_lower or dom in pub_lower for dom in INSTITUTIONAL_DOMAINS):
            return SourceType.INSTITUTIONAL

        # Check peer-reviewed secondary literature
        if any(k in pub_lower or k in title_lower for k in SECONDARY_KEYWORDS):
            return SourceType.SECONDARY

        # Check tertiary compendiums
        if any(k in url_lower or k in pub_lower or k in title_lower for k in TERTIARY_KEYWORDS):
            return SourceType.TERTIARY

        return SourceType.SECONDARY

    @classmethod
    def evaluate(
        cls,
        source: SourceMetadata,
        raw_content: Optional[str] = None,
        corroborating_source_count: int = 1
    ) -> SourceMetadata:
        """
        Performs transparent multidimensional evaluation of a source.
        Adds interpretable reliability notes and methodological transparency rationale.
        """
        if source.source_type != SourceType.USER_PROVIDED:
            source_type = cls.classify_source_type(
                url=source.url,
                title=source.title,
                publisher=source.publisher,
                raw_text=raw_content
            )
            source.source_type = source_type
        else:
            source_type = SourceType.USER_PROVIDED

        notes: List[str] = []
        methodology: List[str] = []

        # 1. Authority & Methodology by Source Type
        if source_type == SourceType.PRIMARY:
            notes.append("Primary foundational evidence: Direct archival, empirical, or legal document.")
            methodology.append("Direct empirical or statutory observation")
        elif source_type == SourceType.INSTITUTIONAL:
            notes.append("Institutional authority: Published by recognized regulatory, governmental, or standards body.")
            methodology.append("Institutional review / formal standard specification")
        elif source_type == SourceType.SECONDARY:
            notes.append("Secondary scholarly evidence: Academic analysis, survey, or reputable industry documentation.")
            methodology.append("Peer analysis / editorial review")
        elif source_type == SourceType.TERTIARY:
            notes.append("Tertiary reference: General compendium; best suited for background taxonomy rather than definitive proof.")
            methodology.append("Aggregated general reference")
        elif source_type == SourceType.USER_PROVIDED:
            notes.append("User-provided context: Subject to isolated verification against external grounding.")
            methodology.append("User workspace artifact")

        # 2. Corroboration Signal
        if corroborating_source_count > 1:
            notes.append(f"Corroborated across {corroborating_source_count} independent sources.")
        else:
            notes.append("Single-source observation; corroboration recommended for critical assertions.")

        # 3. Specificity Check
        if raw_content:
            has_numeric_data = bool(re.search(r"\b\d+(\.\d+)?(%|kWh|MW|ms|cm|kg|USD|INR|°C)?\b", raw_content))
            if has_numeric_data:
                methodology.append("Contains quantitative empirical measurements")
            else:
                methodology.append("Qualitative descriptive text")

        source.methodological_transparency = "; ".join(methodology) if methodology else "Standard documentation"
        source.reliability_notes = " | ".join(notes)
        return source


source_evaluator = SourceEvaluator()
