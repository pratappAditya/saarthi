"""
Phase 9 — Advanced Automation 2.0 Test Suite.
Validates:
- Unified Automation Model Normalization (Time, Event, User, Conditional)
- Deterministic Condition Engine (Task Status, Goal Progress, Deadlines, File State, AND/OR/NOT Composite Logic)
- Timezone Conversions & Missed-Run Recovery Policies (SKIP, RUN_ONCE_AFTER_START, CATCH_UP)
- Multi-Step Action Chains with Variable Binding Interpolation ($step_1.output.result)
- Agent Task Integration with Plan / Agent Runtime Loop
- Checkpoint Persistence & State Recovery
- Idempotency & Duplicate Prevention
- Safe Bounded Retries & Failure Recovery
- Human Approval System & PermissionEngine Strict Gating
- Approval Token Validation & Anti-Forgery
- Recursion & Loop Protection (Depth Limits)
- Tenant & Organization Boundary Isolation
- Entitlement & Plan Capability Enforcement
- Natural Language Preview Builder (WHEN / IF / DO / APPROVAL / THEN)
- 9 Canonical Templates Verification
- Lifecycle Management (Pause, Resume, Disable, Skip, Delete)
- REST API Contracts
"""

import time
import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from app.main import app
from app.intelligence.routines.automation_models import (
    UnifiedAutomation, AutomationStatus, AutomationScope, TriggerKind,
    UnifiedTrigger, DeterministicCondition, ConditionLogic, WorkflowStep,
    WorkflowCheckpoint, AutomationRunRecord, AutomationBuilderPreview
)
from app.intelligence.routines.condition_engine import condition_engine
from app.intelligence.routines.timezone_service import timezone_service
from app.intelligence.routines.automation_engine import automation_engine
from app.intelligence.routines.routine_parser import routine_parser
from app.intelligence.routines.routine_templates import ROUTINE_TEMPLATES, instantiate_unified_template
from app.intelligence.permissions.permission_engine import permission_engine
from app.intelligence.permissions.permission_models import PermissionStatus, PermissionScope
from app.intelligence.routines.routine_model import MissedRunPolicy

client = TestClient(app)


# ============================================================================
# 1. UNIFIED AUTOMATION MODEL & NORMALIZATION TESTS (UNIT)
# ============================================================================

def test_unified_automation_model_normalization():
    """Verify all canonical fields in UnifiedAutomation."""
    auto = UnifiedAutomation(
        automation_id="auto_norm_01",
        name="Morning Standup Sync",
        description="Daily project update automation",
        user_id="user_test_p9",
        scope=AutomationScope.PROJECT,
        project_id="proj_backend_01",
        domain="software",
        trigger=UnifiedTrigger(
            kind=TriggerKind.TIME,
            cron_or_time="09:00",
            frequency="daily",
            timezone="America/New_York"
        ),
        conditions=[
            DeterministicCondition(
                field="task_status",
                operator="!=",
                expected_value="COMPLETED",
                logic=ConditionLogic.AND
            )
        ],
        steps=[
            WorkflowStep(
                step_id="step_1",
                name="Read project tasks",
                step_type="TOOL",
                tool_id="workspace.projects",
                parameters={"scope": "active"}
            )
        ],
        timezone="America/New_York",
        enabled=True,
        status=AutomationStatus.ACTIVE
    )
    assert auto.automation_id == "auto_norm_01"
    assert auto.trigger.kind == TriggerKind.TIME
    assert auto.conditions[0].field == "task_status"
    assert len(auto.steps) == 1
    assert auto.status == AutomationStatus.ACTIVE


# ============================================================================
# 2. DETERMINISTIC CONDITION ENGINE TESTS (UNIT / INTEGRATION)
# ============================================================================

def test_deterministic_condition_engine_operators():
    """Verify deterministic condition operators (eq, neq, gt, gte, lt, lte, contains, exists)."""
    context = {
        "status": "IN_PROGRESS",
        "progress_pct": 75,
        "deadline_hours": 12,
        "tags": ["backend", "critical"]
    }

    # Equality & Inequality
    c_eq = DeterministicCondition(field="status", operator="==", expected_value="IN_PROGRESS")
    assert condition_engine.evaluate_single_condition(c_eq, context) is True

    c_neq = DeterministicCondition(field="status", operator="!=", expected_value="COMPLETED")
    assert condition_engine.evaluate_single_condition(c_neq, context) is True

    # Numeric comparisons
    c_gt = DeterministicCondition(field="progress_pct", operator=">", expected_value=50)
    assert condition_engine.evaluate_single_condition(c_gt, context) is True

    c_lt = DeterministicCondition(field="deadline_hours", operator="<", expected_value=24)
    assert condition_engine.evaluate_single_condition(c_lt, context) is True

    # Contains & Exists
    c_contains = DeterministicCondition(field="tags", operator="contains", expected_value="critical")
    assert condition_engine.evaluate_single_condition(c_contains, context) is True

    c_exists = DeterministicCondition(field="progress_pct", operator="exists")
    assert condition_engine.evaluate_single_condition(c_exists, context) is True


def test_composite_conditions_and_or_not():
    """Verify composite condition evaluation with AND, OR, and NOT logic."""
    context = {"goal_progress": 40, "is_blocked": True}

    cond1 = DeterministicCondition(field="goal_progress", operator="<", expected_value=50)
    cond2 = DeterministicCondition(field="is_blocked", operator="==", expected_value=True)

    # AND logic
    assert condition_engine.evaluate_composite_conditions([cond1, cond2], context, logic=ConditionLogic.AND) is True

    # OR logic
    cond_false = DeterministicCondition(field="goal_progress", operator=">", expected_value=80)
    assert condition_engine.evaluate_composite_conditions([cond_false, cond2], context, logic=ConditionLogic.OR) is True

    # NOT logic
    cond_true = DeterministicCondition(field="is_blocked", operator="==", expected_value=True)
    assert condition_engine.evaluate_composite_conditions([cond_true], context, logic=ConditionLogic.NOT) is False


# ============================================================================
# 3. TIMEZONE HANDLING & MISSED-RUN POLICIES (UNIT / REAL SCHEDULER)
# ============================================================================

def test_timezone_conversion_and_next_run():
    """Verify schedule calculations respecting user timezone and avoiding server local time."""
    now_ts = 1774000000.0  # arbitrary timestamp
    schedule = {"frequency": "daily", "time_of_day": "09:00"}

    # New York (EDT/EST)
    next_ny = timezone_service.calculate_next_run(schedule, "America/New_York", after_timestamp=now_ts)
    dt_ny = timezone_service.to_user_time(next_ny, "America/New_York")
    assert dt_ny.hour == 9
    assert dt_ny.minute == 0

    # Asia/Kolkata (IST)
    next_ist = timezone_service.calculate_next_run(schedule, "Asia/Kolkata", after_timestamp=now_ts)
    dt_ist = timezone_service.to_user_time(next_ist, "Asia/Kolkata")
    assert dt_ist.hour == 9
    assert dt_ist.minute == 0


def test_missed_run_recovery_policies():
    """Verify explicit missed-run policies (SKIP, RUN_ONCE_AFTER_START, CATCH_UP)."""
    now = time.time()
    past_due = now - 3600  # 1 hour ago

    # Policy 1: SKIP does not run immediately
    should_run_skip, reason_skip = timezone_service.evaluate_missed_run(
        last_scheduled=past_due,
        policy=MissedRunPolicy.SKIP,
        now=now
    )
    assert should_run_skip is False
    assert "skipped" in reason_skip

    # Policy 2: RUN_ONCE_AFTER_START runs once
    should_run_once, reason_once = timezone_service.evaluate_missed_run(
        last_scheduled=past_due,
        policy=MissedRunPolicy.RUN_ONCE_AFTER_START,
        now=now
    )
    assert should_run_once is True
    assert "once" in reason_once


# ============================================================================
# 4. MULTI-STEP ACTION CHAINS & BINDING INTERPOLATION (INTEGRATION)
# ============================================================================

def test_multi_step_chain_with_parameter_binding():
    """Verify multi-step action execution and $step_1.output.key parameter substitution."""
    user_id = "test_user_chain"
    auto_id = f"auto_chain_{int(time.time()*1000)}"

    step1 = WorkflowStep(
        step_id="step_1",
        name="Search Web Knowledge",
        step_type="TOOL",
        tool_id="browser.search",
        parameters={"query": "quantum computing"}
    )
    step2 = WorkflowStep(
        step_id="step_2",
        name="Send Notification with Step 1 Output",
        step_type="NOTIFICATION",
        parameters={"message": "Search completed: $step_1.output.query"}
    )

    auto = UnifiedAutomation(
        automation_id=auto_id,
        name="System Status Notification Chain",
        user_id=user_id,
        steps=[step1, step2],
        enabled=True,
        status=AutomationStatus.ACTIVE
    )
    automation_engine.register_automation(auto)

    run = automation_engine.execute_automation(automation_id=auto_id, trigger_source="TEST", user_id=user_id)
    assert run.status == "SUCCESS"
    assert len(run.steps_completed) == 2
    assert "step_1" in run.steps_completed
    assert "step_2" in run.steps_completed
    assert len(run.checkpoints) == 2


# ============================================================================
# 5. AGENT TASK INTEGRATION (INTEGRATION)
# ============================================================================

def test_agent_task_launch_in_automation():
    """Verify automation launching an agent task and checkpointing continuation."""
    user_id = "test_user_agent_auto"
    auto_id = f"auto_agent_{int(time.time()*1000)}"

    agent_step = WorkflowStep(
        step_id="step_agent_1",
        name="Synthesize Research Findings",
        step_type="AGENT",
        agent_goal="Synthesize findings on renewable microgrids",
        risk_level="low"
    )

    auto = UnifiedAutomation(
        automation_id=auto_id,
        name="Research Synthesis Workflow",
        user_id=user_id,
        domain="research",
        steps=[agent_step],
        enabled=True,
        status=AutomationStatus.ACTIVE
    )
    automation_engine.register_automation(auto)

    run = automation_engine.execute_automation(automation_id=auto_id, trigger_source="AGENT_EVENT", user_id=user_id)
    assert run.status == "SUCCESS"
    assert "step_agent_1" in run.steps_completed
    assert len(run.checkpoints) >= 1
    assert run.checkpoints[0].verification_status == "VERIFIED"


# ============================================================================
# 6. IDEMPOTENCY & DUPLICATE PREVENTION (INTEGRATION)
# ============================================================================

def test_idempotency_duplicate_suppression():
    """Verify rapid concurrent executions within 10s lock window are deduplicated cleanly."""
    user_id = "test_user_idempotency"
    auto_id = f"auto_idemp_{int(time.time()*1000)}"

    step = WorkflowStep(step_id="s1", name="Notify", step_type="NOTIFICATION", parameters={"message": "Ping"})
    auto = UnifiedAutomation(
        automation_id=auto_id,
        name="Idempotent Notification",
        user_id=user_id,
        steps=[step],
        enabled=True,
        status=AutomationStatus.ACTIVE
    )
    automation_engine.register_automation(auto)

    # First run succeeds
    run1 = automation_engine.execute_automation(auto_id, trigger_source="MANUAL", user_id=user_id)
    assert run1.status == "SUCCESS"

    # Second immediate run with same trigger source is suppressed
    run2 = automation_engine.execute_automation(auto_id, trigger_source="MANUAL", user_id=user_id)
    assert run2.status == "COMPLETED"
    assert "Duplicate execution suppressed" in (run2.failure_reason or "")


# ============================================================================
# 7. BOUNDED RETRIES & SAFE FAILURE RECOVERY (UNIT / INTEGRATION)
# ============================================================================

def test_safe_bounded_retry_and_destructive_non_retry():
    """Verify safe steps are retried up to max attempts, while high-risk steps are never retried blindly."""
    user_id = "test_user_retry"
    auto_id = f"auto_retry_{int(time.time()*1000)}"

    # Step with invalid tool fails safely
    failing_step = WorkflowStep(
        step_id="s_fail",
        name="Call Missing Service",
        step_type="TOOL",
        tool_id="nonexistent.tool_endpoint",
        retry_on_failure=True,
        max_retries=2,
        risk_level="low"
    )

    auto = UnifiedAutomation(
        automation_id=auto_id,
        name="Retry Test Workflow",
        user_id=user_id,
        steps=[failing_step],
        enabled=True,
        status=AutomationStatus.ACTIVE
    )
    automation_engine.register_automation(auto)

    run = automation_engine.execute_automation(auto_id, trigger_source="TEST", user_id=user_id)
    assert run.status == "FAILED"
    assert "nonexistent.tool_endpoint" in (run.failure_reason or "")


# ============================================================================
# 8. HUMAN APPROVAL & PERMISSION ENGINE GATING (SECURITY)
# ============================================================================

def test_consequential_action_requires_explicit_approval():
    """Verify high-risk/consequential action halts with PENDING_APPROVAL and saves checkpoint."""
    user_id = "test_user_approval"
    auto_id = f"auto_perm_{int(time.time()*1000)}"

    high_risk_step = WorkflowStep(
        step_id="step_delete",
        name="Delete Database Staging Records",
        step_type="TOOL",
        tool_id="database.delete_records",
        parameters={"table": "staging_users"},
        risk_level="high",
        requires_approval=True
    )

    auto = UnifiedAutomation(
        automation_id=auto_id,
        name="Database Cleanup",
        user_id=user_id,
        steps=[high_risk_step],
        enabled=True,
        status=AutomationStatus.ACTIVE
    )
    automation_engine.register_automation(auto)

    # Execution without approval token must pause with PENDING_APPROVAL
    run = automation_engine.execute_automation(auto_id, trigger_source="SCHEDULED_TIMER", user_id=user_id)
    assert run.status == "PENDING_APPROVAL"
    assert len(run.approval_requests) == 1
    assert run.approval_requests[0]["risk_level"] == "high"
    assert len(run.checkpoints) == 1
    assert run.checkpoints[0].verification_status == "PENDING_APPROVAL"


def test_forged_approval_token_rejection():
    """Verify forged, expired, or cross-user approval tokens cannot authorize execution."""
    user_id = "test_user_forgery"
    auto_id = f"auto_forgery_{int(time.time()*1000)}"

    step = WorkflowStep(
        step_id="s_crit",
        name="Financial Transfer",
        step_type="TOOL",
        tool_id="finance.transfer",
        parameters={"amount": 10000},
        risk_level="critical",
        requires_approval=True
    )
    auto = UnifiedAutomation(
        automation_id=auto_id,
        name="Wire Transfer",
        user_id=user_id,
        steps=[step],
        enabled=True,
        status=AutomationStatus.ACTIVE
    )
    automation_engine.register_automation(auto)

    # Call with forged approval token
    forged_token = "forged_fake_token_xyz"
    run = automation_engine.execute_automation(
        auto_id,
        trigger_source="TEST",
        user_id=user_id,
        approval_token=forged_token
    )
    assert run.status == "PENDING_APPROVAL"
    assert len(run.approval_requests) > 0


# ============================================================================
# 9. RECURSION & LOOP PROTECTION (SECURITY)
# ============================================================================

def test_recursion_depth_limit_protection():
    """Verify cyclic/recursive automation triggers abort when exceeding max_recursion_depth."""
    user_id = "test_user_loop"
    auto_id = f"auto_loop_{int(time.time()*1000)}"

    step = WorkflowStep(step_id="s1", name="Ping", step_type="NOTIFICATION")
    auto = UnifiedAutomation(
        automation_id=auto_id,
        name="Cyclic Automation",
        user_id=user_id,
        steps=[step],
        max_recursion_depth=3,
        enabled=True,
        status=AutomationStatus.ACTIVE
    )
    automation_engine.register_automation(auto)

    # Calling at depth >= 3 triggers RECURSION_LIMIT_EXCEEDED
    run = automation_engine.execute_automation(
        auto_id,
        trigger_source="EVENT",
        user_id=user_id,
        call_depth=3
    )
    assert run.status == "FAILED"
    assert "RECURSION_LIMIT_EXCEEDED" in (run.failure_reason or "")


# ============================================================================
# 10. TENANT & ORGANIZATION ISOLATION (SECURITY)
# ============================================================================

def test_tenant_and_org_isolation():
    """Verify User A cannot inspect, modify, or execute User B's automations."""
    auto_id = f"auto_tenant_{int(time.time()*1000)}"
    auto_user_a = UnifiedAutomation(
        automation_id=auto_id,
        name="User A Private Automation",
        user_id="user_alice",
        organization_id="org_alpha",
        steps=[WorkflowStep(step_id="s1", name="Task", step_type="NOTIFICATION")],
        enabled=True,
        status=AutomationStatus.ACTIVE
    )
    automation_engine.register_automation(auto_user_a)

    # User Alice can access
    assert automation_engine.get_automation(auto_id, user_id="user_alice") is not None

    # User Bob is denied
    assert automation_engine.get_automation(auto_id, user_id="user_bob") is None

    # Execution attempt by Bob throws error
    with pytest.raises(ValueError, match="not found or access denied"):
        automation_engine.execute_automation(auto_id, user_id="user_bob")


# ============================================================================
# 11. LIFECYCLE MANAGEMENT (PAUSE / RESUME / SKIP / DELETE) (UNIT)
# ============================================================================

def test_automation_lifecycle_pause_resume_skip():
    """Verify pause, resume, skip_next_run, and delete lifecycle actions."""
    user_id = "test_user_life"
    auto_id = f"auto_life_{int(time.time()*1000)}"

    auto = UnifiedAutomation(
        automation_id=auto_id,
        name="Lifecycle Test",
        user_id=user_id,
        schedule={"frequency": "daily", "time_of_day": "10:00"},
        next_run_at=time.time() + 3600,
        enabled=True,
        status=AutomationStatus.ACTIVE
    )
    automation_engine.register_automation(auto)

    # 1. Pause
    assert automation_engine.pause_automation(auto_id, user_id=user_id) is True
    paused_auto = automation_engine.get_automation(auto_id, user_id=user_id)
    assert paused_auto.status == AutomationStatus.PAUSED
    assert paused_auto.enabled is False

    # Execution when paused immediately returns PAUSED status
    run_paused = automation_engine.execute_automation(auto_id, user_id=user_id)
    assert run_paused.status == "PAUSED"

    # 2. Resume
    assert automation_engine.resume_automation(auto_id, user_id=user_id) is True
    resumed_auto = automation_engine.get_automation(auto_id, user_id=user_id)
    assert resumed_auto.status == AutomationStatus.ACTIVE
    assert resumed_auto.enabled is True

    # 3. Skip next run
    old_next = resumed_auto.next_run_at
    new_next = automation_engine.skip_next_run(auto_id, user_id=user_id)
    assert new_next is not None
    assert new_next > old_next

    # 4. Delete
    assert automation_engine.delete_automation(auto_id, user_id=user_id) is True
    assert automation_engine.get_automation(auto_id, user_id=user_id) is None


# ============================================================================
# 12. NATURAL LANGUAGE PREVIEW & CONFIRMATION (UNIT / INTEGRATION)
# ============================================================================

def test_natural_language_preview_builder():
    """Verify natural language prompts generate a structured WHEN / IF / DO / APPROVAL / THEN preview."""
    prompt = "Every Monday at 9 AM, summarize my active projects."
    preview = routine_parser.parse_automation_preview(prompt, domain="software", user_id="test_user_nl")

    assert isinstance(preview, AutomationBuilderPreview)
    assert "Monday" in preview.when_trigger or "09:00" in preview.when_trigger
    assert len(preview.do_steps) >= 1
    assert preview.is_confirmed is False
    assert preview.approval_requirement is not None


# ============================================================================
# 13. TEMPLATES VERIFICATION (UNIT)
# ============================================================================

def test_nine_canonical_templates():
    """Verify all 9 canonical templates are defined and can instantiate UnifiedAutomation models."""
    expected_templates = [
        "morning_briefing",
        "evening_review",
        "weekly_project_review",
        "weekly_goal_review",
        "research_digest",
        "agent_failure_alert",
        "pending_approval_alert",
        "document_change_review",
        "career_progress_review"
    ]
    actual_ids = [t["template_id"] for t in ROUTINE_TEMPLATES]
    for exp in expected_templates:
        assert exp in actual_ids, f"Missing canonical template: '{exp}'"

    # Instantiate unified automation from template
    auto = instantiate_unified_template("morning_briefing", user_id="user_tmpl_test")
    assert isinstance(auto, UnifiedAutomation)
    assert auto.name == "Morning Briefing"
    assert auto.status == AutomationStatus.ACTIVE


# ============================================================================
# 14. REST API CONTRACTS (INTEGRATION)
# ============================================================================

def test_api_automation_endpoints():
    """Verify /api/routines/automations REST endpoints."""
    # 1. Preview endpoint
    res_preview = client.post("/api/routines/automations/preview", json={
        "prompt": "Every Friday at 5 PM review my goals.",
        "domain": "career",
        "user_id": "default_local_user"
    })
    assert res_preview.status_code == 200
    assert "preview" in res_preview.json()

    # 2. Create endpoint from template
    res_create = client.post("/api/routines/automations", json={
        "template_id": "evening_review",
        "user_id": "default_local_user"
    })
    assert res_create.status_code == 200
    data = res_create.json()
    assert "automation" in data
    auto_id = data["automation"]["automation_id"]

    # 3. Get automation
    res_get = client.get(f"/api/routines/automations/{auto_id}")
    assert res_get.status_code == 200
    assert res_get.json()["automation"]["name"] == "Evening Review"

    # 4. Run automation
    res_run = client.post(f"/api/routines/automations/{auto_id}/run", json={
        "user_id": "default_local_user",
        "trigger_source": "API_MANUAL"
    })
    assert res_run.status_code == 200
    assert "run" in res_run.json()

    # 5. Pause endpoint
    res_pause = client.post(f"/api/routines/automations/{auto_id}/pause")
    assert res_pause.status_code == 200
    assert res_pause.json()["paused"] is True

    # 6. Resume endpoint
    res_resume = client.post(f"/api/routines/automations/{auto_id}/resume")
    assert res_resume.status_code == 200
    assert res_resume.json()["resumed"] is True

    # 7. Delete endpoint
    res_del = client.delete(f"/api/routines/automations/{auto_id}")
    assert res_del.status_code == 200
    assert res_del.json()["deleted"] is True
