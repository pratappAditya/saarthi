import pytest
from app.db.career import CareerRepository
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def test_repo(tmp_path):
    db_file = str(tmp_path / "test_career.db")
    return CareerRepository(db_path=db_file)

def test_job_application_crud(test_repo):
    # 1. Create Application
    created = test_repo.create_application({
        "company": "TechCorp",
        "role": "Software Engineer",
        "job_url": "https://techcorp.com/jobs/123",
        "location": "Bengaluru",
        "salary": "12 LPA",
        "status": "APPLIED"
    })
    assert created["id"] is not None
    assert created["company"] == "TechCorp"
    assert created["status"] == "APPLIED"

    # 2. Get Application
    app_id = created["id"]
    retrieved = test_repo.get_application(app_id)
    assert retrieved is not None
    assert retrieved["role"] == "Software Engineer"

    # 3. Update Application Status
    updated = test_repo.update_application(app_id, {"status": "INTERVIEW", "interview_date": "2026-08-25T10:00"})
    assert updated["status"] == "INTERVIEW"
    assert updated["interview_date"] == "2026-08-25T10:00"

    # 4. List Applications & Stats
    apps = test_repo.list_applications()
    assert len(apps) == 1

    stats = test_repo.get_application_stats()
    assert stats["total_applications"] == 1
    assert stats["interviews"] == 1
    assert stats["offers"] == 0

    # 5. Delete Application
    deleted = test_repo.delete_application(app_id)
    assert deleted is True
    assert test_repo.get_application(app_id) is None

def test_resume_import_and_facts(test_repo):
    raw_resume = """JOHN DOE
Python developer with experience in FastAPI, React, SQL, and Docker.
Built local AI tools and web interfaces."""
    
    res = test_repo.save_resume("Default Resume", raw_resume, {"skills": ["Python", "React", "FastAPI"]}, is_default=True)
    assert res["id"] is not None
    assert res["is_default"] == 1
    
    def_res = test_repo.get_default_resume()
    assert def_res is not None
    assert def_res["title"] == "Default Resume"

def test_student_verification(test_repo):
    # Valid student email
    res1 = test_repo.verify_student("student@iitb.ac.in")
    assert res1["verified"] is True
    assert "verified" in res1["message"].lower()

    # Invalid non-student domain
    res2 = test_repo.verify_student("user@gmail.com")
    assert res2["verified"] is False

def test_career_api_endpoints():
    client = TestClient(app)
    
    # List applications
    resp = client.get("/api/career/applications")
    assert resp.status_code == 200
    assert "applications" in resp.json()

    # Analyze ATS Match
    match_payload = {
        "resume_text": "Python Developer proficient in FastAPI, SQL, Docker, React, and Git.",
        "job_description": "We are looking for a Python Developer with FastAPI, Docker, and React experience.",
        "company": "InnovateTech",
        "role": "Python Engineer"
    }
    match_resp = client.post("/api/career/analyze-match", json=match_payload)
    assert match_resp.status_code == 200
    data = match_resp.json()
    assert data["ats_score"] > 50
    assert "fastapi" in [k.lower() for k in data["matching_keywords"]]

    # Cover Letter Generation
    cl_resp = client.post("/api/career/cover-letter", json={
        "resume_text": "Python engineer",
        "job_description": "Building backend APIs",
        "company": "InnovateTech",
        "role": "Python Engineer"
    })
    assert cl_resp.status_code == 200
    assert "InnovateTech" in cl_resp.json()["cover_letter"]

    # Email Drafting with Explicit User Confirmation Notice
    email_resp = client.post("/api/career/email/draft", json={
        "email_type": "recruiter_follow_up",
        "company": "InnovateTech",
        "role": "Python Engineer",
        "confirmed_by_user": False
    })
    assert email_resp.status_code == 200
    email_data = email_resp.json()
    assert email_data["requires_explicit_confirmation"] is True
    assert email_data["status"] == "DRAFTED_PENDING_CONFIRMATION"

    # Calendar Event Generation
    cal_resp = client.post("/api/career/calendar/event", json={
        "event_type": "interview",
        "company": "InnovateTech",
        "role": "Python Engineer",
        "event_time": "2026-08-25T14:00",
        "confirmed_by_user": False
    })
    assert cal_resp.status_code == 200
    cal_data = cal_resp.json()
    assert cal_data["requires_explicit_confirmation"] is True
    assert "BEGIN:VCALENDAR" in cal_data["ics_content"]

    # Interview Prep
    prep_resp = client.post("/api/career/interview-prep", json={
        "resume_text": "Python engineer",
        "job_description": "Building backend APIs",
        "company": "InnovateTech",
        "role": "Python Engineer"
    })
    assert prep_resp.status_code == 200
    prep_data = prep_resp.json()
    assert len(prep_data["technical_questions"]) > 0
    assert "star_coaching" in prep_data
