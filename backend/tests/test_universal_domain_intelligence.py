import pytest
from fastapi.testclient import TestClient
from app.main import app

from app.intelligence.domains.domain_registry import domain_registry
from app.intelligence.domains.domain_router import domain_router
from app.intelligence.domains.research_engine import research_engine

client = TestClient(app)

def test_domain_registry_all_17_packs():
    """TEST 1: Verify all 17 initial domain packs are registered and configured."""
    packs = domain_registry.list_packs()
    assert len(packs) >= 17
    
    pack_ids = {p.id for p in packs}
    expected = {
        "general", "career", "education", "writing", "research", "business",
        "software", "cybersecurity", "cs", "mechanical", "civil", "electrical",
        "biology", "chemistry", "physics", "archaeology", "history"
    }
    assert expected.issubset(pack_ids)

def test_domain_router_intent_classification():
    """TEST 2: Intent-based domain classification across multiple domains."""
    # Software Engineering query
    swe_res = domain_router.route_request("Why is my Spring Boot service throwing null pointer error in C++?")
    assert swe_res.primary_domain == "software"
    assert swe_res.confidence >= 0.70

    # Cybersecurity query
    sec_res = domain_router.route_request("Analyze this Nmap vulnerability scan output for CVE exploits.")
    assert sec_res.primary_domain == "cybersecurity"

    # Archaeology query
    arch_res = domain_router.route_request("Analyze this excavation report and Harappan artifact typology.")
    assert arch_res.primary_domain == "archaeology"

    # Biology query
    bio_res = domain_router.route_request("Explain this protein gene expression data graph.")
    assert bio_res.primary_domain == "biology"

    # Civil Engineering query
    civ_res = domain_router.route_request("Calculate the structural beam loading for concrete bridge.")
    assert civ_res.primary_domain == "civil"

def test_explicit_domain_override_and_lock():
    """TEST 3: Explicit user domain selection override."""
    res = domain_router.route_request(
        prompt="Tell me about ancient history.",
        explicit_domain="cybersecurity"
    )
    assert res.primary_domain == "cybersecurity"
    assert res.is_explicit_override is True
    assert res.confidence == 1.0

def test_research_engine_evidence_classification():
    """TEST 4: Research Mode question decomposition and evidence classification."""
    r_res = research_engine.analyze_research_query("What are the urban planning features of Harappan sites?", domain_id="archaeology")
    assert r_res.research_question == "What are the urban planning features of Harappan sites?"
    assert len(r_res.decomposed_subqueries) >= 2
    assert len(r_res.evidence_items) >= 3

    classifications = {item.classification for item in r_res.evidence_items}
    assert "FACT" in classifications
    assert "SOURCE-DERIVED" in classifications
    assert "INFERENCE" in classifications

def test_domain_rest_apis():
    """TEST 5: REST API endpoints for domain listing and routing."""
    # List domains
    list_resp = client.get("/api/domains")
    assert list_resp.status_code == 200
    assert len(list_resp.json()["domains"]) >= 17

    # Get specific domain
    get_resp = client.get("/api/domains/software")
    assert get_resp.status_code == 200
    assert get_resp.json()["domain"]["id"] == "software"

    # Route endpoint
    route_resp = client.post("/api/domains/route", json={"prompt": "How to fix a memory leak in C++?"})
    assert route_resp.status_code == 200
    assert route_resp.json()["route"]["primary_domain"] == "software"
