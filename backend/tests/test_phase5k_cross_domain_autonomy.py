import pytest
from app.intelligence.planning.task_graph import TaskGraph, TaskStep, TaskStatus
from app.intelligence.planning.planner import planner_service
from app.intelligence.domains.domain_router import domain_router
from app.intelligence.domains.domain_handoff import domain_handoff_manager
from app.intelligence.domains.research_engine import research_engine
from app.intelligence.context.context_engine import context_engine
from app.intelligence.memory.memory_manager import memory_manager
from app.intelligence.orchestration.orchestrator import orchestrator
from app.intelligence.projects.project_manager import project_manager
from app.intelligence.routines.routine_engine import routine_engine
from app.intelligence.proactive.goal_system import goal_system
from app.intelligence.voice.voice_conversation_engine import voice_conversation_engine
from app.intelligence.proactive.proactive_engine import proactive_engine
from app.core.plans import PlanService
from app.core.entitlements import get_current_plan

def test_cross_domain_task_graph_structure():
    graph = planner_service.create_plan(
        goal="Analyze these archaeological excavation photographs, compare them with historical records, research similar findings and prepare a report.",
        domain="archaeology"
    )
    assert graph.task_id.startswith("task_")
    assert len(graph.steps) >= 4
    assert len(graph.subdomains) >= 3
    assert "archaeology" in graph.subdomains
    assert "history" in graph.subdomains
    assert "research" in graph.subdomains
    assert "writing" in graph.subdomains
    
    step_domains = [s.domain for s in graph.steps]
    assert "archaeology" in step_domains
    assert "history" in step_domains

def test_automatic_domain_transitions():
    seq = domain_router.detect_domain_sequence(
        "Analyze excavation photos, check historical archives, search research papers, write summary."
    )
    domains = [s["domain"] for s in seq]
    assert "archaeology" in domains
    assert "history" in domains
    assert "research" in domains
    assert "writing" in domains

def test_explicit_domain_override():
    res = domain_router.route_request(
        prompt="Analyze excavation photos and historical records",
        explicit_domain="cybersecurity"
    )
    assert res.primary_domain == "cybersecurity"
    assert res.is_explicit_override is True

def test_domain_handoff_creation():
    handoff = domain_handoff_manager.create_handoff(
        source_domain="archaeology",
        destination_domain="history",
        reason="Visual typology analysis payload transfer",
        input_artifact={"pottery_observed": "red-ware fragments"},
        output_artifact={"archival_match": "Harappan Period III"}
    )
    assert handoff.source_domain == "archaeology"
    assert handoff.destination_domain == "history"
    assert handoff.verification_status == "verified"

def test_cross_domain_context_isolation():
    bundle = context_engine.build_context_bundle(
        user_message="Analyze archaeological excavation photos and compare with historical archives",
        user_id="default_local_user"
    )
    assert bundle.domain_context.active_domain is not None
    assert len(bundle.domain_context.active_subdomains) >= 2
    assert isinstance(bundle.verified_facts, list)
    assert isinstance(bundle.model_inferences, list)

def test_multi_domain_research_synthesis():
    res = research_engine.analyze_research_query(
        query="Archaeological pottery analysis and historical settlement context",
        domains=["archaeology", "history", "research"]
    )
    assert len(res.decomposed_subqueries) == 3
    assert len(res.evidence_items) >= 6
    facts = [e for e in res.evidence_items if e.classification == "FACT"]
    inferences = [e for e in res.evidence_items if e.classification == "INFERENCE"]
    assert len(facts) > 0
    assert len(inferences) > 0

def test_cross_domain_agent_orchestration():
    orch_res = orchestrator.process_message(
        user_message="Analyze archaeological excavation photographs and compare with historical records",
        user_id="default_local_user"
    )
    assert orch_res["status"] in ["success", "pending_confirmation"]
    assert "subdomains" in orch_res
    assert len(orch_res["subdomains"]) >= 2

def test_cross_domain_project_management():
    proj = project_manager.create_project(
        name="Ancient Settlement Research",
        description="Cross-domain archaeology and historical investigation",
        domain="archaeology"
    )
    proj.subdomains = ["archaeology", "history", "research", "writing"]
    assert proj.project_id.startswith("proj_")
    assert "history" in proj.subdomains

def test_cross_domain_goal_milestones():
    goal = goal_system.create_goal(
        title="Become a Cybersecurity Engineer",
        domain="cybersecurity",
        milestones=["Security Audit", "C++ Systems Roadmap", "Career Alignment"]
    )
    goal.subdomains = ["cybersecurity", "cs", "career"]
    assert goal.id.startswith("goal_")
    assert len(goal.milestones) == 3

def test_cross_domain_voice_directives():
    session = voice_conversation_engine.start_session()
    turn_res = voice_conversation_engine.process_voice_turn(
        session_id=session.session_id,
        text_override="Why did you switch to history?"
    )
    assert turn_res["status"] == "success"
    assert "switched domain" in turn_res["assistant_text"].lower()

def test_proactive_cross_domain_alerts():
    suggestions = proactive_engine.detect_opportunities(active_domain="archaeology")
    titles = [s.title for s in suggestions]
    assert "Cross-Domain Handoff Optimization" in titles

def test_entitlement_canonical_tier_mapping():
    plan = get_current_plan("default_local_user")
    assert plan.upper() in ["FREE", "STUDENT", "PERSONAL", "POWER", "TEAMS", "ENTERPRISE"]
