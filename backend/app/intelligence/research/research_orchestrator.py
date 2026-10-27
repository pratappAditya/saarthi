"""
Universal Research Orchestrator (Phase 7).
Coordinates the end-to-end deep research lifecycle:
QUESTION -> DECOMPOSE -> PLAN -> SEARCH -> COLLECT -> EVALUATE -> EXTRACT -> COMPARE -> SYNTHESIZE -> VERIFY -> CITE
Integrates Entitlements/Quota, Multimodal inputs, Agents, Caching, and Explicit Memory retention.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from app.intelligence.research.evidence_models import (
    ResearchSynthesisResult, ResearchPlan, ResearchOutputMode, SourceMetadata
)
from app.intelligence.research.question_decomposer import question_decomposer
from app.intelligence.research.source_discovery import source_discovery_manager
from app.intelligence.research.source_evaluator import source_evaluator
from app.intelligence.research.recency_handler import recency_handler
from app.intelligence.research.evidence_extractor import evidence_extractor
from app.intelligence.research.conflict_detector import conflict_detector
from app.intelligence.research.research_safety import research_safety_guard
from app.intelligence.research.research_synthesizer import research_synthesizer
from app.intelligence.research.research_verifier import research_verifier
from app.intelligence.research.research_cache import research_cache
from app.intelligence.research.domain_intelligence import domain_intelligence_manager

from app.security.quota import QuotaManager
from app.core.plans import PlanService
from app.core.entitlements import get_current_plan

logger = logging.getLogger("app.intelligence.research.orchestrator")


class ResearchOrchestrator:
    def __init__(self):
        self.decomposer = question_decomposer
        self.discovery = source_discovery_manager
        self.extractor = evidence_extractor
        self.conflict_detector = conflict_detector
        self.synthesizer = research_synthesizer
        self.verifier = research_verifier
        self.cache = research_cache

    def conduct_research(
        self,
        query: str,
        user_id: str = "default_local_user",
        session_id: str = "default_session",
        domain_id: Optional[str] = None,
        explicit_domains: Optional[List[str]] = None,
        user_attachments: Optional[List[Dict[str, Any]]] = None,
        output_mode_override: Optional[str] = None,
        user_preferences: Optional[Dict[str, Any]] = None,
        bypass_cache: bool = False
    ) -> ResearchSynthesisResult:
        """
        Executes the full 10-stage Universal Research pipeline with strict auditability,
        bounded performance limits, quota enforcement, and verifiable provenance.
        """
        start_time = datetime.now(timezone.utc)
        logger.info(f"Initiating Universal Research for query: '{query}' (user={user_id})")

        # 1. Quota & Entitlement Gate
        current_plan = get_current_plan(user_id)
        allowed, quota_info = QuotaManager.check_and_increment_quota(user_id, current_plan)
        if not allowed:
            raise PermissionError(quota_info.get("error", "Daily research usage quota exhausted. Please upgrade."))

        # 2. Check Cache (if applicable and not bypassed)
        target_mode = output_mode_override or "evidence_summary"
        cached_result = None
        if not bypass_cache and not self.cache.is_bypass_query(query):
            cached_result = self.cache.get(query, domain=domain_id or "research", output_mode=target_mode)
            if cached_result:
                logger.info(f"Returning cached research synthesis for: '{query}'")
                return cached_result

        # 3. Question Decomposition & Planning
        plan = self.decomposer.decompose(query, explicit_domain=domain_id)
        if explicit_domains:
            for ed in explicit_domains:
                if ed not in plan.relevant_domains:
                    plan.relevant_domains.append(ed)

        if output_mode_override:
            try:
                plan.output_mode = ResearchOutputMode(output_mode_override)
            except ValueError:
                pass

        primary_domain = plan.relevant_domains[0] if plan.relevant_domains else "research"

        # 4. Source Discovery (Bounded collection, stopping criteria)
        discovered_sources_with_text = self.discovery.discover_sources(
            query=query,
            domain=primary_domain,
            max_sources=plan.max_sources,
            user_attachments=user_attachments
        )

        # 5. Source Evaluation & Untrusted Data Sanitization
        evaluated_sources: List[SourceMetadata] = []
        sanitized_sources_with_text: List[Any] = []

        is_current_requested = bool(plan.time_constraints and "CURRENT" in plan.time_constraints)

        for src, raw_text in discovered_sources_with_text:
            # Enforce zero-trust content wrapping
            safe_text = research_safety_guard.sanitize_untrusted_source(
                raw_text=raw_text,
                source_title=src.title,
                source_url=src.url
            )
            # Evaluate recency and authority
            src = source_evaluator.evaluate(src, raw_content=safe_text, corroborating_source_count=len(discovered_sources_with_text))
            src = recency_handler.evaluate_source(src, domain=primary_domain, user_requested_current=is_current_requested)

            evaluated_sources.append(src)
            sanitized_sources_with_text.append((src, safe_text))

        # 6. Evidence Extraction & Claim-Citation Mapping
        evidence_items, citations = self.extractor.extract_evidence(
            sources_with_text=sanitized_sources_with_text,
            domain=primary_domain,
            research_dimensions=plan.research_dimensions
        )

        # 7. Cross-Source Disagreement & Conflict Detection
        conflicts = self.conflict_detector.detect_conflicts(
            evidence_items=evidence_items,
            sources=evaluated_sources
        )

        # 8. Synthesis across Requested Output Mode
        result = self.synthesizer.synthesize(
            question=query,
            plan=plan,
            sources=evaluated_sources,
            evidence=evidence_items,
            conflicts=conflicts,
            citations=citations,
            domain=primary_domain,
            user_preferences=user_preferences
        )

        # 9. Pre-Flight Verification
        is_verified, verification_notes = self.verifier.verify(result)
        result.verification_status = "VERIFIED" if is_verified else "PARTIAL"
        result.verification_notes = verification_notes

        # 10. Cache Result (if allowed)
        if not self.cache.is_bypass_query(query):
            self.cache.set(
                query=query,
                domain=primary_domain,
                output_mode=result.output_mode.value,
                result=result
            )

        logger.info(f"Universal Research complete for '{query}' ({len(result.evidence_items)} evidence, {len(result.citations)} citations, verified={is_verified})")
        return result

    def persist_conclusion_to_memory(
        self,
        research_result: ResearchSynthesisResult,
        conclusion_statement: str,
        user_id: str = "default_local_user",
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Phase 7 Memory Integration:
        Persists a research conclusion to permanent memory ONLY upon explicit user instruction.
        Retains source provenance, date, project, evidence class, and uncertainty.
        """
        from app.intelligence.memory.memory_manager import memory_manager
        from app.intelligence.memory.memory_models import MemoryProvenance, MemoryScope

        # Find supporting evidence class
        matching_evidence = [e for e in research_result.evidence_items if e.statement in conclusion_statement or conclusion_statement in e.statement]
        e_class = matching_evidence[0].classification.value if matching_evidence else "SOURCE-DERIVED"

        citation_refs = [f"{c.citation_id}: {c.title}" for c in research_result.citations[:3]]
        provenance_str = f"Sources: {', '.join(citation_refs)} | Date: {research_result.created_at[:10]} | Evidence Class: {e_class}"

        mem_content = f"{conclusion_statement}\n[Provenance: {provenance_str}]"

        saved_mem = memory_manager.create_fact(
            content=mem_content,
            source=MemoryProvenance.USER_EXPLICIT,
            importance=8,
            domain=research_result.domain_id,
            user_id=user_id,
            scope=MemoryScope.PROJECT if project_id else MemoryScope.GLOBAL_USER,
            project_id=project_id
        )

        return {
            "status": "success",
            "message": "Research conclusion persisted to durable memory with explicit provenance.",
            "memory": saved_mem.model_dump()
        }


research_orchestrator = ResearchOrchestrator()
