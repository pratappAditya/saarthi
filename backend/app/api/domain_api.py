import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel, Field

from app.core.entitlements import require_capability
from app.intelligence.domains.domain_registry import domain_registry
from app.intelligence.domains.domain_router import domain_router, DomainRouteResult
from app.intelligence.domains.research_engine import research_engine
from app.intelligence.research.research_orchestrator import research_orchestrator
from app.intelligence.research.domain_intelligence import domain_intelligence_manager
from app.intelligence.research.research_cache import research_cache

logger = logging.getLogger("app.api.domain_api")
router = APIRouter(prefix="/domains", tags=["domains"])

class RouteRequest(BaseModel):
    prompt: str
    explicit_domain: Optional[str] = None
    project_domain: Optional[str] = None

class ResearchRequest(BaseModel):
    query: str
    domain_id: Optional[str] = "research"

class DeepResearchRequest(BaseModel):
    query: str
    domain_id: Optional[str] = "research"
    output_mode: Optional[str] = "evidence_summary"
    user_id: Optional[str] = "default_local_user"
    user_attachments: Optional[List[Dict[str, Any]]] = None
    bypass_cache: bool = False

class PersistResearchMemoryRequest(BaseModel):
    research_id: str
    conclusion: str
    user_id: Optional[str] = "default_local_user"
    project_id: Optional[str] = None
    evidence_class: Optional[str] = "FACT"
    sources: Optional[List[str]] = Field(default_factory=list)
    uncertainty: Optional[str] = ""

@router.get("")
def list_domains_endpoint():
    packs = domain_registry.list_packs()
    return {"domains": [p.model_dump() for p in packs]}

@router.get("/{domain_id}")
def get_domain_endpoint(domain_id: str):
    pack = domain_registry.get_pack(domain_id)
    if not pack:
        raise HTTPException(status_code=404, detail=f"Domain pack '{domain_id}' not found.")
    return {"domain": pack.model_dump()}

@router.get("/{domain_id}/intelligence")
def get_domain_intelligence_endpoint(domain_id: str):
    spec = domain_intelligence_manager.get_domain_spec(domain_id)
    if not spec:
        raise HTTPException(status_code=404, detail=f"Domain intelligence specification for '{domain_id}' not found.")
    return {"domain_id": domain_id, "intelligence": spec.model_dump()}

@router.post("/route")
def route_domain_endpoint(req: RouteRequest):
    res = domain_router.route_request(
        prompt=req.prompt,
        explicit_domain=req.explicit_domain,
        project_domain=req.project_domain
    )
    return {"route": res.model_dump()}

@router.post("/research/analyze", dependencies=[Depends(require_capability("domain.research"))])
def run_research_endpoint(req: ResearchRequest):
    res = research_engine.analyze_research_query(query=req.query, domain_id=req.domain_id or "research")
    return {"research": res.model_dump()}

@router.post("/research/deep", dependencies=[Depends(require_capability("domain.research"))])
def run_deep_research_endpoint(req: DeepResearchRequest):
    try:
        res = research_orchestrator.conduct_research(
            query=req.query,
            domain_id=req.domain_id or "research",
            output_mode_override=req.output_mode,
            user_id=req.user_id or "default_local_user",
            user_attachments=req.user_attachments,
            bypass_cache=req.bypass_cache
        )
        return {"status": "success", "result": res.model_dump()}
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail=str(pe))
    except Exception as e:
        logger.error(f"Error in deep research endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/research/memory/persist")
def persist_research_memory_endpoint(req: PersistResearchMemoryRequest):
    from app.intelligence.memory.memory_manager import memory_manager
    from app.intelligence.memory.memory_models import MemoryProvenance, MemoryScope

    try:
        sources_str = ", ".join(req.sources) if req.sources else "Verified Grounded Repository"
        provenance_str = f"Sources: {sources_str} | Evidence Class: {req.evidence_class}"

        saved_mem = memory_manager.create_fact(
            content=f"{req.conclusion}\n[Provenance: {provenance_str}]",
            source=MemoryProvenance.USER_EXPLICIT,
            importance=8,
            domain="research",
            user_id=req.user_id or "default_local_user",
            scope=MemoryScope.PROJECT if req.project_id else MemoryScope.GLOBAL_USER,
            project_id=req.project_id
        )
        return {"status": "success", "message": "Research conclusion persisted to memory with provenance.", "memory": saved_mem.model_dump()}
    except Exception as e:
        logger.error(f"Error persisting research memory: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/research/cache/invalidate")
def invalidate_cache_endpoint(payload: Dict[str, Any] = Body(default={})):
    query = payload.get("query")
    research_cache.invalidate(query)
    return {"status": "success", "message": f"Cache invalidated for '{query or 'ALL'}'"}
