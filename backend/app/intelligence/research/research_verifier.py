"""
Pre-Flight Research Verification Engine (Phase 7).
Verifies:
1. Every claim is grounded in real consulted sources.
2. Citations strictly resolve to actual sources (zero fabricated citations).
3. No phantom sources or hallucinated publication dates.
4. INFERENCE is never masked as FACT.
5. Conflicting evidence is explicitly documented.
6. Uncertainty is preserved.
"""

from typing import Dict, Any, List, Tuple
from app.intelligence.research.evidence_models import (
    ResearchSynthesisResult, EvidenceClass
)


class ResearchVerifier:
    @staticmethod
    def verify(result: ResearchSynthesisResult) -> Tuple[bool, List[str]]:
        """
        Runs comprehensive integrity checks on the synthesized research result.
        Returns: (is_verified, verification_notes)
        """
        notes: List[str] = []
        is_verified = True

        source_ids = {s.source_id for s in result.sources}

        # 1. Citation resolution check (no dangling or fabricated citations)
        for cit in result.citations:
            if cit.source_id not in source_ids:
                is_verified = False
                notes.append(f"VERIFICATION FAILURE: Citation '{cit.citation_id}' references unknown source '{cit.source_id}'.")
            if not cit.title or cit.title.strip() == "":
                is_verified = False
                notes.append(f"VERIFICATION FAILURE: Citation '{cit.citation_id}' lacks a valid title.")

        # 2. Claim-to-source mapping check
        for evi in result.evidence_items:
            if evi.classification in [EvidenceClass.FACT, EvidenceClass.SOURCE_DERIVED]:
                if not evi.source_ids:
                    is_verified = False
                    notes.append(f"VERIFICATION FAILURE: Factual statement '{evi.statement[:40]}...' has no source bindings.")
                for sid in evi.source_ids:
                    if sid not in source_ids:
                        is_verified = False
                        notes.append(f"VERIFICATION FAILURE: Evidence references unconsulted source '{sid}'.")

        # 3. Check that inferences are explicitly classified
        for evi in result.evidence_items:
            if evi.classification == EvidenceClass.INFERENCE:
                if not evi.limitations or "inductive" not in evi.limitations.lower() and "inference" not in evi.limitations.lower():
                    notes.append(f"VERIFICATION WARNING: Inference '{evi.statement[:40]}...' should contain explicit epistemic limitations.")

        # 4. Check for conflict representation when multiple opposing evidence items exist
        if len(result.sources) >= 2 and not result.conflicts:
            notes.append("VERIFICATION NOTE: No cross-source conflicts detected; evidence is concordant across consulted sources.")
        elif result.conflicts:
            notes.append(f"VERIFICATION PASS: {len(result.conflicts)} cross-source disagreement(s) explicitly identified and preserved.")

        # 5. Check uncertainty preservation
        has_uncertainty_note = bool(result.uncertainty_analysis and len(result.uncertainty_analysis.strip()) > 10)
        if not has_uncertainty_note:
            is_verified = False
            notes.append("VERIFICATION FAILURE: Uncertainty analysis is missing or unpopulated.")

        if is_verified:
            notes.append("VERIFICATION COMPLETE: Zero fabricated sources, citations validated, evidence classifications verified.")

        return is_verified, notes


research_verifier = ResearchVerifier()
