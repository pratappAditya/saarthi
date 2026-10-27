import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query, Body

from app.intelligence.planning.planner import planner_service
from app.intelligence.planning.task_store import task_store
from app.intelligence.domains.domain_router import domain_router
from app.intelligence.domains.domain_handoff import domain_handoff_manager
from app.intelligence.orchestration.orchestrator import orchestrator
from app.intelligence.domains.research_engine import research_engine
from app.core.entitlements import get_current_plan

logger = logging.getLogger("app.api.cross_domain_api")

router = APIRouter(prefix="/cross-domain", tags=["CrossDomain"])

@router.post("/workflow/start")
def start_cross_domain_workflow(payload: Dict[str, Any] = Body(...)):
    """
    Synthesizes and initiates execution of a multi-domain task graph.
    """
    objective = payload.get("objective")
    if not objective:
        raise HTTPException(status_code=400, detail="Objective is required.")
    
    domain = payload.get("domain", "general")
    user_id = payload.get("user_id", "default_local_user")
    
    graph = planner_service.create_plan(goal=objective, domain=domain, user_id=user_id)
    
    # Process through orchestrator to trigger initial step
    res = orchestrator.process_message(
        user_message=objective,
        session_id=f"workflow_{graph.task_id}",
        user_id=user_id
    )
    
    return {
        "status": "success",
        "task_id": graph.task_id,
        "task_graph": graph.model_dump(),
        "orchestration": res
    }

@router.get("/workflow/{task_id}")
def get_cross_domain_workflow(task_id: str):
    """
    Returns full cross-domain task graph state, steps, handoffs, and verification status.
    """
    task = task_store.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found.")
    
    handoffs = domain_handoff_manager.get_handoffs_for_task(task_id)
    
    return {
        "task": task,
        "handoffs": [h.model_dump() for h in handoffs],
        "verification_state": task.get("verification_state", "unverified")
    }

@router.post("/workflow/{task_id}/approve")
def approve_workflow_step(task_id: str, payload: Dict[str, Any] = Body(...)):
    """
    Approves a pending approval checkpoint in the task graph.
    """
    step_id = payload.get("step_id")
    task = task_store.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found.")
    
    steps = task["steps"]
    updated = False
    for step in steps:
        if step_id is None or step["step_id"] == step_id:
            if step.get("approval_required"):
                step["approval_state"] = "approved"
                updated = True
                
    if updated:
        task_store.update_task_status(task_id=task_id, status="in_progress", steps=steps)
    
    return {
        "status": "success",
        "message": f"Step '{step_id or 'all_pending'}' approved.",
        "task": task_store.get_task(task_id)
    }

@router.post("/workflow/{task_id}/cancel")
def cancel_workflow(task_id: str):
    res = planner_service.cancel_task(task_id)
    if not res:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found.")
    return {"status": "success", "message": f"Workflow '{task_id}' cancelled."}

@router.post("/workflow/{task_id}/resume")
def resume_workflow(task_id: str):
    res = planner_service.resume_task(task_id)
    if not res:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found.")
    return {"status": "success", "message": f"Workflow '{task_id}' resumed."}

@router.post("/workflow/{task_id}/replan")
def replan_workflow(task_id: str, payload: Dict[str, Any] = Body(...)):
    error_msg = payload.get("error_message", "Manual user re-plan requested.")
    failed_step = payload.get("failed_step_id", "step_1")
    res = planner_service.replan_on_failure(task_id, failed_step, error_msg)
    if not res:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found.")
    return {"status": "success", "task_graph": res.model_dump()}

@router.get("/transitions")
def list_domain_transitions(limit: int = Query(20, ge=1, le=100)):
    handoffs = domain_handoff_manager.handoff_history[-limit:]
    return {
        "status": "success",
        "transitions": [h.model_dump() for h in reversed(handoffs)]
    }

@router.post("/research/synthesis")
def synthesize_multi_domain_research(payload: Dict[str, Any] = Body(...)):
    query = payload.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="Query is required.")
    
    domains = payload.get("domains", ["research"])
    res = research_engine.analyze_research_query(query=query, domains=domains)
    return {
        "status": "success",
        "result": res.model_dump()
    }
