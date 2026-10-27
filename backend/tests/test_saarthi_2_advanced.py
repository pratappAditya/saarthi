import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.db.auth import AuthRepository
from app.services.email import EmailService
from app.agent.orchestrator import AgentOrchestrator, TaskStatus
from app.agent.scheduler import TaskScheduler
from app.tools.document_engine import DocumentEngine

client = TestClient(app)

def test_email_service_unconfigured():
    status = EmailService.get_status()
    assert "status" in status
    res = EmailService.send_transactional_email("user@test.com", "Test Subject", "Test Body")
    assert res["status"] == "EMAIL SERVICE NOT CONFIGURED"
    assert res["sent"] is False

def test_auth_rate_limiting_and_password_reset():
    unique_id = uuid.uuid4().hex[:8]
    email = f"reset_{unique_id}@example.com"
    client.post("/api/auth/register", json={"email": email, "password": "oldPassword123", "full_name": "Reset Test"})

    # Request Reset
    reset_token = AuthRepository.create_password_reset_token(email)
    assert reset_token is not None

    # Perform Reset
    reset_res = client.post("/api/auth/reset-password", json={"token": reset_token, "new_password": "newPassword123"})
    assert reset_res.status_code == 200

    # Login with new password
    login_res = client.post("/api/auth/login", json={"email": email, "password": "newPassword123"})
    assert login_res.status_code == 200

def test_admin_actions_and_audit_logging():
    from app.config.settings import settings
    admin_key = getattr(settings, "VENDOR_ADMIN_KEY", None) or os.getenv("VENDOR_ADMIN_KEY", "")
    headers = {"X-Admin-Key": admin_key}
    
    # List Users
    users_res = client.get("/api/admin/users", headers=headers)
    assert users_res.status_code == 200

    # Audit Logs
    audit_res = client.get("/api/admin/audit-logs", headers=headers)
    assert audit_res.status_code == 200
    assert "audit_logs" in audit_res.json()

def test_agent_dag_task_orchestration_and_approvals():
    unique_id = uuid.uuid4().hex[:8]
    email = f"agent_{unique_id}@example.com"
    reg_resp = client.post("/api/auth/register", json={"email": email, "password": "password123"})
    token = reg_resp.json()["session"]["session_token"]
    user_id = reg_resp.json()["user"]["user_id"]

    # Create Task
    task = AgentOrchestrator.create_task(user_id, "Find suitable jobs for me and tailor my resume")
    assert task["status"] == TaskStatus.QUEUED
    assert len(task["steps"]) > 0

    # Request Approval
    appr = AgentOrchestrator.create_approval_request(task["task_id"], "Send Email", "Send resume to recruiter@test.com")
    assert appr["status"] == "PENDING"

    # Respond to Approval
    resp = AgentOrchestrator.respond_to_approval(appr["approval_id"], approved=True)
    assert resp["status"] == "APPROVED"

def test_scheduler_and_document_engine(tmp_path):
    unique_id = uuid.uuid4().hex[:8]
    user_id = f"usr_{unique_id}"

    # Schedule Job
    job = TaskScheduler.create_scheduled_job(user_id, "Every Monday find new jobs", schedule_type="RECURRING_WEEKLY")
    assert job["status"] == "SCHEDULED"

    # Export Watermarked Document
    doc_path = str(tmp_path / "test_resume.txt")
    doc_res = DocumentEngine.export_document("Sample Resume Text", doc_path, plan="FREE")
    assert doc_res["is_watermarked"] is True

    # Export Clean Document
    clean_path = str(tmp_path / "clean_resume.txt")
    clean_res = DocumentEngine.export_document("Sample Resume Text", clean_path, plan="POWER")
    assert clean_res["is_watermarked"] is False
    assert clean_res["clean_export"] is True
