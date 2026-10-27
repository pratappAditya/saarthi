"""
Question Decomposition for Universal Research Orchestration (Phase 7).
Identifies research dimensions, time/geographic constraints, domain mappings,
and uncertainty boundaries without over-decomposing simple factual queries.
"""

import re
import uuid
from typing import Dict, Any, List, Optional
from app.intelligence.research.evidence_models import (
    ResearchPlan, ResearchOutputMode, EvidenceClass, SourceType
)
from app.intelligence.domains.domain_router import domain_router

COMPLEX_INDICATORS = [
    "compare", "comparison", "evaluate", "trade-off", "tradeoff", "versus", "vs",
    "analyze", "analysis", "implications", "long-term", "review", "state of the art",
    "pros and cons", "synthesis", "comprehensive", "literature", "architecture",
    "difference between", "feasibility", "benchmark", "stratigraphy", "deep dive"
]

DOMAIN_DIMENSION_MAP = {
    "software": ["architecture", "performance", "maintainability", "security", "tooling_ecosystem"],
    "cybersecurity": ["threat_model", "vulnerability_vectors", "mitigations", "compliance", "exploitability"],
    "engineering": ["materials", "efficiency", "structural_load", "thermal_dynamics", "manufacturability"],
    "mechanical": ["materials", "efficiency", "thermal_dynamics", "kinematics", "durability"],
    "civil": ["structural_loading", "soil_mechanics", "materials_durability", "seismic_safety", "regulations"],
    "electrical": ["circuit_topology", "power_efficiency", "signal_integrity", "thermal_limits", "standards"],
    "biology": ["molecular_mechanism", "cellular_pathway", "genomic_conservation", "clinical_expression"],
    "chemistry": ["reaction_mechanism", "stoichiometry", "thermodynamics", "safety", "synthesis_yield"],
    "physics": ["theoretical_model", "experimental_evidence", "conservation_laws", "boundary_conditions"],
    "archaeology": ["stratigraphy", "material_typology", "radiocarbon_chronology", "cultural_context"],
    "history": ["primary_sources", "historiographical_debate", "chronological_sequence", "geopolitical_context"],
    "business": ["market_size", "unit_economics", "competitive_landscape", "regulatory_risk", "growth_drivers"],
    "career": ["skill_alignment", "industry_demand", "compensation_benchmark", "progression_path"]
}

BATTERY_STORAGE_DIMENSIONS = [
    "chemistry", "energy_density", "cycle_life", "safety",
    "cost_lcoe", "availability_supply_chain", "deployment_maturity", "environmental_lifecycle"
]


class QuestionDecomposer:
    @staticmethod
    def is_complex_query(query: str) -> bool:
        """
        Determines whether a query requires multi-dimensional research decomposition
        versus simple factual answer.
        """
        q_lower = query.lower()
        words = q_lower.split()

        # Simple short questions are not complex unless explicit comparison
        if len(words) < 6 and not any(k in q_lower for k in ["compare", "vs", "versus"]):
            return False

        # Check explicit keywords
        for ind in COMPLEX_INDICATORS:
            if ind in q_lower:
                return True

        # Queries spanning multiple entities or conjunctions with research terms
        if (" and " in q_lower or " or " in q_lower) and len(words) >= 8:
            return True

        return False

    @staticmethod
    def extract_temporal_constraints(query: str) -> Optional[str]:
        q_lower = query.lower()
        if any(k in q_lower for k in ["latest", "current", "today", "now", "recent", "2026", "2025"]):
            return "CURRENT (2025-2026 prioritized)"
        year_matches = re.findall(r"\b(19\d\d|20\d\d)\b", query)
        if year_matches:
            return f"SPECIFIC_YEARS: {', '.join(year_matches)}"
        if any(k in q_lower for k in ["ancient", "medieval", "century", "bce", "ce", "era", "historical"]):
            return "HISTORICAL_ARCHIVAL"
        return None

    @staticmethod
    def extract_geographic_constraints(query: str) -> Optional[str]:
        q_lower = query.lower()
        regions = {
            "india": "India / South Asia",
            "us": "United States / North America",
            "usa": "United States",
            "europe": "European Union / Europe",
            "china": "East Asia / China",
            "global": "Global / International",
            "harappan": "Indus Valley / South Asia",
            "indus": "Indus River Basin"
        }
        found = [v for k, v in regions.items() if re.search(rf"\b{k}\b", q_lower)]
        return ", ".join(set(found)) if found else None

    @staticmethod
    def detect_output_mode(query: str) -> ResearchOutputMode:
        q_lower = query.lower()
        if "compare" in q_lower or "versus" in q_lower or " vs " in q_lower:
            return ResearchOutputMode.COMPARISON
        if "timeline" in q_lower or "chronology" in q_lower or "history of" in q_lower:
            return ResearchOutputMode.TIMELINE
        if "literature" in q_lower or "papers on" in q_lower or "state of the art" in q_lower:
            return ResearchOutputMode.LITERATURE_REVIEW
        if "table" in q_lower or "matrix" in q_lower:
            return ResearchOutputMode.SOURCE_TABLE
        if "brief" in q_lower or "executive summary" in q_lower:
            return ResearchOutputMode.RESEARCH_BRIEF
        if "technical report" in q_lower or "specification" in q_lower:
            return ResearchOutputMode.TECHNICAL_REPORT
        if "decision" in q_lower or "recommendation" in q_lower:
            return ResearchOutputMode.DECISION_SUPPORT
        if len(q_lower.split()) < 8 and not any(k in q_lower for k in ["detail", "explain", "why"]):
            return ResearchOutputMode.CONCISE_ANSWER
        return ResearchOutputMode.EVIDENCE_SUMMARY

    def decompose(self, query: str, explicit_domain: Optional[str] = None) -> ResearchPlan:
        plan_id = f"plan_{uuid.uuid4().hex[:8]}"
        route = domain_router.route_request(query, explicit_domain=explicit_domain)
        primary_domain = route.primary_domain
        secondary_domains = route.secondary_domains

        all_domains = [primary_domain]
        for sec in secondary_domains:
            if sec not in all_domains:
                all_domains.append(sec)

        is_complex = self.is_complex_query(query)
        time_constraints = self.extract_temporal_constraints(query)
        geo_constraints = self.extract_geographic_constraints(query)
        output_mode = self.detect_output_mode(query)

        q_lower = query.lower()
        subquestions = []
        dimensions = []

        if not is_complex:
            # Simple query: single subquestion, direct focus
            subquestions.append({
                "subquery": query,
                "domain": primary_domain,
                "dimension": "direct_fact"
            })
            dimensions = ["direct_fact"]
            req_evidence = [EvidenceClass.FACT, EvidenceClass.SOURCE_DERIVED]
            target_sources = [SourceType.PRIMARY, SourceType.INSTITUTIONAL, SourceType.SECONDARY]
            max_sources = 3
        else:
            # Complex query: identify meaningful research dimensions
            if "battery" in q_lower and ("storage" in q_lower or "grid" in q_lower or "compare" in q_lower):
                dimensions = BATTERY_STORAGE_DIMENSIONS
            else:
                domain_dims = DOMAIN_DIMENSION_MAP.get(primary_domain, ["theoretical_basis", "empirical_evidence", "practical_application"])
                dimensions = domain_dims[:5]
                if len(all_domains) > 1:
                    for extra_d in all_domains[1:]:
                        extra_dims = DOMAIN_DIMENSION_MAP.get(extra_d, ["cross_domain_synthesis"])
                        dimensions.append(extra_dims[0])

            # Generate targeted subqueries per dimension
            for dim in dimensions:
                dim_readable = dim.replace("_", " ")
                assigned_domain = primary_domain
                # If dimension aligns with a secondary domain, route appropriately
                for sd in all_domains:
                    if sd in dim:
                        assigned_domain = sd
                        break
                subquestions.append({
                    "subquery": f"Examine {dim_readable} for: '{query}'",
                    "domain": assigned_domain,
                    "dimension": dim
                })

            req_evidence = [
                EvidenceClass.FACT,
                EvidenceClass.SOURCE_DERIVED,
                EvidenceClass.INFERENCE,
                EvidenceClass.UNCERTAIN
            ]
            target_sources = [
                SourceType.PRIMARY,
                SourceType.INSTITUTIONAL,
                SourceType.SECONDARY
            ]
            max_sources = min(12, max(5, len(subquestions) * 2))

        return ResearchPlan(
            plan_id=plan_id,
            primary_question=query,
            is_complex=is_complex,
            research_dimensions=dimensions,
            subquestions=subquestions,
            required_evidence_types=req_evidence,
            target_source_types=target_sources,
            relevant_domains=all_domains,
            time_constraints=time_constraints,
            geographic_constraints=geo_constraints,
            output_mode=output_mode,
            max_sources=max_sources,
            max_iterations=3,
            stopping_criteria=f"Acquire corroborated evidence across {len(dimensions)} dimensions or reach {max_sources} sources"
        )


question_decomposer = QuestionDecomposer()
