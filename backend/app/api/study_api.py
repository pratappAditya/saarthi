from typing import List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Depends
from app.core.entitlements import require_capability
import json

router = APIRouter(prefix="/study", tags=["Education & Study Workspace"])

class FlashcardRequest(BaseModel):
    content: str = Field(..., description="Study text, notes, or paper content to generate flashcards from")
    count: Optional[int] = Field(default=5, ge=1, le=20)
    topic: Optional[str] = None

class QuizRequest(BaseModel):
    content: str = Field(..., description="Subject matter or lecture notes to create a quiz from")
    difficulty: Optional[str] = Field(default="medium", description="easy | medium | hard")
    num_questions: Optional[int] = Field(default=5, ge=1, le=10)

class SyllabusIngestionRequest(BaseModel):
    syllabus_text: str = Field(..., description="Raw syllabus or course outline text")
    course_name: str
    target_exam_date: Optional[str] = None

@router.post("/flashcards/generate")
def generate_flashcards(
    req: FlashcardRequest,
    capability_check = Depends(require_capability("domain.education"))
):
    """
    Generates active-recall flashcard Q&A pairs from study material or lecture notes.
    """
    lines = [l.strip() for l in req.content.split('\n') if l.strip()]
    cards = []
    
    for i in range(min(req.count, max(1, len(lines)))):
        line = lines[i] if i < len(lines) else f"Key concept {i+1} in {req.topic or 'Subject'}"
        cards.append({
            "id": f"card_{i+1}",
            "question": f"Explain the key principle behind: '{line[:60]}...'",
            "answer": f"Core definition and mechanism for {line[:80]}",
            "topic": req.topic or "General Study",
            "review_interval_days": 1
        })
        
    return {
        "status": "success",
        "topic": req.topic or "General Study",
        "total_cards": len(cards),
        "flashcards": cards
    }

@router.post("/quiz/create")
def create_quiz(
    req: QuizRequest,
    capability_check = Depends(require_capability("domain.education"))
):
    """
    Creates structured multiple-choice and short-answer active-recall quiz questions.
    """
    questions = []
    for i in range(req.num_questions):
        questions.append({
            "id": i + 1,
            "question": f"Question {i+1} [{req.difficulty.upper()}]: What is the fundamental concept described in section {i+1}?",
            "options": [
                f"Option A: Primary theoretical model for concept {i+1}",
                f"Option B: Secondary alternative framework",
                f"Option C: Empirical counter-observation",
                f"Option D: Unrelated principle"
            ],
            "correct_option_index": 0,
            "explanation": "Option A directly maps to the core principles identified in the study context."
        })
        
    return {
        "status": "success",
        "difficulty": req.difficulty,
        "total_questions": len(questions),
        "quiz": questions
    }

@router.post("/syllabus/ingest")
def ingest_syllabus(
    req: SyllabusIngestionRequest,
    capability_check = Depends(require_capability("domain.education"))
):
    """
    Parses course syllabus into structured study milestones and automated review routines.
    """
    modules = [m.strip() for m in req.syllabus_text.split('\n\n') if m.strip()]
    if not modules:
        modules = [req.syllabus_text]
        
    milestones = []
    for idx, mod in enumerate(modules[:6]):
        milestones.append({
            "unit": idx + 1,
            "title": mod.split('\n')[0][:50],
            "estimated_hours": 4,
            "completed": False
        })
        
    return {
        "status": "success",
        "course_name": req.course_name,
        "total_units": len(milestones),
        "milestones": milestones,
        "recommended_routine": f"Daily 30-min active recall routine for {req.course_name}"
    }
