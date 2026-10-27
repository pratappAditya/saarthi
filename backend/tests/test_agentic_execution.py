import pytest
from fastapi.testclient import TestClient
from app.main import app

from app.intelligence.tools.tool_registry import ToolRegistry, RiskLevel
from app.intelligence.tools.tool_executor import tool_executor
from app.intelligence.planning.task_store import task_store
from app.intelligence.planning.planner import planner_service
from app.intelligence.agents.agent_runtime import agent_runtime

client = TestClient(app)

def test_tool_registration_and_risk_classification():
    """TEST 1: Tool registry catalog and risk classification."""
    tools = ToolRegistry.list_tools()
    assert len(tools) >= 5
    read_tool = ToolRegistry.get_tool("file.read")
    assert read_tool is not None
    assert read_tool.risk_level == RiskLevel.READ_ONLY

    term_tool = ToolRegistry.get_tool("terminal.execute")
    assert term_tool is not None
    assert term_tool.requires_confirmation is True

def test_tool_execution_verification_and_id():
    """TEST 2: Tool execution produces execution_id and verification metrics."""
    res = tool_executor.execute_tool(
        tool_id="career.analyze_jd",
        arguments={"jd_text": "Senior C++ Engineer with 5 years experience in Nmap."}
    )
    assert res["success"] is True
    assert "execution_id" in res
    assert res["verified"] is True

def test_sqlite_task_persistence():
    """TEST 3: Agent tasks persist in SQLite and support status updates."""
    task = task_store.save_task(
        task_id="task_test_001",
        objective="Research Quantum Encryption",
        domain="research",
        status="in_progress",
        user_id="default_local_user",
        steps=[{"step_id": "step_1", "title": "Literature Query"}]
    )
    assert task["task_id"] == "task_test_001"

    updated = task_store.update_task_status("task_test_001", "completed")
    assert updated["status"] == "completed"

def test_dynamic_replanning_on_failure():
    """TEST 4: Planner service creates plans and handles dynamic re-planning on failure."""
    graph = planner_service.create_plan("Target Stripe Security Architect Role", domain="career")
    assert graph.task_id is not None
    assert len(graph.steps) >= 2

    replanned = planner_service.replan_on_failure(graph.task_id, "step_1", "Simulated step failure")
    assert replanned is not None
    assert len(replanned.steps) > len(graph.steps)

def test_task_cancellation_and_resumption():
    """TEST 5: Task cancellation and resumption."""
    graph = planner_service.create_plan("Sample Task", domain="general")
    cancelled = planner_service.cancel_task(graph.task_id)
    assert cancelled is True

    resumed = planner_service.resume_task(graph.task_id)
    assert resumed["status"] == "in_progress"

def test_agent_runtime_bounded_execution():
    """TEST 6: Bounded AgentRuntime execution loop with trace."""
    run_res = agent_runtime.run_agent(
        agent_id="career_architect",
        task_prompt="Apply for Senior Cybersecurity Engineer position."
    )
    assert run_res["success"] is True
    assert run_res["verified"] is True
    assert len(run_res["trace"]) >= 1

def test_agent_tasks_rest_apis():
    """TEST 7: Agent Tasks REST endpoints."""
    tasks_resp = client.get("/api/agents/tasks")
    assert tasks_resp.status_code == 200
    assert "tasks" in tasks_resp.json()
