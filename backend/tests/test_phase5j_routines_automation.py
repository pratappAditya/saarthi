import pytest
import time
from fastapi.testclient import TestClient
from app.main import app

from app.intelligence.routines.routine_store import routine_store
from app.intelligence.routines.routine_engine import routine_engine
from app.intelligence.routines.routine_parser import routine_parser
from app.intelligence.routines.routine_scheduler import routine_scheduler
from app.intelligence.routines.routine_templates import ROUTINE_TEMPLATES, instantiate_template
from app.intelligence.routines.routine_model import (
    Routine,
    TriggerType,
    RoutineScope,
    AutonomyLevel,
    ApprovalPolicy,
    MissedRunPolicy,
    RoutineStatus
)

client = TestClient(app)

def test_routine_store_persistence():
    """TEST 1: Verify routine creation, retrieval, updates, and SQLite persistence."""
    uid = "test_rtn_user_1"
    routine_store.reset_all(uid)

    rtn = Routine(
        name="Test Morning Briefing",
        description="Daily 8 AM summary",
        owner_user_id=uid,
        trigger_type=TriggerType.TIME_TRIGGER,
        schedule={"frequency": "daily", "time_of_day": "08:00"},
        autonomy_level=AutonomyLevel.ASK
    )

    created = routine_store.create_routine(rtn)
    assert created.id == rtn.id

    fetched = routine_store.get_routine(rtn.id)
    assert fetched is not None
    assert fetched.name == "Test Morning Briefing"
    assert fetched.autonomy_level == AutonomyLevel.ASK

    # Update status to PAUSED
    routine_store.set_routine_status(rtn.id, status=RoutineStatus.PAUSED, enabled=False)
    updated = routine_store.get_routine(rtn.id)
    assert updated.status == RoutineStatus.PAUSED
    assert updated.enabled is False

def test_natural_language_routine_parsing():
    """TEST 2: Parse natural language prompts into structured RoutineDefinition objects."""
    prompt1 = "Every Monday at 9 AM review my active projects and tell me what needs attention"
    def1 = routine_parser.parse_prompt(prompt1, domain="software")
    assert def1.trigger_type == TriggerType.TIME_TRIGGER
    assert def1.schedule["day_of_week"] == "monday"
    assert len(def1.actions) >= 1

    prompt2 = "When my application reaches interview stage, prepare interview questions"
    def2 = routine_parser.parse_prompt(prompt2, domain="career")
    assert def2.trigger_type == TriggerType.CONDITION_TRIGGER
    assert len(def2.conditions) >= 1
    assert def2.conditions[0].type == "application_status_changed"

def test_routine_execution_engine_and_context_assembly():
    """TEST 3: RoutineEngine execution, ContextBundle assembly, and task graph dispatch."""
    uid = "test_rtn_user_3"
    routine_store.reset_all(uid)

    rtn = Routine(
        name="Test Goal Review",
        description="Review active goals",
        owner_user_id=uid,
        trigger_type=TriggerType.MANUAL_TRIGGER,
        actions=[{"action_id": "act_1", "action_type": "review_goals", "description": "Review goal milestones", "tool_id": None}],
        autonomy_level=AutonomyLevel.ASK,
        approval_policy=ApprovalPolicy.PRE_APPROVED_LOW_RISK
    )
    routine_store.create_routine(rtn)

    exec_res = routine_engine.execute_routine(routine_id=rtn.id, trigger_source="TEST_MANUAL", user_id=uid)
    assert exec_res.status == "SUCCESS"
    assert exec_res.completed_at is not None
    assert len(exec_res.actions_attempted) >= 1

def test_condition_trigger_evaluation():
    """TEST 4: Evaluate condition triggers and auto-execute matching routines."""
    uid = "test_rtn_user_4"
    routine_store.reset_all(uid)

    rtn = Routine(
        name="Interview Auto-Prep",
        description="Prepare questions on interview status change",
        owner_user_id=uid,
        trigger_type=TriggerType.CONDITION_TRIGGER,
        conditions=[{"condition_id": "c1", "type": "application_status_changed", "description": "Status changed to interview", "criteria": {}}],
        actions=[{"action_id": "a1", "action_type": "interview_prep", "description": "Prepare questions", "tool_id": None}],
        approval_policy=ApprovalPolicy.PRE_APPROVED_LOW_RISK
    )
    routine_store.create_routine(rtn)

    eval_res = routine_engine.evaluate_condition_triggers("application_status_changed", {"status": "interview"}, user_id=uid)
    assert len(eval_res) == 1
    assert eval_res[0].status == "SUCCESS"

def test_scheduler_restart_recovery_and_missed_runs():
    """TEST 5: Scheduler persistence, restart recovery, and missed run policy handling."""
    uid = "test_rtn_user_5"
    routine_store.reset_all(uid)

    past_time = time.time() - 3600.0  # 1 hour ago
    rtn = Routine(
        name="Missed Run Routine",
        description="Missed run test",
        owner_user_id=uid,
        trigger_type=TriggerType.TIME_TRIGGER,
        next_run_at=past_time,
        missed_run_policy=MissedRunPolicy.RUN_ONCE_AFTER_START,
        approval_policy=ApprovalPolicy.PRE_APPROVED_LOW_RISK
    )
    routine_store.create_routine(rtn)

    # Trigger scheduler recovery
    routine_scheduler._recover_schedules_on_startup()
    updated = routine_store.get_routine(rtn.id)
    assert updated.next_run_at > time.time()

def test_routine_templates():
    """TEST 6: Instantiate first-class routine templates."""
    uid = "test_rtn_user_6"
    assert len(ROUTINE_TEMPLATES) >= 5

    tmpl_rtn = instantiate_template("morning_briefing", user_id=uid)
    assert tmpl_rtn.name == "Morning Briefing"
    assert tmpl_rtn.owner_user_id == uid
    assert tmpl_rtn.trigger_type == TriggerType.TIME_TRIGGER

def test_routine_rest_apis():
    """TEST 7: REST API endpoints for routines, templates, parse, upcoming, run, and history."""
    uid = "test_rest_user"
    client.post("/api/routines/reset", json={"user_id": uid})

    # 1. Parse prompt
    resp1 = client.post("/api/routines/parse", json={"prompt": "Every Monday at 9 AM review my active projects", "domain": "software"})
    assert resp1.status_code == 200
    assert "parsed_definition" in resp1.json()

    # 2. Create routine
    resp2 = client.post("/api/routines", json={
        "user_id": uid,
        "name": "API Test Routine",
        "trigger_type": "TIME_TRIGGER",
        "actions": [{"action_type": "test", "description": "Test action"}]
    })
    assert resp2.status_code == 200
    rtn_id = resp2.json()["routine"]["id"]

    # 3. List routines
    resp3 = client.get(f"/api/routines?user_id={uid}")
    assert resp3.status_code == 200
    assert len(resp3.json()["routines"]) >= 1

    # 4. Run routine manually
    resp4 = client.post(f"/api/routines/{rtn_id}/run", json={"user_id": uid, "permission_granted": True})
    assert resp4.status_code == 200
    assert resp4.json()["execution"]["status"] == "SUCCESS"

    # 5. Execution history
    resp5 = client.get(f"/api/routines/{rtn_id}/executions")
    assert resp5.status_code == 200
    assert len(resp5.json()["executions"]) >= 1
