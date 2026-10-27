import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.core.entitlements import require_capability
from app.intelligence.orchestration.orchestrator import orchestrator
from app.intelligence.memory.memory_manager import memory_manager
from app.intelligence.permissions.permission_engine import permission_engine, PermissionScope
from app.intelligence.agents.agent_runtime import agent_runtime
from app.intelligence.agents.agent_definition import AGENT_CATALOG
from app.intelligence.tools.tool_registry import ToolRegistry
from app.intelligence.tools.tool_executor import tool_executor
from app.intelligence.models.model_registry import ModelRegistry
from app.intelligence.context.context_engine import context_engine
from app.intelligence.planning.planner import planner_service

logger = logging.getLogger("app.api.intelligence_api")
router = APIRouter(prefix="", tags=["intelligence"])

# Request Schemas
class IntelligenceChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default_session"
    permission_granted: Optional[bool] = False

class IntelligencePlanRequest(BaseModel):
    goal: str
    domain: Optional[str] = "general"

class MemoryCreateRequest(BaseModel):
    content: str
    importance: Optional[int] = 7
    domain: Optional[str] = "general"
    scope: Optional[str] = "global_user"
    project_id: Optional[str] = None
    provenance: Optional[str] = "USER_EXPLICIT"
    user_id: Optional[str] = "default_local_user"

class PermissionApproveRequest(BaseModel):
    request_id: str

class AgentRunRequest(BaseModel):
    agent_id: Optional[str] = None
    task_prompt: str

class ToolExecuteRequest(BaseModel):
    tool_id: Optional[str] = None
    arguments: Dict[str, Any]

# --- INTELLIGENCE CHAT & ORCHESTRATION ---

@router.post("/intelligence/chat", dependencies=[Depends(require_capability("core.chat.basic"))])
def intelligence_chat_endpoint(req: IntelligenceChatRequest):
    return orchestrator.process_message(
        user_message=req.message,
        session_id=req.session_id or "default_session",
        permission_granted=req.permission_granted or False
    )

@router.post("/intelligence/plan", dependencies=[Depends(require_capability("agents.guided"))])
def intelligence_plan_endpoint(req: IntelligencePlanRequest):
    graph = planner_service.create_plan(req.goal, domain=req.domain or "general")
    return {"plan": graph.model_dump()}

@router.get("/intelligence/models")
def get_models_endpoint():
    return {"models": ModelRegistry.list_models()}

@router.get("/intelligence/tools")
def get_intelligence_tools_endpoint():
    return {"tools": ToolRegistry.list_tools()}

@router.get("/intelligence/context")
def get_intelligence_context_endpoint(query: str = "general context"):
    bundle = context_engine.build_context_bundle(query)
    return {"context": bundle.model_dump()}

# --- MEMORY APIS ---

@router.get("/memory")
def list_memories_endpoint(domain: Optional[str] = None):
    memories = memory_manager.list_all_memories(domain=domain)
    return {"memories": memories}

@router.post("/memory", dependencies=[Depends(require_capability("memory.profile"))])
def create_memory_endpoint(req: MemoryCreateRequest):
    from app.intelligence.memory.memory_models import MemoryScope, MemoryProvenance
    scope_enum = MemoryScope(req.scope) if req.scope in MemoryScope._value2member_map_ else MemoryScope.GLOBAL_USER
    prov_enum = MemoryProvenance(req.provenance) if req.provenance in MemoryProvenance._value2member_map_ else MemoryProvenance.USER_EXPLICIT

    item = memory_manager.create_fact(
        content=req.content,
        importance=req.importance or 7,
        domain=req.domain or "general",
        scope=scope_enum,
        project_id=req.project_id,
        source=prov_enum,
        user_id=req.user_id or "default_local_user"
    )
    return {"memory": item.model_dump(), "message": "Memory item persisted to memory store."}

@router.delete("/memory/{mem_id}")
def delete_memory_endpoint(mem_id: int):
    deleted = memory_manager.forget(mem_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Memory not found.")
    return {"deleted": True, "message": "Memory removed."}

# --- PERMISSION APIS ---

@router.get("/intelligence/permissions")
def list_permissions_endpoint():
    pending = permission_engine.list_pending_permissions()
    return {"permissions": [p.model_dump() for p in pending]}

@router.post("/intelligence/permissions/{req_id}/approve")
def approve_permission_endpoint(req_id: str):
    approved = permission_engine.grant_permission(req_id)
    if not approved:
        raise HTTPException(status_code=404, detail="Permission request not found.")
    return {"permission": approved.model_dump(), "message": "Permission approved."}

@router.post("/intelligence/permissions/{req_id}/deny")
def deny_permission_endpoint(req_id: str):
    denied = permission_engine.deny_permission(req_id)
    if not denied:
        raise HTTPException(status_code=404, detail="Permission request not found.")
    return {"permission": denied.model_dump(), "message": "Permission denied."}

# --- AGENTS APIS ---

@router.get("/agents")
def list_agents_endpoint():
    agents = [a.model_dump() for a in AGENT_CATALOG.values()]
    return {"agents": agents}

@router.post("/agents/{agent_id}/run", dependencies=[Depends(require_capability("agents.custom"))])
def run_agent_endpoint(agent_id: str, req: AgentRunRequest):
    res = agent_runtime.run_agent(agent_id=agent_id, task_prompt=req.task_prompt)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("message") or res.get("error"))
    return res

@router.get("/agents/tasks")
def list_agent_tasks_endpoint():
    from app.intelligence.planning.task_store import task_store
    tasks = task_store.list_tasks()
    return {"tasks": tasks}

@router.get("/agents/tasks/{task_id}")
def get_agent_task_endpoint(task_id: str):
    from app.intelligence.planning.task_store import task_store
    t = task_store.get_task(task_id)
    if not t:
        raise HTTPException(status_code=404, detail="Agent task not found.")
    return {"task": t}

@router.post("/agents/tasks/{task_id}/cancel")
def cancel_agent_task_endpoint(task_id: str):
    from app.intelligence.planning.planner import planner_service
    success = planner_service.cancel_task(task_id)
    return {"cancelled": success, "message": f"Task '{task_id}' cancelled."}

@router.post("/agents/tasks/{task_id}/resume")
def resume_agent_task_endpoint(task_id: str):
    from app.intelligence.planning.planner import planner_service
    res = planner_service.resume_task(task_id)
    return {"task": res, "message": f"Task '{task_id}' resumed."}

# --- TOOL APIS ---


@router.post("/tools/{tool_id}/execute")
def execute_tool_api_endpoint(tool_id: str, req: ToolExecuteRequest):
    res = tool_executor.execute_tool(tool_id=tool_id, arguments=req.arguments)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("message") or res.get("error"))
    return res

# --- PROJECTS APIS ---

class ProjectCreateRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    domain: Optional[str] = "general"

@router.get("/projects")
def list_projects_endpoint():
    from app.intelligence.projects.project_manager import project_manager
    projs = project_manager.list_projects()
    return {"projects": [p.model_dump() for p in projs]}

@router.post("/projects", dependencies=[Depends(require_capability("workspace.projects"))])
def create_project_endpoint(req: ProjectCreateRequest):
    from app.intelligence.projects.project_manager import project_manager
    p = project_manager.create_project(name=req.name, description=req.description or "", domain=req.domain or "general")
    return {"project": p.model_dump(), "message": "Project created."}

@router.delete("/projects/{proj_id}")
def delete_project_endpoint(proj_id: str):
    from app.intelligence.projects.project_manager import project_manager
    deleted = project_manager.delete_project(proj_id)
    return {"deleted": deleted, "message": "Project removed."}

# --- TRUST CENTER APIS ---

@router.get("/trust/summary")
def get_trust_summary_endpoint():
    from app.intelligence.audit.intelligence_audit import audit_service
    logs = audit_service.list_audit_logs(limit=20)
    return {
        "local_processing": True,
        "active_model": "nemotron-3-nano:4b (Local Ollama)",
        "privacy_mode": "STRICT_LOCAL_ONLY",
        "cloud_fallback": False,
        "recent_actions_count": len(logs),
        "audit_logs": logs
    }

@router.get("/trust/audit-history")
def get_trust_audit_history_endpoint(limit: int = 50):
    from app.intelligence.audit.intelligence_audit import audit_service
    return {"audit_history": audit_service.list_audit_logs(limit=limit)}

# --- VOICE APIS ---

@router.get("/voice/profile")
def get_voice_profile_endpoint():
    from app.intelligence.voice.voice_engine import voice_engine
    from app.intelligence.voice.voice_providers import stt_provider, tts_provider, wakeword_provider
    return {
        "profile": voice_engine.get_voice_profile().model_dump(),
        "stt_status": stt_provider.get_status(),
        "tts_status": tts_provider.get_status(),
        "wakeword_status": wakeword_provider.get_status()
    }

@router.post("/voice/synthesize")
def synthesize_voice_endpoint(text: str):
    from app.intelligence.voice.voice_engine import voice_engine
    return voice_engine.synthesize_speech(text)

# --- ASSISTANT PROFILE APIS ---

class AssistantProfileUpdateRequest(BaseModel):
    name: Optional[str] = "Saarthi"
    tone: Optional[str] = "intelligent, calm, helpful"
    verbosity: Optional[str] = "concise"
    formality: Optional[str] = "adaptive"
    proactivity: Optional[str] = "risk_aware"
    confirmation_policy: Optional[str] = "risk_based"

@router.get("/profile/assistant")
def get_assistant_profile_endpoint():
    from app.intelligence.profile.assistant_profile import assistant_profile_service
    return {"profile": assistant_profile_service.get_profile().model_dump()}

@router.post("/profile/assistant")
def update_assistant_profile_endpoint(req: AssistantProfileUpdateRequest):
    from app.intelligence.profile.assistant_profile import assistant_profile_service
    updated = assistant_profile_service.update_profile(req.model_dump(exclude_unset=True))
    return {"profile": updated.model_dump(), "message": "Assistant profile updated and persisted to SQLite."}
