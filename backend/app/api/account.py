import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.core.plans import (
    PlanService, CAPABILITIES, PLAN_CATALOG, ALL_PLANS
)
from app.core.entitlements import (
    account_service, usage_service, get_current_plan
)
from app.core.domain_packs import DomainPackService

logger = logging.getLogger("app.api.account")
router = APIRouter(prefix="/account", tags=["account"])

class PlanSwitchRequest(BaseModel):
    plan_id: str

@router.get("/plan")
def get_plan():
    """Returns active subscription plan and pricing catalog."""
    current_plan = get_current_plan()
    sub_data = account_service.get_account_subscription()
    plan_info = PLAN_CATALOG.get(current_plan, PLAN_CATALOG["free"])
    return {
        "subscription": sub_data,
        "active_plan": plan_info,
        "catalog": PLAN_CATALOG
    }

@router.get("/entitlements")
def get_entitlements():
    """Returns boolean capability map for current active plan."""
    current_plan = get_current_plan()
    capabilities = PlanService.get_capabilities_for_plan(current_plan)
    return {
        "plan_id": current_plan,
        "capabilities": capabilities
    }

@router.get("/capabilities")
def get_all_capabilities():
    """Returns comprehensive capability taxonomy, plan entitlements, limits, and domain packs."""
    current_plan = get_current_plan()
    capabilities_map = PlanService.get_capabilities_for_plan(current_plan)
    limits = PlanService.get_limits_for_plan(current_plan)
    domain_packs = DomainPackService.list_domain_packs()

    return {
        "plan_id": current_plan,
        "plan_name": PLAN_CATALOG.get(current_plan, {}).get("name", "Free"),
        "capabilities_taxonomy": CAPABILITIES,
        "entitlements": capabilities_map,
        "limits": limits,
        "domain_packs": domain_packs
    }

@router.get("/usage")
def get_usage():
    """Returns current usage counters and plan limit status."""
    current_plan = get_current_plan()
    limits = PlanService.get_limits_for_plan(current_plan)
    usage = usage_service.get_usage()

    return {
        "plan_id": current_plan,
        "limits": limits,
        "usage": usage
    }

@router.post("/dev-switch-plan")
def dev_switch_plan(req: PlanSwitchRequest):
    """
    Local Development Plan Switcher.
    Allows testing UI and backend capability enforcement across plans.
    """
    plan_id = req.plan_id.lower()
    if plan_id not in ALL_PLANS:
        raise HTTPException(status_code=400, detail=f"Invalid plan ID '{req.plan_id}'. Choose from: {ALL_PLANS}")

    updated_sub = account_service.update_account_plan(plan_id)
    new_capabilities = PlanService.get_capabilities_for_plan(plan_id)
    new_limits = PlanService.get_limits_for_plan(plan_id)

    logger.info(f"Local dev switched active plan to '{plan_id}'")
    return {
        "status": "ok",
        "message": f"Successfully switched active plan to '{plan_id.upper()}'.",
        "subscription": updated_sub,
        "active_plan": PLAN_CATALOG[plan_id],
        "entitlements": new_capabilities,
        "limits": new_limits
    }
