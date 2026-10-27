import os
import time
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from app.db.connection import get_db_connection, with_db_retry

class TaskStatus(str):
    QUEUED = "QUEUED"
    PLANNING = "PLANNING"
    RUNNING = "RUNNING"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    PAUSED = "PAUSED"
    RETRYING = "RETRYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class TaskStep(BaseModel):
    step_id: str
    title: str
    description: str
    tool_name: Optional[str] = None
    arguments: Dict[str, Any] = {}
    requires_approval: bool = False
    status: str = TaskStatus.QUEUED
    output: Optional[str] = None
    error: Optional[str] = None

def init_agent_task_tables():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT UNIQUE NOT NULL,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                prompt TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'QUEUED',
                plan_dag_json TEXT NOT NULL DEFAULT '[]',
                current_step_index INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_approvals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                approval_id TEXT UNIQUE NOT NULL,
                task_id TEXT NOT NULL,
                action_title TEXT NOT NULL,
                action_details TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'PENDING',
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()

init_agent_task_tables()

class AgentOrchestrator:
    @staticmethod
    def create_task(user_id: str, prompt: str, title: Optional[str] = None) -> Dict[str, Any]:
        init_agent_task_tables()
        task_id = f"task_{uuid.uuid4().hex[:12]}"
        now_str = datetime.now(timezone.utc).isoformat()
        if not title:
            title = prompt[:50] + ("..." if len(prompt) > 50 else "")

        # Initial Task DAG Planning
        dag_steps = AgentOrchestrator._generate_task_dag(prompt)
        dag_json = json.dumps([step.model_dump() for step in dag_steps])

        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO agent_tasks (task_id, user_id, title, prompt, status, plan_dag_json, current_step_index, created_at, updated_at)
                VALUES (?, ?, ?, ?, 'QUEUED', ?, 0, ?, ?)
            """, (task_id, user_id, title, prompt, dag_json, now_str, now_str))
            conn.commit()

        return AgentOrchestrator.get_task(task_id)

    @staticmethod
    def _generate_task_dag(prompt: str) -> List[TaskStep]:
        """
        Decomposes complex multi-step career directives into structured TaskStep DAG.
        """
        prompt_lower = prompt.lower()
        steps = []
        
        if "find" in prompt_lower or "job" in prompt_lower or "search" in prompt_lower:
            steps.append(TaskStep(
                step_id="step_1",
                title="Search and Rank Jobs",
                description="Search for target job opportunities matching candidate profile skills.",
                tool_name="browser_search",
                arguments={"query": prompt},
                requires_approval=False
            ))
            steps.append(TaskStep(
                step_id="step_2",
                title="Analyze Job & ATS Comparison",
                description="Compare job descriptions against candidate resume skills.",
                tool_name="resume_ats_match",
                arguments={"job_title": "Target Role"},
                requires_approval=False
            ))
            steps.append(TaskStep(
                step_id="step_3",
                title="Tailor Resume & Draft Cover Letter",
                description="Synthesize tailored resume and customized cover letter.",
                tool_name="career_assistant",
                arguments={"action": "tailor_resume"},
                requires_approval=False
            ))
            steps.append(TaskStep(
                step_id="step_4",
                title="Submit Application / Follow up",
                description="Send application or follow up email to recruiter.",
                tool_name="send_email",
                arguments={"recipient": "recruiter@company.com"},
                requires_approval=True # Requires Human Approval!
            ))
        else:
            steps.append(TaskStep(
                step_id="step_1",
                title="Analyze Prompt & Gather Context",
                description="Extract intent and relevant career memory facts.",
                tool_name="suggest_memory",
                arguments={"query": prompt},
                requires_approval=False
            ))
            steps.append(TaskStep(
                step_id="step_2",
                title="Execute Local Nemotron Assistant",
                description="Generate answer or career document.",
                tool_name="nemotron_generate",
                arguments={"prompt": prompt},
                requires_approval=False
            ))
            
        return steps

    @staticmethod
    def get_task(task_id: str) -> Optional[Dict[str, Any]]:
        with get_db_connection() as conn:
            row = conn.execute("SELECT * FROM agent_tasks WHERE task_id = ?", (task_id,)).fetchone()
            if not row:
                return None
            d = dict(row)
            d["steps"] = json.loads(d["plan_dag_json"])
            return d

    @staticmethod
    def list_user_tasks(user_id: str) -> List[Dict[str, Any]]:
        with get_db_connection() as conn:
            rows = conn.execute("SELECT * FROM agent_tasks WHERE user_id = ? ORDER BY id DESC", (user_id,)).fetchall()
            result = []
            for r in rows:
                d = dict(r)
                d["steps"] = json.loads(d["plan_dag_json"])
                result.append(d)
            return result

    @staticmethod
    def update_task_status(task_id: str, status: str, current_step_index: Optional[int] = None):
        now_str = datetime.now(timezone.utc).isoformat()
        with get_db_connection() as conn:
            if current_step_index is not None:
                conn.execute("UPDATE agent_tasks SET status = ?, current_step_index = ?, updated_at = ? WHERE task_id = ?",
                             (status, current_step_index, now_str, task_id))
            else:
                conn.execute("UPDATE agent_tasks SET status = ?, updated_at = ? WHERE task_id = ?",
                             (status, now_str, task_id))
            conn.commit()

    @staticmethod
    def create_approval_request(task_id: str, action_title: str, action_details: str) -> Dict[str, Any]:
        approval_id = f"appr_{uuid.uuid4().hex[:8]}"
        now_str = datetime.now(timezone.utc).isoformat()
        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO task_approvals (approval_id, task_id, action_title, action_details, status, created_at)
                VALUES (?, ?, ?, ?, 'PENDING', ?)
            """, (approval_id, task_id, action_title, action_details, now_str))
            conn.commit()
        AgentOrchestrator.update_task_status(task_id, TaskStatus.WAITING_APPROVAL)
        return {"approval_id": approval_id, "task_id": task_id, "action_title": action_title, "action_details": action_details, "status": "PENDING"}

    @staticmethod
    def respond_to_approval(approval_id: str, approved: bool) -> Dict[str, Any]:
        now_str = datetime.now(timezone.utc).isoformat()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            appr = cursor.execute("SELECT * FROM task_approvals WHERE approval_id = ?", (approval_id,)).fetchone()
            if not appr:
                raise ValueError("Approval request not found.")
            status = "APPROVED" if approved else "REJECTED"
            cursor.execute("UPDATE task_approvals SET status = ? WHERE approval_id = ?", (status, approval_id))
            
            task_id = appr["task_id"]
            if approved:
                cursor.execute("UPDATE agent_tasks SET status = 'RUNNING', updated_at = ? WHERE task_id = ?", (now_str, task_id))
            else:
                cursor.execute("UPDATE agent_tasks SET status = 'CANCELLED', updated_at = ? WHERE task_id = ?", (now_str, task_id))
            conn.commit()
        return {"approval_id": approval_id, "status": status}
