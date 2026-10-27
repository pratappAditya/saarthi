import os
import sqlite3
import json
import datetime
from typing import List, Dict, Any, Optional
from app.config.settings import settings
from app.tools.document_engine import DocumentEngine

from app.db.connection import get_db_connection

def init_career_tables(db_path: str = None):
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                role TEXT NOT NULL,
                job_url TEXT,
                location TEXT,
                salary TEXT,
                date_applied TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'SAVED',
                resume_version TEXT,
                cover_letter TEXT,
                recruiter_contact TEXT,
                next_action TEXT,
                follow_up_date TEXT,
                interview_date TEXT,
                notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                filename TEXT,
                file_type TEXT,
                file_path TEXT,
                raw_content TEXT NOT NULL,
                target_role TEXT,
                summary TEXT,
                skills TEXT,
                parsed_facts TEXT,
                sections TEXT,
                versions TEXT,
                active_version_id TEXT,
                is_default INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        # Auto-migrate missing columns for existing SQLite DBs
        cursor.execute("PRAGMA table_info(resumes)")
        existing_cols = {row["name"] for row in cursor.fetchall()}
        new_cols = {
            "filename": "TEXT",
            "file_type": "TEXT",
            "file_path": "TEXT",
            "target_role": "TEXT",
            "summary": "TEXT",
            "skills": "TEXT",
            "sections": "TEXT",
            "versions": "TEXT",
            "active_version_id": "TEXT",
        }
        for col, col_type in new_cols.items():
            if col not in existing_cols:
                cursor.execute(f"ALTER TABLE resumes ADD COLUMN {col} {col_type}")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_verifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                institution TEXT,
                status TEXT NOT NULL DEFAULT 'VERIFIED',
                verified_at TEXT NOT NULL
            )
        """)

        # Auto-migrate job_applications missing columns
        cursor.execute("PRAGMA table_info(job_applications)")
        existing_app_cols = {row["name"] for row in cursor.fetchall()}
        new_app_cols = {
            "job_description": "TEXT",
            "work_mode": "TEXT DEFAULT 'REMOTE'",
            "salary_min": "REAL",
            "salary_max": "REAL",
            "priority": "TEXT DEFAULT 'MEDIUM'",
            "deadline": "TEXT",
            "interview_status": "TEXT",
            "next_action_date": "TEXT",
        }
        for col, col_type in new_app_cols.items():
            if col not in existing_app_cols:
                cursor.execute(f"ALTER TABLE job_applications ADD COLUMN {col} {col_type}")

        # Phase 4 Tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interview_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id INTEGER,
                category TEXT NOT NULL,
                question TEXT NOT NULL,
                difficulty TEXT NOT NULL DEFAULT 'Medium',
                reason TEXT,
                preparation_topics TEXT,
                created_at TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS star_answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER NOT NULL,
                situation TEXT,
                task TEXT,
                action TEXT,
                result TEXT,
                score INTEGER DEFAULT 80,
                scoring_breakdown TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS salary_offers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id INTEGER,
                company TEXT NOT NULL,
                role TEXT NOT NULL,
                base_salary REAL DEFAULT 0,
                variable_pay REAL DEFAULT 0,
                bonus REAL DEFAULT 0,
                equity TEXT,
                location TEXT,
                competing_offer TEXT,
                target_compensation REAL,
                minimum_acceptable REAL,
                analysis TEXT,
                counter_offer_draft TEXT,
                created_at TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS career_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT NOT NULL DEFAULT 'SKILLS',
                priority TEXT NOT NULL DEFAULT 'MEDIUM',
                target_date TEXT,
                status TEXT NOT NULL DEFAULT 'IN_PROGRESS',
                progress INTEGER DEFAULT 0,
                milestones TEXT,
                notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Purge legacy corrupted resume records that contain raw PDF binary streams or markers
        try:
            cursor.execute("DELETE FROM resumes WHERE raw_content LIKE '%PDF-%' OR raw_content LIKE '%/Title%' OR raw_content LIKE '%endobj%'")
            conn.commit()
        except Exception:
            pass

class CareerRepository:
    def __init__(self, db_path: str = None):
        self._db_path = db_path
        init_career_tables(self.db_path)

    @property
    def db_path(self) -> str:
        return self._db_path or settings.DATABASE_PATH

    @db_path.setter
    def db_path(self, val: str):
        self._db_path = val

    # --- JOB APPLICATIONS ---
    def create_application(self, app_data: Dict[str, Any]) -> Dict[str, Any]:
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        date_applied = app_data.get("date_applied") or now_str.split("T")[0]
        status = app_data.get("status", "SAVED").upper()
        
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO job_applications (
                    company, role, job_url, location, salary, date_applied, status,
                    resume_version, cover_letter, recruiter_contact, next_action,
                    follow_up_date, interview_date, notes, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                app_data.get("company", ""),
                app_data.get("role", ""),
                app_data.get("job_url", ""),
                app_data.get("location", ""),
                app_data.get("salary", ""),
                date_applied,
                status,
                app_data.get("resume_version", ""),
                app_data.get("cover_letter", ""),
                app_data.get("recruiter_contact", ""),
                app_data.get("next_action", ""),
                app_data.get("follow_up_date", ""),
                app_data.get("interview_date", ""),
                app_data.get("notes", ""),
                now_str,
                now_str
            ))
            app_id = cursor.lastrowid
            conn.commit()
            return self.get_application(app_id)

    def get_application(self, app_id: int) -> Optional[Dict[str, Any]]:
        with get_db_connection(self.db_path) as conn:
            row = conn.cursor().execute("SELECT * FROM job_applications WHERE id = ?", (app_id,)).fetchone()
            if row:
                return dict(row)
        return None

    def list_applications(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        with get_db_connection(self.db_path) as conn:
            if status:
                rows = conn.cursor().execute(
                    "SELECT * FROM job_applications WHERE status = ? ORDER BY updated_at DESC", (status.upper(),)
                ).fetchall()
            else:
                rows = conn.cursor().execute("SELECT * FROM job_applications ORDER BY updated_at DESC").fetchall()
            return [dict(r) for r in rows]

    def update_application(self, app_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        current = self.get_application(app_id)
        if not current:
            return None
        
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        fields = ["company", "role", "job_url", "location", "salary", "date_applied", "status",
                  "resume_version", "cover_letter", "recruiter_contact", "next_action",
                  "follow_up_date", "interview_date", "notes"]
        
        set_clauses = []
        values = []
        for field in fields:
            if field in updates:
                val = updates[field]
                if field == "status" and isinstance(val, str):
                    val = val.upper()
                set_clauses.append(f"{field} = ?")
                values.append(val)
                
        if not set_clauses:
            return current
            
        set_clauses.append("updated_at = ?")
        values.append(now_str)
        values.append(app_id)
        
        with get_db_connection(self.db_path) as conn:
            conn.cursor().execute(
                f"UPDATE job_applications SET {', '.join(set_clauses)} WHERE id = ?", values
            )
            conn.commit()
            
        return self.get_application(app_id)

    def delete_application(self, app_id: int) -> bool:
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor().execute("DELETE FROM job_applications WHERE id = ?", (app_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_application_stats(self) -> Dict[str, Any]:
        with get_db_connection(self.db_path) as conn:
            rows = conn.cursor().execute("SELECT status, count(*) as cnt FROM job_applications GROUP BY status").fetchall()
            counts = {r["status"]: r["cnt"] for r in rows}
            
            total_apps = sum(counts.values())
            applied_cnt = counts.get("APPLIED", 0) + counts.get("SCREENING", 0) + counts.get("INTERVIEW", 0) + counts.get("OFFER", 0) + counts.get("REJECTED", 0)
            interviews_cnt = counts.get("INTERVIEW", 0)
            offers_cnt = counts.get("OFFER", 0)
            
            response_rate = round((applied_cnt / total_apps * 100), 1) if total_apps > 0 else 0.0
            
            # Count upcoming followups
            today_str = datetime.date.today().isoformat()
            followup_rows = conn.cursor().execute(
                "SELECT count(*) as cnt FROM job_applications WHERE follow_up_date IS NOT NULL AND follow_up_date >= ?", (today_str,)
            ).fetchone()
            upcoming_followups = followup_rows["cnt"] if followup_rows else 0

            return {
                "total_applications": total_apps,
                "interviews": interviews_cnt,
                "offers": offers_cnt,
                "response_rate": f"{response_rate}%",
                "upcoming_followups": upcoming_followups,
                "status_breakdown": counts
            }

    # --- RESUMES ---
    def save_resume(
        self,
        title: str,
        raw_content: str,
        parsed_facts: Dict[str, Any],
        is_default: bool = False,
        filename: str = None,
        file_type: str = None,
        file_path: str = None,
        target_role: str = None,
        summary: str = None,
        skills: List[str] = None,
        sections: List[Dict[str, Any]] = None,
        versions: List[Dict[str, Any]] = None,
        active_version_id: str = None
    ) -> Dict[str, Any]:
        clean_raw = DocumentEngine.clean_extracted_text(raw_content)
        clean_sum = DocumentEngine.clean_extracted_text(summary or "") or "Parsed candidate experience."
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            if is_default:
                cursor.execute("UPDATE resumes SET is_default = 0")
            cursor.execute("""
                INSERT INTO resumes (
                    title, filename, file_type, file_path, raw_content,
                    target_role, summary, skills, parsed_facts, sections,
                    versions, active_version_id, is_default, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                title,
                filename or "",
                file_type or "txt",
                file_path or "",
                clean_raw,
                target_role or "Software Engineer",
                clean_sum,
                json.dumps(skills) if skills else json.dumps([]),
                json.dumps(parsed_facts),
                json.dumps(sections) if sections else json.dumps([]),
                json.dumps(versions) if versions else json.dumps([]),
                active_version_id or "",
                1 if is_default else 0,
                now_str,
                now_str
            ))
            res_id = cursor.lastrowid
            conn.commit()
            return self.get_resume(res_id)

    def get_resume(self, resume_id: int) -> Optional[Dict[str, Any]]:
        with get_db_connection(self.db_path) as conn:
            row = conn.cursor().execute("SELECT * FROM resumes WHERE id = ?", (resume_id,)).fetchone()
            if row:
                return self._format_resume_dict(dict(row))
        return None

    def get_default_resume(self) -> Optional[Dict[str, Any]]:
        with get_db_connection(self.db_path) as conn:
            row = conn.cursor().execute("SELECT * FROM resumes WHERE is_default = 1 ORDER BY id DESC LIMIT 1").fetchone()
            if not row:
                row = conn.cursor().execute("SELECT * FROM resumes ORDER BY id DESC LIMIT 1").fetchone()
            if row:
                return self._format_resume_dict(dict(row))
        return None

    def list_resumes(self) -> List[Dict[str, Any]]:
        with get_db_connection(self.db_path) as conn:
            rows = conn.cursor().execute("SELECT * FROM resumes ORDER BY updated_at DESC").fetchall()
            return [self._format_resume_dict(dict(r)) for r in rows]

    def update_resume(self, resume_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        current = self.get_resume(resume_id)
        if not current:
            return None

        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        allowed_fields = [
            "title", "filename", "file_type", "file_path", "raw_content",
            "target_role", "summary", "is_default", "active_version_id"
        ]
        json_fields = ["skills", "parsed_facts", "sections", "versions"]

        set_clauses = []
        values = []

        for field in allowed_fields:
            if field in updates:
                set_clauses.append(f"{field} = ?")
                values.append(updates[field])

        for field in json_fields:
            if field in updates:
                set_clauses.append(f"{field} = ?")
                val = updates[field]
                values.append(json.dumps(val) if not isinstance(val, str) else val)

        if updates.get("is_default"):
            with get_db_connection(self.db_path) as conn:
                conn.cursor().execute("UPDATE resumes SET is_default = 0 WHERE id != ?", (resume_id,))
                conn.commit()

        if not set_clauses:
            return current

        set_clauses.append("updated_at = ?")
        values.append(now_str)
        values.append(resume_id)

        with get_db_connection(self.db_path) as conn:
            conn.cursor().execute(f"UPDATE resumes SET {', '.join(set_clauses)} WHERE id = ?", values)
            conn.commit()

        return self.get_resume(resume_id)

    def delete_resume(self, resume_id: int) -> bool:
        resume = self.get_resume(resume_id)
        if not resume:
            return False
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor().execute("DELETE FROM resumes WHERE id = ?", (resume_id,))
            conn.commit()
            deleted = cursor.rowcount > 0
        if deleted and resume.get("file_path") and os.path.exists(resume["file_path"]):
            try:
                os.remove(resume["file_path"])
            except Exception:
                pass
        return deleted

    def add_resume_version(self, resume_id: int, version_tag: str, sections: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        current = self.get_resume(resume_id)
        if not current:
            return None
        versions = current.get("versions", [])
        version_id = f"ver-{int(datetime.datetime.now().timestamp() * 1000)}"
        new_version = {
            "id": version_id,
            "tag": version_tag,
            "createdAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "sections": sections
        }
        versions.append(new_version)
        return self.update_resume(resume_id, {"versions": versions, "active_version_id": version_id})

    def _format_resume_dict(self, res: Dict[str, Any]) -> Dict[str, Any]:
        json_fields = ["parsed_facts", "sections", "versions", "skills"]
        for jf in json_fields:
            if jf in res and res[jf]:
                if isinstance(res[jf], str):
                    try:
                        res[jf] = json.loads(res[jf])
                    except Exception:
                        res[jf] = [] if jf != "parsed_facts" else {}
            else:
                res[jf] = [] if jf != "parsed_facts" else {}
        return res

    # --- STUDENT VERIFICATION ---
    def verify_student(self, email: str, institution: Optional[str] = None) -> Dict[str, Any]:
        domain = email.split("@")[-1].lower() if "@" in email else ""
        is_valid_student = domain.endswith(".edu") or domain.endswith(".ac.in") or "student" in domain or "univ" in domain or "college" in domain
        
        if not is_valid_student:
            return {"verified": False, "reason": f"Email domain '{domain}' is not recognized as a valid academic domain (.edu, .ac.in)."}

        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with get_db_connection(self.db_path) as conn:
            conn.cursor().execute("""
                INSERT INTO student_verifications (email, institution, status, verified_at)
                VALUES (?, ?, 'VERIFIED', ?)
                ON CONFLICT (email) DO UPDATE SET
                    institution = excluded.institution,
                    status = excluded.status,
                    verified_at = excluded.verified_at
            """, (email, institution or domain, now_str))
            conn.commit()

        return {
            "verified": True,
            "email": email,
            "institution": institution or domain,
            "verified_at": now_str,
            "message": "Student eligibility successfully verified."
        }

    # --- PHASE 4: INTERVIEW PREP & STAR ANSWERS ---
    def save_interview_questions(self, questions: List[Dict[str, Any]], application_id: Optional[int] = None) -> List[Dict[str, Any]]:
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        saved = []
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            for q in questions:
                cursor.execute("""
                    INSERT INTO interview_questions (
                        application_id, category, question, difficulty, reason, preparation_topics, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    application_id or q.get("application_id"),
                    q.get("category", "General"),
                    q.get("question", ""),
                    q.get("difficulty", "Medium"),
                    q.get("reason", ""),
                    json.dumps(q.get("preparation_topics", [])),
                    now_str
                ))
                q_id = cursor.lastrowid
                saved.append({
                    "id": q_id,
                    "application_id": application_id or q.get("application_id"),
                    "category": q.get("category", "General"),
                    "question": q.get("question", ""),
                    "difficulty": q.get("difficulty", "Medium"),
                    "reason": q.get("reason", ""),
                    "preparation_topics": q.get("preparation_topics", []),
                    "created_at": now_str
                })
            conn.commit()
        return saved

    def list_interview_questions(self, application_id: Optional[int] = None) -> List[Dict[str, Any]]:
        with get_db_connection(self.db_path) as conn:
            if application_id:
                rows = conn.cursor().execute("SELECT * FROM interview_questions WHERE application_id = ? ORDER BY id DESC", (application_id,))
            else:
                rows = conn.cursor().execute("SELECT * FROM interview_questions ORDER BY id DESC")
            result = []
            for r in rows.fetchall():
                d = dict(r)
                if d.get("preparation_topics") and isinstance(d["preparation_topics"], str):
                    try:
                        d["preparation_topics"] = json.loads(d["preparation_topics"])
                    except Exception:
                        d["preparation_topics"] = []
                result.append(d)
            return result

    def save_star_answer(self, answer_data: Dict[str, Any]) -> Dict[str, Any]:
        q_id = answer_data["question_id"]
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        sb = answer_data.get("scoring_breakdown", {})
        sb_str = json.dumps(sb) if isinstance(sb, dict) else (sb or "{}")

        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            existing = cursor.execute("SELECT id FROM star_answers WHERE question_id = ?", (q_id,)).fetchone()
            if existing:
                cursor.execute("""
                    UPDATE star_answers SET situation=?, task=?, action=?, result=?, score=?, scoring_breakdown=?, updated_at=?
                    WHERE question_id=?
                """, (
                    answer_data.get("situation", ""),
                    answer_data.get("task", ""),
                    answer_data.get("action", ""),
                    answer_data.get("result", ""),
                    answer_data.get("score", 80),
                    sb_str,
                    now_str,
                    q_id
                ))
            else:
                cursor.execute("""
                    INSERT INTO star_answers (question_id, situation, task, action, result, score, scoring_breakdown, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    q_id,
                    answer_data.get("situation", ""),
                    answer_data.get("task", ""),
                    answer_data.get("action", ""),
                    answer_data.get("result", ""),
                    answer_data.get("score", 80),
                    sb_str,
                    now_str,
                    now_str
                ))
            conn.commit()
        return self.get_star_answer(q_id) or {}

    def get_star_answer(self, question_id: int) -> Optional[Dict[str, Any]]:
        with get_db_connection(self.db_path) as conn:
            row = conn.cursor().execute("SELECT * FROM star_answers WHERE question_id = ?", (question_id,)).fetchone()
            if row:
                d = dict(row)
                if d.get("scoring_breakdown") and isinstance(d["scoring_breakdown"], str):
                    try:
                        d["scoring_breakdown"] = json.loads(d["scoring_breakdown"])
                    except Exception:
                        d["scoring_breakdown"] = {}
                return d
        return None

    # --- SALARY COACH ---
    def save_salary_offer(self, offer_data: Dict[str, Any]) -> Dict[str, Any]:
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO salary_offers (
                    application_id, company, role, base_salary, variable_pay, bonus, equity,
                    location, competing_offer, target_compensation, minimum_acceptable,
                    analysis, counter_offer_draft, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                offer_data.get("application_id"),
                offer_data.get("company", ""),
                offer_data.get("role", ""),
                offer_data.get("base_salary", 0),
                offer_data.get("variable_pay", 0),
                offer_data.get("bonus", 0),
                offer_data.get("equity", ""),
                offer_data.get("location", ""),
                offer_data.get("competing_offer", ""),
                offer_data.get("target_compensation", 0),
                offer_data.get("minimum_acceptable", 0),
                json.dumps(offer_data.get("analysis", {})),
                offer_data.get("counter_offer_draft", ""),
                now_str
            ))
            offer_id = cursor.lastrowid
            conn.commit()
            return {
                "id": offer_id,
                **offer_data,
                "created_at": now_str
            }

    def list_salary_offers(self) -> List[Dict[str, Any]]:
        with get_db_connection(self.db_path) as conn:
            rows = conn.cursor().execute("SELECT * FROM salary_offers ORDER BY id DESC").fetchall()
            result = []
            for r in rows:
                d = dict(r)
                if d.get("analysis") and isinstance(d["analysis"], str):
                    try:
                        d["analysis"] = json.loads(d["analysis"])
                    except Exception:
                        d["analysis"] = {}
                result.append(d)
            return result

    # --- CAREER GOALS ---
    def create_career_goal(self, goal_data: Dict[str, Any]) -> Dict[str, Any]:
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO career_goals (
                    title, description, category, priority, target_date, status, progress, milestones, notes, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                goal_data.get("title", ""),
                goal_data.get("description", ""),
                goal_data.get("category", "SKILLS"),
                goal_data.get("priority", "MEDIUM"),
                goal_data.get("target_date", ""),
                goal_data.get("status", "IN_PROGRESS"),
                goal_data.get("progress", 0),
                json.dumps(goal_data.get("milestones", [])),
                goal_data.get("notes", ""),
                now_str,
                now_str
            ))
            goal_id = cursor.lastrowid
            conn.commit()
            return self.get_career_goal(goal_id) or {}

    def get_career_goal(self, goal_id: int) -> Optional[Dict[str, Any]]:
        with get_db_connection(self.db_path) as conn:
            row = conn.cursor().execute("SELECT * FROM career_goals WHERE id = ?", (goal_id,)).fetchone()
            if row:
                d = dict(row)
                if d.get("milestones") and isinstance(d["milestones"], str):
                    try:
                        d["milestones"] = json.loads(d["milestones"])
                    except Exception:
                        d["milestones"] = []
                return d
        return None

    def list_career_goals(self) -> List[Dict[str, Any]]:
        with get_db_connection(self.db_path) as conn:
            rows = conn.cursor().execute("SELECT * FROM career_goals ORDER BY updated_at DESC").fetchall()
            result = []
            for r in rows:
                d = dict(r)
                if d.get("milestones") and isinstance(d["milestones"], str):
                    try:
                        d["milestones"] = json.loads(d["milestones"])
                    except Exception:
                        d["milestones"] = []
                result.append(d)
            return result

    def update_career_goal(self, goal_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        current = self.get_career_goal(goal_id)
        if not current:
            return None
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        fields = ["title", "description", "category", "priority", "target_date", "status", "progress", "notes"]
        set_clauses = []
        values = []
        for field in fields:
            if field in updates:
                set_clauses.append(f"{field} = ?")
                values.append(updates[field])
        if "milestones" in updates:
            set_clauses.append("milestones = ?")
            val = updates["milestones"]
            values.append(json.dumps(val) if not isinstance(val, str) else val)

        if not set_clauses:
            return current

        set_clauses.append("updated_at = ?")
        values.append(now_str)
        values.append(goal_id)

        with get_db_connection(self.db_path) as conn:
            conn.cursor().execute(f"UPDATE career_goals SET {', '.join(set_clauses)} WHERE id = ?", values)
            conn.commit()
        return self.get_career_goal(goal_id)

    def delete_career_goal(self, goal_id: int) -> bool:
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor().execute("DELETE FROM career_goals WHERE id = ?", (goal_id,))
            conn.commit()
            return cursor.rowcount > 0
