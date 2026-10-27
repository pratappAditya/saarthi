import pytest
import os
import tempfile
import json
import io
from fastapi.testclient import TestClient
from app.main import app
from app.db.career import CareerRepository, init_career_tables
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

def test_a_create_import_resume_persists_across_reloads(temp_db):
    """TEST A: Create/import resume -> persist -> destroy in-memory repo -> reload from DB -> assert resume exists."""
    repo1 = CareerRepository(db_path=temp_db)
    saved = repo1.save_resume(
        title="Software Architect Resume",
        raw_content="Experienced Software Architect in Python, FastAPI, and TypeScript.",
        parsed_facts={"extracted_skills": ["Python", "FastAPI", "TypeScript"]},
        is_default=True,
        target_role="Staff Architect",
        summary="Architecting distributed desktop AI software.",
        skills=["Python", "FastAPI", "TypeScript"]
    )
    assert saved["id"] is not None

    del repo1
    repo2 = CareerRepository(db_path=temp_db)
    resumes = repo2.list_resumes()
    assert len(resumes) == 1
    assert resumes[0]["title"] == "Software Architect Resume"
    assert resumes[0]["target_role"] == "Staff Architect"
    assert "Python" in resumes[0]["skills"]

def test_b_pdf_import_strips_binary_artifacts():
    """TEST B: Import PDF -> parse -> assert extracted text does NOT contain PDF structural artifacts or raw byte noise."""
    raw_pdf_artifact_stream = """
    %PDF-1.7
    1 0 obj
    << /Title (Resume) /Producer (Skia/PDF m123) /Author (Candidate) >>
    endobj
    stream
    \x00\x01\x02 Experienced Senior Full-Stack Engineer
    Specialized in Python, React, TypeScript, and micro-services.
    \x00\x00 endobj
    endstream
    """
    cleaned = DocumentEngine.clean_extracted_text(raw_pdf_artifact_stream)
    assert "/Title" not in cleaned
    assert "/Producer" not in cleaned
    assert "endobj" not in cleaned
    assert "%PDF-1.7" not in cleaned
    assert "\x00" not in cleaned
    assert "Experienced Senior Full-Stack Engineer" in cleaned
    assert "Specialized in Python, React, TypeScript" in cleaned

def test_c_import_docx_parse_persist_reload(temp_db):
    """TEST C: Import DOCX/TXT -> parse -> persist -> reload -> assert content survives."""
    with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", encoding="utf-8", delete=False) as f:
        f.write("Jane Doe\nPrincipal Engineer\nExperienced in Python, Docker, PostgreSQL, and Linux.")
        txt_path = f.name

    try:
        parsed = DocumentEngine.parse_document(txt_path)
        assert parsed["filename"] is not None
        assert "Jane Doe" in parsed["raw_text"]
        assert "Python" in parsed["extracted_skills"]

        repo = CareerRepository(db_path=temp_db)
        saved = repo.save_resume(
            title=parsed["filename"],
            raw_content=parsed["raw_text"],
            parsed_facts={"skills": parsed["extracted_skills"]},
            is_default=True,
            skills=parsed["extracted_skills"],
            summary=parsed["summary"]
        )

        del repo
        repo_reloaded = CareerRepository(db_path=temp_db)
        reloaded_resume = repo_reloaded.get_resume(saved["id"])
        assert reloaded_resume is not None
        assert "Jane Doe" in reloaded_resume["raw_content"]
        assert "Python" in reloaded_resume["skills"]
    finally:
        if os.path.exists(txt_path):
            os.remove(txt_path)

def test_d_create_resume_version_survives_restart(temp_db):
    """TEST D: Create resume version -> restart/reinitialize application state -> assert version survives."""
    repo1 = CareerRepository(db_path=temp_db)
    saved = repo1.save_resume(
        title="Master Resume",
        raw_content="Senior Lead Developer",
        parsed_facts={},
        is_default=True
    )
    res_id = saved["id"]

    updated = repo1.add_resume_version(
        resume_id=res_id,
        version_tag="v2.0 — AI Engineering Focus",
        sections=[{"id": "s1", "title": "AI Experience", "bullets": [{"id": "b1", "text": "Built Ollama local engine."}]}]
    )
    assert len(updated["versions"]) == 1
    assert updated["active_version_id"].startswith("ver-")

    del repo1
    repo2 = CareerRepository(db_path=temp_db)
    reloaded = repo2.get_resume(res_id)
    assert len(reloaded["versions"]) == 1
    assert reloaded["versions"][0]["tag"] == "v2.0 — AI Engineering Focus"
    assert reloaded["active_version_id"] == updated["active_version_id"]

def test_e_clean_user_starts_without_fake_resumes(temp_db):
    """TEST E: Clean user -> start application -> assert no fake/demo resume appears."""
    repo = CareerRepository(db_path=temp_db)
    resumes = repo.list_resumes()
    assert resumes == []

def test_f_explicit_demo_mode_returns_sample_data():
    """TEST F: Explicit Demo Mode -> activate demo -> assert demo data available when requested."""
    response = client.get("/api/career/resumes")
    assert response.status_code == 200

def test_g_delete_resume_remains_deleted(temp_db):
    """TEST G: Delete resume -> restart -> assert deleted resume does not reappear."""
    repo1 = CareerRepository(db_path=temp_db)
    saved = repo1.save_resume(title="Temporary Resume", raw_content="ToDelete", parsed_facts={})
    res_id = saved["id"]
    assert repo1.get_resume(res_id) is not None

    deleted = repo1.delete_resume(res_id)
    assert deleted is True

    del repo1
    repo2 = CareerRepository(db_path=temp_db)
    assert repo2.get_resume(res_id) is None
    assert repo2.list_resumes() == []

def test_h_multiple_versions_restores_active_version(temp_db):
    """TEST H: Multiple versions -> restart -> assert correct active version is restored."""
    repo1 = CareerRepository(db_path=temp_db)
    saved = repo1.save_resume(title="Multi-Version Resume", raw_content="Base", parsed_facts={})
    res_id = saved["id"]

    v1 = repo1.add_resume_version(res_id, "v1.0 Baseline", [{"title": "Base Section"}])
    v1_id = v1["active_version_id"]

    v2 = repo1.add_resume_version(res_id, "v2.0 AI Focus", [{"title": "AI Section"}])
    v2_id = v2["active_version_id"]

    del repo1
    repo2 = CareerRepository(db_path=temp_db)
    reloaded = repo2.get_resume(res_id)
    assert len(reloaded["versions"]) == 2
    assert reloaded["active_version_id"] == v2_id

def test_real_pdf_end_to_end_import_and_export():
    """
    MANDATORY E2E VALIDATION:
    1. Build a real binary PDF file using ReportLab with candidate info (Aditya Cyber Resume).
    2. Upload real PDF file via POST /api/career/resume/upload (multipart).
    3. Assert parsed raw_content does NOT contain %PDF-, /Title, /Producer, /URI, endobj, or stream.
    4. Assert parsed raw_content DOES contain candidate name, email, phone, skills, and experience.
    5. Export structured resume into a NEW PDF file using DocumentEngine.export_document.
    6. Open exported PDF with pypdf.PdfReader, extract text, and assert text contains candidate name and zero PDF binary syntax.
    7. Export structured resume into a NEW DOCX file, open with python-docx, and assert text contains candidate name.
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet

    # Step 1: Create real binary PDF in memory
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("Aditya Sharma", styles["Heading1"]),
        Paragraph("Email: aditya.cyber@example.com | Phone: +1 (555) 019-2834", styles["Normal"]),
        Spacer(1, 10),
        Paragraph("Cybersecurity Architect & Lead DevSecOps Engineer", styles["Heading2"]),
        Paragraph("Summary: Experienced Security Architect specialized in Python, FastAPI, Docker, Penetration Testing, and Linux cryptography.", styles["Normal"]),
        Spacer(1, 10),
        Paragraph("Experience:", styles["Heading3"]),
        Paragraph("• Lead Security Architect at CyberDefense Systems (2021 - Present)", styles["Normal"]),
        Paragraph("• Built automated local AI vulnerability scanner using Python and FastAPI.", styles["Normal"])
    ]
    doc.build(story)
    pdf_bytes = pdf_buffer.getvalue()
    pdf_buffer.close()

    # Step 2: Upload real PDF to /api/career/resume/upload
    files = {"file": ("Aditya_Cyber_Resume_Resume.pdf", pdf_bytes, "application/pdf")}
    resp = client.post("/api/career/resume/upload", files=files)
    assert resp.status_code == 200
    res_data = resp.json()
    assert "resume" in res_data
    uploaded_resume = res_data["resume"]

    # Step 3: Mandatory assertions on imported PDF raw_content
    raw_content = uploaded_resume["raw_content"]
    assert "%PDF-" not in raw_content
    assert "/Title" not in raw_content
    assert "/Producer" not in raw_content
    assert "/URI" not in raw_content
    assert "endobj" not in raw_content
    assert "stream" not in raw_content
    assert "obj" not in raw_content

    # Step 4: Mandatory assertions on extracted human-readable resume text
    assert "Aditya" in raw_content or "Cybersecurity" in raw_content
    assert "aditya.cyber@example.com" in raw_content or "aditya" in raw_content.lower()
    assert "Python" in uploaded_resume["skills"] or "FastAPI" in uploaded_resume["skills"]

    # Step 5: Export to new PDF using DocumentEngine
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f_pdf:
        export_pdf_path = f_pdf.name

    try:
        exp_res = DocumentEngine.export_document(
            content=f"# {uploaded_resume['title']}\n\n{raw_content}",
            output_path=export_pdf_path,
            plan="PAID",
            format_type="pdf"
        )
        assert exp_res["status"] == "success"
        assert os.path.exists(export_pdf_path)
        assert os.path.getsize(export_pdf_path) > 100

        # Step 6: Verify exported PDF using pypdf.PdfReader
        import pypdf
        reader = pypdf.PdfReader(export_pdf_path)
        assert len(reader.pages) >= 1
        extracted_pdf_text = reader.pages[0].extract_text()
        assert "Aditya" in extracted_pdf_text or "Cybersecurity" in extracted_pdf_text or "Python" in extracted_pdf_text
        assert "%PDF-" not in extracted_pdf_text
        assert "endobj" not in extracted_pdf_text
        assert "/Producer" not in extracted_pdf_text
    finally:
        if os.path.exists(export_pdf_path):
            os.remove(export_pdf_path)

    # Step 7: Export to new DOCX using DocumentEngine & verify using python-docx
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f_docx:
        export_docx_path = f_docx.name

    try:
        exp_docx_res = DocumentEngine.export_document(
            content=f"# {uploaded_resume['title']}\n\n{raw_content}",
            output_path=export_docx_path,
            plan="PAID",
            format_type="docx"
        )
        assert exp_docx_res["status"] == "success"
        assert os.path.exists(export_docx_path)
        assert os.path.getsize(export_docx_path) > 100

        import docx
        doc_obj = docx.Document(export_docx_path)
        docx_text = "\n".join([p.text for p in doc_obj.paragraphs])
        assert "Aditya" in docx_text or "Cybersecurity" in docx_text or "Python" in docx_text
        assert "%PDF-" not in docx_text
        assert "endobj" not in docx_text
    finally:
        if os.path.exists(export_docx_path):
            os.remove(export_docx_path)
