"""
Proactive REST API Endpoints (Phase 8 - Proactive Saarthi 2.0).
Provides REST endpoints for suggestions, categorized feeds, acceptance/dismissal,
snoozing, safe execution, and user-controlled settings (quiet hours, categories, anti-fatigue).
"""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel

from app.core.entitlements import require_capability
from app.intelligence.proactive.proactive_engine import proactive_engine
from app.intelligence.proactive.goal_system import goal_system
from app.intelligence.proactive.routine_manager import routine_manager
from app.intelligence.proactive.proactive_models import UserProactiveSettings

logger = logging.getLogger("app.api.proactive_api")
router = APIRouter(prefix="/proactive", tags=["proactive"])


# --- Request & Response Models ---

class GoalCreateRequest(BaseModel):
    title: str
    domain: Optional[str] = "general"
    milestones: Optional[List[str]] = None
    recommended_next_action: Optional[str] = ""


class RoutineCreateRequest(BaseModel):
    name: str
    trigger_type: Optional[str] = "scheduled"
    cron_expression: Optional[str] = "0 9 * * *"
    domain: Optional[str] = "general"
    tool_id: Optional[str] = "file.read"
    arguments: Optional[Dict[str, Any]] = None


class SnoozeRequest(BaseModel):
    minutes: int = 60


class ExecuteActionRequest(BaseModel):
    approval_token: Optional[str] = None
    session_id: Optional[str] = "default_session"


class SettingsUpdateRequest(BaseModel):
    enabled: Optional[bool] = None
    frequency: Optional[str] = None
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    voice_notifications_enabled: Optional[bool] = None
    desktop_notifications_enabled: Optional[bool] = None
    enabled_categories: Optional[Dict[str, bool]] = None
    disabled_types: Optional[List[str]] = None


class DisableCategoryRequest(BaseModel):
    category: str


# --- Proactive Suggestions & Feed Endpoints ---

@router.get("/suggestions", dependencies=[Depends(require_capability("agents.proactive"))])
def list_suggestions_endpoint(active_domain: Optional[str] = "general", user_id: str = "default_local_user"):
    sugs = proactive_engine.detect_opportunities(user_id=user_id, active_domain=active_domain or "general")
    return {"suggestions": [s.model_dump() for s in sugs]}


@router.get("/feed", dependencies=[Depends(require_capability("agents.proactive"))])
def get_proactive_feed_endpoint(active_domain: Optional[str] = "general", user_id: str = "default_local_user"):
    feed = proactive_engine.get_proactive_feed(user_id=user_id, active_domain=active_domain or "general")
    return {
        "status": "success",
        "feed": {cat: [item.model_dump() for item in items] for cat, items in feed.items()}
    }


@router.post("/suggestions/{sug_id}/accept")
def accept_suggestion_endpoint(sug_id: str, user_id: str = "default_local_user"):
    sug = proactive_engine.accept_suggestion(sug_id, user_id=user_id)
    if not sug:
        raise HTTPException(status_code=404, detail="Suggestion not found.")
    return {"suggestion": sug.model_dump(), "message": "Suggestion accepted."}


@router.post("/suggestions/{sug_id}/dismiss")
def dismiss_suggestion_endpoint(sug_id: str, user_id: str = "default_local_user"):
    sug = proactive_engine.dismiss_suggestion(sug_id, user_id=user_id)
    if not sug:
        raise HTTPException(status_code=404, detail="Suggestion not found.")
    return {"suggestion": sug.model_dump(), "message": "Suggestion dismissed."}


@router.post("/suggestions/{sug_id}/snooze")
def snooze_suggestion_endpoint(sug_id: str, req: SnoozeRequest, user_id: str = "default_local_user"):
    sug = proactive_engine.snooze_suggestion(sug_id, minutes=req.minutes, user_id=user_id)
    if not sug:
        raise HTTPException(status_code=404, detail="Suggestion not found.")
    return {"suggestion": sug.model_dump(), "message": f"Suggestion snoozed for {req.minutes} minutes."}


@router.post("/suggestions/{sug_id}/execute")
def execute_suggestion_endpoint(sug_id: str, req: ExecuteActionRequest, user_id: str = "default_local_user"):
    res = proactive_engine.execute_suggestion_action(
        suggestion_id=sug_id,
        user_id=user_id,
        session_id=req.session_id or "default_session",
        approval_token=req.approval_token
    )
    return res


# --- User Controls & Settings Endpoints ---

@router.get("/settings", dependencies=[Depends(require_capability("agents.proactive"))])
def get_settings_endpoint(user_id: str = "default_local_user"):
    settings = proactive_engine.get_settings(user_id=user_id)
    return {"settings": settings.model_dump()}


@router.put("/settings", dependencies=[Depends(require_capability("agents.proactive"))])
def update_settings_endpoint(req: SettingsUpdateRequest, user_id: str = "default_local_user"):
    updated = proactive_engine.update_settings(user_id=user_id, new_settings=req.model_dump(exclude_unset=True))
    return {"settings": updated.model_dump(), "message": "Proactive settings updated."}


@router.post("/settings/disable-category", dependencies=[Depends(require_capability("agents.proactive"))])
def disable_category_endpoint(req: DisableCategoryRequest, user_id: str = "default_local_user"):
    updated = proactive_engine.disable_category(user_id=user_id, category=req.category)
    return {"settings": updated.model_dump(), "message": f"Category '{req.category}' disabled."}


# --- Goal Endpoints ---

@router.get("/goals", dependencies=[Depends(require_capability("career.goals"))])
def list_goals_endpoint(user_id: str = "default_local_user"):
    goals = goal_system.list_goals(user_id=user_id)
    return {"goals": [g.model_dump() for g in goals]}


@router.post("/goals", dependencies=[Depends(require_capability("career.goals"))])
def create_goal_endpoint(req: GoalCreateRequest, user_id: str = "default_local_user"):
    goal = goal_system.create_goal(
        title=req.title,
        domain=req.domain or "general",
        user_id=user_id,
        milestones=req.milestones,
        recommended_next_action=req.recommended_next_action or ""
    )
    return {"goal": goal.model_dump(), "message": f"Created goal '{req.title}'."}


# --- Routine Endpoints ---

@router.get("/routines", dependencies=[Depends(require_capability("agents.background"))])
def list_routines_endpoint(user_id: str = "default_local_user"):
    routines = routine_manager.list_routines()
    return {"routines": [r.model_dump() for r in routines]}


@router.post("/routines", dependencies=[Depends(require_capability("agents.background"))])
def create_routine_endpoint(req: RoutineCreateRequest, user_id: str = "default_local_user"):
    routine = routine_manager.create_routine(
        name=req.name,
        trigger_type=req.trigger_type or "scheduled",
        cron_expression=req.cron_expression or "0 9 * * *",
        domain=req.domain or "general",
        user_id=user_id,
        tool_id=req.tool_id or "file.read",
        arguments=req.arguments or {}
    )
    return {"routine": routine.model_dump(), "message": f"Created routine '{req.name}'."}
