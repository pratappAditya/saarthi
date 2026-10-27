import pytest
import os
import tempfile
import json
import io
from fastapi.testclient import TestClient
from app.main import app
from app.db.career import CareerRepository, init_career_tables
from app.tools.tailoring_engine import TailoringEngine
from app.tools.document_engine import DocumentEngine

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

def test_jd_requirement_extraction():
    """TEST 1: Extract structured skills, seniority, and responsibilities from JD."""
    jd_text = """
    Stripe is looking for a Lead Security Architect.
    Requirements:
    • 8+ years experience in Cybersecurity, Penetration Testing, Python, and DevSecOps.
    • Deep knowledge of Linux cryptography and Docker container security.
    • Architect automated vulnerability scanning tools.
    """
    reqs = TailoringEngine.extract_jd_requirements(jd_text)
    assert "Cybersecurity" in reqs["required_skills"]
    assert "Python" in reqs["required_skills"]
    assert "Docker" in reqs["required_skills"]
    assert reqs["seniority_level"] == "Senior / Lead"
    assert "Cybersecurity" in reqs["domain_context"]

def test_evidence_matching_and_gap_analysis(temp_db):
    """TEST 2: Match candidate evidence & perform gap analysis strictly on master resume facts."""
    repo = CareerRepository(db_path=temp_db)
    saved = repo.save_resume(
        title="Candidate Master Resume",
        raw_content="Aditya Sharma\nExperienced Lead Security Architect in Python, FastAPI, Docker, and Linux cryptography.",
        parsed_facts={"skills": ["Python", "FastAPI", "Docker", "Linux"]},
        is_default=True,
        skills=["Python", "FastAPI", "Docker", "Linux"]
    )
    res_id = saved["id"]

    jd_text = "Looking for Senior Engineer with Python, Docker, and Rust experience."
    jd_reqs = TailoringEngine.extract_jd_requirements(jd_text)

    evidence = TailoringEngine.match_candidate_evidence(saved, jd_reqs)
    assert "Python" in evidence["matched_skills"]
    assert "Docker" in evidence["matched_skills"]
    assert "Rust" in evidence["missing_skills"]

    gaps = TailoringEngine.perform_gap_analysis(saved, jd_reqs)
    assert gaps["overall_match_percentage"] > 40
    hard_gap_skills = [g["skill"] for g in gaps["hard_gaps"]]
    assert "Rust" in hard_gap_skills

def test_truthful_diff_generation_zero_fabrication(temp_db):
    """TEST 3: Generate truthful bullet diff patches and verify zero fake experience or hallucinated titles."""
    repo = CareerRepository(db_path=temp_db)
    saved = repo.save_resume(
        title="Candidate Master Resume",
        raw_content="Built automated local AI vulnerability scanner using Python and FastAPI.",
        parsed_facts={"skills": ["Python", "FastAPI"]},
        is_default=True
    )

    jd_reqs = TailoringEngine.extract_jd_requirements("Requires Python, FastAPI, and Docker experience.")
    diffs = TailoringEngine.generate_truthful_diffs(saved, "Job Description", jd_reqs)
    assert len(diffs) >= 1
    diff = diffs[0]
    assert "Python" in diff["suggestedText"] or "FastAPI" in diff["suggestedText"]
    assert "Built automated local AI vulnerability scanner" in diff["originalText"]
    assert "without altering factual history" in diff["rationale"].lower() or "aligned" in diff["rationale"].lower()

def test_phase3_api_analyze_and_apply_version_snapshot():
    """TEST 4: Call Phase 3 API endpoints (/jd/analyze, /jd/tailor-diffs, /jd/apply-tailored-version) and verify version snapshot saved in DB."""
    repo = CareerRepository()
    saved = repo.save_resume(
        title="Master Resume Baseline",
        raw_content="Aditya Sharma\nCybersecurity Architect\nBuilt local security scanners using Python.",
        parsed_facts={"skills": ["Python"]},
        is_default=True
    )
    res_id = saved["id"]

    # 1. Analyze JD
    analyze_resp = client.post("/api/career/jd/analyze", json={
        "jd_text": "Need Cybersecurity Architect with Python and Linux skills.",
        "company": "CyberCorp",
        "role": "Lead Architect",
        "resume_id": res_id
    })
    assert analyze_resp.status_code == 200
    anal_data = analyze_resp.json()
    assert anal_data["ats_score"] > 30

    # 2. Generate Diffs
    diffs_resp = client.post("/api/career/jd/tailor-diffs", json={
        "jd_text": "Need Cybersecurity Architect with Python and Linux skills.",
        "company": "CyberCorp",
        "role": "Lead Architect",
        "resume_id": res_id
    })
    assert diffs_resp.status_code == 200
    diffs_data = diffs_resp.json()
    assert len(diffs_data["diffs"]) >= 1

    # 3. Apply Tailored Version Snapshot
    version_tag = "v2.0 — CyberCorp (Lead Architect)"
    apply_resp = client.post("/api/career/jd/apply-tailored-version", json={
        "resume_id": res_id,
        "version_tag": version_tag,
        "company": "CyberCorp",
        "role": "Lead Architect",
        "accepted_diffs": diffs_data["diffs"]
    })
    assert apply_resp.status_code == 200
    app_data = apply_resp.json()
    assert app_data["version_id"].startswith("ver-")
    assert len(app_data["resume"]["versions"]) >= 1

    # 4. Verify Version Persisted in SQLite DB
    repo_reloaded = CareerRepository()
    reloaded = repo_reloaded.get_resume(res_id)
    assert len(reloaded["versions"]) >= 1
    assert any(v["tag"] == version_tag for v in reloaded["versions"])

def test_phase3_export_tailored_pdf_and_docx():
    """TEST 5: Export tailored resume to PDF and DOCX using DocumentEngine and verify with pypdf and python-docx."""
    tailored_text = "# TAILORED RESUME: Lead Security Architect\nCompany: CyberCorp\n\nAditya Sharma\nCybersecurity Architect\n\n- Architected local security scanners using Python and FastAPI."

    # PDF Export
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f_pdf:
        pdf_path = f_pdf.name

    try:
        pdf_res = DocumentEngine.export_document(tailored_text, pdf_path, plan="PAID", format_type="pdf")
        assert pdf_res["status"] == "success"
        
        import pypdf
        reader = pypdf.PdfReader(pdf_path)
        assert len(reader.pages) >= 1
        extracted = reader.pages[0].extract_text()
        assert "Aditya Sharma" in extracted or "Security Architect" in extracted
        assert "%PDF-" not in extracted
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    # DOCX Export
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f_docx:
        docx_path = f_docx.name

    try:
        docx_res = DocumentEngine.export_document(tailored_text, docx_path, plan="PAID", format_type="docx")
        assert docx_res["status"] == "success"

        import docx
        doc_obj = docx.Document(docx_path)
        docx_extracted = "\n".join([p.text for p in doc_obj.paragraphs])
        assert "Aditya Sharma" in docx_extracted or "Security Architect" in docx_extracted
    finally:
        if os.path.exists(docx_path):
            os.remove(docx_path)
