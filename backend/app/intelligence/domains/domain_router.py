import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from app.intelligence.domains.domain_registry import domain_registry, DomainPack

logger = logging.getLogger("app.intelligence.domain_router")

class DomainRouteResult(BaseModel):
    primary_domain: str
    confidence: float
    secondary_domains: List[str] = Field(default_factory=list)
    reason: str
    is_explicit_override: bool = False
    active_pack: Optional[Dict[str, Any]] = None
    allowed_tools: List[str] = Field(default_factory=list)

class DomainRouter:
    @staticmethod
    def classify_domain(text: str) -> Dict[str, Any]:
        """Backward-compatible wrapper for ContextEngine and Phase 5B tests."""
        res = domain_router.route_request(prompt=text)
        return {
            "domain": res.primary_domain,
            "domain_pack_id": res.primary_domain,
            "confidence": res.confidence,
            "reason": res.reason,
            "allowed_tools": res.allowed_tools
        }

    def route_request(
        self,
        prompt: str,
        explicit_domain: Optional[str] = None,
        project_domain: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> DomainRouteResult:
        """
        Classifies user prompt and context into primary and secondary domain packs.
        Respects explicit domain overrides if provided.
        """
        # 1. Explicit Override Check
        if explicit_domain and explicit_domain.lower() != "auto":
            pack = domain_registry.get_pack(explicit_domain.lower())
            if pack:
                return DomainRouteResult(
                    primary_domain=pack.id,
                    confidence=1.0,
                    secondary_domains=[],
                    reason=f"User explicitly selected '{pack.name}' domain.",
                    is_explicit_override=True,
                    active_pack=pack.model_dump(),
                    allowed_tools=pack.allowed_tools
                )

        # 2. Project Domain Bias
        if project_domain and project_domain.lower() != "general":
            p_pack = domain_registry.get_pack(project_domain.lower())
            if p_pack and any(kw in prompt.lower() for kw in p_pack.aliases + [p_pack.id, p_pack.name.lower()]):
                return DomainRouteResult(
                    primary_domain=p_pack.id,
                    confidence=0.95,
                    secondary_domains=["research"],
                    reason=f"Matched project domain '{p_pack.name}'.",
                    is_explicit_override=False,
                    active_pack=p_pack.model_dump(),
                    allowed_tools=p_pack.allowed_tools
                )

        # 3. Rule-based Keyword Scoring
        prompt_lower = prompt.lower()

        scores: Dict[str, float] = {}
        for pack in domain_registry.list_packs():
            score = 0.0
            if pack.id in prompt_lower or pack.name.lower() in prompt_lower:
                score += 3.0
            for alias in pack.aliases:
                if alias in prompt_lower:
                    score += 2.0

            # Domain specific keyword triggers
            if pack.id == "software" and any(k in prompt_lower for k in ["code", "error", "bug", "python", "java", "spring boot", "react", "c++", "git"]):
                score += 4.0
            elif pack.id == "cybersecurity" and any(k in prompt_lower for k in ["nmap", "vulnerability", "sec audit", "security audit", "security", "exploit", "cve"]):
                score += 4.0
            elif pack.id == "archaeology" and any(k in prompt_lower for k in ["excavation", "artifact", "site", "stratigraphy", "harappan", "pottery"]):
                score += 4.0
            elif pack.id == "biology" and any(k in prompt_lower for k in ["protein", "gene", "dna", "cell", "expression", "biological"]):
                score += 4.0
            elif pack.id == "civil" and any(k in prompt_lower for k in ["beam", "loading", "concrete", "structural", "bridge", "truss"]):
                score += 4.0
            elif pack.id == "research" and any(k in prompt_lower for k in ["paper", "arxiv", "research", "literature", "academic", "journal", "citation"]):
                score += 5.0
            elif pack.id == "career" and any(k in prompt_lower for k in ["resume", "job", "interview", "salary", "cover letter", "ats"]):
                score += 5.0

            scores[pack.id] = score

        sorted_domains = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        top_id, top_score = sorted_domains[0]

        if top_score > 0.0:
            top_pack = domain_registry.get_pack(top_id)
            secondary = [d_id for d_id, s in sorted_domains[1:3] if s > 0.0]
            return DomainRouteResult(
                primary_domain=top_id,
                confidence=min(0.95, 0.5 + (top_score * 0.1)),
                secondary_domains=secondary,
                reason=f"Detected '{top_pack.name}' from query intent.",
                is_explicit_override=False,
                active_pack=top_pack.model_dump(),
                allowed_tools=top_pack.allowed_tools
            )

        # Fallback to General
        gen_pack = domain_registry.get_pack("general")
        return DomainRouteResult(
            primary_domain="general",
            confidence=0.90,
            secondary_domains=[],
            reason="General conversation routing.",
            is_explicit_override=False,
            active_pack=gen_pack.model_dump(),
            allowed_tools=gen_pack.allowed_tools
        )

    def detect_domain_sequence(self, prompt: str) -> List[Dict[str, Any]]:
        """
        Decomposes complex cross-domain prompt into sequence of ordered domain steps.
        """
        p_lower = prompt.lower()
        sequence = []

        if "archaeol" in p_lower or "excavation" in p_lower or "pottery" in p_lower:
            sequence.append({"domain": "archaeology", "reason": "Artifact & excavation analysis"})
        if "photo" in p_lower or "image" in p_lower or "visual" in p_lower:
            sequence.append({"domain": "vision", "reason": "Multimodal visual feature extraction"})
        if "histor" in p_lower or "record" in p_lower or "archive" in p_lower:
            sequence.append({"domain": "history", "reason": "Comparative historical archival matching"})
        if "research" in p_lower or "paper" in p_lower or "finding" in p_lower:
            sequence.append({"domain": "research", "reason": "Literature search & evidence synthesis"})
        if "report" in p_lower or "write" in p_lower or "prepare" in p_lower or "draft" in p_lower:
            sequence.append({"domain": "writing", "reason": "Final structured documentation"})

        if not sequence:
            res = self.route_request(prompt)
            sequence = [{"domain": res.primary_domain, "reason": res.reason}]

        return sequence

domain_router = DomainRouter()
