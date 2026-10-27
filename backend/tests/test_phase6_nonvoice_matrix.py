import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.plans import ALL_PLANS, CAPABILITIES, PLAN_CATALOG, FREE_CAPABILITIES, POWER_CAPABILITIES
from app.intelligence.domains.domain_registry import domain_registry

client = TestClient(app)

def test_canonical_plans_exist():
    expected_plans = {"free", "student", "personal", "power", "teams", "enterprise"}
    assert set(ALL_PLANS) == expected_plans

def test_frozen_commercial_tiers_flags():
    # TEAMS and ENTERPRISE functionality is implemented but commercially frozen
    assert "teams" in ALL_PLANS
    assert "enterprise" in ALL_PLANS
    assert "teams" in PLAN_CATALOG
    assert "enterprise" in PLAN_CATALOG

def test_all_17_domain_packs_registered():
    packs = domain_registry.list_packs()
    pack_ids = {p.id for p in packs}
    expected_17_domains = {
        "general", "career", "education", "writing", "research", "business",
        "software", "cybersecurity", "cs", "mechanical", "civil", "electrical",
        "biology", "chemistry", "physics", "archaeology", "history"
    }
    assert expected_17_domains.issubset(pack_ids)

def test_study_workspace_api():
    # Flashcard Generation
    res_fc = client.post("/api/study/flashcards/generate", json={
        "content": "Quantum Mechanics principles:\nSuperposition of states\nWavefunction collapse\nQuantum entanglement",
        "count": 3,
        "topic": "Physics"
    })
    assert res_fc.status_code == 200
    data_fc = res_fc.json()
    assert data_fc["status"] == "success"
    assert len(data_fc["flashcards"]) == 3

    # Quiz Creation
    res_q = client.post("/api/study/quiz/create", json={
        "content": "Cell biology lecture notes",
        "difficulty": "medium",
        "num_questions": 4
    })
    assert res_q.status_code == 200
    data_q = res_q.json()
    assert data_q["status"] == "success"
    assert len(data_q["quiz"]) == 4

    # Syllabus Ingestion
    res_syll = client.post("/api/study/syllabus/ingest", json={
        "syllabus_text": "Unit 1: Classical Mechanics\n\nUnit 2: Electromagnetism\n\nUnit 3: Thermodynamics",
        "course_name": "Physics 101"
    })
    assert res_syll.status_code == 200
    data_syll = res_syll.json()
    assert data_syll["status"] == "success"
    assert len(data_syll["milestones"]) == 3

def test_global_search_api():
    res = client.get("/api/search?q=career")
    assert res.status_code == 200
    data = res.json()
    assert data["query"] == "career"
    assert "conversations" in data
    assert "memories" in data
    assert "projects" in data
    assert "tasks" in data

def test_entitlement_gating_matrix():
    # Test free vs power plan capabilities
    assert "core.chat.basic" in FREE_CAPABILITIES
    assert "career.master_resume" in FREE_CAPABILITIES
    
    assert "tools.terminal" in POWER_CAPABILITIES
    assert "domain.cybersecurity" in POWER_CAPABILITIES
