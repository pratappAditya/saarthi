import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, Request, HTTPException
from app.core.telemetry import telemetry
from app.db.connection import get_db_connection, with_db_retry

router = APIRouter(prefix="/beta", tags=["External Beta Readiness"])

class BetaFeedbackRequest(BaseModel):
    category: str = Field(default="FEEDBACK", description="BUG | FEATURE_REQUEST | FEEDBACK | UX")
    title: str = Field(..., min_length=2, max_length=200)
    description: str = Field(..., min_length=5, max_length=4000)
    user_email: Optional[str] = None
    rating: Optional[int] = Field(default=5, ge=1, le=5)
    page_context: Optional[str] = None

class CrashReportRequest(BaseModel):
    component: str
    error_name: str
    error_message: str
    stack_trace: Optional[str] = None
    user_agent: Optional[str] = None
    page_url: Optional[str] = None

@with_db_retry()
def init_beta_tables():
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_beta_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                user_email TEXT,
                rating INTEGER DEFAULT 5,
                page_context TEXT,
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS crash_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                component TEXT NOT NULL,
                error_name TEXT NOT NULL,
                error_message TEXT NOT NULL,
                stack_trace TEXT,
                user_agent TEXT,
                page_url TEXT,
                created_at TEXT NOT NULL
            )
        """)

# Initialize tables safely
try:
    init_beta_tables()
except Exception:
    pass

@router.post("/feedback")
def submit_beta_feedback(req: BetaFeedbackRequest, request: Request):
    """
    Ingest external beta user feedback, bug reports, and feature suggestions.
    """
    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        init_beta_tables()
        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO user_beta_feedback (category, title, description, user_email, rating, page_context, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (req.category, req.title, req.description, req.user_email, req.rating, req.page_context, now_str))
        return {
            "status": "success",
            "message": "Thank you for contributing to the Saarthi Beta! Your feedback has been recorded."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")

@router.post("/crash-report")
def submit_crash_report(req: CrashReportRequest, request: Request):
    """
    Ingest client-side frontend crash reports and unhandled React error telemetry.
    """
    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
    telemetry.record_crash_report()
    try:
        init_beta_tables()
        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO crash_reports (component, error_name, error_message, stack_trace, user_agent, page_url, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (req.component, req.error_name, req.error_message, req.stack_trace, req.user_agent or request.headers.get("User-Agent"), req.page_url, now_str))
        return {"status": "success", "message": "Crash report recorded."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record crash report: {str(e)}")

@router.get("/status")
def get_beta_environment_status():
    """
    Returns beta environment status and release notes for onboarding users.
    """
    return {
        "status": "success",
        "beta_channel": "External Public Beta (Candidate v0.5.0-rc2)",
        "build_version": "0.5.0-rc2",
        "features_active": [
            "Universal AI Operating Companion",
            "17 Autonomous Domain Packs",
            "Local Zero-Leak Memory Core",
            "Privileged Admin Control Panel",
            "Hardware-Adaptive Nemotron Intelligence Engine"
        ],
        "beta_support_email": "beta@saarthi.ai"
    }
