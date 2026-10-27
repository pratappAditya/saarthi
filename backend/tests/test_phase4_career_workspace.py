import pytest
import os
import tempfile
import json
from fastapi.testclient import TestClient
from app.main import app
from app.db.career import CareerRepository, init_career_tables
from app.tools.career_workspace_engine import CareerWorkspaceEngine

client = TestClient(app)

@pytest.fixture
def temp_db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    init_career_tables(db_path)
    yield db_path
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass

def test_application_crud_and_stage_transitions(temp_db):
    """TEST 1: Application Tracker CRUD & 11-stage pipeline movement."""
    repo = CareerRepository(db_path=temp_db)
    
    # 1. Create
    app_item = repo.create_application({
        "company": "Stripe",
        "role": "Lead Security Architect",
        "job_url": "https://stripe.com/jobs/sec-arch",
        "location": "Remote",
        "salary": "$180,000 - $220,000",
        "status": "SAVED"
    })
    app_id = app_item["id"]
    assert app_item["company"] == "Stripe"
    assert app_item["status"] == "SAVED"

    # 2. Update Stage
    updated = repo.update_application(app_id, {"status": "TECHNICAL_INTERVIEW"})
    assert updated["status"] == "TECHNICAL_INTERVIEW"

    # 3. List
    apps = repo.list_applications()
    assert len(apps) == 1

    # 4. Delete
    deleted = repo.delete_application(app_id)
    assert deleted is True
    assert repo.get_application(app_id) is None

def test_interview_prep_and_star_8_dimension_scoring():
    """TEST 2: Generate interview questions & score STAR responses along 8 dimensions."""
    resume_data = {
        "raw_content": "Pratap Aditya\nCybersecurity Architect\nBuilt C++ stealth keylogger and NMAP packet sniffer."
    }
    jd_text = "Requires Lead Security Architect with C++, BASH, Nmap, and Incident Response expertise."

    questions = CareerWorkspaceEngine.generate_interview_questions(
        jd_text=jd_text,
        resume_data=resume_data,
        company="Stripe",
        role="Lead Security Architect"
    )
    assert len(questions) >= 3
    cat_types = [q["category"] for q in questions]
    assert "Technical" in cat_types or "Behavioral" in cat_types or "Gap" in cat_types

    # Score STAR Answer
    eval_res = CareerWorkspaceEngine.score_star_answer(
        question="Tell me about a time you triaged a critical security vulnerability.",
        situation="Identified zero-day memory leak in core C++ daemon.",
        task="Contained potential exploit vector within 2 hours.",
        action="Architected emergency patch, wrote automated regression tests, and deployed to staging.",
        result="Prevented data leakage across 50,000 active nodes with zero downtime."
    )
    assert eval_res["overall_score"] >= 80
    assert "Structure" in eval_res["dimensions"]
    assert "Specificity" in eval_res["dimensions"]
    assert "Impact" in eval_res["dimensions"]

def test_salary_coach_offer_analysis():
    """TEST 3: Salary coach breakdown & counter-offer draft distinguishing facts vs AI analysis."""
    offer_data = {
        "company": "Stripe",
        "role": "Lead Security Architect",
        "base_salary": 140000,
        "variable_pay": 20000,
        "bonus": 15000,
        "equity": "$50k RSUs",
        "target_compensation": 195000
    }
    analysis = CareerWorkspaceEngine.analyze_salary_and_counter_offer(offer_data)
    assert "user_facts" in analysis
    assert "analysis" in analysis
    assert "counter_offer_draft" in analysis
    assert "$140,000.00" in analysis["user_facts"]["base_salary"]
    assert "Dear Hiring Team at Stripe" in analysis["counter_offer_draft"]

def test_career_goals_crud(temp_db):
    """TEST 4: Career Goals CRUD & SQLite persistence."""
    repo = CareerRepository(db_path=temp_db)
    goal = repo.create_career_goal({
        "title": "Master Rust for Security Architecture",
        "description": "Complete advanced systems security certifications.",
        "category": "SKILLS",
        "priority": "HIGH",
        "progress": 30
    })
    goal_id = goal["id"]
    assert goal["title"] == "Master Rust for Security Architecture"

    updated = repo.update_career_goal(goal_id, {"progress": 75, "status": "IN_PROGRESS"})
    assert updated["progress"] == 75

    goals = repo.list_career_goals()
    assert len(goals) == 1

    deleted = repo.delete_career_goal(goal_id)
    assert deleted is True

def test_phase4_api_endpoints():
    """TEST 5: Phase 4 API endpoints (/applications, /applications/move, /applications/dossier, /interview/generate, /goals, /dashboard, /trajectory)."""
    # 1. Create Application
    create_resp = client.post("/api/career/applications", json={
        "company": "Stripe",
        "role": "Lead Security Architect",
        "location": "Remote",
        "salary": "$180k - $220k",
        "status": "APPLIED"
    })
    assert create_resp.status_code == 200
    app_data = create_resp.json()["application"]
    app_id = app_data["id"]

    # 2. Move Stage
    move_resp = client.post(f"/api/career/applications/{app_id}/move", json={"stage": "TECHNICAL_INTERVIEW"})
    assert move_resp.status_code == 200
    assert move_resp.json()["application"]["status"] == "TECHNICAL_INTERVIEW"

    # 3. Get Dossier
    dossier_resp = client.get(f"/api/career/applications/{app_id}/dossier")
    assert dossier_resp.status_code == 200
    assert dossier_resp.json()["application"]["company"] == "Stripe"

    # 4. Generate Interview Prep
    prep_resp = client.post("/api/career/interview/generate", json={
        "jd_text": "Requires Cybersecurity, Nmap, and C++ experience.",
        "company": "Stripe",
        "role": "Lead Security Architect",
        "application_id": app_id
    })
    assert prep_resp.status_code == 200
    assert len(prep_resp.json()["questions"]) >= 1

    # 5. Dashboard & Trajectory
    dash_resp = client.get("/api/career/dashboard")
    assert dash_resp.status_code == 200
    assert "stats" in dash_resp.json()

    traj_resp = client.get("/api/career/trajectory")
    assert traj_resp.status_code == 200
    assert isinstance(traj_resp.json()["trajectory"], list)
