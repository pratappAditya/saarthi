import logging
import time
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.intelligence.routines.routine_model import (
    Routine,
    RoutineStatus,
    RoutineScope,
    TriggerType,
    AutonomyLevel,
    ApprovalPolicy,
    RoutineDefinition
)
from app.intelligence.routines.routine_store import routine_store
from app.intelligence.routines.routine_engine import routine_engine
from app.intelligence.routines.routine_parser import routine_parser
from app.intelligence.routines.routine_templates import (
    ROUTINE_TEMPLATES, instantiate_template, instantiate_unified_template
)
from app.intelligence.routines.routine_notification_engine import routine_notification_engine
from app.intelligence.routines.automation_models import (
    UnifiedAutomation, AutomationStatus, AutomationScope, TriggerKind,
    UnifiedTrigger, DeterministicCondition, ConditionLogic, WorkflowStep
)
from app.intelligence.routines.automation_engine import automation_engine
from app.core.plans import PlanService
from app.core.entitlements import get_current_plan

logger = logging.getLogger("app.api.routine_api")
router = APIRouter(prefix="/routines", tags=["routines"])

class ParseRoutineRequest(BaseModel):
    user_id: Optional[str] = "default_local_user"
    prompt: str
    domain: Optional[str] = "general"

class CreateRoutineRequest(BaseModel):
    user_id: Optional[str] = "default_local_user"
    name: str
    description: Optional[str] = ""
    natural_language_definition: Optional[str] = None
    scope: Optional[str] = "GLOBAL"
    project_id: Optional[str] = None
    domain: Optional[str] = "general"
    trigger_type: Optional[str] = "TIME_TRIGGER"
    schedule: Optional[Dict[str, Any]] = None
    conditions: Optional[List[Dict[str, Any]]] = None
    actions: Optional[List[Dict[str, Any]]] = None
    autonomy_level: Optional[str] = "ASK"
    approval_policy: Optional[str] = "ASK_FOR_EACH_HIGH_RISK_ACTION"
    template_id: Optional[str] = None

class RunRoutineRequest(BaseModel):
    user_id: Optional[str] = "default_local_user"
    permission_granted: Optional[bool] = False

@router.get("")
def list_routines_endpoint(
    user_id: str = "default_local_user",
    scope: Optional[str] = None,
    project_id: Optional[str] = None
):
    routines = routine_store.list_routines(user_id=user_id, scope=scope, project_id=project_id)
    return {"routines": [r.model_dump() for r in routines]}

@router.post("")
def create_routine_endpoint(req: CreateRoutineRequest):
    uid = req.user_id or "default_local_user"
    current_plan = get_current_plan(uid)

    if not PlanService.is_capability_entitled(current_plan, "agents.routines"):
        raise HTTPException(status_code=403, detail=f"Plan '{current_plan.upper()}' lacks capability 'agents.routines'. Upgrade plan to unlock routines.")

    if req.template_id:
        try:
            rtn = instantiate_template(req.template_id, user_id=uid)
            routine_store.create_routine(rtn)
            return {"routine": rtn.model_dump(), "message": f"Routine created from template '{req.template_id}'."}
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    rtn = Routine(
        name=req.name,
        description=req.description or "",
        natural_language_definition=req.natural_language_definition,
        owner_user_id=uid,
        scope=RoutineScope(req.scope.upper()) if req.scope else RoutineScope.GLOBAL,
        project_id=req.project_id,
        domain=req.domain or "general",
        trigger_type=TriggerType(req.trigger_type.upper()) if req.trigger_type else TriggerType.TIME_TRIGGER,
        schedule=req.schedule or {"frequency": "daily", "time_of_day": "09:00"},
        conditions=req.conditions or [],
        actions=req.actions or [],
        autonomy_level=AutonomyLevel(req.autonomy_level.upper()) if req.autonomy_level else AutonomyLevel.ASK,
        approval_policy=ApprovalPolicy(req.approval_policy.upper()) if req.approval_policy else ApprovalPolicy.ASK_FOR_EACH_HIGH_RISK_ACTION,
        enabled=True,
        status=RoutineStatus.ACTIVE
    )
    routine_store.create_routine(rtn)
    return {"routine": rtn.model_dump(), "message": "Routine created successfully."}

@router.get("/templates")
def list_routine_templates_endpoint():
    return {"templates": ROUTINE_TEMPLATES}

@router.post("/parse")
def parse_routine_prompt_endpoint(req: ParseRoutineRequest):
    parsed = routine_parser.parse_prompt(prompt=req.prompt, domain=req.domain or "general")
    return {"parsed_definition": parsed.model_dump()}

@router.get("/upcoming")
def get_upcoming_routines_endpoint(user_id: str = "default_local_user"):
    routines = routine_store.list_routines(user_id=user_id)
    upcoming = []

    for r in routines:
        if r.enabled and r.status == RoutineStatus.ACTIVE and r.next_run_at:
            upcoming.append({
                "routine_id": r.id,
                "name": r.name,
                "trigger_type": r.trigger_type,
                "next_run_at": r.next_run_at,
                "autonomy_level": r.autonomy_level
            })

    upcoming.sort(key=lambda x: x["next_run_at"])
    return {"upcoming": upcoming}

@router.get("/notifications")
def get_routine_notifications_endpoint(user_id: str = "default_local_user"):
    notifs = routine_notification_engine.get_unread_notifications(user_id=user_id)
    return {"notifications": notifs}

class PreviewAutomationRequest(BaseModel):
    prompt: str
    user_id: Optional[str] = "default_local_user"
    domain: Optional[str] = "general"

class CreateUnifiedAutomationRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = ""
    user_id: Optional[str] = "default_local_user"
    organization_id: Optional[str] = None
    scope: Optional[str] = "GLOBAL"
    project_id: Optional[str] = None
    goal_id: Optional[str] = None
    domain: Optional[str] = "general"
    trigger: Optional[Dict[str, Any]] = None
    conditions: Optional[List[Dict[str, Any]]] = None
    steps: Optional[List[Dict[str, Any]]] = None
    schedule: Optional[Dict[str, Any]] = None
    timezone: Optional[str] = "UTC"
    condition_logic: Optional[str] = "AND"
    template_id: Optional[str] = None

class RunUnifiedAutomationRequest(BaseModel):
    user_id: Optional[str] = "default_local_user"
    trigger_source: Optional[str] = "MANUAL"
    approval_token: Optional[str] = None
    permission_granted: Optional[bool] = False

@router.post("/automations/preview")
def preview_automation_endpoint(req: PreviewAutomationRequest):
    preview = routine_parser.parse_automation_preview(
        prompt=req.prompt,
        domain=req.domain or "general",
        user_id=req.user_id or "default_local_user"
    )
    return {"preview": preview.model_dump()}

@router.get("/automations")
def list_automations_endpoint(
    user_id: str = "default_local_user",
    organization_id: Optional[str] = None
):
    autos = automation_engine.list_automations(user_id=user_id, organization_id=organization_id)
    return {"automations": [a.model_dump() for a in autos]}

@router.post("/automations")
def create_automation_endpoint(req: CreateUnifiedAutomationRequest):
    uid = req.user_id or "default_local_user"
    current_plan = get_current_plan(uid)

    if not PlanService.is_capability_entitled(current_plan, "agents.routines"):
        raise HTTPException(
            status_code=403,
            detail=f"Plan '{current_plan.upper()}' lacks capability 'agents.routines'. Upgrade plan to unlock automations."
        )

    if req.template_id:
        try:
            auto = instantiate_unified_template(req.template_id, user_id=uid)
            if req.project_id:
                auto.project_id = req.project_id
            if req.goal_id:
                auto.goal_id = req.goal_id
            if req.organization_id:
                auto.organization_id = req.organization_id
            automation_engine.register_automation(auto)
            return {"automation": auto.model_dump(), "message": f"Automation created from template '{req.template_id}'."}
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    if not req.name:
        raise HTTPException(status_code=400, detail="Automation 'name' is required.")

    trig_dict = req.trigger or {"kind": "TIME", "frequency": "daily", "cron_or_time": "09:00"}
    trigger = UnifiedTrigger(
        kind=TriggerKind(trig_dict.get("kind", "TIME")),
        event_name=trig_dict.get("event_name"),
        cron_or_time=trig_dict.get("cron_or_time"),
        frequency=trig_dict.get("frequency")
    )

    conditions = [
        DeterministicCondition(**c) for c in (req.conditions or [])
    ]
    steps = [
        WorkflowStep(**s) for s in (req.steps or [])
    ]

    auto = UnifiedAutomation(
        name=req.name,
        description=req.description or "",
        user_id=uid,
        organization_id=req.organization_id,
        scope=AutomationScope(req.scope.upper()) if req.scope else AutomationScope.GLOBAL,
        project_id=req.project_id,
        goal_id=req.goal_id,
        domain=req.domain or "general",
        trigger=trigger,
        conditions=conditions,
        condition_logic=ConditionLogic(req.condition_logic.upper()) if req.condition_logic else ConditionLogic.AND,
        steps=steps,
        schedule=req.schedule or {},
        timezone=req.timezone or "UTC",
        enabled=True,
        status=AutomationStatus.ACTIVE
    )
    automation_engine.register_automation(auto)
    return {"automation": auto.model_dump(), "message": "Automation created successfully."}

@router.get("/automations/runs/{run_id}/checkpoints")
def get_automation_checkpoints_endpoint(run_id: str):
    chks = automation_engine.get_checkpoints(run_id)
    return {"run_id": run_id, "checkpoints": [c.model_dump() for c in chks]}

@router.get("/automations/{automation_id}")
def get_automation_endpoint(automation_id: str, user_id: str = "default_local_user"):
    auto = automation_engine.get_automation(automation_id, user_id=user_id)
    if not auto:
        raise HTTPException(status_code=404, detail=f"Automation '{automation_id}' not found or access denied.")
    return {"automation": auto.model_dump()}

@router.delete("/automations/{automation_id}")
def delete_automation_endpoint(automation_id: str, user_id: str = "default_local_user"):
    ok = automation_engine.delete_automation(automation_id, user_id=user_id)
    if not ok:
        raise HTTPException(status_code=404, detail=f"Automation '{automation_id}' not found.")
    return {"deleted": True, "message": f"Automation '{automation_id}' deleted."}

@router.post("/automations/{automation_id}/run")
def run_automation_endpoint(automation_id: str, req: RunUnifiedAutomationRequest):
    uid = req.user_id or "default_local_user"
    try:
        rec = automation_engine.execute_automation(
            automation_id=automation_id,
            trigger_source=req.trigger_source or "MANUAL",
            user_id=uid,
            approval_token=req.approval_token,
            permission_granted=req.permission_granted or False
        )
        return {"run": rec.model_dump(), "message": f"Automation finished with status '{rec.status}'."}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/automations/{automation_id}/pause")
def pause_automation_endpoint(automation_id: str, user_id: str = "default_local_user"):
    ok = automation_engine.pause_automation(automation_id, user_id=user_id)
    if not ok:
        raise HTTPException(status_code=404, detail=f"Automation '{automation_id}' not found.")
    return {"paused": True, "message": f"Automation '{automation_id}' paused."}

@router.post("/automations/{automation_id}/resume")
def resume_automation_endpoint(automation_id: str, user_id: str = "default_local_user"):
    ok = automation_engine.resume_automation(automation_id, user_id=user_id)
    if not ok:
        raise HTTPException(status_code=404, detail=f"Automation '{automation_id}' not found.")
    return {"resumed": True, "message": f"Automation '{automation_id}' resumed."}

@router.post("/automations/{automation_id}/skip")
def skip_automation_next_run_endpoint(automation_id: str, user_id: str = "default_local_user"):
    new_next = automation_engine.skip_next_run(automation_id, user_id=user_id)
    if new_next is None:
        raise HTTPException(status_code=404, detail=f"Automation '{automation_id}' not found or has no schedule.")
    return {"skipped": True, "next_run_at": new_next}

@router.get("/{routine_id}")
def get_routine_endpoint(routine_id: str):
    rtn = routine_store.get_routine(routine_id)
    if not rtn:
        raise HTTPException(status_code=404, detail=f"Routine '{routine_id}' not found.")
    return {"routine": rtn.model_dump()}

@router.patch("/{routine_id}")
def update_routine_endpoint(routine_id: str, updates: Dict[str, Any]):
    rtn = routine_store.get_routine(routine_id)
    if not rtn:
        raise HTTPException(status_code=404, detail=f"Routine '{routine_id}' not found.")

    for k, v in updates.items():
        if hasattr(rtn, k) and v is not None:
            setattr(rtn, k, v)

    routine_store.update_routine(rtn)
    return {"routine": rtn.model_dump(), "message": "Routine updated successfully."}

@router.delete("/{routine_id}")
def delete_routine_endpoint(routine_id: str):
    ok = routine_store.delete_routine(routine_id)
    if not ok:
        raise HTTPException(status_code=404, detail=f"Routine '{routine_id}' not found.")
    return {"deleted": True, "message": f"Routine '{routine_id}' deleted."}

@router.post("/{routine_id}/activate")
def activate_routine_endpoint(routine_id: str):
    ok = routine_store.set_routine_status(routine_id, status=RoutineStatus.ACTIVE, enabled=True)
    if not ok:
        raise HTTPException(status_code=404, detail=f"Routine '{routine_id}' not found.")
    return {"activated": True, "message": f"Routine '{routine_id}' activated."}

@router.post("/{routine_id}/pause")
def pause_routine_endpoint(routine_id: str):
    ok = routine_store.set_routine_status(routine_id, status=RoutineStatus.PAUSED, enabled=False)
    if not ok:
        raise HTTPException(status_code=404, detail=f"Routine '{routine_id}' not found.")
    return {"paused": True, "message": f"Routine '{routine_id}' paused."}

@router.post("/{routine_id}/resume")
def resume_routine_endpoint(routine_id: str):
    ok = routine_store.set_routine_status(routine_id, status=RoutineStatus.ACTIVE, enabled=True)
    if not ok:
        raise HTTPException(status_code=404, detail=f"Routine '{routine_id}' not found.")
    return {"resumed": True, "message": f"Routine '{routine_id}' resumed."}

@router.post("/{routine_id}/run")
def run_routine_manual_endpoint(routine_id: str, req: RunRoutineRequest):
    uid = req.user_id or "default_local_user"
    try:
        exec_res = routine_engine.execute_routine(
            routine_id=routine_id,
            trigger_source="MANUAL_TRIGGER",
            user_id=uid,
            permission_granted=req.permission_granted or False
        )
        return {"execution": exec_res.model_dump(), "message": f"Routine '{routine_id}' execution finished with status '{exec_res.status}'."}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{routine_id}/executions")
def get_routine_executions_endpoint(routine_id: str, limit: int = 50):
    execs = routine_store.list_executions(routine_id=routine_id, limit=limit)
    return {"routine_id": routine_id, "executions": [e.model_dump() for e in execs]}
