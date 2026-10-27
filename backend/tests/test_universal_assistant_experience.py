import pytest
from fastapi.testclient import TestClient
from app.main import app

from app.intelligence.projects.project_manager import project_manager, ProjectItem
from app.intelligence.orchestration.orchestrator import orchestrator
from app.intelligence.voice.voice_engine import voice_engine, WakeWordDetector
from app.intelligence.research.research_provider import research_provider
from app.intelligence.multimodal.attachment_engine import attachment_engine
from app.intelligence.profile.assistant_profile import assistant_profile

client = TestClient(app)

def test_projects_crud():
    """TEST 1: Universal project creation, list, and deletion."""
    proj = project_manager.create_project(
        name="Stripe Security Architect Campaign",
        description="Target job application project",
        domain="career"
    )
    assert proj.project_id is not None
    assert proj.domain == "career"

    projs = project_manager.list_projects()
    assert len(projs) >= 1

    deleted = project_manager.delete_project(proj.project_id)
    assert deleted is True

def test_structured_orchestrator_response():
    """TEST 2: Upgraded Orchestrator returning structured response payload."""
    res = orchestrator.process_message("Analyze job description requiring C++ and Nmap.")
    assert "message" in res
    assert "intent" in res
    assert "domain" in res
    assert "confidence" in res
    assert "memories_used" in res
    assert "tools_used" in res
    assert "suggestions" in res

def test_voice_contracts_and_wake_word():
    """TEST 3: Saarthi voice profile, synthesizer, and inactive wake-word contract."""
    profile = voice_engine.get_voice_profile()
    assert profile.name == "Saarthi AI Identity Voice"
    assert profile.language == "en-IN"
    assert WakeWordDetector.is_active() is False

    syn = voice_engine.synthesize_speech("Hello Pratap, I am Saarthi.")
    assert syn["status"] == "synthesized"

def test_research_provider_provenance():
    """TEST 4: Research provider claims and citation provenance."""
    res = research_provider.analyze_paper_literature("Quantum Computing Key Distribution")
    assert len(res["claims"]) >= 1
    assert len(res["citations"]) >= 1
    assert res["claims"][0]["provenance_source"] == "paper_derived"

def test_multimodal_attachment_engine():
    """TEST 5: Multimodal attachment ingestion."""
    att = attachment_engine.process_attachment("resume.pdf", "Sample PDF text content", "application/pdf")
    assert att.filename == "resume.pdf"
    assert att.content_type == "document"

def test_assistant_profile():
    """TEST 6: Structured AssistantProfile configuration."""
    assert assistant_profile.name == "Saarthi"
    assert assistant_profile.tone == "intelligent, calm, helpful"

def test_phase5c_rest_apis():
    """TEST 7: REST APIs (/api/projects, /api/trust/summary, /api/voice/profile)."""
    # 1. Projects REST
    proj_resp = client.get("/api/projects")
    assert proj_resp.status_code == 200
    assert "projects" in proj_resp.json()

    # 2. Trust Summary REST
    trust_resp = client.get("/api/trust/summary")
    assert trust_resp.status_code == 200
    assert trust_resp.json()["local_processing"] is True

    # 3. Voice Profile REST
    voice_resp = client.get("/api/voice/profile")
    assert voice_resp.status_code == 200
    assert voice_resp.json()["profile"]["id"] == "saarthi_voice_hi_en"
