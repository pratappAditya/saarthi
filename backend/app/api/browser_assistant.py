from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.db.profile import ProfileRepository

router = APIRouter(prefix="/browser-assistant", tags=["browser-assistant"])

class UserProfileRequest(BaseModel):
    full_name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    education: List[Dict[str, Any]] = []
    skills: List[str] = []
    experience: List[Dict[str, Any]] = []
    projects: List[Dict[str, Any]] = []
    links: Dict[str, str] = {}
    work_authorization: str = "Authorized to work"
    notice_period_days: int = 0
    preferred_locations: List[str] = []

class FormFieldDescriptor(BaseModel):
    field_id: str
    label: str
    field_type: str = "text"
    placeholder: Optional[str] = ""

class DetectFieldsRequest(BaseModel):
    url: str
    fields: List[FormFieldDescriptor]

class ConfirmFillRequest(BaseModel):
    field_values: Dict[str, str]
    confirmed_by_user: bool = False

@router.get("/profile")
def get_profile_endpoint():
    return ProfileRepository.get_profile()

@router.put("/profile")
def update_profile_endpoint(req: UserProfileRequest):
    updated = ProfileRepository.save_profile(req.model_dump())
    return {"profile": updated, "message": "User profile updated successfully."}

@router.post("/detect-fields")
def detect_fields_endpoint(req: DetectFieldsRequest):
    profile = ProfileRepository.get_profile()
    suggestions = []

    for f in req.fields:
        label_lower = (f.label + " " + f.field_id + " " + (f.placeholder or "")).lower()
        suggested_val = ""
        fact_source = "AI SUGGESTION"

        if any(k in label_lower for k in ["name", "full name", "applicant_name", "first name", "last name"]):
            suggested_val = profile.get("full_name", "")
            fact_source = "USER-PROVIDED FACT" if suggested_val else "AI SUGGESTION"
        elif any(k in label_lower for k in ["email", "email_address", "mail"]):
            suggested_val = profile.get("email", "")
            fact_source = "USER-PROVIDED FACT" if suggested_val else "AI SUGGESTION"
        elif any(k in label_lower for k in ["phone", "mobile", "contact", "tel"]):
            suggested_val = profile.get("phone", "")
            fact_source = "USER-PROVIDED FACT" if suggested_val else "AI SUGGESTION"
        elif any(k in label_lower for k in ["location", "city", "address"]):
            suggested_val = profile.get("location", "")
            fact_source = "STORED PROFILE FACT" if suggested_val else "AI SUGGESTION"
        elif any(k in label_lower for k in ["skill", "technologies"]):
            suggested_val = ", ".join(profile.get("skills", []))
            fact_source = "STORED PROFILE FACT" if suggested_val else "AI SUGGESTION"
        elif any(k in label_lower for k in ["notice", "joining"]):
            suggested_val = f"{profile.get('notice_period_days', 0)} days"
            fact_source = "STORED PROFILE FACT" if suggested_val else "AI SUGGESTION"
        elif any(k in label_lower for k in ["work auth", "authorization", "visa"]):
            suggested_val = profile.get("work_authorization", "Authorized to work")
            fact_source = "STORED PROFILE FACT" if suggested_val else "AI SUGGESTION"
        elif any(k in label_lower for k in ["github", "portfolio", "linkedin", "link"]):
            links = profile.get("links", {})
            suggested_val = links.get("github") or links.get("linkedin") or links.get("portfolio", "")
            fact_source = "STORED PROFILE FACT" if suggested_val else "AI SUGGESTION"

        suggestions.append({
            "field_id": f.field_id,
            "label": f.label,
            "suggested_value": suggested_val,
            "fact_source": fact_source,
            "requires_user_confirmation": True
        })

    return {
        "url": req.url,
        "matched_fields": suggestions,
        "policy": "Explicit user confirmation required for all field filling. Autonomous submit, CAPTCHA bypass, and anti-bot evasion are strictly disabled."
    }

@router.post("/confirm-fill")
def confirm_fill_endpoint(req: ConfirmFillRequest):
    if not req.confirmed_by_user:
        raise HTTPException(
            status_code=400,
            detail="Action rejected: Explicit user confirmation is required before filling job application fields."
        )

    return {
        "status": "APPROVED",
        "filled_fields_count": len(req.field_values),
        "field_instructions": req.field_values,
        "auto_submit_executed": False,
        "message": "Fields populated successfully. User must review and submit the application manually."
    }
