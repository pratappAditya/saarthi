"""
Evidence Extraction & Claim-Citation Mapping (Phase 7).
Extracts discrete statements from source text, classifies into FACT,
SOURCE-DERIVED, INFERENCE, UNCERTAIN, and binds them to verifiable source passages.
Enforces the invariant: INFERENCE is NEVER silently promoted to FACT.
"""

import uuid
import re
from typing import Dict, Any, List, Tuple, Optional
from app.intelligence.research.evidence_models import (
    EvidenceItem, EvidenceClass, SourceMetadata, SupportingPassage, Citation
)
from app.intelligence.research.research_safety import research_safety_guard


class EvidenceExtractor:
    @staticmethod
    def extract_sentences(text: str) -> List[str]:
        if not text:
            return []
        # Split on sentence boundaries
        raw_sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        return [s.strip() for s in raw_sentences if len(s.strip()) > 15]

    def extract_evidence(
        self,
        sources_with_text: List[Tuple[SourceMetadata, str]],
        domain: str = "general",
        research_dimensions: Optional[List[str]] = None
    ) -> Tuple[List[EvidenceItem], List[Citation]]:
        """
        Parses source texts to extract discrete evidence statements, classifies each,
        and generates strictly traceable citations.
        """
        evidence_items: List[EvidenceItem] = []
        citations: List[Citation] = []
        source_citation_map: Dict[str, str] = {}

        for src, raw_text in sources_with_text:
            # 1. Create or retrieve Citation for this source
            cit_id = f"cit_{len(citations) + 1:03d}"
            source_citation_map[src.source_id] = cit_id

            clean_url = research_safety_guard.validate_citation_url(src.url)
            citations.append(Citation(
                citation_id=cit_id,
                source_id=src.source_id,
                title=src.title,
                url=clean_url,
                publisher=src.publisher,
                author=src.author,
                publication_date=src.publication_date,
                accessed_date=src.accessed_date,
                supporting_passage=raw_text[:250] + "..." if len(raw_text) > 250 else raw_text
            ))

            sentences = self.extract_sentences(raw_text)
            if not sentences:
                continue

            for sent in sentences:
                sent_lower = sent.lower()

                # Determine evidence classification
                # FACT: Explicit empirical observation, statute, standard, direct measurement
                is_fact = (
                    src.source_type in ["PRIMARY", "INSTITUTIONAL"]
                    and bool(re.search(r"\b(\d+(\.\d+)?(%|kwh|mw|cycles|years|bce|ce|km|°c|mv)?)\b", sent_lower))
                )

                # UNCERTAIN: Contains hedged phrases, low sample size, dispute
                is_uncertain = any(h in sent_lower for h in [
                    "might", "could", "may", "preliminary", "uncertain", "disputed", "emerging", "controversial"
                ])

                if is_uncertain:
                    e_class = EvidenceClass.UNCERTAIN
                    confidence = 0.65
                    limitations = "Preliminary findings or emerging technology; high variance in experimental/deployment conditions."
                elif is_fact:
                    e_class = EvidenceClass.FACT
                    confidence = 0.95
                    limitations = None
                else:
                    e_class = EvidenceClass.SOURCE_DERIVED
                    confidence = 0.88
                    limitations = "Asserted in secondary literature; dependent on cited study methodology."

                # Domain-specific confidence tier
                domain_tier = None
                if domain in ["physics", "biology", "chemistry", "software"]:
                    domain_tier = research_safety_guard.determine_scientific_tier(
                        claim=sent,
                        is_empirically_replicated=is_fact,
                        sample_size_adequate=not is_uncertain
                    ).value
                elif domain in ["archaeology", "history"]:
                    domain_tier = research_safety_guard.determine_historical_tier(
                        claim=sent,
                        has_primary_document=(src.source_type == "PRIMARY"),
                        is_conjectural=is_uncertain
                    ).value

                evidence_items.append(EvidenceItem(
                    evidence_id=f"evi_{uuid.uuid4().hex[:6]}",
                    statement=sent,
                    classification=e_class,
                    source_ids=[src.source_id],
                    supporting_passages=[
                        SupportingPassage(
                            text=sent,
                            section_name=src.title,
                            verified_in_source=True
                        )
                    ],
                    confidence=confidence,
                    domain=domain,
                    limitations=limitations,
                    domain_confidence_tier=domain_tier,
                    provenance={
                        "source_title": src.title,
                        "citation_id": cit_id,
                        "source_type": src.source_type.value,
                        "pub_date": src.publication_date
                    }
                ))

        # Synthesize Inferences explicitly (Rule 7: Never silently promote INFERENCE to FACT)
        if len(evidence_items) >= 2:
            fact_count = sum(1 for e in evidence_items if e.classification in [EvidenceClass.FACT, EvidenceClass.SOURCE_DERIVED])
            if fact_count >= 2:
                inference_stmt = f"Synthesizing {fact_count} documented observations across {len(sources_with_text)} sources indicates a technological and operational trade-off profile specific to this domain."
                evidence_items.append(EvidenceItem(
                    evidence_id=f"evi_inf_{uuid.uuid4().hex[:6]}",
                    statement=inference_stmt,
                    classification=EvidenceClass.INFERENCE,
                    source_ids=[s.source_id for s, _ in sources_with_text[:2]],
                    supporting_passages=[], # Inferences are derived conclusions, not direct source quotes
                    confidence=0.82,
                    domain=domain,
                    limitations="Derived synthesis across evaluated evidence; represents inductive model reasoning, not direct empirical proof.",
                    domain_confidence_tier="PLAUSIBLE_INTERPRETATION",
                    provenance={
                        "derivation_type": "cross_source_synthesis",
                        "derived_from_count": fact_count
                    }
                ))

        return evidence_items, citations


evidence_extractor = EvidenceExtractor()
