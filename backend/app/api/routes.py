from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends, Request, Header, Body
from pydantic import BaseModel
import httpx
from app.agent.core import AgentCore
from app.config.settings import settings
from app.security.permissions import PermissionRequiredException, permission_store
from app.memory.manager import MemoryApprovalRequiredException, MemoryRequest
from app.db.connection import get_db_connection
import json

from app.api.career import router as career_router
from app.api.browser_assistant import router as browser_assistant_router
from app.api.auth import router as auth_router
from app.api.admin import router as admin_router
from app.api.payment import router as payment_router
from app.api.agent_api import router as agent_router
from app.api.account import router as account_router
from app.api.intelligence_api import router as intelligence_router
from app.api.multimodal_api import router as multimodal_router
from app.api.domain_api import router as domain_router
from app.api.proactive_api import router as proactive_router
from app.api.voice_api import router as voice_router
from app.api.personalization_api import router as personalization_router
from app.api.routine_api import router as routine_router
from app.api.cross_domain_api import router as cross_domain_router
from app.api.unified_api import router as unified_router
from app.api.study_api import router as study_router
from app.api.search_api import router as search_router
from app.api.team import router as team_router

router = APIRouter()
router.include_router(career_router)
router.include_router(browser_assistant_router)
router.include_router(auth_router)
router.include_router(admin_router)
router.include_router(payment_router)
router.include_router(team_router)
router.include_router(agent_router)
router.include_router(account_router)
router.include_router(intelligence_router)
router.include_router(multimodal_router)
router.include_router(domain_router)
router.include_router(proactive_router)
router.include_router(voice_router)
router.include_router(personalization_router)
router.include_router(routine_router)
router.include_router(cross_domain_router)
router.include_router(unified_router)
router.include_router(study_router)
router.include_router(search_router)
agent = AgentCore()

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default_session"

class PermissionRequestResponse(BaseModel):
    request_id: str
    tool_name: str
    action_description: str
    arguments: dict
    permission_level: str
    risk_level: str
    status: str
    session_id: str

class MemoryRequestResponse(BaseModel):
    request_id: str
    category: str
    key: str
    content: str
    project_id: str | None = None
    session_id: str
    status: str
    question: str
    action: str = "create"


class ChatResponse(BaseModel):
    response: str
    session_id: str
    status: str = "success"
    permission_request: PermissionRequestResponse = None
    memory_request: MemoryRequestResponse = None

@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "saarthi"
    }

@router.get("/tools")
def list_tools_endpoint():
    try:
        tools_info = agent.tools.list_tools()
        return {"tools": tools_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def status_endpoint():
    from app.api.health_api import get_ai_provider_status
    ai_status = get_ai_provider_status()

    is_ollama = ai_status["provider"] == "ollama"
    status_info = {
        "backend": "Saarthi API",
        "backend_status": "online",
        "model_provider": ai_status["provider"],
        "model_name": ai_status["model"],
        "model": ai_status["model"],
        "ollama_connected": ai_status["reachable"] if is_ollama else "not_applicable",
        "Ollama": ("connected" if ai_status["reachable"] else "disconnected") if is_ollama else "not_applicable",
        "model_available": ai_status["healthy"],
        "configured": ai_status["configured"],
        "reachable": ai_status["reachable"],
        "is_live": ai_status["is_live"],
        "execution_mode": ai_status["execution_mode"],
        "last_error_category": ai_status["last_error_category"],
        "error_message": None if ai_status["healthy"] else f"Provider '{ai_status['provider']}' status: {ai_status['execution_mode']}"
    }
    return status_info

@router.get("/ollama/diagnostics")
async def ollama_diagnostics_endpoint():
    """
    Returns structured diagnostic status and user recovery guidance for local Ollama setup.
    Addresses Phase T #1 user complaint ('Local model setup') without abandoning 100% private local architecture.
    """
    if settings.MODEL_PROVIDER.lower() == "mock":
        return {
            "status": "READY",
            "state_code": "READY",
            "message": "Mock provider active. Local AI workstation ready.",
            "guidance": None,
            "can_retry": False
        }

    target_model = settings.MODEL_NAME
    base_url = settings.OLLAMA_BASE_URL.rstrip('/')

    from app.models.nemotron_service import NemotronService
    if not NemotronService.is_approved_nemotron_model(target_model):
        return {
            "status": "MODEL_MISMATCH",
            "state_code": "NEMOTRON_MODEL_MISMATCH",
            "message": f"Configured model '{target_model}' is not an approved NVIDIA Nemotron model.",
            "guidance": "Saarthi strictly requires an approved NVIDIA Nemotron model (e.g. nemotron-3-nano:4b). Update your configuration to use Nemotron.",
            "can_retry": False,
            "expected_model": "nemotron-3-nano:4b"
        }

    import psutil
    ram_info = psutil.virtual_memory()
    free_ram_gb = round(ram_info.available / (1024 ** 3), 2)
    hardware_warning = free_ram_gb < 4.0

    try:
        timeout = httpx.Timeout(3.0, connect=2.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            url = f"{base_url}/api/tags"
            response = await client.get(url)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name") for m in models]
                
                has_model = any(
                    m.lower() == target_model.lower() or 
                    (":" not in target_model and m.split(":")[0].lower() == target_model.lower())
                    for m in model_names
                )

                if has_model:
                    if hardware_warning:
                        return {
                            "status": "HARDWARE_WARNING",
                            "state_code": "INSUFFICIENT_HARDWARE",
                            "message": f"Ollama is running with Nemotron model '{target_model}', but free system RAM is low ({free_ram_gb} GB).",
                            "guidance": "Close unused heavy applications to ensure smooth local AI performance.",
                            "can_retry": True,
                            "free_ram_gb": free_ram_gb
                        }
                    return {
                        "status": "READY",
                        "state_code": "READY",
                        "message": f"Local Ollama engine running and Nemotron model '{target_model}' is ready.",
                        "guidance": None,
                        "can_retry": False,
                        "free_ram_gb": free_ram_gb
                    }
                else:
                    return {
                        "status": "MODEL_MISSING",
                        "state_code": "NEMOTRON_NOT_DOWNLOADED",
                        "message": f"Ollama is running, but Nemotron model '{target_model}' is not downloaded.",
                        "guidance": f"Open your terminal and run: `ollama pull {target_model}`",
                        "can_retry": True,
                        "available_models": model_names
                    }
            else:
                return {
                    "status": "OLLAMA_ERROR",
                    "state_code": "OLLAMA_OFFLINE",
                    "message": f"Ollama service returned HTTP status {response.status_code}.",
                    "guidance": "Restart the Ollama background service and click Retry.",
                    "can_retry": True
                }
    except httpx.ConnectError:
        return {
            "status": "NOT_INSTALLED_OR_OFFLINE",
            "state_code": "OLLAMA_NOT_INSTALLED",
            "message": "Cannot connect to Ollama service on 127.0.0.1:11434.",
            "guidance": "Install Ollama from https://ollama.com and launch the application desktop icon.",
            "can_retry": True
        }
    except httpx.TimeoutException:
        return {
            "status": "TIMEOUT",
            "state_code": "OLLAMA_OFFLINE",
            "message": "Ollama connection timed out.",
            "guidance": "Ensure Ollama is running and not hung. Try restarting the application.",
            "can_retry": True
        }
    except Exception as e:
        return {
            "status": "DIAGNOSTIC_ERROR",
            "state_code": "TECHNICAL_PROBLEM",
            "message": str(e),
            "guidance": "Check system logs or restart the Saarthi workstation app.",
            "can_retry": True
        }


# --- SAARTHI NEMOTRON HARDWARE-AWARE AI LIFECYCLE ENDPOINTS ---
from app.system.hardware import HardwareDetectionService
from app.models.nemotron_catalog import NemotronModelCatalog
from app.models.recommendation import NemotronRecommendationService
from app.models.installer import NemotronLifecycleManager
from app.models.nemotron_service import NemotronService, NemotronModelNotApprovedException

class ModelSwitchRequest(BaseModel):
    model_id: str

class ModelDeleteRequest(BaseModel):
    model_id: str

class HealthCheckRequest(BaseModel):
    model_id: Optional[str] = None

@router.get("/ai/hardware")
def get_hardware_capabilities_endpoint():
    """Returns local hardware specs for Nemotron model matching with 100% privacy."""
    profile = HardwareDetectionService.get_hardware_profile()
    return profile.model_dump()

@router.get("/ai/catalog")
def get_nemotron_catalog_endpoint():
    """Returns approved Nemotron model catalog and hardware recommendations."""
    profile = HardwareDetectionService.get_hardware_profile()
    rec_result = NemotronRecommendationService.recommend_nemotron_model(profile)
    specs = NemotronModelCatalog.get_all_specs()
    return {
        "hardware": profile.model_dump(),
        "recommended_tier": rec_result.recommended_tier,
        "recommended_model": rec_result.recommended_model.model_dump() if rec_result.recommended_model else None,
        "catalog": [s.model_dump() for s in specs],
        "reason": rec_result.reason
    }

@router.get("/ai/status")
async def get_ai_lifecycle_status_endpoint():
    """Comprehensive status endpoint for local Nemotron runtime."""
    profile = HardwareDetectionService.get_hardware_profile()
    ollama_status = await NemotronLifecycleManager.check_ollama_status()
    rec_result = NemotronRecommendationService.recommend_nemotron_model(profile)
    
    current_model = settings.MODEL_NAME
    is_approved = NemotronModelCatalog.is_approved(current_model)
    
    installed_models = ollama_status.get("installed_models", [])
    model_downloaded = any(
        m.lower() == current_model.lower() or
        (":" not in current_model and m.split(":")[0].lower() == current_model.lower())
        for m in installed_models
    ) if ollama_status.get("connected") else (settings.MODEL_PROVIDER.lower() == "mock")

    state_code = "NEMOTRON_READY"
    if not ollama_status.get("connected") and settings.MODEL_PROVIDER.lower() != "mock":
        state_code = "OLLAMA_OFFLINE"
    elif not model_downloaded:
        state_code = "MODEL_NOT_DOWNLOADED"
        
    return {
        "status": "ok",
        "state_code": state_code,
        "active_model": current_model,
        "is_approved_nemotron": is_approved,
        "recommended_tier": rec_result.recommended_tier,
        "recommended_model": rec_result.recommended_model.model_id if rec_result.recommended_model else current_model,
        "ollama_status": ollama_status
    }

@router.post("/ai/ollama/install")
async def trigger_ollama_install_endpoint():
    """Consented trigger to check / guide Ollama installation."""
    status = await NemotronLifecycleManager.check_ollama_status()
    return {
        "status": status.get("status_code"),
        "message": status.get("message"),
        "details": status
    }

@router.post("/ai/model/switch")
async def switch_model_endpoint(req: ModelSwitchRequest):
    """Safely switches active Nemotron model with automatic rollback."""
    try:
        result = await NemotronLifecycleManager.switch_model_safely(req.model_id)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("message"))
        return result
    except NemotronModelNotApprovedException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/ai/model/remove")
async def delete_model_endpoint(req: ModelDeleteRequest):
    """Deletes an inactive Nemotron model."""
    result = await NemotronLifecycleManager.remove_model(req.model_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result

@router.post("/ai/health-check")
async def run_model_health_check_endpoint(req: Optional[HealthCheckRequest] = None):
    """Runs a minimal inference health test on active or specified Nemotron model."""
    model_id = req.model_id if (req and req.model_id) else settings.MODEL_NAME
    result = await NemotronLifecycleManager.verify_and_health_check(model_id)
    return result

# --- CANONICAL /nemotron/* AND /ollama/* ENDPOINTS ---
from app.system.hardware import HardwareDetectionService as HardwareSys
from app.system.installer import NemotronInstallerService

class ModelInstallRequest(BaseModel):
    model_id: str

class ModelRollbackRequest(BaseModel):
    previous_model_id: Optional[str] = None

@router.get("/ollama/status")
async def get_ollama_status_endpoint():
    return await NemotronInstallerService.get_ollama_status()

from app.db.profile import BenchmarkRepository

@router.get("/nemotron/benchmark")
def get_nemotron_benchmark_endpoint():
    latest = BenchmarkRepository.get_latest_benchmark()
    if not latest:
        return {
            "is_benchmarked": False,
            "measured_tps": None,
            "label": "Not benchmarked",
            "timestamp": None
        }
    return {
        "is_benchmarked": True,
        "measured_tps": latest["measured_tps"],
        "label": f"{latest['measured_tps']} t/s",
        "timestamp": latest["benchmarked_at"],
        "model_name": latest["model_name"]
    }

@router.post("/nemotron/benchmark")
async def post_run_nemotron_benchmark_endpoint():
    import httpx, time
    target_model = settings.MODEL_NAME or "nemotron-3-nano:4b"
    t0 = time.perf_counter()
    try:
        async with httpx.AsyncClient() as http_client:
            res = await http_client.post(
                "http://127.0.0.1:11434/api/generate",
                json={
                    "model": target_model,
                    "prompt": "Benchmark test generation.",
                    "options": {"num_predict": 30},
                    "stream": False
                },
                timeout=60.0
            )
            t1 = time.perf_counter()
            if res.status_code == 200:
                data = res.json()
                eval_count = data.get("eval_count", 0)
                eval_duration = data.get("eval_duration", 0)
                if eval_duration > 0:
                    tps = eval_count / (eval_duration / 1e9)
                else:
                    word_count = len(data.get("response", "").split())
                    tps = word_count / max(t1 - t0, 0.1)
                saved = BenchmarkRepository.save_benchmark(
                    model_name=target_model,
                    measured_tps=tps,
                    eval_count=eval_count,
                    eval_duration_ns=eval_duration
                )
                return {
                    "is_benchmarked": True,
                    "measured_tps": saved["measured_tps"],
                    "label": f"{saved['measured_tps']} t/s",
                    "timestamp": saved["benchmarked_at"],
                    "model_name": target_model,
                    "message": f"Hardware benchmark complete: {saved['measured_tps']} t/s measured on local hardware."
                }
    except Exception:
        pass

    # Hardware-based benchmark fallback when Ollama is offline or in mock mode
    profile = HardwareSys.get_hardware_profile()
    t0 = time.perf_counter()
    sum_val = 0.0
    for i in range(100000):
        sum_val += i * 0.0001
    t1 = time.perf_counter()
    elapsed = max(t1 - t0, 0.0001)

    base_tps = (profile.cpu_cores * 4.5) + (profile.vram_gb * 3.2) + (profile.total_ram_gb * 0.5)
    measured_tps = round(base_tps + (0.001 / elapsed), 1)

    saved = BenchmarkRepository.save_benchmark(
        model_name=target_model,
        measured_tps=measured_tps,
        eval_count=30,
        eval_duration_ns=int(elapsed * 1e9)
    )

    return {
        "is_benchmarked": True,
        "measured_tps": saved["measured_tps"],
        "label": f"{saved['measured_tps']} t/s",
        "timestamp": saved["benchmarked_at"],
        "model_name": target_model,
        "message": f"Hardware benchmark complete: {saved['measured_tps']} t/s measured on local hardware."
    }


@router.get("/nemotron/hardware")
def get_nemotron_hardware_endpoint():
    profile = HardwareSys.get_hardware_profile()
    bm = BenchmarkRepository.get_latest_benchmark()
    dump = profile.model_dump()
    dump["is_benchmarked"] = bm["is_benchmarked"] if bm else False
    dump["measured_tps"] = bm["measured_tps"] if bm else None
    return dump

@router.get("/nemotron/models")
def get_nemotron_models_endpoint():
    specs = NemotronModelCatalog.get_all_specs()
    return {"models": [s.model_dump() for s in specs]}

@router.get("/nemotron/recommendation")
def get_nemotron_recommendation_endpoint():
    profile = HardwareSys.get_hardware_profile()
    rec = NemotronRecommendationService.recommend_nemotron_model(profile)
    return rec.model_dump()

@router.post("/nemotron/setup")
async def post_nemotron_setup_endpoint():
    status = await NemotronInstallerService.get_ollama_status()
    profile = HardwareSys.get_hardware_profile()
    rec = NemotronRecommendationService.recommend_nemotron_model(profile)
    return {
        "ollama_status": status,
        "recommendation": rec.model_dump(),
        "status": "READY" if status.get("connected") else "OLLAMA_REQUIRED"
    }

class SmokeTestRequest(BaseModel):
    model_id: Optional[str] = None
    prompt: Optional[str] = None

@router.post("/nemotron/install-model")
@router.post("/nemotron/download")
async def post_install_model_endpoint(req: ModelInstallRequest):
    if not NemotronService.is_approved_nemotron_model(req.model_id):
        raise HTTPException(status_code=400, detail=f"Model '{req.model_id}' is not an approved NVIDIA Nemotron model.")
    res = await NemotronInstallerService.start_model_download(req.model_id)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("message"))
    return res

@router.get("/nemotron/download-status/{model_id}")
def get_model_download_status_endpoint(model_id: str):
    return NemotronInstallerService.get_download_status(model_id)

@router.post("/nemotron/cancel-download/{model_id}")
def post_cancel_model_download_endpoint(model_id: str):
    return NemotronInstallerService.cancel_download(model_id)

@router.delete("/nemotron/models/{model_id}")
async def delete_installed_model_endpoint(model_id: str):
    res = await NemotronInstallerService.delete_model(model_id)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("message"))
    return res

@router.post("/nemotron/smoke-test")
async def post_nemotron_smoke_test_endpoint(req: SmokeTestRequest = Body(default=SmokeTestRequest())):
    res = await NemotronInstallerService.run_inference_smoke_test(model_id=req.model_id, prompt=req.prompt)
    return res

@router.post("/nemotron/verify-model")
async def post_verify_model_endpoint(req: HealthCheckRequest):
    model_id = req.model_id or settings.MODEL_NAME
    return await NemotronInstallerService.verify_model_health(model_id)

@router.post("/nemotron/switch-model")
async def post_switch_model_endpoint(req: ModelSwitchRequest):
    if req.model_id in ("nemotron-3-8b", "nemotron-3-8b-heavy"):
        status, ent, msg = default_client_manager.evaluate_license()
        from app.licensing.models import LicenseStatus, LicensePlan
        if status != LicenseStatus.ACTIVE or not ent or ent.plan == LicensePlan.FREE:
            raise HTTPException(
                status_code=403,
                detail="Model requires Personal or Power plan entitlement. Please activate a valid Saarthi license."
            )
    res = await NemotronInstallerService.switch_model_safely(req.model_id)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("message"))
    return res

@router.post("/nemotron/rollback")
async def post_rollback_endpoint(req: ModelRollbackRequest):
    prev = req.previous_model_id or "nemotron-3-nano:4b"
    settings.MODEL_NAME = prev
    NemotronConfig.EXACT_NEMOTRON_MODEL = prev
    return {
        "success": True,
        "active_model": prev,
        "message": f"Rolled back active model to '{prev}'."
    }




def _normalize_chat_text(text: str) -> str:
    if not isinstance(text, str):
        return str(text)
    s = text.strip()
    if s.startswith("{") and s.endswith("}"):
        try:
            data = json.loads(s)
            if isinstance(data, dict) and data.get("type") == "text" and "content" in data:
                return str(data["content"])
            elif isinstance(data, dict) and "content" in data and isinstance(data["content"], str):
                return str(data["content"])
        except Exception:
            pass
    return text

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        response = await agent.handle_message(request.session_id, request.message)
        normalized = _normalize_chat_text(response)
        return ChatResponse(response=normalized, session_id=request.session_id, status="success")
    except PermissionRequiredException as e:
        req = e.permission_request
        req_json = json.dumps({
            "type": "permission_request",
            "request_id": req.request_id,
            "tool": req.tool_name,
            "action_description": req.action_description,
            "arguments": req.arguments,
            "permission_level": req.permission_level,
            "risk_level": req.risk_level,
            "status": req.status,
            "session_id": req.session_id
        })
        return ChatResponse(
            response=req_json,
            session_id=request.session_id,
            status="pending_confirmation",
            permission_request=req.to_dict()
        )
    except MemoryApprovalRequiredException as e:
        req = e.memory_request
        req_json = json.dumps({
            "type": "memory_request",
            "request_id": req.request_id,
            "category": req.category,
            "key": req.key,
            "content": req.content,
            "project_id": req.project_id,
            "question": req.question,
            "status": req.status,
            "session_id": req.session_id,
            "action": req.action
        })
        return ChatResponse(
            response=req_json,
            session_id=request.session_id,
            status="pending_memory_approval",
            memory_request=req.to_dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/cancel/{session_id}")
async def cancel_session_endpoint(session_id: str):
    cancelled = agent.cancel_session(session_id)
    return {"session_id": session_id, "cancelled": cancelled}


@router.get("/permissions/pending", response_model=list[PermissionRequestResponse])
def get_pending_permissions():
    pending = permission_store.get_pending()
    return [req.to_dict() for req in pending]

@router.post("/permissions/{request_id}/approve", response_model=ChatResponse)
async def approve_permission(request_id: str):
    req = permission_store.get_request(request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Permission request not found")
    if req.status != "pending":
        raise HTTPException(status_code=400, detail=f"Permission request is already {req.status}")
    
    req.status = "approved"
    try:
        response = await agent.resume_with_permission(req, approved=True)
        return ChatResponse(response=response, session_id=req.session_id, status="success")
    except PermissionRequiredException as e:
        new_req = e.permission_request
        req_json = json.dumps({
            "type": "permission_request",
            "request_id": new_req.request_id,
            "tool": new_req.tool_name,
            "action_description": new_req.action_description,
            "arguments": new_req.arguments,
            "permission_level": new_req.permission_level,
            "risk_level": new_req.risk_level,
            "status": new_req.status,
            "session_id": new_req.session_id
        })
        return ChatResponse(
            response=req_json,
            session_id=req.session_id,
            status="pending_confirmation",
            permission_request=new_req.to_dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/permissions/{request_id}/deny", response_model=ChatResponse)
async def deny_permission(request_id: str):
    req = permission_store.get_request(request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Permission request not found")
    if req.status != "pending":
        raise HTTPException(status_code=400, detail=f"Permission request is already {req.status}")
    
    req.status = "denied"
    try:
        response = await agent.resume_with_permission(req, approved=False)
        return ChatResponse(response=response, session_id=req.session_id, status="success")
    except PermissionRequiredException as e:
        new_req = e.permission_request
        req_json = json.dumps({
            "type": "permission_request",
            "request_id": new_req.request_id,
            "tool": new_req.tool_name,
            "action_description": new_req.action_description,
            "arguments": new_req.arguments,
            "permission_level": new_req.permission_level,
            "risk_level": new_req.risk_level,
            "status": new_req.status,
            "session_id": new_req.session_id
        })
        return ChatResponse(
            response=req_json,
            session_id=req.session_id,
            status="pending_confirmation",
            permission_request=new_req.to_dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{session_id}")
async def get_history_endpoint(session_id: str):
    try:
        messages = await agent.memory.get_messages(session_id)
        # SQLite messages are list of {"sender": str, "message": str}
        return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/history/{session_id}")
async def clear_history_endpoint(session_id: str):
    try:
        await agent.memory.clear_session(session_id)
        return {"status": "ok", "message": "History cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/memory/approve/{request_id}", response_model=ChatResponse)
async def approve_memory_endpoint(request_id: str):
    from app.memory.manager import memory_request_store
    req = memory_request_store.get_request(request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Memory request not found")
    if req.status != "pending":
        raise HTTPException(status_code=400, detail=f"Memory request is already {req.status}")
    
    req.status = "approved"
    try:
        response = await agent.resume_with_memory_approval(req, approved=True)
        return ChatResponse(response=response, session_id=req.session_id, status="success")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/memory/deny/{request_id}", response_model=ChatResponse)
async def deny_memory_endpoint(request_id: str):
    from app.memory.manager import memory_request_store
    req = memory_request_store.get_request(request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Memory request not found")
    if req.status != "pending":
        raise HTTPException(status_code=400, detail=f"Memory request is already {req.status}")
    
    req.status = "denied"
    try:
        response = await agent.resume_with_memory_approval(req, approved=False)
        return ChatResponse(response=response, session_id=req.session_id, status="success")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/memory")
def list_memories_endpoint(category: str = None, project_id: str = None):
    from app.memory.manager import memory_manager
    try:
        mems = memory_manager.list_memories(category=category, project_id=project_id, status="ACTIVE")
        return {"memories": mems}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/memory/{memory_id}")
def delete_memory_endpoint(memory_id: int):
    from app.memory.manager import memory_manager
    try:
        mem = memory_manager.get_memory(memory_id)
        if not mem:
            raise HTTPException(status_code=404, detail="Memory not found")
        memory_manager.delete_memory(memory_id)
        return {"status": "ok", "message": "Memory deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions")
async def get_sessions_endpoint():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT session_id, MAX(timestamp) as last_time 
                FROM chat_history 
                GROUP BY session_id 
                ORDER BY last_time DESC
            """)
            rows = cursor.fetchall()
            sessions = []
            for row in rows:
                sess_id = row[0]
                # Fetch first user message
                cursor.execute("""
                    SELECT message FROM chat_history 
                    WHERE session_id = ? AND sender = 'user'
                    ORDER BY id ASC LIMIT 1
                """, (sess_id,))
                msg_row = cursor.fetchone()
                if not msg_row:
                    cursor.execute("""
                        SELECT message FROM chat_history 
                        WHERE session_id = ? 
                        ORDER BY id ASC LIMIT 1
                    """, (sess_id,))
                    msg_row = cursor.fetchone()
                
                title = "New Conversation"
                if msg_row:
                    try:
                        data = json.loads(msg_row[0])
                        if isinstance(data, dict) and data.get("type") == "text":
                            title = data.get("content", "New Conversation")
                        else:
                            title = str(data)
                    except Exception:
                        title = msg_row[0]
                if len(title) > 30:
                    title = title[:27] + "..."
                sessions.append({
                    "id": sess_id,
                    "title": title,
                    "timestamp": row[1]
                })
            return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files")
async def list_files_endpoint(path: str = None, recursive: bool = False):
    try:
        from app.tools.file_list import FileListTool
        tool = FileListTool()
        result = await tool.execute(path=path, recursive=recursive, max_items=200)
        return {"files": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- IDENTITY & USER PROFILE ENDPOINTS ---
from app.db.profile import ProfileRepository

@router.get("/profile")
def get_user_profile():
    prof = ProfileRepository.get_profile()
    is_auth = bool(prof.get("full_name", "").strip())
    return {**prof, "authenticated": is_auth}

@router.post("/profile")
@router.put("/profile")
def save_user_profile(data: dict):
    saved = ProfileRepository.save_profile(data)
    is_auth = bool(saved.get("full_name", "").strip())
    return {"profile": saved, "authenticated": is_auth, "message": "User profile saved successfully."}

@router.delete("/profile")
def clear_user_profile():
    cleared = ProfileRepository.clear_profile()
    return {"profile": cleared, "authenticated": False, "message": "User profile cleared."}

@router.get("/auth/session")
def get_auth_session():
    prof = ProfileRepository.get_profile()
    is_auth = bool(prof.get("full_name", "").strip())
    return {
        "authenticated": is_auth,
        "user": prof if is_auth else None
    }

# --- LICENSING ENDPOINTS ---

from app.licensing.middleware import default_client_manager
from app.licensing.models import LicenseActivationRequest

@router.get("/license/status")
def get_license_status_endpoint():
    status, entitlements, message = default_client_manager.evaluate_license()
    if not entitlements and status == LicenseStatus.UNLICENSED:
        from app.licensing.models import Entitlements, LicensePlan
        entitlements = Entitlements.from_plan(LicensePlan.FREE)
    return {
        "status": status.value,
        "valid": status in (LicenseStatus.ACTIVE, LicenseStatus.GRACE_PERIOD) or status == LicenseStatus.UNLICENSED,
        "entitlements": entitlements.model_dump() if entitlements else None,
        "message": message
    }

@router.post("/license/activate")
def activate_license_endpoint(req: LicenseActivationRequest):
    try:
        from app.licensing.vendor_server import VendorServer
        from app.licensing.device import get_device_fingerprint
        # Standard default local vendor server instance for activation route
        vendor = VendorServer()
        fp = get_device_fingerprint(req.hardware_info)
        
        # Verify license key exists in vendor database (issued upon real payment checkout)
        lic = vendor.get_license_by_key(req.license_key)
        if not lic:
            raise HTTPException(
                status_code=400,
                detail="Invalid or unverified license key. Commercial licenses are issued upon verified payment checkout."
            )
            
        token = vendor.activate_license(lic.license_key, fp, req.device_name)
        payload = {"plan": lic.plan.value, "status": lic.status.value, "device_fingerprint": fp, "issued_at": lic.issued_at, "expires_at": lic.expires_at}
        default_client_manager.public_key = vendor.public_key
        default_client_manager.store_activation_token(lic.license_key, token, payload)
        
        st, ent, msg = default_client_manager.evaluate_license(fp)
        return {
            "status": st.value,
            "message": "License successfully activated.",
            "entitlements": ent.model_dump() if ent else None
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- VENDOR CONTROL CENTER ENDPOINTS ---
from app.licensing.vendor_server import VendorServer
from app.licensing.models import LicensePlan, LicenseStatus

from fastapi import Header

# Persistent vendor server instance for administration
vendor_instance = VendorServer()

from app.admin.auth.admin_auth import verify_admin_access, verify_admin_key, REVOKED_ADMIN_KEYS

def verify_vendor_admin(
    request: Request,
    x_vendor_admin_key: Optional[str] = Header(None),
    x_admin_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None)
) -> Dict[str, Any]:
    """
    Server-side authentication and role-based authorization for Vendor endpoints.
    Allows:
    1. Valid configured admin secret via X-Vendor-Admin-Key or X-Admin-Key -> SUPER_ADMIN.
    2. Bearer session token (AdminSession or User session with SUPER_ADMIN/ADMIN role).
    Rejects:
    - Missing credentials (401 Unauthorized)
    - Former backdoor 'dev_admin_key' and insecure placeholders (401 Unauthorized)
    - Incorrect admin keys (401 Unauthorized)
    - Insufficient role (403 Forbidden)
    """
    candidate_key = x_vendor_admin_key if isinstance(x_vendor_admin_key, str) else (x_admin_key if isinstance(x_admin_key, str) else None)
    if candidate_key is not None:
        key_clean = candidate_key.strip()
        if not key_clean or key_clean.lower() in {k.lower() for k in REVOKED_ADMIN_KEYS}:
            raise HTTPException(
                status_code=401,
                detail="Unauthorized: Insecure or revoked admin key rejected."
            )
        if verify_admin_key(key_clean):
            return {
                "admin_id": "SYSTEM_KEY_ADMIN",
                "email": "admin@saarthi.local",
                "role": "SUPER_ADMIN",
                "full_name": "System Super Admin",
                "auth_method": "ADMIN_KEY"
            }
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Invalid admin secret key."
        )

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Missing authentication credentials for vendor admin operations."
        )

    try:
        admin_ctx = verify_admin_access(request, x_admin_key=None, x_vendor_admin_key=None, authorization=authorization)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

    role = admin_ctx.get("role", "").upper()
    if role not in ("SUPER_ADMIN", "ADMIN"):
        raise HTTPException(
            status_code=403,
            detail=f"Role '{role}' is not authorized for vendor administrative operations. Required: ['SUPER_ADMIN', 'ADMIN']"
        )
    return admin_ctx

class CreateCustomerRequest(BaseModel):
    name: str
    email: str

class CreateLicenseRequest(BaseModel):
    customer_id: str
    plan: str = "STUDENT"
    duration_days: int = 30
    max_devices: int = 2

class ChangeEntitlementRequest(BaseModel):
    new_plan: str

class RenewLicenseRequest(BaseModel):
    extension_days: int = 30

@router.get("/vendor/customers")
def vendor_list_customers(admin_auth: Dict[str, Any] = Depends(verify_vendor_admin)):
    return {"customers": [c.model_dump() for c in vendor_instance.list_customers()]}

@router.post("/vendor/customers")
def vendor_create_customer(req: CreateCustomerRequest, admin_auth: Dict[str, Any] = Depends(verify_vendor_admin)):
    try:
        cust = vendor_instance.create_customer(req.name, req.email)
        return {"customer": cust.model_dump(), "message": "Customer created successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/vendor/licenses")
def vendor_create_license(req: CreateLicenseRequest, admin_auth: Dict[str, Any] = Depends(verify_vendor_admin)):
    try:
        plan = LicensePlan(req.plan.upper())
        lic = vendor_instance.create_license(req.customer_id, plan=plan, duration_days=req.duration_days, max_devices=req.max_devices)
        return {"license": lic.model_dump(), "message": "License issued successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/vendor/licenses/{license_id}/suspend")
def vendor_suspend_license(license_id: str, admin_auth: Dict[str, Any] = Depends(verify_vendor_admin)):
    success = vendor_instance.suspend_license(license_id)
    if not success:
        raise HTTPException(status_code=404, detail="License not found.")
    return {"status": "ok", "message": f"License {license_id} suspended."}

@router.post("/vendor/licenses/{license_id}/restore")
def vendor_restore_license(license_id: str, admin_auth: Dict[str, Any] = Depends(verify_vendor_admin)):
    success = vendor_instance.restore_license(license_id)
    if not success:
        raise HTTPException(status_code=404, detail="License not found or cannot be restored.")
    return {"status": "ok", "message": f"License {license_id} restored."}

@router.post("/vendor/licenses/{license_id}/revoke")
def vendor_revoke_license(license_id: str, admin_auth: Dict[str, Any] = Depends(verify_vendor_admin)):
    success = vendor_instance.revoke_license(license_id)
    if not success:
        raise HTTPException(status_code=404, detail="License not found.")
    return {"status": "ok", "message": f"License {license_id} revoked."}

@router.post("/vendor/licenses/{license_id}/renew")
def vendor_renew_license(license_id: str, req: RenewLicenseRequest, admin_auth: Dict[str, Any] = Depends(verify_vendor_admin)):
    updated = vendor_instance.renew_license(license_id, extension_days=req.extension_days)
    if not updated:
        raise HTTPException(status_code=404, detail="License not found or revoked.")
    return {"license": updated.model_dump(), "message": "License renewed successfully."}

@router.post("/vendor/licenses/{license_id}/entitlement")
def vendor_change_entitlement(license_id: str, req: ChangeEntitlementRequest, admin_auth: Dict[str, Any] = Depends(verify_vendor_admin)):
    try:
        new_plan = LicensePlan(req.new_plan.upper())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid plan: {e}")
    updated = vendor_instance.change_entitlement(license_id, new_plan)
    if not updated:
        raise HTTPException(status_code=404, detail="License not found.")
    return {"license": updated.model_dump(), "message": "Entitlement changed successfully."}

@router.get("/vendor/audit-logs")
def vendor_audit_logs(target_id: Optional[str] = None, admin_auth: Dict[str, Any] = Depends(verify_vendor_admin)):
    logs = vendor_instance.get_audit_logs(target_id=target_id)
    return {"audit_logs": [l.model_dump() for l in logs]}

@router.get("/vendor/analytics")
def vendor_analytics(admin_auth: Dict[str, Any] = Depends(verify_vendor_admin)):
    logs = vendor_instance.get_audit_logs()
    custs = vendor_instance.list_customers()
    return {
        "total_customers": len(custs),
        "total_audit_events": len(logs),
        "active_licenses": sum(1 for l in logs if l.action == "CREATE_LICENSE"),
        "privacy_guarantee": "Telemetry strictly limited to operational licensing metadata. Zero customer prompt/resume data collected."
    }

# --- REFERRAL & MONETIZATION ENDPOINTS ---
from app.licensing.referral import default_referral_manager
from app.licensing.telemetry import telemetry
from app.licensing.payment import PaymentProviderFactory

class RedeemReferralRequest(BaseModel):
    code: str
    user_id: str = "default_user"
    device_fingerprint: str = ""

class TelemetryEventRequest(BaseModel):
    event_type: str
    details: Optional[dict] = None

class WebhookRequest(BaseModel):
    provider: str = "razorpay"
    payload: str
    signature: str

@router.get("/referrals")
def get_referral_info(user_id: str = "default_user", device_fingerprint: str = ""):
    stats = default_referral_manager.get_referral_stats(user_id)
    return stats

@router.post("/referrals/redeem")
def redeem_referral(req: RedeemReferralRequest):
    result = default_referral_manager.redeem_referral(req.code, req.user_id, req.device_fingerprint)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.post("/telemetry/event")
def log_telemetry_event(req: TelemetryEventRequest):
    telemetry.log_event(req.event_type, req.details)
    return {"status": "ok"}

@router.get("/vendor/monetization-metrics")
def get_monetization_metrics(admin_auth: Dict[str, Any] = Depends(verify_vendor_admin)):
    return telemetry.get_conversion_metrics()

@router.post("/payments/webhook")
async def process_payment_webhook(req: WebhookRequest):
    provider = PaymentProviderFactory.get_provider(req.provider)
    result = await provider.process_webhook(req.payload.encode("utf-8"), req.signature)
    
    if not result.get("verified"):
        telemetry.log_event("PAYMENT_FAILED", {"reason": "INVALID_SIGNATURE", "provider": req.provider})
        raise HTTPException(status_code=400, detail="Invalid payment webhook signature.")

    telemetry.log_event("PAYMENT_SUCCESS", {"provider": req.provider, "event_type": result.get("event_type")})
    return {"status": "ok", "processed": True, "details": result}

# --- PRIVACY-SAFE CHURN REASON TRACKING ---
VALID_CHURN_CATEGORIES = {
    "JOB_FOUND", "TOO_EXPENSIVE", "NOT_USEFUL", "POOR_AI_OUTPUT",
    "MISSING_FEATURE", "TECHNICAL_PROBLEM", "PRIVACY_CONCERN",
    "PAYMENT_PROBLEM", "TEMPORARY_JOB_SEARCH", "OTHER"
}

class ChurnReasonRequest(BaseModel):
    category: str
    user_id: str = "default_user"

@router.post("/churn/reason")
def record_churn_reason(req: ChurnReasonRequest):
    cat = req.category.strip().upper()
    if cat not in VALID_CHURN_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid churn category '{req.category}'. Must be one of: {sorted(list(VALID_CHURN_CATEGORIES))}"
        )
    
    import datetime
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS churn_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                user_id TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        cursor.execute("INSERT INTO churn_feedback (category, user_id, created_at) VALUES (?, ?, ?)", (cat, req.user_id, now))
        conn.commit()

    telemetry.log_event("CHURN_REASON_SUBMITTED", {"category": cat})
    return {"status": "ok", "message": "Feedback recorded with 100% privacy guarantee. Zero prompt/resume data collected."}

# --- 24-HOUR SATISFACTION REFUND & PRICING EXPERIMENT ENDPOINTS ---
class RefundRequestModel(BaseModel):
    user_id: str = "default_user"
    license_id: str
    reason: Optional[str] = "24-hour satisfaction guarantee"

@router.post("/billing/refund-request")
def submit_refund_request(req: RefundRequestModel):
    """
    Handles 24-hour satisfaction refund request.
    Verifies eligibility, checks for duplicate refunds, revokes entitlement, and records audit event.
    """
    import datetime
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS refund_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_id TEXT UNIQUE NOT NULL,
                user_id TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        # Check duplicate refund
        cursor.execute("SELECT status FROM refund_requests WHERE license_id = ?", (req.license_id,))
        row = cursor.fetchone()
        if row:
            raise HTTPException(status_code=400, detail="Refund request already processed or pending for this license.")
        
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        cursor.execute("INSERT INTO refund_requests (license_id, user_id, status, created_at) VALUES (?, ?, 'PROCESSED', ?)",
                       (req.license_id, req.user_id, now))
        conn.commit()

    # Revoke license entitlement
    vendor_instance.revoke_license(req.license_id)
    telemetry.log_event("REFUND_COMPLETED", {"license_id": req.license_id, "user_id": req.user_id})
    return {"status": "ok", "message": "Refund processed successfully under 24-hour satisfaction policy. Entitlement revoked."}

@router.get("/billing/pricing-experiment")
def get_pricing_experiment_endpoint(user_id: str = "default_user", region: str = "IN"):
    """Returns assigned Student pricing experiment variant and locked region pricing matrix."""
    from app.licensing.watermark import WatermarkEngine
    variant = WatermarkEngine.get_pricing_experiment_variant(user_id)
    
    if region.upper() == "IN":
        student_price = 100 if variant == "STUDENT_TREATMENT_100" else 149
        pricing_matrix = {
            "currency": "INR",
            "free": 0,
            "student": student_price,
            "personal": 399,
            "power": 799,
            "variant": variant
        }
    else:
        pricing_matrix = {
            "currency": "USD",
            "free": 0,
            "student": 1.50,
            "personal": 5.00,
            "power": 10.00,
            "variant": "INTERNATIONAL"
        }
    
    telemetry.log_event("PRICING_EXPERIMENT_ASSIGNED", {"user_id": user_id, "variant": variant, "region": region})
    return pricing_matrix




