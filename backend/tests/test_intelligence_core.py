import pytest
import os
import tempfile
import json
from fastapi.testclient import TestClient
from app.main import app

from app.intelligence.memory.memory_models import MemoryItem, MemoryType, MemoryProvenance, MemoryScope
from app.intelligence.memory.memory_store import MemoryStore
from app.intelligence.memory.memory_retrieval import MemoryRetriever
from app.intelligence.memory.memory_manager import MemoryManager
from app.intelligence.context.context_engine import ContextEngine
from app.intelligence.models.model_router import ModelRouter
from app.intelligence.tools.tool_registry import ToolRegistry, RiskLevel
from app.intelligence.tools.tool_executor import ToolExecutor
from app.intelligence.permissions.permission_engine import PermissionEngine, PermissionScope, PermissionStatus
from app.intelligence.actions.action_engine import ActionEngine, ActionStatus
from app.intelligence.planning.planner import PlannerService
from app.intelligence.agents.agent_runtime import AgentRuntime
from app.intelligence.domains.domain_router import DomainRouter
from app.intelligence.orchestration.orchestrator import Orchestrator
from app.intelligence.audit.intelligence_audit import IntelligenceAuditService

client = TestClient(app)

@pytest.fixture
def temp_intelligence_db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    yield db_path
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass

def test_memory_persistence_provenance_and_retrieval(temp_intelligence_db):
    """TEST 1: Persistent memory storage, provenance tracking, and search ranking."""
    store = MemoryStore(db_path=temp_intelligence_db)
    mgr = MemoryManager(store=store)

    item1 = mgr.create_fact(
        content="Candidate excels at C++ low-level systems programming and stealth keyloggers.",
        source=MemoryProvenance.USER_EXPLICIT,
        importance=9,
        domain="career"
    )
    assert item1.id is not None
    assert item1.source == MemoryProvenance.USER_EXPLICIT

    item2 = mgr.create_fact(
        content="Inferred interest in Rust programming.",
        source=MemoryProvenance.MODEL_INFERENCE,
        importance=4,
        domain="software"
    )

    retriever = MemoryRetriever(store=store)
    results = retriever.search(query="C++ keylogger", domain="career")
    assert len(results) >= 1
    assert "C++" in results[0].content

def test_context_engine_assembly():
    """TEST 2: Structured ContextBundle assembly without dumping raw unstructured text."""
    bundle = ContextEngine.build_context_bundle("Help me prepare for my Stripe interview")
    assert bundle.domain_context.active_domain == "career"
    assert bundle.user_context.user_id == "default_local_user"
    assert isinstance(bundle.memory_context.relevant_memories, list)

def test_model_router_local_policy():
    """TEST 3: Model router local-first selection policy."""
    descriptor = ModelRouter.select_model(task_type="chat", prefer_local=True)
    assert descriptor.is_local is True
    assert "text" in [c.value for c in descriptor.capabilities]

def test_tool_registry_and_executor():
    """TEST 4: Tool registry risk levels and sandboxed execution."""
    tool_def = ToolRegistry.get_tool("career.analyze_jd")
    assert tool_def is not None
    assert tool_def.risk_level == RiskLevel.READ_ONLY

    # Execute tool
    res = ToolExecutor.execute_tool(
        tool_id="career.analyze_jd",
        arguments={"jd_text": "Requires C++, Nmap, and Incident Response."}
    )
    assert res["success"] is True
    assert "required_skills" in res["result"]

def test_permission_and_action_engine(temp_intelligence_db):
    """TEST 5: Risk-based permission request, approval, denial, and action execution."""
    perm_eng = PermissionEngine(db_path=temp_intelligence_db)
    
    # Request permission for terminal command
    req = perm_eng.request_permission(
        tool_id="terminal.execute",
        action_description="Run python test suite",
        arguments={"command": "pytest"},
        risk_level="HIGH_RISK",
        scope=PermissionScope.ONE_TIME
    )
    assert req.status == PermissionStatus.PENDING

    # Grant permission
    approved = perm_eng.grant_permission(req.request_id)
    assert approved.status == PermissionStatus.APPROVED

    # Execute action
    act = ActionEngine.execute_action(
        tool_id="terminal.execute",
        arguments={"command": "pytest"},
        permission_id=req.request_id,
        permission_engine_instance=perm_eng
    )
    assert act.status == ActionStatus.COMPLETED

def test_task_graph_planner():
    """TEST 6: Multi-step TaskGraph plan synthesis."""
    graph = PlannerService.create_plan("Apply for Stripe Lead Security Architect job")
    assert graph.task_id is not None
    assert len(graph.steps) >= 2
    executable = graph.get_executable_steps()
    assert len(executable) >= 1

def test_bounded_agent_runtime():
    """TEST 7: Bounded agent execution within step limits and allowed tools."""
    res = AgentRuntime.run_agent(
        agent_id="career_architect",
        task_prompt="Requires C++ and Incident Response."
    )
    assert res["success"] is True
    assert res["steps_executed"] >= 1

def test_domain_router_classification():
    """TEST 8: Domain intent classification."""
    d1 = DomainRouter.classify_domain("Help me tailor my resume for an ATS audit")
    assert d1["domain"] == "career"

    d2 = DomainRouter.classify_domain("Explain quantum mechanics paper on arXiv")
    assert d2["domain"] == "research"

    d3 = DomainRouter.classify_domain("Fix buffer overflow bug in C++ socket daemon")
    assert d3["domain"] == "software"

def test_orchestrator_end_to_end():
    """TEST 9: Complete orchestrator pipeline execution."""
    res = Orchestrator.process_message("Analyze job description requiring C++ and Nmap.")
    assert res["status"] in ["success", "pending_confirmation"]
    assert res["domain"] == "career"

def test_intelligence_rest_apis():
    """TEST 10: Phase 5B REST APIs (/api/intelligence/chat, /api/intelligence/models, /api/memory, /api/permissions)."""
    # 1. Models
    models_res = client.get("/api/intelligence/models")
    assert models_res.status_code == 200

    # 2. Memory list
    mem_res = client.get("/api/memory")
    assert mem_res.status_code == 200

    # 3. Chat
    chat_res = client.post("/api/intelligence/chat", json={"message": "Hello Saarthi"})
    assert chat_res.status_code == 200
    assert "response" in chat_res.json()
