from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Query, HTTPException, Depends
from app.db.connection import get_db_connection, with_db_retry
from app.core.entitlements import require_capability

router = APIRouter(prefix="/search", tags=["Global Search & Discovery"])

@router.get("")
@with_db_retry()
def global_search(
    q: str = Query(..., min_length=1, max_length=200, description="Search query string across Saarthi workspace"),
    capability_check = Depends(require_capability("core.chat.basic"))
):
    """
    Unified search engine querying chat history, memories, projects, project files, agent tasks, routines, research queries, and career applications.
    """
    query_term = f"%{q.strip()}%"
    results = {
        "query": q,
        "conversations": [],
        "memories": [],
        "projects": [],
        "project_files": [],
        "tasks": [],
        "routines": [],
        "research": [],
        "career_applications": [],
        "total_matches": 0
    }

    with get_db_connection() as conn:
        conn.row_factory = lambda cursor, row: {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
        cursor = conn.cursor()

        # 1. Chat History
        try:
            cursor.execute("""
                SELECT id, session_id, sender, message, timestamp
                FROM chat_history
                WHERE message LIKE ?
                ORDER BY id DESC LIMIT 10
            """, (query_term,))
            results["conversations"] = cursor.fetchall()
        except Exception:
            pass

        # 2. User Memories
        try:
            cursor.execute("""
                SELECT id, category, key, content, created_at
                FROM user_memories
                WHERE (content LIKE ? OR key LIKE ?) AND status = 'ACTIVE'
                ORDER BY id DESC LIMIT 10
            """, (query_term, query_term))
            results["memories"] = cursor.fetchall()
        except Exception:
            pass

        # 3. Projects
        try:
            cursor.execute("""
                SELECT id, name, description, category, created_at
                FROM projects
                WHERE name LIKE ? OR description LIKE ?
                ORDER BY updated_at DESC LIMIT 10
            """, (query_term, query_term))
            results["projects"] = cursor.fetchall()
        except Exception:
            pass

        # 4. Project Files
        try:
            cursor.execute("""
                SELECT id, project_id, filename, file_type, created_at
                FROM project_files
                WHERE filename LIKE ?
                ORDER BY id DESC LIMIT 10
            """, (query_term,))
            results["project_files"] = cursor.fetchall()
        except Exception:
            pass

        # 5. Agent Tasks
        try:
            cursor.execute("""
                SELECT id, goal, status, created_at
                FROM agent_tasks
                WHERE goal LIKE ?
                ORDER BY id DESC LIMIT 10
            """, (query_term,))
            results["tasks"] = cursor.fetchall()
        except Exception:
            pass

        # 6. Routines
        try:
            cursor.execute("""
                SELECT id, name, description, is_active, trigger_type
                FROM routines
                WHERE name LIKE ? OR description LIKE ?
                ORDER BY id DESC LIMIT 10
            """, (query_term, query_term))
            results["routines"] = cursor.fetchall()
        except Exception:
            pass

        # 7. Research Queries
        try:
            cursor.execute("""
                SELECT id, topic, status, created_at
                FROM research_queries
                WHERE topic LIKE ?
                ORDER BY id DESC LIMIT 10
            """, (query_term,))
            results["research"] = cursor.fetchall()
        except Exception:
            pass

        # 8. Career Applications
        try:
            cursor.execute("""
                SELECT id, company_name, job_title, status, created_at
                FROM career_applications
                WHERE company_name LIKE ? OR job_title LIKE ?
                ORDER BY id DESC LIMIT 10
            """, (query_term, query_term))
            results["career_applications"] = cursor.fetchall()
        except Exception:
            pass

    results["total_matches"] = sum(len(v) for k, v in results.items() if isinstance(v, list))
    return results
