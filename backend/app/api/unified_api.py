import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query, Body, Depends

from app.api.auth import get_current_user
from app.intelligence.orchestration.orchestrator import orchestrator
from app.intelligence.memory.memory_manager import memory_manager
from app.intelligence.projects.project_manager import project_manager
from app.intelligence.proactive.goal_system import goal_system
from app.intelligence.routines.routine_store import routine_store
from app.intelligence.proactive.proactive_engine import proactive_engine
from app.intelligence.domains.domain_registry import domain_registry
from app.intelligence.audit.intelligence_audit import audit_service
from app.core.entitlements import get_current_plan

logger = logging.getLogger("app.api.unified_api")

router = APIRouter(prefix="/unified", tags=["UnifiedSaarthi"])

@router.post("/chat")
def unified_chat(
    payload: Dict[str, Any] = Body(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Unified Top-Level Chat & Agent Execution Endpoint.
    Requires authenticated session; binds execution to verified user identity.
    """
    message = payload.get("message")
    if not message:
        raise HTTPException(status_code=400, detail="Message is required.")
    
    auth_user_id = current_user["user_id"]
    client_user_id = payload.get("user_id")
    if client_user_id and client_user_id != auth_user_id and current_user.get("role") not in ["ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(status_code=403, detail="Forbidden: Cannot execute chat on behalf of another user.")
    
    session_id = payload.get("session_id", "default_session")
    project_id = payload.get("project_id")
    approval_token = payload.get("approval_token") or payload.get("permission_approval_id")
    attachment_id = payload.get("attachment_id")
    
    res = orchestrator.process_message(
        user_message=message,
        session_id=session_id,
        user_id=auth_user_id,
        project_id=project_id,
        approval_token=approval_token,
        attachment_id=attachment_id
    )
    return res

@router.get("/command-center")
def get_command_center_payload(
    user_id: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Consolidated payload for Universal Saarthi Home / Command Center Dashboard.
    Enforces user data isolation.
    """
    auth_user_id = current_user["user_id"]
    if user_id and user_id != auth_user_id and current_user.get("role") not in ["ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(status_code=403, detail="Forbidden: Cannot access command center for another user.")
    
    target_user_id = auth_user_id
    plan = get_current_plan(target_user_id)
    projects = [p.model_dump() for p in project_manager.list_projects(user_id=target_user_id)]
    goals = [g.model_dump() for g in goal_system.list_goals(user_id=target_user_id)]
    routines = [r.model_dump() for r in routine_store.list_routines(user_id=target_user_id)]
    proactive = [p.model_dump() for p in proactive_engine.detect_opportunities(user_id=target_user_id)]
    facts = memory_manager.get_user_fact_summary(user_id=target_user_id)
    domains = [p.model_dump() for p in domain_registry.list_packs()]
    
    return {
        "status": "success",
        "user_id": target_user_id,
        "current_plan": plan,
        "active_project": projects[0] if projects else None,
        "projects_count": len(projects),
        "goals": goals[:3],
        "upcoming_routines": routines[:3],
        "proactive_suggestions": proactive[:3],
        "user_facts_count": len(facts),
        "available_domains": len(domains)
    }

@router.post("/memory/remember")
def remember_fact(
    payload: Dict[str, Any] = Body(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    content = payload.get("content")
    if not content:
        raise HTTPException(status_code=400, detail="Content is required.")
    
    auth_user_id = current_user["user_id"]
    client_user_id = payload.get("user_id")
    if client_user_id and client_user_id != auth_user_id and current_user.get("role") not in ["ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(status_code=403, detail="Forbidden: Cannot create memories for another user.")
    
    domain = payload.get("domain", "general")
    res = memory_manager.remember(content=content, domain=domain, user_id=auth_user_id)
    return {"status": "success", "memory": res}

@router.post("/memory/forget")
def forget_fact(
    payload: Dict[str, Any] = Body(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    query = payload.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="Query is required.")
    
    auth_user_id = current_user["user_id"]
    client_user_id = payload.get("user_id")
    if client_user_id and client_user_id != auth_user_id and current_user.get("role") not in ["ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(status_code=403, detail="Forbidden: Cannot delete memories of another user.")
    
    count = memory_manager.forget_by_query(query=query, user_id=auth_user_id)
    return {"status": "success", "forgot_count": count}

@router.get("/memory/explain/{memory_id}")
def explain_memory(
    memory_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    explanation = memory_manager.explain_memory_provenance(memory_id)
    if not explanation:
        raise HTTPException(status_code=404, detail=f"Memory '{memory_id}' not found.")
    
    mem = memory_manager.store.get_memory(memory_id)
    if mem and mem.user_id != current_user["user_id"] and current_user.get("role") not in ["ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(status_code=403, detail="Forbidden: Access to this memory is denied.")
    
    return {"status": "success", "provenance": explanation}

@router.get("/audit-trail")
def get_trust_center_audit(
    user_id: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    auth_user_id = current_user["user_id"]
    if user_id and user_id != auth_user_id and current_user.get("role") not in ["ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(status_code=403, detail="Forbidden: Access to another user's audit trail is denied.")
    
    target_user_id = auth_user_id
    logs = audit_service.get_user_audit_logs(user_id=target_user_id, limit=limit)
    return {"status": "success", "logs": logs}

