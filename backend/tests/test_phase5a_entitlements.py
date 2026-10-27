import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.plans import PlanService, PLAN_CATALOG, PLAN_FREE, PLAN_POWER, PLAN_STUDENT, PLAN_PERSONAL
from app.core.entitlements import account_service

client = TestClient(app)

def test_plan_catalog_and_taxonomy():
    """TEST 1: Verify all 6 plans and capability taxonomy exist in catalog."""
    catalog = PlanService.get_plan_catalog()
    assert "free" in catalog
    assert "student" in catalog
    assert "personal" in catalog
    assert "power" in catalog
    assert "teams" in catalog
    assert "enterprise" in catalog

    assert catalog["free"]["price_inr"] == 0
    assert catalog["student"]["price_inr"] == 99
    assert catalog["personal"]["price_inr"] == 399
    assert catalog["power"]["price_inr"] == 799
    assert catalog["teams"]["price_inr"] == 699

def test_plan_entitlement_matrix():
    """TEST 2: Verify capability matrix per plan."""
    free_caps = PlanService.get_capabilities_for_plan(PLAN_FREE)
    assert free_caps["career.master_resume"] is True
    assert free_caps["core.chat.basic"] is True
    assert free_caps["tools.terminal"] is False
    assert free_caps["agents.autonomous"] is False

    power_caps = PlanService.get_capabilities_for_plan(PLAN_POWER)
    assert power_caps["tools.terminal"] is True
    assert power_caps["agents.autonomous"] is True
    assert power_caps["voice.proactive"] is True
    assert power_caps["domain.cybersecurity"] is True

def test_account_endpoints():
    """TEST 3: Verify /api/account REST endpoints."""
    # 1. /api/account/plan
    plan_resp = client.get("/api/account/plan")
    assert plan_resp.status_code == 200
    assert "subscription" in plan_resp.json()
    assert "catalog" in plan_resp.json()

    # 2. /api/account/entitlements
    ent_resp = client.get("/api/account/entitlements")
    assert ent_resp.status_code == 200
    assert "capabilities" in ent_resp.json()

    # 3. /api/account/capabilities
    cap_resp = client.get("/api/account/capabilities")
    assert cap_resp.status_code == 200
    data = cap_resp.json()
    assert "entitlements" in data
    assert "limits" in data
    assert "domain_packs" in data
    assert len(data["domain_packs"]) >= 10

def test_dev_plan_switch_and_backend_authorization():
    """TEST 4: Switch plan to FREE, verify server 403 denial for STAR scoring, then switch to STUDENT."""
    # Switch to FREE
    switch_free = client.post("/api/account/dev-switch-plan", json={"plan_id": "free"})
    assert switch_free.status_code == 200
    assert switch_free.json()["subscription"]["plan_id"] == "free"

    # Attempt STAR scoring (requires career.star capability -> STUDENT minimum)
    star_resp = client.post("/api/career/interview/answers/1/score", json={
        "question_id": 1,
        "question": "Test question",
        "situation": "Test situation",
        "action": "Test action",
        "result": "Test result"
    })
    assert star_resp.status_code == 403
    assert star_resp.json()["detail"]["error"] == "ENTITLEMENT_FORBIDDEN"
    assert star_resp.json()["detail"]["capability"] == "career.star"

    # Switch to STUDENT
    switch_student = client.post("/api/account/dev-switch-plan", json={"plan_id": "student"})
    assert switch_student.status_code == 200
    assert switch_student.json()["subscription"]["plan_id"] == "student"

    # STAR scoring now allowed
    star_resp_2 = client.post("/api/career/interview/answers/1/score", json={
        "question_id": 1,
        "question": "Test question",
        "situation": "Test situation",
        "action": "Test action",
        "result": "Test result"
    })
    assert star_resp_2.status_code == 200

    # Reset dev plan back to POWER
    client.post("/api/account/dev-switch-plan", json={"plan_id": "power"})
