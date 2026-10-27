import os
import time
import json
import uuid
import threading
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from app.db.connection import get_db_connection, with_db_retry
from app.agent.orchestrator import AgentOrchestrator

logger = logging.getLogger("app.agent.scheduler")

class TaskScheduler:
    _thread = None
    _running = False

    @staticmethod
    def _init_tables():
        with get_db_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scheduled_jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT UNIQUE NOT NULL,
                    user_id TEXT NOT NULL,
                    task_goal TEXT NOT NULL,
                    cron_expression TEXT,
                    interval_seconds INTEGER,
                    next_run_at TEXT NOT NULL,
                    status TEXT DEFAULT 'SCHEDULED',
                    created_at TEXT NOT NULL
                )
            """)
            conn.commit()

    @staticmethod
    def create_scheduled_job(
        user_id: str,
        task_goal: str,
        interval_seconds: Optional[int] = None,
        cron_expression: Optional[str] = None,
        schedule_type: Optional[str] = None
    ) -> Dict[str, Any]:
        TaskScheduler._init_tables()
        job_id = f"job_{uuid.uuid4().hex[:10]}"
        now = datetime.now(timezone.utc)
        
        if interval_seconds:
            next_run = now + timedelta(seconds=interval_seconds)
        else:
            next_run = now + timedelta(minutes=60)
            
        next_run_str = next_run.isoformat()
        now_str = now.isoformat()

        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO scheduled_jobs (job_id, user_id, task_goal, cron_expression, interval_seconds, next_run_at, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, 'SCHEDULED', ?)
            """, (job_id, user_id, task_goal, cron_expression, interval_seconds, next_run_str, now_str))
            conn.commit()

        return TaskScheduler.get_job(job_id)

    @staticmethod
    def get_job(job_id: str) -> Optional[Dict[str, Any]]:
        with get_db_connection() as conn:
            row = conn.execute("SELECT * FROM scheduled_jobs WHERE job_id = ?", (job_id,)).fetchone()
            if row:
                return dict(row)
        return None

    @staticmethod
    def list_jobs(user_id: str) -> List[Dict[str, Any]]:
        with get_db_connection() as conn:
            rows = conn.execute("SELECT * FROM scheduled_jobs WHERE user_id = ? ORDER BY id DESC", (user_id,)).fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def start_scheduler_daemon():
        if TaskScheduler._running:
            return
        TaskScheduler._running = True
        TaskScheduler._thread = threading.Thread(target=TaskScheduler._loop, daemon=True)
        TaskScheduler._thread.start()
        logger.info("Saarthi Background Automation Scheduler Daemon started.")

    @staticmethod
    def _loop():
        while TaskScheduler._running:
            try:
                TaskScheduler._evaluate_due_jobs()
            except Exception as e:
                logger.error(f"Scheduler loop error: {e}")
            time.sleep(30)

    @staticmethod
    @with_db_retry()
    def _evaluate_due_jobs():
        now = datetime.now(timezone.utc)
        now_str = now.isoformat()

        with get_db_connection() as conn:
            cursor = conn.cursor()
            rows = cursor.execute("SELECT * FROM scheduled_jobs WHERE status = 'SCHEDULED'").fetchall()
            for r in rows:
                job = dict(r)
                run_at_dt = datetime.fromisoformat(job["run_at"])
                if now >= run_at_dt:
                    logger.info(f"Executing due scheduled job {job['job_id']}: '{job['prompt']}'")
                    # Trigger task orchestrator
                    AgentOrchestrator.create_task(job["user_id"], job["prompt"], title=f"[Scheduled] {job['prompt'][:30]}")
                    
                    if job["schedule_type"] == "ONE_TIME":
                        cursor.execute("UPDATE scheduled_jobs SET status = 'EXECUTED', last_run_at = ? WHERE job_id = ?", (now_str, job["job_id"]))
                    else:
                        # Schedule next weekly run
                        next_run = (now + timedelta(days=7)).isoformat()
                        cursor.execute("UPDATE scheduled_jobs SET run_at = ?, last_run_at = ? WHERE job_id = ?", (next_run, now_str, job["job_id"]))
            conn.commit()

# Auto-start scheduler daemon
TaskScheduler.start_scheduler_daemon()
