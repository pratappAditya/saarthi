"""
Phase 5 Production Test Suite: Advanced Agents + Computer Control + Multi-Step Autonomous Execution.
Verifies:
- Observe -> Plan -> Permission -> Act -> Verify -> Replan lifecycle
- Multi-step DAG planning with dependencies, conditions, and parallel steps
- Observable action verification (never claiming success without real post-condition verification)
- Desktop computer control (OBSERVATION vs ACTION, credential manager protection)
- Browser operations & SSRF protections
- File operations, tenant isolation, and path traversal guards
- Document generation & verification
- Research evidence classes (FACT, SOURCE-DERIVED, INFERENCE, UNCERTAIN)
- Strict server-side approval verification & anti-replay token revocation
- Dynamic failure diagnosis, replanning, and loop guards
- Task pause, resume, cancellation, and checkpoint rollback
- Multimodal untrusted content boundaries & prompt injection defense
- Universal intelligence core (single orchestrator across domains, desktop, voice)
"""

import os
import sys
import json
import pytest
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.config.settings import settings
from app.intelligence.planning.planner import planner_service
from app.intelligence.planning.task_graph import TaskGraph, TaskStep, TaskStatus
from app.intelligence.planning.task_store import task_store
from app.intelligence.agents.agent_runtime import agent_runtime
from app.intelligence.agents.verification import action_verification_service, VerificationResult
from app.intelligence.tools.tool_registry import ToolRegistry, RiskLevel
from app.intelligence.tools.tool_executor import tool_executor
from app.intelligence.permissions.permission_engine import permission_engine
from app.intelligence.permissions.permission_models import PermissionStatus, PermissionScope
from app.intelligence.orchestration.orchestrator import orchestrator
from app.intelligence.voice.voice_conversation_engine import voice_conversation_engine


# ============================================================
# 1. SIMPLE & MULTI-STEP TASK PLANNING TESTS
# ============================================================

def test_simple_agent_task_execution():
    """Verifies that a single-goal autonomous task executes and passes observable verification."""
    res = agent_runtime.run_agent(
        agent_id="general",
        task_prompt="Inspect workspace files and summarize notes",
        user_id="test_user_phase5"
    )
    assert res["success"] is True
    assert res["status"] in ["completed", "completed_with_replanning"]
    assert res["steps_executed"] >= 1
    assert res["verified"] is True
    assert len(res["trace"]) >= 1
    assert all("status" in t for t in res["trace"])


def test_multi_step_compound_planning_with_dependencies():
    """
    Verifies that a compound research, report, workspace save, and email draft goal
    decomposes into a 5-step DAG with explicit dependencies and domain transitions.
    """
    goal = "Research the latest information on quantum computing, compare the sources, create a report, save it to my project, and prepare an email draft."
    graph = planner_service.create_plan(goal=goal, domain="research", user_id="test_user_phase5")

    assert graph.task_id.startswith("task_")
    assert len(graph.steps) == 5

    step1 = graph.steps[0]
    step2 = graph.steps[1]
    step3 = graph.steps[2]
    step4 = graph.steps[3]
    step5 = graph.steps[4]

    # Verify sequential dependency chain
    assert step1.tool_id in ["browser.search", "research.multi_source"]
    assert step1.step_type == "OBSERVATION"

    assert "step_1" in step2.dependencies
    assert step2.tool_id == "research.synthesize"
    assert step2.step_type == "SYNTHESIS"

    assert "step_2" in step3.dependencies
    assert step3.tool_id == "document.generate_report"
    assert step3.step_type == "ACTION"

    assert "step_3" in step4.dependencies
    assert step4.tool_id == "file.write"
    assert step4.step_type == "ACTION"

    assert "step_3" in step5.dependencies
    assert step5.tool_id == "email.draft"
    assert step5.step_type == "ACTION"

    # Verify domain transitions
    assert len(graph.domain_transitions) >= 2


# ============================================================
# 2. OBSERVABLE ACTION VERIFICATION TESTS
# ============================================================

def test_action_verification_observable_evidence():
    """
    Verifies that ActionVerificationService inspects physical files on disk
    and rejects actions that claim success without observable proof.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = os.path.join(temp_dir, "verified_artifact.md")
        
        # 1. File does not exist yet -> verification must fail
        fake_result = {"file_path": test_file, "status": "written"}
        ver_fail = action_verification_service.verify("file.write", {"file_path": test_file}, fake_result)
        assert ver_fail.verified is False
        assert "does not exist on disk" in ver_fail.reason

        # 2. Write real non-empty file on physical disk -> verification must pass
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("# Executive Report\nObservable data verified.\n")
        
        real_result = {"file_path": test_file, "size_bytes": os.path.getsize(test_file), "status": "written"}
        ver_pass = action_verification_service.verify("file.write", {"file_path": test_file, "content": "Observable data"}, real_result)
        assert ver_pass.verified is True
        assert ver_pass.evidence["exists"] is True
        assert ver_pass.evidence["size_bytes"] > 0


def test_action_verification_rejects_empty_payload():
    """Ensures tool returning empty dictionary is never marked verified."""
    res = action_verification_service.verify("browser.navigate", {"url": "https://example.com"}, {})
    assert res.verified is False
    assert "empty or null" in res.reason


# ============================================================
# 3. COMPUTER CONTROL FOUNDATION TESTS
# ============================================================

def test_desktop_observation_vs_action_classification():
    """Verifies that desktop tools explicitly declare OBSERVATION vs ACTION."""
    obs_tool = ToolRegistry.get_tool("desktop.observe")
    assert obs_tool is not None
    assert obs_tool.operation_type == "OBSERVATION"
    assert obs_tool.risk_level == RiskLevel.READ_ONLY

    shot_tool = ToolRegistry.get_tool("desktop.capture_screenshot")
    assert shot_tool is not None
    assert shot_tool.operation_type == "OBSERVATION"

    insert_tool = ToolRegistry.get_tool("desktop.insert_text")
    assert insert_tool is not None
    assert insert_tool.operation_type == "ACTION"
    assert insert_tool.risk_level == RiskLevel.MODERATE


def test_desktop_insertion_credential_manager_protection():
    """Verifies that direct text insertion into password managers is blocked."""
    for sensitive_app in ["1Password", "Bitwarden", "KeePass", "LastPass Vault"]:
        res = tool_executor.execute_tool(
            tool_id="desktop.insert_text",
            arguments={"text": "sensitive_token", "target_app": sensitive_app},
            user_id="test_user_phase5",
            permission_granted=True
        )
        assert res["success"] is False
        assert "blocked by security policy" in res["message"]


def test_desktop_observation_and_screenshot():
    """Verifies desktop observe and screenshot capture return valid context and file."""
    obs_res = tool_executor.execute_tool(
        tool_id="desktop.observe",
        arguments={},
        user_id="test_user_phase5",
        permission_granted=True
    )
    assert obs_res["success"] is True
    assert obs_res["verified"] is True
    assert obs_res["operation_type"] == "OBSERVATION"
    assert "active_app" in obs_res["result"]

    shot_res = tool_executor.execute_tool(
        tool_id="desktop.capture_screenshot",
        arguments={"scope": "active_window"},
        user_id="test_user_phase5",
        permission_granted=True
    )
    assert shot_res["success"] is True
    assert shot_res["verified"] is True
    assert os.path.exists(shot_res["result"]["screenshot_path"])


# ============================================================
# 4. BROWSER OPERATIONS & SSRF PROTECTION TESTS
# ============================================================

def test_browser_ssrf_prevention():
    """Verifies that private IP ranges, localhost, and metadata endpoints are blocked."""
    forbidden_urls = [
        "http://127.0.0.1:8080/admin",
        "http://localhost/secret",
        "http://169.254.169.254/latest/meta-data/",
        "http://10.0.0.1/internal",
        "http://192.168.1.1/router",
        "http://172.16.0.5/private"
    ]
    for url in forbidden_urls:
        res = tool_executor.execute_tool(
            tool_id="browser.navigate",
            arguments={"url": url},
            user_id="test_user_phase5",
            permission_granted=True
        )
        assert res["success"] is False
        assert "blocked for security" in res["message"] or "Invalid URL" in res["message"]


def test_browser_invalid_scheme_blocked():
    """Verifies that dangerous non-HTTP schemes are rejected."""
    for bad_url in ["file:///etc/passwd", "javascript:alert(1)", "gopher://evil.com"]:
        res = tool_executor.execute_tool(
            tool_id="browser.navigate",
            arguments={"url": bad_url},
            user_id="test_user_phase5",
            permission_granted=True
        )
        assert res["success"] is False
        assert "Only HTTP and HTTPS are permitted" in res["message"]


def test_browser_navigation_and_extraction():
    """Verifies safe web navigation and structured content extraction."""
    nav_res = tool_executor.execute_tool(
        tool_id="browser.navigate",
        arguments={"url": "https://example.com/research"},
        user_id="test_user_phase5",
        permission_granted=True
    )
    assert nav_res["success"] is True
    assert nav_res["verified"] is True
    assert nav_res["result"]["status_code"] == 200

    ext_res = tool_executor.execute_tool(
        tool_id="browser.extract",
        arguments={"url": "https://example.com/research", "selector": "article"},
        user_id="test_user_phase5",
        permission_granted=True
    )
    assert ext_res["success"] is True
    assert ext_res["verified"] is True
    assert len(ext_res["result"]["extracted_content"]) > 0


# ============================================================
# 5. FILE OPERATIONS & PATH TRAVERSAL TESTS
# ============================================================

def test_file_path_traversal_protection():
    """Verifies that directory traversal (../) attacks are blocked."""
    traversal_paths = [
        "../../../../windows/system32/cmd.exe",
        "../../../etc/shadow",
        "workspace/../../.env"
    ]
    for p in traversal_paths:
        res = tool_executor.execute_tool(
            tool_id="file.read",
            arguments={"file_path": p},
            user_id="test_user_phase5",
            permission_granted=True
        )
        assert res["success"] is False
        assert "Path traversal detected" in res["message"] or "sensitive file" in res["message"]


def test_file_lifecycle_write_read_move_delete():
    """Tests the full observable file lifecycle: create -> read -> move -> delete."""
    user_id = "test_user_phase5_files"
    filename = "lifecycle_test.txt"
    content = "Sample content for Phase 5 verification test."

    # 1. Write file
    w_res = tool_executor.execute_tool(
        tool_id="file.write",
        arguments={"file_path": filename, "content": content},
        user_id=user_id,
        permission_granted=True
    )
    assert w_res["success"] is True
    assert w_res["verified"] is True
    created_path = w_res["result"]["file_path"]
    assert os.path.exists(created_path)

    # 2. Read file
    r_res = tool_executor.execute_tool(
        tool_id="file.read",
        arguments={"file_path": filename},
        user_id=user_id,
        permission_granted=True
    )
    assert r_res["success"] is True
    assert r_res["result"]["content"] == content

    # 3. Move file
    moved_name = "lifecycle_moved.txt"
    m_res = tool_executor.execute_tool(
        tool_id="file.move",
        arguments={"source_path": filename, "destination_path": moved_name},
        user_id=user_id,
        permission_granted=True
    )
    assert m_res["success"] is True
    assert m_res["verified"] is True
    assert os.path.exists(m_res["result"]["destination_path"])
    assert not os.path.exists(created_path)

    # 4. Delete file (requires approval if not granted)
    d_res = tool_executor.execute_tool(
        tool_id="file.delete",
        arguments={"file_path": moved_name},
        user_id=user_id,
        permission_granted=True
    )
    assert d_res["success"] is True
    assert d_res["verified"] is True
    assert not os.path.exists(m_res["result"]["destination_path"])


# ============================================================
# 6. DOCUMENT GENERATION & RESEARCH EVIDENCE TESTS
# ============================================================

def test_document_generation_and_disk_verification():
    """Verifies that generated documents exist on disk and have verified structural sections."""
    doc_res = tool_executor.execute_tool(
        tool_id="document.generate_report",
        arguments={
            "title": "Quantum Cryptography Audit",
            "content": "Comprehensive analysis of post-quantum lattice encryption.",
            "doc_type": "security_audit"
        },
        user_id="test_user_phase5",
        permission_granted=True
    )
    assert doc_res["success"] is True
    assert doc_res["verified"] is True
    path = doc_res["result"]["file_path"]
    assert os.path.exists(path)
    assert os.path.getsize(path) > 0
    assert len(doc_res["result"]["sections"]) >= 3


def test_research_evidence_classes_enforced():
    """
    Verifies that research synthesis categorizes claims strictly into:
    FACT, SOURCE-DERIVED, INFERENCE, UNCERTAIN.
    """
    res = tool_executor.execute_tool(
        tool_id="research.synthesize",
        arguments={"topic": "Archaeological Pottery Typology", "sources": ["Excavation Log 1", "Archival Registry"]},
        user_id="test_user_phase5",
        permission_granted=True
    )
    assert res["success"] is True
    assert res["verified"] is True
    evidence_classes = res["result"]["evidence_classes"]
    assert "FACT" in evidence_classes
    assert "SOURCE-DERIVED" in evidence_classes
    assert "INFERENCE" in evidence_classes
    assert "UNCERTAIN" in evidence_classes


# ============================================================
# 7. STRICT SERVER-SIDE APPROVAL & FORGERY PREVENTION TESTS
# ============================================================

def test_strict_server_side_approval_required_for_destructive_actions():
    """Verifies that high-risk actions pause and return PERMISSION_REQUIRED when approval is missing."""
    res = tool_executor.execute_tool(
        tool_id="file.delete",
        arguments={"file_path": "important_dataset.csv"},
        user_id="test_user_phase5",
        permission_granted=False,
        approval_token=None
    )
    assert res["success"] is False
    assert res["error"] == "PERMISSION_REQUIRED"
    assert "permission_request_id" in res


def test_approval_forgery_rejection():
    """Verifies that a forged approval token is rejected by the server."""
    res = tool_executor.execute_tool(
        tool_id="file.delete",
        arguments={"file_path": "important_dataset.csv"},
        user_id="test_user_phase5",
        permission_granted=False,
        approval_token="forged_token_12345"
    )
    assert res["success"] is False
    assert res["error"] == "PERMISSION_REQUIRED"


def test_approval_grant_and_one_time_revocation():
    """
    Verifies that a valid server-side approval allows execution,
    and the token is revoked afterwards to prevent replay attacks.
    """
    # 1. Create permission request in DB
    perm = permission_engine.request_permission(
        tool_id="terminal.execute",
        action_description="Execute terminal check",
        arguments={"command": "dir"},
        risk_level="HIGH_RISK",
        user_id="test_user_phase5"
    )
    assert perm.status == PermissionStatus.PENDING

    # 2. Grant permission on the server
    approved_perm = permission_engine.grant_permission(perm.request_id)
    assert approved_perm.status == PermissionStatus.APPROVED

    # 3. First execution with approval token succeeds
    res1 = tool_executor.execute_tool(
        tool_id="terminal.execute",
        arguments={"command": "dir"},
        user_id="test_user_phase5",
        approval_token=perm.request_id
    )
    assert res1["success"] is True

    # 4. Attempting replay with same token fails because it was revoked
    res2 = tool_executor.execute_tool(
        tool_id="terminal.execute",
        arguments={"command": "dir"},
        user_id="test_user_phase5",
        approval_token=perm.request_id
    )
    assert res2["success"] is False
    assert res2["error"] == "PERMISSION_REQUIRED"


# ============================================================
# 8. FAILURE RECOVERY, REPLANNING & LOOP GUARDS
# ============================================================

def test_dynamic_replanning_on_verification_failure():
    """Verifies that when a step fails verification, the planner generates a corrective fallback step."""
    task = planner_service.create_plan(goal="Inspect and clean directory files", domain="files", user_id="test_user_phase5")
    initial_step_count = len(task.steps)

    replan_graph = planner_service.replan_on_failure(
        task_id=task.task_id,
        failed_step_id="step_2",
        error_message="Directory not found",
        failure_diagnosis="Target workspace path was missing"
    )
    assert replan_graph is not None
    assert len(replan_graph.steps) == initial_step_count + 1
    fallback_step = replan_graph.steps[-1]
    assert "fallback" in fallback_step.step_id
    assert "step_2" in fallback_step.dependencies


def test_replan_loop_guard_prevents_infinite_loops():
    """Verifies that exceeding max replans (3) halts execution and prevents runaway loops."""
    task = planner_service.create_plan(goal="Unstable operation", domain="general", user_id="test_user_phase5")
    
    # Trigger 3 replans
    planner_service.replan_on_failure(task.task_id, "step_1", "Failure 1")
    planner_service.replan_on_failure(task.task_id, "step_1", "Failure 2")
    planner_service.replan_on_failure(task.task_id, "step_1", "Failure 3")

    # 4th replan should be rejected by loop guard
    fourth_replan = planner_service.replan_on_failure(task.task_id, "step_1", "Failure 4")
    assert fourth_replan is None
    
    task_after = task_store.get_task(task.task_id)
    assert task_after["status"] == "failed"


# ============================================================
# 9. PAUSE, RESUME, CANCELLATION & CHECKPOINTS TESTS
# ============================================================

def test_task_pause_resume_cancellation_lifecycle():
    """Verifies pause, resume, and cancel state transitions in task store."""
    task = planner_service.create_plan(goal="Long running background process", domain="general", user_id="test_user_phase5")
    task_id = task.task_id

    # Pause
    planner_service.pause_task(task_id)
    assert task_store.get_task(task_id)["status"] == "paused"

    # Resume
    planner_service.resume_task(task_id)
    assert task_store.get_task(task_id)["status"] == "in_progress"

    # Cancel
    planner_service.cancel_task(task_id)
    assert task_store.get_task(task_id)["status"] == "cancelled"


def test_milestone_checkpoints_and_rollback():
    """Verifies milestone checkpoint creation and rollback to previous state."""
    task = planner_service.create_plan(goal="Multi-stage project audit", domain="general", user_id="test_user_phase5")
    task_id = task.task_id

    # Create checkpoint
    chk_id = planner_service.create_checkpoint(task_id, "before_mutation")
    assert chk_id is not None
    assert chk_id in task_store.get_checkpoints(task_id)

    # Rollback to checkpoint
    rolled_back_graph = planner_service.rollback_to_checkpoint(task_id, chk_id)
    assert rolled_back_graph is not None
    assert rolled_back_graph.task_id == task_id


# ============================================================
# 10. MULTIMODAL UNTRUSTED BOUNDARY & VOICE-TO-AGENT TESTS
# ============================================================

def test_multimodal_untrusted_content_sanitization():
    """Verifies that screenshot and document processing treat content as untrusted input."""
    screen_res = tool_executor.execute_tool(
        tool_id="multimodal.analyze_screenshot",
        arguments={"image_path": "screen.png"},
        user_id="test_user_phase5",
        permission_granted=True
    )
    assert screen_res["success"] is True
    assert screen_res["result"]["untrusted_content_sanitized"] is True

    doc_res = tool_executor.execute_tool(
        tool_id="multimodal.process_document",
        arguments={"file_path": "input.pdf"},
        user_id="test_user_phase5",
        permission_granted=True
    )
    assert doc_res["success"] is True
    assert doc_res["result"]["untrusted_content_sanitized"] is True


def test_voice_turn_triggers_central_agent_planning():
    """Verifies that spoken instructions route into central orchestrator and generate agent plans."""
    session = voice_conversation_engine.start_session(user_id="test_voice_agent_user")
    
    spoken_instruction = "Research recent developments in quantum encryption and prepare a summary report"
    res = voice_conversation_engine.process_voice_turn(
        session_id=session.session_id,
        text_override=spoken_instruction,
        language_hint="en-IN"
    )
    assert res["status"] == "success"
    assert "audio_synthesis" in res
    assert res["assistant_text"] is not None
    voice_conversation_engine.stop_session(session.session_id)


def test_cross_domain_workflow_provenance_preservation():
    """Verifies that cross-domain archetypes preserve provenance across domains."""
    arch_goal = "Analyze excavation photographs of settlement pottery and compare with historical archival records"
    graph = planner_service.create_plan(goal=arch_goal, domain="archaeology", user_id="test_user_phase5")
    
    assert len(graph.subdomains) > 1
    assert "archaeology" in graph.subdomains
    assert "history" in graph.subdomains
    assert len(graph.domain_transitions) >= 1
    for tr in graph.domain_transitions:
        assert "from" in tr
        assert "to" in tr
        assert "reason" in tr


def test_tenant_isolation_paths():
    """Verifies that different users receive isolated workspace directories."""
    user1_p = tool_executor._sanitize_path("my_notes.txt", user_id="user_alice")
    user2_p = tool_executor._sanitize_path("my_notes.txt", user_id="user_bob")
    
    assert "user_alice" in user1_p
    assert "user_bob" in user2_p
    assert user1_p != user2_p
