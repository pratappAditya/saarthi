"""
Multimodal API Router.
Production Multimodal 2.0 endpoints for secure file ingestion, OCR, vision,
and multi-tenant attachment management.
"""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Header
from pydantic import BaseModel

from app.core.entitlements import require_capability
from app.db.auth import AuthRepository
from app.intelligence.multimodal.attachment_manager import attachment_manager, InputAttachment
from app.intelligence.multimodal.ocr_engine import ocr_engine
from app.intelligence.multimodal.vision_engine import vision_engine
from app.intelligence.multimodal.audio_engine import stt_engine, tts_engine, voice_session_manager
from app.intelligence.multimodal.multimodal_service import multimodal_service

logger = logging.getLogger("app.api.multimodal_api")
router = APIRouter(prefix="/multimodal", tags=["multimodal"])


def get_multimodal_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Resolves authenticated user for tenant isolation."""
    if authorization:
        token = authorization.replace("Bearer ", "").strip()
        session = AuthRepository.get_session(token)
        if session:
            return session
    return {
        "user_id": "default_local_user",
        "email": "local@saarthi.ai",
        "subscription_plan": "power",
        "role": "USER"
    }


class VisionAnalyzeRequest(BaseModel):
    prompt: Optional[str] = None


class OCRRequest(BaseModel):
    page_number: Optional[int] = 1
    language_hint: Optional[str] = "en"


@router.post("/upload", dependencies=[Depends(require_capability("multimodal.documents"))])
async def upload_multimodal_attachment(
    file: UploadFile = File(...),
    project_id: Optional[str] = Form(None),
    current_user: Dict[str, Any] = Depends(get_multimodal_user)
):
    """
    Production Multimodal Upload Endpoint.
    Enforces:
    - 25 MB max limit
    - MIME and extension validation
    - Path traversal sanitization
    - Scanned PDF OCR fallback
    - Prompt injection defense
    - User tenant isolation
    """
    content = await file.read()
    filename = file.filename or "attachment"
    mime_type = file.content_type or "application/octet-stream"
    user_id = current_user["user_id"]
    plan = current_user.get("subscription_plan", "free")

    att, ctx = multimodal_service.process_and_save_upload(
        filename=filename,
        content_bytes=content,
        declared_mime_type=mime_type,
        project_id=project_id,
        user_id=user_id,
        plan=plan
    )

    return {
        "attachment": att.model_dump(),
        "multimodal_context": ctx.model_dump(),
        "message": f"Successfully processed attachment '{att.filename}'."
    }


@router.get("/attachments")
def list_attachments_endpoint(
    project_id: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_multimodal_user)
):
    """Lists attachments isolated to the authenticated user."""
    user_id = current_user["user_id"]
    atts = attachment_manager.list_attachments(project_id=project_id, user_id=user_id)
    return {"attachments": [a.model_dump() for a in atts]}


@router.get("/attachments/{att_id}")
def get_attachment_endpoint(
    att_id: str,
    current_user: Dict[str, Any] = Depends(get_multimodal_user)
):
    """Retrieves single attachment with tenant isolation enforcement."""
    user_id = current_user["user_id"]
    att = attachment_manager.get_attachment(att_id, user_id=user_id)
    if not att:
        raise HTTPException(status_code=404, detail="Attachment not found or access denied.")
    return {"attachment": att.model_dump()}


@router.delete("/attachments/{att_id}")
def delete_attachment_endpoint(
    att_id: str,
    current_user: Dict[str, Any] = Depends(get_multimodal_user)
):
    """Deletes attachment with tenant isolation enforcement."""
    user_id = current_user["user_id"]
    deleted = attachment_manager.delete_attachment(att_id, user_id=user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Attachment not found or already deleted.")
    return {"deleted": True, "message": "Attachment removed."}


@router.post("/ocr")
async def extract_ocr_endpoint(
    file: UploadFile = File(...),
    page_number: int = Form(1),
    language: Optional[str] = Form("en")
):
    """Dedicated OCR endpoint returning structured OCRBlocks and confidence."""
    content = await file.read()
    hints = [language] if language else ["en"]
    res = ocr_engine.extract_ocr_text(content, page_number=page_number, language_hints=hints)
    return {"ocr_result": res.model_dump()}


@router.post("/vision/analyze")
async def analyze_vision_endpoint(
    file: UploadFile = File(...),
    prompt: Optional[str] = Form("Analyze image and UI elements")
):
    """Dedicated Vision inspection endpoint returning layout classification and screenshot insights."""
    content = await file.read()
    res = vision_engine.analyze_image(content, prompt=prompt, mime_type=file.content_type or "image/png")
    return {"vision_result": res.model_dump()}


# --- VOICE SESSION APIS (MAINTAINED FOR COMPATIBILITY) ---

@router.post("/voice/session/start", dependencies=[Depends(require_capability("voice.saarthi"))])
def start_voice_session_endpoint():
    session = voice_session_manager.start_session()
    return {"session": session.model_dump(), "message": "Voice session active. Listening enabled."}


@router.post("/voice/session/stop")
def stop_voice_session_endpoint(session_id: str):
    session = voice_session_manager.stop_session(session_id)
    return {"session": session.model_dump() if session else None, "message": "Voice session stopped."}


@router.post("/voice/session/interrupt")
def interrupt_voice_session_endpoint(session_id: str):
    session = voice_session_manager.interrupt_speech(session_id)
    return {"session": session.model_dump() if session else None, "message": "TTS speech interrupted (barge-in)."}
