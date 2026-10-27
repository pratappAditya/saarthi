import os
import sys

# Add backend directory to sys.path to ensure 'app' imports resolve cleanly
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Set model provider to mock globally for all unit tests to prevent hitting live Ollama
os.environ["MODEL_PROVIDER"] = "mock"

# Provide a dedicated non-placeholder test admin key for general integration tests
TEST_ADMIN_KEY = "test_configured_saarthi_admin_key_for_testing_suite_only_7777"

import pytest
import tempfile
from app.config.settings import settings

if not getattr(settings, "VENDOR_ADMIN_KEY", None) or settings.VENDOR_ADMIN_KEY in (
    "saarthi_vendor_secret_key_change_in_production", "dev_admin_key"
):
    settings.VENDOR_ADMIN_KEY = TEST_ADMIN_KEY
from app.db.auth import init_auth_tables
from app.db.billing_db import init_billing_tables
from app.db.admin_db import init_admin_tables
from app.licensing.payment import init_payment_tables
from app.db.career import init_career_tables
from app.db.profile import init_profile_table
from app.agent.orchestrator import init_agent_task_tables
from app.core.entitlements import AccountService
from app.intelligence.personalization.personalization_store import PersonalizationStore
from app.intelligence.routines.routine_store import RoutineStore
from app.intelligence.proactive.goal_system import GoalSystem
from app.intelligence.proactive.routine_manager import RoutineManager
from app.intelligence.projects.project_manager import ProjectManager
from app.intelligence.permissions.permission_engine import PermissionEngine
from app.intelligence.multimodal.attachment_manager import AttachmentManager
from app.intelligence.memory.memory_store import MemoryStore
from app.intelligence.audit.intelligence_audit import IntelligenceAuditService
from app.licensing.referral import ReferralManager

@pytest.fixture(autouse=True, scope="function")
def isolate_test_db(tmp_path):
    """
    Creates an isolated temporary database for each test to eliminate lock contention.
    """
    db_file = str(tmp_path / "test_saarthi.db")
    orig_db = settings.DATABASE_PATH
    settings.DATABASE_PATH = db_file
    try:
        init_auth_tables()
        init_billing_tables()
        init_admin_tables()
        init_payment_tables()
        init_career_tables()
        init_profile_table()
        init_agent_task_tables()
        from app.mcp.request_state import init_request_state_table
        init_request_state_table()
        from app.intelligence.planning.task_store import TaskStoreService
        TaskStoreService()._init_tables()
        AccountService()._init_account_tables()
        PersonalizationStore()._init_tables()
        RoutineStore()._init_db()
        GoalSystem()._init_tables()
        RoutineManager()._init_tables()
        ProjectManager()._init_tables()
        PermissionEngine()._init_tables()
        AttachmentManager()._init_tables()
        MemoryStore()._init_memory_tables()
        IntelligenceAuditService()._init_tables()
        ReferralManager()._init_db()
        from app.licensing.middleware import default_client_manager
        default_client_manager._init_db()
        yield db_file
    finally:
        settings.DATABASE_PATH = orig_db

