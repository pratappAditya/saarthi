import pytest
from fastapi.testclient import TestClient
from app.main import app

from app.intelligence.proactive.situational_awareness import situational_awareness_engine
from app.intelligence.proactive.proactive_engine import proactive_engine
from app.intelligence.proactive.goal_system import goal_system
from app.intelligence.proactive.routine_manager import routine_manager

client = TestClient(app)

def test_situational_awareness_aggregation():
    """TEST 1: Live runtime situational awareness state aggregation."""
    state = situational_awareness_engine.get_current_state(active_domain="career")
    assert state.user_id == "default_local_user"
    assert state.active_domain == "career"
    assert len(state.recent_activity) >= 1
    assert len(state.relevant_memories) >= 1

def test_proactive_engine_opportunity_detection():
    """TEST 2: Proactive suggestion generation with 'I noticed...' and 'Why Saarthi suggested this'."""
    sugs = proactive_engine.detect_opportunities(active_domain="career")
    assert len(sugs) >= 1
    
    sug = sugs[0]
    assert sug.notice_text.startswith("I noticed")
    assert len(sug.rationale) >= 10
    assert sug.action_type in ["SUGGEST", "ASK", "ACT"]

    # Test acceptance and dismissal
    acc = proactive_engine.accept_suggestion(sug.id)
    assert acc.status == "accepted"

def test_sqlite_goal_system_persistence():
    """TEST 3: SQLite persistence for AgentGoals and milestones."""
    goal = goal_system.create_goal(
        title="Deploy Phase 5G JARVIS Core",
        domain="software",
        milestones=["Run pytest", "Build frontend", "Perform live verification"],
        recommended_next_action="Run pytest suite"
    )
    assert goal.id is not None
    assert len(goal.milestones) == 3
    assert goal.status == "in_progress"

    fetched = goal_system.list_goals()
    assert len(fetched) >= 1
    found = [g for g in fetched if g.id == goal.id]
    assert len(found) == 1
    assert found[0].title == "Deploy Phase 5G JARVIS Core"

def test_sqlite_routine_manager_persistence():
    """TEST 4: SQLite persistence for AgentRoutines and schedules."""
    routine = routine_manager.create_routine(
        name="Daily Workspace Health Check",
        trigger_type="scheduled",
        cron_expression="0 9 * * *",
        domain="software",
        tool_id="file.read"
    )
    assert routine.id is not None
    assert routine.is_active is True

    fetched = routine_manager.list_routines()
    assert len(fetched) >= 1
    found = [r for r in fetched if r.id == routine.id]
    assert len(found) == 1
    assert found[0].name == "Daily Workspace Health Check"

def test_proactive_jarvis_rest_apis():
    """TEST 5: Proactive, Goal, and Routine REST API endpoints."""
    # Suggestions API
    sug_res = client.get("/api/proactive/suggestions?active_domain=career")
    assert sug_res.status_code == 200
    assert "suggestions" in sug_res.json()

    # Goals API list
    g_res = client.get("/api/proactive/goals")
    assert g_res.status_code == 200
    assert "goals" in g_res.json()

    # Routines API list
    r_res = client.get("/api/proactive/routines")
    assert r_res.status_code == 200
    assert "routines" in r_res.json()
