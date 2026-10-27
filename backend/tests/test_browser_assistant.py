import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.profile import ProfileRepository

client = TestClient(app)

def test_profile_repository_crud():
    profile_data = {
        "full_name": "Rahul Sharma",
        "email": "rahul.sharma@iitb.ac.in",
        "phone": "+91 9876543210",
        "location": "Mumbai, India",
        "education": [{"degree": "B.Tech Computer Science", "institution": "IIT Bombay", "year": 2026}],
        "skills": ["Python", "FastAPI", "React", "TypeScript", "SQLite"],
        "experience": [{"role": "Backend Intern", "company": "TechCorp", "duration": "6 months"}],
        "projects": [{"title": "Local AI Workstation", "tech": "Python, React"}],
        "links": {"github": "https://github.com/rahulsharma", "linkedin": "https://linkedin.com/in/rahulsharma"},
        "work_authorization": "Authorized to work in India",
        "notice_period_days": 15,
        "preferred_locations": ["Mumbai", "Bengaluru", "Remote"]
    }

    saved = ProfileRepository.save_profile(profile_data)
    assert saved["full_name"] == "Rahul Sharma"
    assert saved["email"] == "rahul.sharma@iitb.ac.in"
    assert saved["notice_period_days"] == 15
    assert saved["fact_source"] == "STORED PROFILE FACT"

    fetched = ProfileRepository.get_profile()
    assert fetched["full_name"] == "Rahul Sharma"
    assert "Python" in fetched["skills"]

def test_browser_assistant_field_detection():
    # Save test profile
    ProfileRepository.save_profile({
        "full_name": "Priya Patel",
        "email": "priya.patel@stanford.edu",
        "phone": "+1 650 555 0199",
        "location": "Palo Alto, CA",
        "skills": ["Python", "Machine Learning", "FastAPI"],
        "notice_period_days": 0
    })

    fields_payload = {
        "url": "https://careers.example.com/apply/backend-engineer",
        "fields": [
            {"field_id": "applicant_name", "label": "Full Name"},
            {"field_id": "applicant_email", "label": "Email Address"},
            {"field_id": "phone_num", "label": "Contact Phone"},
            {"field_id": "skills_input", "label": "Technical Skills"}
        ]
    }

    resp = client.post("/api/browser-assistant/detect-fields", json=fields_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["matched_fields"]) == 4

    name_field = next(f for f in data["matched_fields"] if f["field_id"] == "applicant_name")
    assert name_field["suggested_value"] == "Priya Patel"
    assert name_field["fact_source"] == "USER-PROVIDED FACT"

    skills_field = next(f for f in data["matched_fields"] if f["field_id"] == "skills_input")
    assert "Python" in skills_field["suggested_value"]
    assert skills_field["requires_user_confirmation"] is True

def test_browser_assistant_confirm_fill_policy():
    # Unconfirmed request -> Should fail 400
    resp_unconfirmed = client.post("/api/browser-assistant/confirm-fill", json={
        "field_values": {"applicant_name": "Priya Patel"},
        "confirmed_by_user": False
    })
    assert resp_unconfirmed.status_code == 400
    assert "Explicit user confirmation is required" in resp_unconfirmed.json()["detail"]

    # Confirmed request -> Should pass 200 without auto-submit
    resp_confirmed = client.post("/api/browser-assistant/confirm-fill", json={
        "field_values": {"applicant_name": "Priya Patel"},
        "confirmed_by_user": True
    })
    assert resp_confirmed.status_code == 200
    data = resp_confirmed.json()
    assert data["status"] == "APPROVED"
    assert data["auto_submit_executed"] is False
