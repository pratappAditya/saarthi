import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.career import CareerRepository

client = TestClient(app)

def test_job_application_full_crud_lifecycle():
    repo = CareerRepository()
    
    # 1. Create Application
    create_payload = {
        "company": "Anthropic PBC",
        "role": "Staff Systems Architect",
        "location": "San Francisco, CA",
        "salary": "$250k – $320k",
        "status": "APPLIED",
        "notes": "End-to-end integration verification test"
    }
    create_res = client.post("/api/career/applications", json=create_payload)
    assert create_res.status_code == 200
    create_data = create_res.json()
    assert "application" in create_data
    app_id = create_data["application"]["id"]
    assert create_data["application"]["company"] == "Anthropic PBC"
    assert create_data["application"]["status"] == "APPLIED"

    try:
        # 2. List Applications
        list_res = client.get("/api/career/applications")
        assert list_res.status_code == 200
        apps = list_res.json().get("applications", [])
        matched = [a for a in apps if a["id"] == app_id]
        assert len(matched) == 1
        assert matched[0]["role"] == "Staff Systems Architect"

        # 3. Update Application
        update_payload = {
            "salary": "$280k – $350k",
            "notes": "Updated compensation expectation"
        }
        update_res = client.put(f"/api/career/applications/{app_id}", json=update_payload)
        assert update_res.status_code == 200
        updated_data = update_res.json().get("application", {})
        assert updated_data["salary"] == "$280k – $350k"

        # 4. Move Stage
        move_res = client.post(f"/api/career/applications/{app_id}/move", json={"stage": "interview"})
        assert move_res.status_code == 200
        moved_data = move_res.json().get("application", {})
        assert moved_data["status"] == "INTERVIEW"

        # 5. Get Dossier
        dossier_res = client.get(f"/api/career/applications/{app_id}/dossier")
        assert dossier_res.status_code == 200
        dossier_data = dossier_res.json()
        assert "application" in dossier_data
        assert "gap_analysis" in dossier_data
        assert "ats_score" in dossier_data

    finally:
        # 6. Delete Application
        del_res = client.delete(f"/api/career/applications/{app_id}")
        assert del_res.status_code == 200
        assert del_res.json().get("deleted") is True

    # 7. Verify Deleted
    get_res = client.get(f"/api/career/applications/{app_id}")
    assert get_res.status_code == 404

def test_cover_letter_synthesis_and_watermark_enforcement():
    payload = {
        "resume_text": "Lead Architect with 10 years experience in distributed systems, TypeScript, and high-load backend infrastructure.",
        "job_description": "We are seeking a Staff Engineer to build resilient distributed services.",
        "company": "Linear Orbit Inc.",
        "role": "Staff Engineer",
        "hiring_manager": "Engineering Director"
    }
    res = client.post("/api/career/cover-letter", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["company"] == "Linear Orbit Inc."
    assert data["role"] == "Staff Engineer"
    assert "Linear Orbit Inc." in data["cover_letter"]
    assert "Staff Engineer" in data["cover_letter"]
    assert "watermarked" in data
