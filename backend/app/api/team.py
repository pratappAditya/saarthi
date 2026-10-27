from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from app.api.auth import get_current_user
from app.services.team_service import TeamService

router = APIRouter(prefix="/team", tags=["Team & Organizations"])

class CreateOrgRequest(BaseModel):
    name: str
    plan_name: Optional[str] = "TEAMS"
    seat_limit: Optional[int] = 5

class InviteMemberRequest(BaseModel):
    email: str
    role: Optional[str] = "MEMBER"

class AcceptInviteRequest(BaseModel):
    token: str

class UpdateRoleRequest(BaseModel):
    role: str

class UpdateSeatsRequest(BaseModel):
    seat_limit: int

@router.post("/create")
def create_organization(req: CreateOrgRequest, user: Dict[str, Any] = Depends(get_current_user)):
    return TeamService.create_organization(
        owner_id=user["user_id"],
        name=req.name,
        plan_name=req.plan_name or "TEAMS",
        seat_limit=req.seat_limit or 5
    )

@router.get("/my-orgs")
def get_my_organizations(user: Dict[str, Any] = Depends(get_current_user)):
    return {"organizations": TeamService.get_user_organizations(user["user_id"])}

@router.get("/{org_id}")
def get_organization_details(org_id: str, user: Dict[str, Any] = Depends(get_current_user)):
    return TeamService.get_organization_details(org_id, user["user_id"])

@router.post("/{org_id}/invite")
def invite_member(org_id: str, req: InviteMemberRequest, user: Dict[str, Any] = Depends(get_current_user)):
    return TeamService.invite_member(
        org_id=org_id,
        actor_id=user["user_id"],
        email=req.email,
        role=req.role or "MEMBER"
    )

@router.post("/accept-invite")
def accept_invitation(req: AcceptInviteRequest, user: Dict[str, Any] = Depends(get_current_user)):
    return TeamService.accept_invitation(token=req.token, user_id=user["user_id"])

@router.delete("/{org_id}/members/{target_user_id}")
def remove_member(org_id: str, target_user_id: str, user: Dict[str, Any] = Depends(get_current_user)):
    success = TeamService.remove_member(org_id=org_id, actor_id=user["user_id"], target_user_id=target_user_id)
    return {"status": "success", "message": "Member removed from organization."}

@router.patch("/{org_id}/members/{target_user_id}/role")
def update_member_role(org_id: str, target_user_id: str, req: UpdateRoleRequest, user: Dict[str, Any] = Depends(get_current_user)):
    success = TeamService.update_member_role(org_id=org_id, actor_id=user["user_id"], target_user_id=target_user_id, new_role=req.role)
    return {"status": "success", "message": f"Member role updated to {req.role}."}

@router.patch("/{org_id}/seats")
def update_seat_limit(org_id: str, req: UpdateSeatsRequest, user: Dict[str, Any] = Depends(get_current_user)):
    return TeamService.update_seat_limit(org_id=org_id, actor_id=user["user_id"], new_seat_limit=req.seat_limit)
