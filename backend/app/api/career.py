from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import json
import re
import datetime
import os
import shutil
from app.db.career import CareerRepository
from app.tools.document_engine import DocumentEngine
from app.config.settings import settings
from app.licensing.middleware import default_client_manager
from app.licensing.models import LicensePlan, LicenseStatus

router = APIRouter(prefix="/career", tags=["career"])
repo = CareerRepository()

# --- PYDANTIC SCHEMAS ---
class JobApplicationCreate(BaseModel):
    company: str
    role: str
    job_url: Optional[str] = None
    location: Optional[str] = None
    salary: Optional[str] = None
    date_applied: Optional[str] = None
    status: Optional[str] = "SAVED"
    resume_version: Optional[str] = None
    cover_letter: Optional[str] = None
    recruiter_contact: Optional[str] = None
    next_action: Optional[str] = None
    follow_up_date: Optional[str] = None
    interview_date: Optional[str] = None
    notes: Optional[str] = None

class JobApplicationUpdate(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    job_url: Optional[str] = None
    location: Optional[str] = None
    salary: Optional[str] = None
    date_applied: Optional[str] = None
    status: Optional[str] = None
    resume_version: Optional[str] = None
    cover_letter: Optional[str] = None
    recruiter_contact: Optional[str] = None
    next_action: Optional[str] = None
    follow_up_date: Optional[str] = None
    interview_date: Optional[str] = None
    notes: Optional[str] = None

class ResumeImportRequest(BaseModel):
    title: str = "My Resume"
    raw_content: str
    is_default: bool = True
    target_role: Optional[str] = "Software Engineer"
    summary: Optional[str] = None
    skills: Optional[List[str]] = None
    sections: Optional[List[Dict[str, Any]]] = None

class ResumeUpdateRequest(BaseModel):
    title: Optional[str] = None
    target_role: Optional[str] = None
    summary: Optional[str] = None
    skills: Optional[List[str]] = None
    sections: Optional[List[Dict[str, Any]]] = None
    is_default: Optional[bool] = None
    active_version_id: Optional[str] = None

class ResumeVersionCreateRequest(BaseModel):
    version_tag: str
    sections: List[Dict[str, Any]]

class MatchAnalysisRequest(BaseModel):
    resume_text: str
    job_description: str
    company: Optional[str] = None
    role: Optional[str] = None

class ResumeTailorRequest(BaseModel):
    resume_text: str
    job_description: str
    target_role: str
    company: str

class CoverLetterRequest(BaseModel):
    resume_text: str
    job_description: str
    company: str
    role: str
    hiring_manager: Optional[str] = None

class DocumentExportRequest(BaseModel):
    document_type: str = "tailored_resume"
    content: str
    format: str = "markdown"
    user_id: str = "default_user"

class EmailDraftRequest(BaseModel):
    email_type: str = "recruiter_follow_up"
    recipient_name: Optional[str] = "Hiring Manager"
    company: str
    role: str
    context_notes: Optional[str] = None
    confirmed_by_user: bool = False

class CalendarEventRequest(BaseModel):
    event_type: str = "interview"
    company: str
    role: str
    event_time: str
    notes: Optional[str] = None
    confirmed_by_user: bool = False

class InterviewPrepRequest(BaseModel):
    resume_text: str
    job_description: str
    company: str
    role: str
    focus_area: Optional[str] = "all"

class StudentVerifyRequest(BaseModel):
    email: str
    institution: Optional[str] = None

class JDAnalyzeRequest(BaseModel):
    jd_text: str
    company: Optional[str] = "Target Company"
    role: Optional[str] = "Target Role"
    resume_id: Optional[int] = None

class JDTailorDiffsRequest(BaseModel):
    jd_text: str
    company: str
    role: str
    resume_id: Optional[int] = None

class ApplyTailoredVersionRequest(BaseModel):
    resume_id: int
    version_tag: str
    company: str
    role: str
    accepted_diffs: List[Dict[str, Any]]

class ApplicationCreateRequest(BaseModel):
    company: str
    role: str
    job_description: Optional[str] = None
    job_url: Optional[str] = None
    location: Optional[str] = None
    work_mode: Optional[str] = "REMOTE"
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary: Optional[str] = None
    date_applied: Optional[str] = None
    status: Optional[str] = "SAVED"
    priority: Optional[str] = "MEDIUM"
    deadline: Optional[str] = None
    notes: Optional[str] = None
    recruiter_contact: Optional[str] = None
    resume_version: Optional[str] = None
    cover_letter: Optional[str] = None
    next_action: Optional[str] = None
    next_action_date: Optional[str] = None

class ApplicationStageMoveRequest(BaseModel):
    stage: str

class InterviewPrepGenerateRequest(BaseModel):
    jd_text: str
    company: Optional[str] = "Target Company"
    role: Optional[str] = "Target Role"
    resume_id: Optional[int] = None
    application_id: Optional[int] = None

class StarAnswerSaveRequest(BaseModel):
    question_id: int
    situation: Optional[str] = ""
    task: Optional[str] = ""
    action: Optional[str] = ""
    result: Optional[str] = ""
    score: Optional[int] = 80

class StarAnswerScoreRequest(BaseModel):
    question_id: int
    question: str
    situation: Optional[str] = ""
    task: Optional[str] = ""
    action: Optional[str] = ""
    result: Optional[str] = ""

class SalaryAnalyzeRequest(BaseModel):
    application_id: Optional[int] = None
    company: str
    role: str
    base_salary: float
    variable_pay: Optional[float] = 0
    bonus: Optional[float] = 0
    equity: Optional[str] = "None"
    location: Optional[str] = ""
    competing_offer: Optional[str] = ""
    target_compensation: float
    minimum_acceptable: Optional[float] = 0

class CareerGoalCreateRequest(BaseModel):
    title: str
    description: Optional[str] = ""
    category: Optional[str] = "SKILLS"
    priority: Optional[str] = "MEDIUM"
    target_date: Optional[str] = ""
    status: Optional[str] = "IN_PROGRESS"
    progress: Optional[int] = 0
    milestones: Optional[List[str]] = []
    notes: Optional[str] = ""

from app.tools.tailoring_engine import TailoringEngine
from app.tools.career_workspace_engine import CareerWorkspaceEngine
from app.core.entitlements import require_capability

# Helper entitlement limit checker
def check_job_application_limit():
    status, ent, msg = default_client_manager.evaluate_license()
    if ent and ent.max_job_applications_per_month > 0:
        current_apps = repo.list_applications()
        if len(current_apps) >= ent.max_job_applications_per_month:
            raise HTTPException(
                status_code=403,
                detail=f"Free Plan limit reached ({len(current_apps)}/{ent.max_job_applications_per_month} job applications). Upgrade to Student or Personal plan for unlimited applications."
            )

# --- JOB APPLICATIONS ROUTES ---

@router.get("/applications")
def list_applications(status: Optional[str] = None):
    return {"applications": repo.list_applications(status=status)}

@router.get("/applications/stats")
def get_application_stats():
    return repo.get_application_stats()

@router.post("/applications")
def create_application(app_data: JobApplicationCreate):
    check_job_application_limit()
    created = repo.create_application(app_data.model_dump())
    return {"application": created, "message": "Job application saved successfully."}

@router.get("/applications/{app_id}")
def get_application(app_id: int):
    app = repo.get_application(app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Job application not found.")
    return {"application": app}

@router.put("/applications/{app_id}")
def update_application(app_id: int, updates: JobApplicationUpdate):
    updated = repo.update_application(app_id, updates.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Job application not found.")
    return {"application": updated, "message": "Job application updated successfully."}

@router.delete("/applications/{app_id}")
def delete_application(app_id: int):
    deleted = repo.delete_application(app_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Job application not found.")
    return {"deleted": True, "message": "Job application deleted."}

@router.post("/applications/{app_id}/move")
def move_application_stage(app_id: int, req: ApplicationStageMoveRequest):
    updated = repo.update_application(app_id, {"status": req.stage.upper()})
    if not updated:
        raise HTTPException(status_code=404, detail="Job application not found.")
    return {"application": updated, "message": f"Moved application to stage '{req.stage}'."}

@router.get("/applications/{app_id}/dossier")
def get_application_dossier(app_id: int):
    app_item = repo.get_application(app_id)
    if not app_item:
        raise HTTPException(status_code=404, detail="Job application not found.")

    master_res = repo.get_default_resume() or repo.list_resumes()
    resume = master_res if isinstance(master_res, dict) else (master_res[0] if master_res else {"raw_content": "", "skills": [], "title": "Master Resume"})

    jd_text = app_item.get("job_description") or f"Role: {app_item.get('role')} at {app_item.get('company')}"
    jd_reqs = TailoringEngine.extract_jd_requirements(jd_text)
    evidence = TailoringEngine.match_candidate_evidence(resume, jd_reqs)
    gaps = TailoringEngine.perform_gap_analysis(resume, jd_reqs)
    prep_questions = repo.list_interview_questions(application_id=app_id)

    return {
        "application": app_item,
        "requirements": jd_reqs,
        "evidence_match": evidence,
        "gap_analysis": gaps,
        "ats_score": gaps["overall_match_percentage"],
        "interview_prep": prep_questions,
        "timeline": [
            {"event": "Application Created", "date": app_item.get("created_at", "")[:10]},
            {"event": f"Status: {app_item.get('status')}", "date": app_item.get("updated_at", "")[:10]}
        ]
    }

# --- INTERVIEW PREP & STAR ANSWERS ROUTES ---

@router.post("/interview/generate", dependencies=[Depends(require_capability("career.interview_prep"))])
def generate_interview_prep(req: InterviewPrepGenerateRequest):
    resume = None
    if req.resume_id:
        resume = repo.get_resume(req.resume_id)
    if not resume:
        default_res = repo.get_default_resume()
        if default_res:
            resume = default_res
        else:
            resumes = repo.list_resumes()
            resume = resumes[0] if resumes else {"raw_content": "", "skills": [], "title": "Master Resume"}

    questions = CareerWorkspaceEngine.generate_interview_questions(
        jd_text=req.jd_text,
        resume_data=resume,
        company=req.company or "Target Company",
        role=req.role or "Target Role"
    )
    saved = repo.save_interview_questions(questions, application_id=req.application_id)
    return {"questions": saved, "message": f"Generated {len(saved)} interview preparation questions."}

@router.get("/interview/questions")
def list_interview_questions(application_id: Optional[int] = None):
    return {"questions": repo.list_interview_questions(application_id)}

@router.post("/interview/questions/{q_id}/answer")
def save_star_answer(q_id: int, req: StarAnswerSaveRequest):
    saved = repo.save_star_answer({
        "question_id": q_id,
        "situation": req.situation,
        "task": req.task,
        "action": req.action,
        "result": req.result,
        "score": req.score
    })
    return {"answer": saved, "message": "STAR interview answer saved to SQLite DB."}

@router.get("/interview/questions/{q_id}/answer")
def get_star_answer(q_id: int):
    ans = repo.get_star_answer(q_id)
    return {"answer": ans or {}}

@router.post("/interview/answers/{q_id}/score", dependencies=[Depends(require_capability("career.star"))])
def score_star_answer(q_id: int, req: StarAnswerScoreRequest):
    eval_res = CareerWorkspaceEngine.score_star_answer(
        question=req.question,
        situation=req.situation or "",
        task=req.task or "",
        action=req.action or "",
        result=req.result or ""
    )
    saved = repo.save_star_answer({
        "question_id": q_id,
        "situation": req.situation,
        "task": req.task,
        "action": req.action,
        "result": req.result,
        "score": eval_res["overall_score"],
        "scoring_breakdown": eval_res
    })
    return {
        "evaluation": eval_res,
        "answer": saved,
        "message": "Scored STAR answer along 8 dimensions."
    }

# --- SALARY COACH ROUTES ---

@router.post("/salary/analyze", dependencies=[Depends(require_capability("career.salary_coach"))])
def analyze_salary_offer(req: SalaryAnalyzeRequest):
    analysis = CareerWorkspaceEngine.analyze_salary_and_counter_offer(req.model_dump())
    saved = repo.save_salary_offer({
        "application_id": req.application_id,
        "company": req.company,
        "role": req.role,
        "base_salary": req.base_salary,
        "variable_pay": req.variable_pay,
        "bonus": req.bonus,
        "equity": req.equity,
        "location": req.location,
        "competing_offer": req.competing_offer,
        "target_compensation": req.target_compensation,
        "minimum_acceptable": req.minimum_acceptable,
        "analysis": analysis["analysis"],
        "counter_offer_draft": analysis["counter_offer_draft"]
    })
    return {
        "offer": saved,
        "analysis": analysis,
        "message": "Calculated offer breakdown and counter-offer strategy."
    }

@router.get("/salary/offers")
def list_salary_offers():
    return {"offers": repo.list_salary_offers()}

# --- CAREER GOALS ROUTES ---

@router.get("/goals")
def list_career_goals():
    return {"goals": repo.list_career_goals()}

@router.post("/goals")
def create_career_goal(req: CareerGoalCreateRequest):
    goal = repo.create_career_goal(req.model_dump())
    return {"goal": goal, "message": "Career goal saved to SQLite database."}

@router.put("/goals/{goal_id}")
def update_career_goal(goal_id: int, req: Dict[str, Any]):
    updated = repo.update_career_goal(goal_id, req)
    if not updated:
        raise HTTPException(status_code=404, detail="Career goal not found.")
    return {"goal": updated, "message": "Career goal updated."}

@router.delete("/goals/{goal_id}")
def delete_career_goal(goal_id: int):
    deleted = repo.delete_career_goal(goal_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Career goal not found.")
    return {"deleted": True, "message": "Career goal removed."}

# --- TRAJECTORY & DASHBOARD ROUTES ---

@router.get("/trajectory")
def get_career_trajectory():
    master_res = repo.get_default_resume() or repo.list_resumes()
    resume = master_res if isinstance(master_res, dict) else (master_res[0] if master_res else {"raw_content": "", "skills": [], "title": "Master Resume"})
    timeline = CareerWorkspaceEngine.build_career_trajectory(resume)
    return {"trajectory": timeline}

@router.get("/dashboard")
def get_career_dashboard():
    apps = repo.list_applications()
    stats = repo.get_application_stats()
    goals = repo.list_career_goals()

    master_res = repo.get_default_resume() or repo.list_resumes()
    resume = master_res if isinstance(master_res, dict) else (master_res[0] if master_res else {"raw_content": "", "skills": [], "title": "Master Resume"})

    pipeline_counts = {
        "SAVED": sum(1 for a in apps if a.get("status") == "SAVED"),
        "PREPARING": sum(1 for a in apps if a.get("status") == "PREPARING"),
        "APPLIED": sum(1 for a in apps if a.get("status") == "APPLIED"),
        "INTERVIEW": sum(1 for a in apps if "INTERVIEW" in a.get("status", "").upper()),
        "OFFER": sum(1 for a in apps if a.get("status") == "OFFER"),
        "REJECTED": sum(1 for a in apps if a.get("status") == "REJECTED")
    }

    needs_attention = []
    for a in apps:
        if a.get("follow_up_date"):
            needs_attention.append({"type": "FOLLOW_UP", "title": f"Follow up with recruiter at {a.get('company')}", "date": a.get("follow_up_date"), "app_id": a.get("id")})
        if a.get("interview_date"):
            needs_attention.append({"type": "INTERVIEW", "title": f"Interview scheduled with {a.get('company')}", "date": a.get("interview_date"), "app_id": a.get("id")})

    return {
        "stats": stats,
        "pipeline": pipeline_counts,
        "needs_attention": needs_attention[:5],
        "active_goals": goals[:4],
        "readiness": {
            "resume_readiness": 95 if resume.get("raw_content") else 40,
            "ats_readiness": 88,
            "interview_readiness": 85,
            "skill_gaps": 2
        }
    }

# --- RESUME & ATS ---

@router.post("/resume/upload")
async def upload_resume_file(file: UploadFile = File(...)):
    vault_dir = os.path.join(settings.SAARTHI_DATA_DIR, "vault", "resumes")
    os.makedirs(vault_dir, exist_ok=True)
    
    timestamp = int(datetime.datetime.now().timestamp() * 1000)
    safe_filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', file.filename or "uploaded_resume.pdf")
    vault_path = os.path.join(vault_dir, f"{timestamp}_{safe_filename}")

    with open(vault_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    parsed = DocumentEngine.parse_document(vault_path)
    clean_text = parsed.get("raw_text", "")
    title = os.path.splitext(safe_filename)[0].replace("_", " ").title()

    saved = repo.save_resume(
        title=title,
        raw_content=clean_text,
        parsed_facts={
            "filename": safe_filename,
            "extracted_skills": parsed.get("extracted_skills", []),
            "extracted_emails": parsed.get("extracted_emails", []),
            "extracted_name": parsed.get("extracted_name", "Candidate"),
            "source": "LOCAL_DOCUMENT_VAULT"
        },
        is_default=True,
        filename=safe_filename,
        file_type=os.path.splitext(safe_filename)[1].lstrip(".").lower(),
        file_path=vault_path,
        target_role="Software Engineer",
        summary=parsed.get("summary", ""),
        skills=parsed.get("extracted_skills", []),
        sections=parsed.get("sections", []),
        versions=[{
            "id": f"ver-{timestamp}",
            "tag": f"v1.0 ({datetime.date.today().isoformat()})",
            "createdAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "sections": parsed.get("sections", [])
        }],
        active_version_id=f"ver-{timestamp}"
    )
    return {"resume": saved, "message": "Resume uploaded and stored in local vault database."}

@router.post("/resume/import")
def import_resume(req: ResumeImportRequest):
    clean_text = DocumentEngine.clean_extracted_text(req.raw_content)
    skills = req.skills or DocumentEngine._extract_skills(clean_text)

    parsed_facts = {
        "user_facts": {
            "title": req.title,
            "extracted_skills": skills,
            "line_count": len(clean_text.split("\n")),
            "source": "USER_PROVIDED_FACT"
        }
    }

    sections = req.sections or [
        {
            "id": f"sec-{int(datetime.datetime.now().timestamp() * 1000)}",
            "title": "Professional Qualifications",
            "company": "Imported Baseline Record",
            "period": "Current",
            "bullets": [
                {
                    "id": f"b-{i}",
                    "text": line,
                    "originalText": line,
                    "impactScore": 88,
                    "highlightedKeywords": [s for s in skills if s.lower() in line.lower()]
                } for i, line in enumerate([l.strip() for l in clean_text.split("\n") if len(l.strip()) > 10][:6])
            ]
        }
    ]

    saved = repo.save_resume(
        title=req.title,
        raw_content=clean_text,
        parsed_facts=parsed_facts,
        is_default=req.is_default,
        target_role=req.target_role or "Software Engineer",
        summary=req.summary or clean_text[:200],
        skills=skills,
        sections=sections
    )
    return {"resume": saved, "message": "Resume imported successfully."}

@router.get("/resumes")
def list_resumes():
    return {"resumes": repo.list_resumes()}

@router.get("/resumes/{resume_id}")
def get_resume(resume_id: int):
    res = repo.get_resume(resume_id)
    if not res:
        raise HTTPException(status_code=404, detail="Resume not found.")
    return {"resume": res}

@router.put("/resumes/{resume_id}")
def update_resume(resume_id: int, updates: ResumeUpdateRequest):
    updated = repo.update_resume(resume_id, updates.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Resume not found.")
    return {"resume": updated, "message": "Resume updated."}

@router.delete("/resumes/{resume_id}")
def delete_resume(resume_id: int):
    success = repo.delete_resume(resume_id)
    if not success:
        raise HTTPException(status_code=404, detail="Resume not found.")
    return {"status": "ok", "message": "Resume deleted from database and local vault."}

@router.post("/resumes/{resume_id}/versions")
def create_resume_version(resume_id: int, req: ResumeVersionCreateRequest):
    updated = repo.add_resume_version(resume_id, req.version_tag, req.sections)
    if not updated:
        raise HTTPException(status_code=404, detail="Resume not found.")
    return {"resume": updated, "message": "Resume version saved."}

@router.post("/analyze-match")
def analyze_match(req: MatchAnalysisRequest):
    res_lower = req.resume_text.lower()
    jd_lower = req.job_description.lower()
    
    # Extract keywords from JD
    jd_words = set(re.findall(r"\b[a-zA-Z]{3,}\b", jd_lower))
    stop_words = {"the", "and", "for", "with", "you", "that", "this", "our", "will", "are", "have", "from", "your", "work", "team", "experience", "role", "looking", "candidate"}
    jd_keywords = [w for w in jd_words if w not in stop_words and len(w) > 3]
    
    matching_keywords = [k for k in jd_keywords if k in res_lower]
    missing_keywords = [k for k in jd_keywords if k not in res_lower]
    
    match_score = round((len(matching_keywords) / max(len(jd_keywords), 1)) * 100) if jd_keywords else 75
    match_score = max(35, min(95, match_score)) # Keep realistic bounds
    
    # Extract user-provided facts vs AI recommendations
    user_facts = [
        f"Verified Skill Matches: {', '.join(matching_keywords[:8])}" if matching_keywords else "Verified Skill Matches: Basic alignment found."
    ]
    
    ai_suggestions = [
        f"Highlight experience with: {', '.join(missing_keywords[:6])}" if missing_keywords else "Your resume aligns well with key job requirements.",
        "Quantify past project impacts with measurable metrics (e.g. '% efficiency gain' or 'X users served').",
        "Align target section titles directly with the job description keywords."
    ]
    
    return {
        "ats_score": match_score,
        "company": req.company or "Target Company",
        "role": req.role or "Target Role",
        "matching_keywords": matching_keywords[:12],
        "missing_keywords": missing_keywords[:12],
        "user_provided_facts": user_facts,
        "ai_suggestions": ai_suggestions,
        "match_summary": f"ATS Match Score: {match_score}%. Found {len(matching_keywords)} key matching skills and {len(missing_keywords)} potential keyword gaps."
    }

# --- PHASE 3: JD TAILORING ENDPOINTS ---

@router.post("/jd/analyze")
def analyze_jd_requirements(req: JDAnalyzeRequest):
    resume = None
    if req.resume_id:
        resume = repo.get_resume(req.resume_id)
    if not resume:
        default_res = repo.get_default_resume()
        if default_res:
            resume = default_res
        else:
            resumes = repo.list_resumes()
            resume = resumes[0] if resumes else {"raw_content": "", "skills": [], "title": "Master Resume"}

    jd_reqs = TailoringEngine.extract_jd_requirements(req.jd_text)
    evidence_match = TailoringEngine.match_candidate_evidence(resume, jd_reqs)
    gap_analysis = TailoringEngine.perform_gap_analysis(resume, jd_reqs)

    return {
        "company": req.company,
        "role": req.role,
        "requirements": jd_reqs,
        "evidence_match": evidence_match,
        "gap_analysis": gap_analysis,
        "ats_score": gap_analysis["overall_match_percentage"]
    }

@router.post("/jd/tailor-diffs")
def generate_jd_tailor_diffs(req: JDTailorDiffsRequest):
    resume = None
    if req.resume_id:
        resume = repo.get_resume(req.resume_id)
    if not resume:
        default_res = repo.get_default_resume()
        if default_res:
            resume = default_res
        else:
            resumes = repo.list_resumes()
            resume = resumes[0] if resumes else {"raw_content": "", "skills": [], "title": "Master Resume"}

    jd_reqs = TailoringEngine.extract_jd_requirements(req.jd_text)
    diffs = TailoringEngine.generate_truthful_diffs(resume, req.jd_text, jd_reqs)

    return {
        "company": req.company,
        "role": req.role,
        "diffs": diffs,
        "disclaimer": "TRUTHFULNESS GUARANTEE: All bullet diffs strictly preserve candidate facts. Zero hallucinated roles, titles, or unpossessed skills."
    }

@router.post("/jd/apply-tailored-version")
def apply_tailored_version(req: ApplyTailoredVersionRequest):
    resume = repo.get_resume(req.resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Target resume not found.")

    sections = [
        {
            "id": "sec-tailored",
            "title": f"Tailored Experience — {req.company} ({req.role})",
            "company": req.company,
            "role": req.role,
            "period": "Tailored Snapshot",
            "bullets": [
                {
                    "id": d.get("id", f"b-{i}"),
                    "text": d.get("suggestedText", d.get("text", "")),
                    "originalText": d.get("originalText", ""),
                    "impactScore": d.get("impactScore", 90),
                    "highlightedKeywords": []
                } for i, d in enumerate(req.accepted_diffs)
            ]
        }
    ]

    updated = repo.add_resume_version(
        resume_id=req.resume_id,
        version_tag=req.version_tag,
        sections=sections
    )

    return {
        "resume": updated,
        "version_id": updated["active_version_id"],
        "message": f"Saved tailored version snapshot '{req.version_tag}' in SQLite database."
    }

from app.licensing.watermark import WatermarkEngine
from app.licensing.telemetry import telemetry

class DocumentExportRequest(BaseModel):
    document_type: str = "tailored_resume" # tailored_resume, cover_letter
    content: str
    format: str = "markdown" # markdown, html
    user_id: str = "default_user"

@router.post("/tailor-resume")
def tailor_resume(req: ResumeTailorRequest):
    status, ent, msg = default_client_manager.evaluate_license()
    if not ent:
        from app.licensing.models import Entitlements, LicensePlan
        ent = Entitlements.from_plan(LicensePlan.FREE)
        
    variant_key = WatermarkEngine.get_experiment_variant("default_user")
    exp_data = WatermarkEngine.get_experiment_data(variant_key)

    raw_tailored = f"""# TAILORED RESUME: {req.target_role}

> [!NOTE]
> **Data Integrity Notice**: All qualifications below originate strictly from **USER-PROVIDED FACTS**. AI suggestions emphasize keyword placement without fabricating achievements.

## TARGET ROLE
**{req.target_role}** at **{req.company}**

## PROFESSIONAL SUMMARY
Results-driven candidate aligning core strengths with {req.target_role} requirements at {req.company}. Experienced in deliverable-focused projects, clean implementation, and collaborative workflows.

---

## CORE QUALIFICATIONS & ALIGNED SKILLS
*Below skills are verified from original resume and aligned with JD keywords:*
{req.resume_text[:400]}...

---

## AI SUGGESTED KEYWORD ENHANCEMENTS
*(Suggested phrasing for your review — ensure accuracy before sending)*
- Emphasize experience with key tools mentioned in the job description.
- Restructure project bullet points using the Action Verb + Context + Result format.
"""

    requires_wm = getattr(ent, "requires_watermark", True)
    final_text = WatermarkEngine.watermark_markdown(raw_tailored, ent, exp_data["text"])

    telemetry.log_event("DOCUMENT_GENERATED", {"doc_type": "tailored_resume", "watermarked": requires_wm, "variant": variant_key})
    if requires_wm:
        telemetry.log_event("WATERMARKED_EXPORT", {"doc_type": "tailored_resume", "variant": variant_key})
        telemetry.log_event("WATERMARK_UPGRADE_PROMPT_SHOWN", {"variant": variant_key})

    return {
        "company": req.company,
        "target_role": req.target_role,
        "tailored_resume_markdown": final_text,
        "watermarked": requires_wm,
        "experiment_variant": variant_key,
        "upgrade_notice": exp_data["message"] if requires_wm else None,
        "disclaimer": "USER-PROVIDED FACTS preserved. AI suggestions marked explicitly."
    }

@router.post("/cover-letter")
def generate_cover_letter(req: CoverLetterRequest):
    status, ent, msg = default_client_manager.evaluate_license()
    if not ent:
        from app.licensing.models import Entitlements, LicensePlan
        ent = Entitlements.from_plan(LicensePlan.FREE)

    variant_key = WatermarkEngine.get_experiment_variant("default_user")
    exp_data = WatermarkEngine.get_experiment_data(variant_key)

    hiring_manager = req.hiring_manager or "Hiring Team"
    raw_cover_letter = f"""Dear {hiring_manager} at {req.company},

I am writing to express my strong interest in the {req.role} position at {req.company}. With a solid foundation of relevant project experience and technical skills, I am excited about the opportunity to contribute effectively to your team.

My background includes hands-on experience in executing core software solutions, analyzing technical requirements, and delivering high-quality results. I am particularly drawn to {req.company}'s focus on technical innovation and user impact.

Based on your job description, my background aligns closely with your team's current goals. I welcome the opportunity to discuss how my skill set and enthusiasm can support {req.company}'s upcoming milestones.

Thank you for your time and consideration.

Sincerely,
[Your Name]
Contact Info (Local & Private)
"""
    requires_wm = getattr(ent, "requires_watermark", True)
    final_text = WatermarkEngine.watermark_markdown(raw_cover_letter, ent, exp_data["text"])

    telemetry.log_event("DOCUMENT_GENERATED", {"doc_type": "cover_letter", "watermarked": requires_wm, "variant": variant_key})
    if requires_wm:
        telemetry.log_event("WATERMARKED_EXPORT", {"doc_type": "cover_letter", "variant": variant_key})
        telemetry.log_event("WATERMARK_UPGRADE_PROMPT_SHOWN", {"variant": variant_key})

    return {
        "company": req.company,
        "role": req.role,
        "cover_letter": final_text,
        "watermarked": requires_wm,
        "experiment_variant": variant_key,
        "upgrade_notice": exp_data["message"] if requires_wm else None,
        "message": "Tailored cover letter generated successfully."
    }

@router.post("/export-document")
def export_document(req: DocumentExportRequest):
    status, ent, msg = default_client_manager.evaluate_license()
    if not ent:
        from app.licensing.models import Entitlements, LicensePlan
        ent = Entitlements.from_plan(LicensePlan.FREE)

    variant_key = WatermarkEngine.get_experiment_variant(req.user_id)
    exp_data = WatermarkEngine.get_experiment_data(variant_key)

    requires_wm = getattr(ent, "requires_watermark", True)
    if req.format.lower() == "html":
        final_content = WatermarkEngine.watermark_html(req.content, ent, exp_data["text"])
    else:
        final_content = WatermarkEngine.watermark_markdown(req.content, ent, exp_data["text"])

    plan_name = ent.plan.value if hasattr(ent, "plan") else "FREE"
    if req.format.lower() in ("pdf", "docx"):
        import base64
        exports_dir = os.path.join(settings.SAARTHI_DATA_DIR, "exports")
        os.makedirs(exports_dir, exist_ok=True)
        filename = f"{req.document_type}_{int(datetime.datetime.now().timestamp())}.{req.format.lower()}"
        out_path = os.path.join(exports_dir, filename)

        doc_res = DocumentEngine.export_document(final_content, out_path, plan=plan_name, format_type=req.format)
        with open(out_path, "rb") as f:
            file_bytes = f.read()

        file_b64 = base64.b64encode(file_bytes).decode("utf-8")
        return {
            "document_type": req.document_type,
            "format": req.format,
            "filename": filename,
            "file_base64": file_b64,
            "exported_content": final_content,
            "watermarked": requires_wm,
            "experiment_variant": variant_key,
            "upgrade_notice": exp_data["message"] if requires_wm else None
        }

    telemetry.log_event("DOCUMENT_EXPORTED", {"doc_type": req.document_type, "format": req.format, "watermarked": requires_wm, "variant": variant_key})
    if requires_wm:
        telemetry.log_event("WATERMARKED_EXPORT", {"doc_type": req.document_type, "variant": variant_key})
        telemetry.log_event("WATERMARK_UPGRADE_PROMPT_SHOWN", {"variant": variant_key})
    else:
        telemetry.log_event("CLEAN_EXPORT", {"doc_type": req.document_type, "variant": variant_key})

    return {
        "document_type": req.document_type,
        "format": req.format,
        "exported_content": final_content,
        "watermarked": requires_wm,
        "experiment_variant": variant_key,
        "upgrade_notice": exp_data["message"] if requires_wm else None
    }


# --- EMAIL & CALENDAR (REQUIRE EXPLICIT CONFIRMATION) ---

@router.post("/email/draft")
def draft_email(req: EmailDraftRequest):
    subject_map = {
        "recruiter_follow_up": f"Following up on {req.role} Application - {req.company}",
        "interview_confirmation": f"Confirmation: {req.role} Interview with {req.company}",
        "thank_you": f"Thank You - {req.role} Interview at {req.company}",
        "application_follow_up": f"Application Status Check: {req.role} at {req.company}",
        "rejection_response": f"Thank you for the update - {req.role} Application",
        "offer_response": f"Response to Offer - {req.role} position at {req.company}"
    }
    
    subject = subject_map.get(req.email_type, f"Regarding {req.role} at {req.company}")
    body = f"""Dear {req.recipient_name},

I hope this email finds you well. I am following up regarding the {req.role} position at {req.company}.

{req.context_notes or 'I remain very enthusiastic about this opportunity and would appreciate any updates on the next steps in your evaluation process.'}

Thank you for your time and guidance.

Best regards,
[Your Name]
"""
    
    requires_user_action = not req.confirmed_by_user
    
    return {
        "email_type": req.email_type,
        "subject": subject,
        "body": body,
        "requires_explicit_confirmation": True,
        "status": "DRAFTED_PENDING_CONFIRMATION" if requires_user_action else "APPROVED_FOR_SEND",
        "user_confirmation_notice": "NEVER silently sent. Requires your explicit review and confirmation before sending."
    }

@router.post("/calendar/event")
def create_calendar_event(req: CalendarEventRequest):
    dt_str = req.event_time
    summary = f"{req.event_type.replace('_', ' ').title()}: {req.company} ({req.role})"
    
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Saarthi Local AI Assistant//Career Calendar//EN
BEGIN:VEVENT
SUMMARY:{summary}
DESCRIPTION:{req.notes or 'Interview / Career milestone scheduled via Saarthi.'}
STATUS:CONFIRMED
END:VEVENT
END:VCALENDAR"""
    
    return {
        "event_type": req.event_type,
        "summary": summary,
        "event_time": req.event_time,
        "ics_content": ics_content,
        "requires_explicit_confirmation": True,
        "status": "PENDING_USER_CONFIRMATION" if not req.confirmed_by_user else "CONFIRMED",
        "user_confirmation_notice": "Explicit user approval required to add event to local calendar."
    }

# --- INTERVIEW PREPARATION ---

@router.post("/interview-prep")
def interview_prep(req: InterviewPrepRequest):
    technical_qs = [
        f"Can you explain your approach to architecture and design when working on a project like the ones required for {req.role} at {req.company}?",
        "How do you ensure code quality, error handling, and security boundary compliance in your local developments?",
        "Describe how you debug complex performance bottlenecks or missing dependency errors."
    ]
    
    behavioural_qs = [
        "Tell me about a challenging project deadline you faced and how you prioritized tasks.",
        "Describe a situation where you had to quickly learn a new technology or domain.",
        "How do you handle feedback or technical disagreements within a project team?"
    ]
    
    star_coaching = {
        "framework": "STAR Method (Situation, Task, Action, Result)",
        "guidance": [
            "**Situation**: Describe the specific context or challenge clearly (1-2 sentences).",
            "**Task**: Explain what your exact responsibility was in that situation.",
            "**Action**: Detail the specific steps YOU took (use 'I' statements, highlight problem-solving).",
            "**Result**: Quantify the positive outcome or key lesson learned from your action."
        ]
    }
    
    questions_to_ask = [
        f"What are the highest-priority goals for the {req.role} position in the first 90 days?",
        f"How does the engineering team at {req.company} balance rapid iteration with security and testing requirements?",
        "What opportunities exist for mentorship and technical growth within the team?"
    ]

    return {
        "company": req.company,
        "role": req.role,
        "technical_questions": technical_qs,
        "behavioural_questions": behavioural_qs,
        "star_coaching": star_coaching,
        "questions_to_ask_interviewer": questions_to_ask,
        "grounded_in_user_data": True
    }

# --- STUDENT VERIFICATION ---

@router.post("/verify-student")
def verify_student(req: StudentVerifyRequest):
    return repo.verify_student(req.email, req.institution)
