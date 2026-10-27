import pytest
from app.intelligence.orchestration.orchestrator import orchestrator
from app.intelligence.memory.memory_manager import memory_manager
from app.intelligence.voice.voice_conversation_engine import voice_conversation_engine
from app.intelligence.proactive.proactive_engine import proactive_engine
from app.intelligence.projects.project_manager import project_manager
from app.intelligence.proactive.goal_system import goal_system
from app.intelligence.routines.routine_engine import routine_engine
from app.intelligence.domains.domain_registry import domain_registry
from app.intelligence.audit.intelligence_audit import audit_service
from app.core.plans import PlanService
from app.core.entitlements import get_current_plan

def test_unified_orchestration_lifecycle():
    orch_res = orchestrator.process_message(
        user_message="Research battery technology developments, analyze excavation PDF, and write a summary report.",
        user_id="default_local_user"
    )
    assert orch_res["status"] in ["success", "pending_confirmation"]
    assert "domain" in orch_res
    assert "subdomains" in orch_res
    assert len(orch_res["subdomains"]) >= 2

def test_single_assistant_identity_state():
    proj = project_manager.create_project(name="Unified Test Project", domain="software")
    fact = memory_manager.remember("User prefers technical depth level expert", domain="software")
    
    assert proj.project_id.startswith("proj_")
    assert fact["content"] == "User prefers technical depth level expert"

def test_chat_to_agent_escalation():
    res = orchestrator.process_message(
        user_message="Execute Python script to benchmark local model speed",
        user_id="default_local_user"
    )
    assert res["status"] in ["success", "pending_confirmation"]
    assert "tools_used" in res

def test_voice_unified_control_directives():
    session = voice_conversation_engine.start_session()
    
    # 1. Remember directive
    res_mem = voice_conversation_engine.process_voice_turn(
        session_id=session.session_id,
        text_override="Saarthi remember I prefer Python 3.14"
    )
    assert res_mem["status"] == "success"
    assert "saved that to your persistent memory" in res_mem["assistant_text"]

    # 2. Show evidence directive
    res_ev = voice_conversation_engine.process_voice_turn(
        session_id=session.session_id,
        text_override="Saarthi show me the evidence"
    )
    assert res_ev["status"] == "success"
    assert "verified evidence items" in res_ev["assistant_text"]

def test_proactive_intelligence_surfacing():
    notices = proactive_engine.detect_opportunities(active_domain="research")
    assert len(notices) > 0
    assert any(n.action_type in ["ASK", "SUGGEST"] for n in notices)

def test_goal_project_routine_linkage():
    goal = goal_system.create_goal(
        title="Master Embedded Systems",
        domain="electrical",
        milestones=["Circuit Analysis", "C Programming", "Microcontroller Layout"]
    )
    proj = project_manager.create_project(name="Embedded Systems Study", domain="electrical")
    
    assert goal.id.startswith("goal_")
    assert proj.project_id.startswith("proj_")

def test_memory_provenance_strictness():
    fact = memory_manager.remember("User is a senior software architect")
    assert "user_explicit" in str(fact["source"]).lower()
    
    provenance = memory_manager.explain_memory_provenance(fact["id"])
    assert provenance is not None
    assert "user_explicit" in str(provenance["source"]).lower()

def test_trust_audit_logging():
    audit_service.log_event(
        user_id="default_local_user",
        session_id="integration_session",
        domain="cybersecurity",
        action_summary="Verified network port vulnerability scan"
    )
    logs = audit_service.list_audit_logs(limit=5, user_id="default_local_user")
    assert len(logs) > 0

def test_canonical_entitlement_tiers():
    plan = get_current_plan("default_local_user")
    assert plan.lower() in ["free", "student", "personal", "power", "teams", "enterprise"]
    assert PlanService.is_capability_entitled(plan, "career.master_resume")
