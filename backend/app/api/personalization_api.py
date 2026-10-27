import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.intelligence.personalization.personalization_engine import personalization_engine
from app.intelligence.personalization.personalization_store import personalization_store
from app.intelligence.personalization.personalization_model import ExpertiseLevel

logger = logging.getLogger("app.api.personalization_api")
router = APIRouter(prefix="/personalization", tags=["personalization"])

class ProfileUpdateRequest(BaseModel):
    user_id: Optional[str] = "default_local_user"
    communication_style: Optional[str] = None
    preferred_response_length: Optional[str] = None
    technical_depth: Optional[str] = None
    preferred_languages: Optional[List[str]] = None
    preferred_tone: Optional[str] = None
    preferred_formatting: Optional[str] = None
    decision_making_style: Optional[str] = None
    autonomy_preference: Optional[str] = None
    confirmation_preference: Optional[str] = None
    proactivity_preference: Optional[str] = None
    preferred_working_hours: Optional[str] = None
    explicit_preferences: Optional[Dict[str, Any]] = None

class ExplicitPreferenceRequest(BaseModel):
    user_id: Optional[str] = "default_local_user"
    key: str
    value: Any
    category: Optional[str] = "general"

class ConfirmRejectRequest(BaseModel):
    user_id: Optional[str] = "default_local_user"
    key: str

class ResetRequest(BaseModel):
    user_id: Optional[str] = "default_local_user"
    category: Optional[str] = None # None means reset all

class DomainExpertiseRequest(BaseModel):
    user_id: Optional[str] = "default_local_user"
    domain: str
    level: str # novice, intermediate, advanced, expert
    confidence: Optional[float] = 1.0

class ProjectOverrideRequest(BaseModel):
    user_id: Optional[str] = "default_local_user"
    project_id: str
    key: str
    value: Any

class SettingsUpdateRequest(BaseModel):
    user_id: Optional[str] = "default_local_user"
    personalization_enabled: Optional[bool] = None
    learning_enabled: Optional[bool] = None
    inference_enabled: Optional[bool] = None
    proactive_learning_enabled: Optional[bool] = None
    voice_personalization_enabled: Optional[bool] = None

@router.get("/profile")
def get_personalization_profile_endpoint(user_id: str = "default_local_user"):
    profile = personalization_store.get_profile(user_id)
    return {"profile": profile.model_dump()}

@router.patch("/profile")
def update_personalization_profile_endpoint(req: ProfileUpdateRequest):
    uid = req.user_id or "default_local_user"
    profile = personalization_store.get_profile(uid)

    for field, val in req.model_dump(exclude_unset=True).items():
        if field != "user_id" and val is not None:
            setattr(profile, field, val)

    personalization_store.save_profile(profile)
    return {"profile": profile.model_dump(), "message": "Personalization profile updated."}

@router.post("/preference/explicit")
def set_explicit_preference_endpoint(req: ExplicitPreferenceRequest):
    uid = req.user_id or "default_local_user"
    item = personalization_store.set_explicit_preference(
        user_id=uid,
        key=req.key,
        value=req.value,
        category=req.category or "general"
    )
    return {"preference": item.model_dump(), "message": f"Explicit preference '{req.key}' set."}

@router.get("/learned")
def get_learned_preferences_endpoint(user_id: str = "default_local_user"):
    profile = personalization_store.get_profile(user_id)
    learned = [p.model_dump() for p in profile.inferred_preferences.values() if not p.rejected]
    return {"learned_preferences": learned}

@router.post("/confirm")
def confirm_preference_endpoint(req: ConfirmRejectRequest):
    uid = req.user_id or "default_local_user"
    ok = personalization_store.confirm_preference(uid, req.key)
    if not ok:
        raise HTTPException(status_code=404, detail="Preference not found.")
    return {"confirmed": True, "message": f"Preference '{req.key}' confirmed."}

@router.post("/reject")
def reject_preference_endpoint(req: ConfirmRejectRequest):
    uid = req.user_id or "default_local_user"
    ok = personalization_store.reject_preference(uid, req.key)
    if not ok:
        raise HTTPException(status_code=404, detail="Preference not found.")
    return {"rejected": True, "message": f"Preference '{req.key}' rejected."}

@router.delete("/preference")
def forget_preference_endpoint(key: str, user_id: str = "default_local_user"):
    ok = personalization_store.forget_preference(user_id, key)
    if not ok:
        raise HTTPException(status_code=404, detail="Preference not found.")
    return {"forgotten": True, "message": f"Preference '{key}' forgotten."}

@router.post("/reset")
def reset_personalization_endpoint(req: ResetRequest):
    uid = req.user_id or "default_local_user"
    if req.category:
        personalization_store.reset_category(uid, req.category)
        msg = f"Reset personalization category '{req.category}'."
    else:
        personalization_store.reset_all(uid)
        msg = "Reset all personalization data."
    return {"reset": True, "message": msg}

@router.get("/explain")
def explain_personalization_endpoint(
    domain: str = "general",
    project_id: Optional[str] = None,
    user_id: str = "default_local_user"
):
    ctx = personalization_engine.build_personalization_context(
        user_id=user_id,
        domain=domain,
        project_id=project_id
    )
    return {"explanation": personalization_engine.explain_personalization(ctx)}

@router.get("/expertise")
def get_domain_expertise_endpoint(user_id: str = "default_local_user"):
    profile = personalization_store.get_profile(user_id)
    exp_map = {k: v.model_dump() for k, v in profile.domain_expertise.items()}
    return {"expertise": exp_map}

@router.post("/expertise")
def set_domain_expertise_endpoint(req: DomainExpertiseRequest):
    uid = req.user_id or "default_local_user"
    try:
        level_enum = ExpertiseLevel(req.level.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid expertise level '{req.level}'. Must be novice, intermediate, advanced, or expert.")

    exp = personalization_store.set_domain_expertise(
        user_id=uid,
        domain=req.domain,
        level=level_enum,
        confidence=req.confidence or 1.0,
        evidence="Explicit user override in Personalization Dashboard",
        explicit_override=True
    )
    return {"expertise": exp.model_dump(), "message": f"Updated expertise for domain '{req.domain}' to '{req.level}'."}

@router.get("/project")
def get_project_overrides_endpoint(project_id: str, user_id: str = "default_local_user"):
    overrides = personalization_store.get_project_overrides(user_id, project_id)
    return {"project_id": project_id, "overrides": overrides}

@router.post("/project")
def set_project_override_endpoint(req: ProjectOverrideRequest):
    uid = req.user_id or "default_local_user"
    personalization_store.set_project_override(uid, req.project_id, req.key, req.value)
    return {"project_id": req.project_id, "key": req.key, "value": req.value, "message": "Project override set."}

@router.get("/settings")
def get_personalization_settings_endpoint(user_id: str = "default_local_user"):
    profile = personalization_store.get_profile(user_id)
    return {
        "personalization_enabled": profile.personalization_enabled,
        "learning_enabled": profile.learning_enabled,
        "inference_enabled": profile.inference_enabled,
        "proactive_learning_enabled": profile.proactive_learning_enabled,
        "voice_personalization_enabled": profile.voice_personalization_enabled
    }

@router.post("/settings")
def update_personalization_settings_endpoint(req: SettingsUpdateRequest):
    uid = req.user_id or "default_local_user"
    profile = personalization_store.get_profile(uid)

    if req.personalization_enabled is not None:
        profile.personalization_enabled = req.personalization_enabled
    if req.learning_enabled is not None:
        profile.learning_enabled = req.learning_enabled
    if req.inference_enabled is not None:
        profile.inference_enabled = req.inference_enabled
    if req.proactive_learning_enabled is not None:
        profile.proactive_learning_enabled = req.proactive_learning_enabled
    if req.voice_personalization_enabled is not None:
        profile.voice_personalization_enabled = req.voice_personalization_enabled

    personalization_store.save_profile(profile)
    return {
        "settings": {
            "personalization_enabled": profile.personalization_enabled,
            "learning_enabled": profile.learning_enabled,
            "inference_enabled": profile.inference_enabled,
            "proactive_learning_enabled": profile.proactive_learning_enabled,
            "voice_personalization_enabled": profile.voice_personalization_enabled
        },
        "message": "Personalization settings updated."
    }

# --- Phase 6 Deep Memory & Inspection Endpoints ---

from app.intelligence.memory.memory_manager import memory_manager

class MemoryCommandRequest(BaseModel):
    user_id: Optional[str] = "default_local_user"
    command: str
    project_id: Optional[str] = None
    domain: Optional[str] = "general"

class MemoryCorrectRequest(BaseModel):
    user_id: Optional[str] = "default_local_user"
    memory_id: int
    new_content: str

class MultimodalMemoryRequest(BaseModel):
    user_id: Optional[str] = "default_local_user"
    content: str
    source_doc: str
    project_id: Optional[str] = None
    confirmed_by_user: Optional[bool] = False

@router.get("/what-saarthi-knows")
def what_saarthi_knows_endpoint(
    user_id: str = "default_local_user",
    project_id: Optional[str] = None,
    scope: Optional[str] = None,
    domain: Optional[str] = None
):
    """
    Transparent 'What Saarthi Knows' inspector returning itemized provenance,
    scopes, confidence, and timestamps.
    """
    items = memory_manager.what_saarthi_knows(
        user_id=user_id,
        project_id=project_id,
        scope=scope,
        domain=domain
    )
    return {"items": items, "count": len(items)}

@router.post("/command")
def process_memory_command_endpoint(req: MemoryCommandRequest):
    """Processes natural language memory directives ('Remember...', 'Forget...', 'What do you know...')."""
    uid = req.user_id or "default_local_user"
    result = memory_manager.process_memory_command(
        command_text=req.command,
        user_id=uid,
        project_id=req.project_id,
        domain=req.domain or "general"
    )
    if not result:
        return {"processed": False, "response": "Could not recognize a standard memory directive."}
    return {"processed": True, "result": result}

@router.post("/correct")
def correct_memory_endpoint(req: MemoryCorrectRequest):
    """Allows user to correct a remembered fact or preference explicitly."""
    uid = req.user_id or "default_local_user"
    updated = memory_manager.correct_memory(
        memory_id=req.memory_id,
        new_content=req.new_content,
        user_id=uid
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Memory item not found.")
    return {"corrected": True, "memory": updated.model_dump(), "message": "Memory item updated."}

@router.delete("/project/{project_id}")
def clear_project_memory_endpoint(project_id: str, user_id: str = "default_local_user"):
    """Purges all project-scoped memories for a specific project."""
    count = memory_manager.clear_project_memory(project_id=project_id, user_id=user_id)
    return {"deleted_count": count, "message": f"Cleared {count} project memories for '{project_id}'."}

@router.post("/multimodal")
def create_multimodal_memory_endpoint(req: MultimodalMemoryRequest):
    """Ingests memory from documents or multimodal sources with SOURCE_DERIVED provenance."""
    uid = req.user_id or "default_local_user"
    mem = memory_manager.create_multimodal_memory(
        content=req.content,
        source_doc=req.source_doc,
        user_id=uid,
        project_id=req.project_id,
        confirmed_by_user=req.confirmed_by_user or False
    )
    return {"memory": mem.model_dump(), "message": "Multimodal memory registered."}

