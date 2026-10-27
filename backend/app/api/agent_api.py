import os
import shutil
import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel, Field

from app.agent.orchestrator import AgentOrchestrator
from app.agent.scheduler import TaskScheduler
from app.intelligence.agents.agent_runtime import agent_runtime
from app.intelligence.planning.planner import planner_service
from app.intelligence.planning.task_store import task_store
from app.intelligence.permissions.permission_engine import permission_engine
from app.intelligence.permissions.permission_models import PermissionStatus
from app.tools.document_engine import DocumentEngine
from app.api.auth import get_current_user
from app.config.settings import settings

logger = logging.getLogger("app.api.agent_api")
router = APIRouter(prefix="/agent", tags=["Agent & Automation"])


class CreateTaskRequest(BaseModel):
    prompt: str
    title: Optional[str] = None
    domain: Optional[str] = "general"


class RunAgentRequest(BaseModel):
    prompt: str
    agent_id: Optional[str] = "general"
    task_id: Optional[str] = None
    approval_token: Optional[str] = None
    max_steps: Optional[int] = 20


class ApprovalResponseRequest(BaseModel):
    approved: bool


class ScheduleJobRequest(BaseModel):
    prompt: str
    schedule_type: str = "ONE_TIME"  # "ONE_TIME" or "RECURRING_WEEKLY"
    delay_seconds: int = 3600
    cron_day: Optional[str] = "Monday"


class ExportDocRequest(BaseModel):
    content: str
    output_filename: str = "resume_export.txt"


class RollbackRequest(BaseModel):
    checkpoint_id: str


# ------------------ Core Agent Task Endpoints ------------------

@router.post("/tasks")
def create_agent_task(req: CreateTaskRequest, user: Dict[str, Any] = Depends(get_current_user)):
    task = AgentOrchestrator.create_task(user["user_id"], req.prompt, req.title)
    return {"status": "success", "task": task}


@router.get("/tasks")
def list_agent_tasks(user: Dict[str, Any] = Depends(get_current_user)):
    tasks = task_store.list_tasks(user["user_id"])
    if not tasks:
        tasks = AgentOrchestrator.list_user_tasks(user["user_id"])
    return {"tasks": tasks}


@router.get("/tasks/{task_id}")
def get_task_details(task_id: str, user: Dict[str, Any] = Depends(get_current_user)):
    task = task_store.get_task(task_id)
    if not task:
        task = AgentOrchestrator.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    return {"task": task}


@router.post("/run")
def run_autonomous_agent(req: RunAgentRequest, user: Dict[str, Any] = Depends(get_current_user)):
    """
    Executes or resumes an autonomous multi-step agent workflow:
    OBSERVE -> PLAN -> PERMISSION -> ACT -> VERIFY -> REPLAN
    """
    res = agent_runtime.run_agent(
        agent_id=req.agent_id or "general",
        task_prompt=req.prompt,
        user_id=user["user_id"],
        task_id=req.task_id,
        approval_token=req.approval_token,
        max_steps=req.max_steps
    )
    return res


@router.post("/tasks/{task_id}/pause")
def pause_agent_task(task_id: str, user: Dict[str, Any] = Depends(get_current_user)):
    success = agent_runtime.pause_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found or could not be paused.")
    return {"status": "success", "task_id": task_id, "state": "paused"}


@router.post("/tasks/{task_id}/resume")
def resume_agent_task(
    task_id: str,
    approval_token: Optional[str] = None,
    user: Dict[str, Any] = Depends(get_current_user)
):
    res = agent_runtime.resume_task(
        task_id=task_id,
        user_id=user["user_id"],
        approval_token=approval_token
    )
    return res


@router.post("/tasks/{task_id}/cancel")
def cancel_agent_task(task_id: str, user: Dict[str, Any] = Depends(get_current_user)):
    success = agent_runtime.cancel_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found or could not be cancelled.")
    return {"status": "success", "task_id": task_id, "state": "cancelled"}


@router.get("/tasks/{task_id}/checkpoints")
def list_task_checkpoints(task_id: str, user: Dict[str, Any] = Depends(get_current_user)):
    checkpoints = task_store.get_checkpoints(task_id)
    return {"task_id": task_id, "checkpoints": checkpoints}


@router.post("/tasks/{task_id}/rollback")
def rollback_task_checkpoint(
    task_id: str,
    req: RollbackRequest,
    user: Dict[str, Any] = Depends(get_current_user)
):
    res = agent_runtime.rollback_to_checkpoint(task_id, req.checkpoint_id)
    if not res:
        raise HTTPException(status_code=400, detail="Checkpoint not found or rollback failed.")
    return {"status": "success", "task_id": task_id, "rolled_back_to": req.checkpoint_id, "task": res}


@router.get("/tasks/{task_id}/verification")
def get_task_verification_trace(task_id: str, user: Dict[str, Any] = Depends(get_current_user)):
    task = task_store.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    steps = task.get("steps", [])
    verification_items = []
    for s in steps:
        verification_items.append({
            "step_id": s.get("step_id"),
            "title": s.get("title"),
            "status": s.get("status"),
            "verification_state": s.get("verification_state", "unverified"),
            "verification_reason": s.get("verification_reason"),
            "verification_evidence": s.get("verification_evidence", {}),
            "step_type": s.get("step_type", "ACTION")
        })
    return {"task_id": task_id, "verification_trace": verification_items}


# ------------------ Approvals & Permissions ------------------

@router.post("/approvals/{approval_id}")
def respond_approval(approval_id: str, req: ApprovalResponseRequest, user: Dict[str, Any] = Depends(get_current_user)):
    # 1. Update permission_engine if database permission request
    perm = permission_engine.get_permission_request(approval_id)
    if perm:
        if req.approved:
            res_perm = permission_engine.grant_permission(approval_id)
        else:
            res_perm = permission_engine.deny_permission(approval_id)
        return {
            "status": "success",
            "approval_id": approval_id,
            "decision": "APPROVED" if req.approved else "DENIED",
            "permission": res_perm.model_dump() if res_perm else None
        }

    # 2. Fallback to task_approvals table if created by legacy orchestrator
    try:
        res = AgentOrchestrator.respond_to_approval(approval_id, req.approved)
        return {"status": "success", "approval": res}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ------------------ Scheduler & Documents ------------------

@router.post("/schedule")
def schedule_job(req: ScheduleJobRequest, user: Dict[str, Any] = Depends(get_current_user)):
    job = TaskScheduler.create_scheduled_job(
        user_id=user["user_id"],
        prompt=req.prompt,
        schedule_type=req.schedule_type,
        delay_seconds=req.delay_seconds,
        cron_day=req.cron_day
    )
    return {"status": "success", "job": job}


@router.get("/schedule")
def list_scheduled_jobs(user: Dict[str, Any] = Depends(get_current_user)):
    jobs = TaskScheduler.list_jobs(user["user_id"])
    return {"jobs": jobs}


@router.post("/documents/parse")
async def parse_uploaded_document(file: UploadFile = File(...), user: Dict[str, Any] = Depends(get_current_user)):
    temp_dir = os.path.join(settings.SAARTHI_DATA_DIR, "uploads")
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, file.filename)
    
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    parsed = DocumentEngine.parse_document(temp_path)
    return {"status": "success", "parsed_document": parsed}


@router.post("/documents/export")
def export_document(req: ExportDocRequest, user: Dict[str, Any] = Depends(get_current_user)):
    out_dir = os.path.join(settings.SAARTHI_DATA_DIR, "exports")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, req.output_filename)
    res = DocumentEngine.export_document(req.content, out_path, plan=user["subscription_plan"])
    return res
