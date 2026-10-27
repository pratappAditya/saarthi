import sqlite3
import os
import json
import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from app.intelligence.memory.memory_models import (
    MemoryItem, MemoryClass, MemoryType, MemoryScope, MemoryProvenance, RetentionState
)
from app.db.connection import get_db_connection
from app.config.settings import settings

logger = logging.getLogger("app.intelligence.memory_store")

# In-memory retrieval cache invalidation registry
_MEMORY_CACHE_REGISTRY: Dict[str, float] = {}


class MemoryStore:
    """
    Production Persistence Store for Saarthi Deep Memory 2.0.
    Supports SQLite and PostgreSQL dual-dialect engines with tenant isolation,
    explicit memory classes, scopes, provenance tracking, automatic expiration pruning,
    and cache invalidation.
    """
    def __init__(self, db_path: Optional[str] = None):
        self._db_path = db_path
        self._init_memory_tables()

    @property
    def db_path(self) -> str:
        return self._db_path or settings.DATABASE_PATH

    @db_path.setter
    def db_path(self, val: str):
        self._db_path = val

    def _get_connection(self):
        return get_db_connection(self.db_path)

    def _init_memory_tables(self):
        conn = self._get_connection()
        try:
            with conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS memories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL DEFAULT 'default_local_user',
                        memory_class TEXT NOT NULL DEFAULT 'USER_MEMORY',
                        type TEXT DEFAULT 'FACT',
                        content TEXT NOT NULL,
                        provenance TEXT NOT NULL DEFAULT 'USER_EXPLICIT',
                        source TEXT DEFAULT 'user_explicit',
                        confidence REAL NOT NULL DEFAULT 1.0,
                        importance INTEGER NOT NULL DEFAULT 5,
                        scope TEXT NOT NULL DEFAULT 'global_user',
                        domain TEXT DEFAULT 'general',
                        project_id TEXT,
                        goal_id TEXT,
                        workflow_id TEXT,
                        conversation_id TEXT,
                        task_id TEXT,
                        retention_state TEXT DEFAULT 'durable',
                        expires_at TEXT,
                        metadata_json TEXT DEFAULT '{}',
                        created_at TEXT NOT NULL DEFAULT '',
                        updated_at TEXT NOT NULL DEFAULT '',
                        last_accessed_at TEXT NOT NULL DEFAULT '',
                        access_count INTEGER NOT NULL DEFAULT 0,
                        is_active INTEGER NOT NULL DEFAULT 1
                    );
                """)

                # Dynamic column migration check
                cols = [row["name"] for row in conn.execute("PRAGMA table_info(memories)").fetchall()]
                for col_name, col_type in [
                    ("memory_class", "TEXT NOT NULL DEFAULT 'USER_MEMORY'"),
                    ("provenance", "TEXT NOT NULL DEFAULT 'USER_EXPLICIT'"),
                    ("scope", "TEXT NOT NULL DEFAULT 'global_user'"),
                    ("domain", "TEXT DEFAULT 'general'"),
                    ("project_id", "TEXT"),
                    ("goal_id", "TEXT"),
                    ("workflow_id", "TEXT"),
                    ("task_id", "TEXT"),
                    ("retention_state", "TEXT DEFAULT 'durable'"),
                    ("expires_at", "TEXT"),
                    ("metadata_json", "TEXT DEFAULT '{}'"),
                    ("user_id", "TEXT NOT NULL DEFAULT 'default_local_user'")
                ]:
                    if col_name not in cols:
                        conn.execute(f"ALTER TABLE memories ADD COLUMN {col_name} {col_type}")

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS memory_sources (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        memory_id INTEGER NOT NULL,
                        source_type TEXT NOT NULL,
                        source_ref TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        FOREIGN KEY (memory_id) REFERENCES memories(id) ON DELETE CASCADE
                    );
                """)
        finally:
            conn.close()

    def invalidate_caches(self, user_id: str = "default_local_user"):
        """Invalidates in-memory retrieval caches and signals recalculation."""
        now_ts = datetime.now(timezone.utc).timestamp()
        _MEMORY_CACHE_REGISTRY[user_id] = now_ts
        logger.debug(f"Invalidated memory cache for user '{user_id}' at timestamp {now_ts}")

    def create_memory(self, item: MemoryItem) -> MemoryItem:
        now = datetime.now(timezone.utc).isoformat()
        conn = self._get_connection()
        try:
            with conn:
                cols = [row["name"] for row in conn.execute("PRAGMA table_info(memories)").fetchall()]
                
                # Normalize provenance and memory_class
                prov_val = item.provenance.value if hasattr(item.provenance, 'value') else str(item.provenance)
                class_val = item.memory_class.value if hasattr(item.memory_class, 'value') else str(item.memory_class)
                scope_val = item.scope.value if hasattr(item.scope, 'value') else str(item.scope)

                insert_dict = {
                    "user_id": item.user_id,
                    "memory_class": class_val,
                    "type": class_val,
                    "content": item.content,
                    "provenance": prov_val,
                    "source": prov_val,
                    "confidence": float(item.confidence),
                    "importance": int(item.importance),
                    "scope": scope_val,
                    "domain": item.domain or "general",
                    "project_id": item.project_id,
                    "goal_id": item.goal_id,
                    "workflow_id": item.workflow_id,
                    "conversation_id": item.conversation_id,
                    "task_id": item.task_id,
                    "retention_state": item.retention_state,
                    "expires_at": item.expires_at,
                    "metadata_json": json.dumps(item.metadata),
                    "created_at": item.created_at or now,
                    "updated_at": item.updated_at or now,
                    "last_accessed_at": item.last_accessed_at or now,
                    "access_count": item.access_count,
                    "is_active": 1 if item.is_active else 0
                }

                if "key" in cols:
                    insert_dict["key"] = f"mem_{uuid.uuid4().hex[:8]}"
                if "value" in cols:
                    insert_dict["value"] = item.content
                if "category" in cols:
                    insert_dict["category"] = item.domain or "general"

                valid_cols = [c for c in cols if c in insert_dict]
                values = [insert_dict[c] for c in valid_cols]

                col_str = ", ".join(valid_cols)
                placeholders = ", ".join(["?"] * len(valid_cols))

                sql = f"INSERT INTO memories ({col_str}) VALUES ({placeholders})"
                cur = conn.execute(sql, values)

                item.id = cur.lastrowid
                item.created_at = insert_dict["created_at"]
                item.updated_at = insert_dict["updated_at"]
                item.last_accessed_at = insert_dict["last_accessed_at"]

                # Record provenance source
                source_ref = item.project_id or item.conversation_id or item.task_id or "system"
                conn.execute("""
                    INSERT INTO memory_sources (memory_id, source_type, source_ref, created_at)
                    VALUES (?, ?, ?, ?)
                """, (item.id, prov_val, source_ref, now))

            self.invalidate_caches(item.user_id)
            return item
        finally:
            conn.close()

    def get_memory(self, memory_id: int, user_id: Optional[str] = None) -> Optional[MemoryItem]:
        conn = self._get_connection()
        try:
            sql = "SELECT * FROM memories WHERE id = ? AND is_active = 1"
            params: List[Any] = [memory_id]
            if user_id:
                sql += " AND user_id = ?"
                params.append(user_id)

            row = conn.execute(sql, params).fetchone()
            if not row:
                return None
            return self._row_to_memory_item(row)
        finally:
            conn.close()

    def update_memory(
        self,
        memory_id: int,
        updates: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        **kwargs
    ) -> Optional[MemoryItem]:
        now = datetime.now(timezone.utc).isoformat()
        merged_updates: Dict[str, Any] = dict(updates or {})
        merged_updates.update(kwargs)

        conn = self._get_connection()
        try:
            with conn:
                fields = []
                values = []
                for k, v in merged_updates.items():
                    if k == "content":
                        fields.append("content = ?")
                        values.append(v)
                    elif k == "importance":
                        fields.append("importance = ?")
                        values.append(int(v))
                    elif k == "confidence":
                        fields.append("confidence = ?")
                        values.append(float(v))
                    elif k in ["memory_class", "type"]:
                        fields.append("memory_class = ?")
                        values.append(v)
                        fields.append("type = ?")
                        values.append(v)
                    elif k in ["provenance", "source"]:
                        fields.append("provenance = ?")
                        values.append(v)
                        fields.append("source = ?")
                        values.append(v)
                    elif k == "scope":
                        fields.append("scope = ?")
                        values.append(v)
                    elif k == "domain":
                        fields.append("domain = ?")
                        values.append(v)
                    elif k == "project_id":
                        fields.append("project_id = ?")
                        values.append(v)
                    elif k == "goal_id":
                        fields.append("goal_id = ?")
                        values.append(v)
                    elif k == "retention_state":
                        fields.append("retention_state = ?")
                        values.append(v)
                    elif k == "expires_at":
                        fields.append("expires_at = ?")
                        values.append(v)
                    elif k == "metadata":
                        fields.append("metadata_json = ?")
                        values.append(json.dumps(v))

                if not fields:
                    return self.get_memory(memory_id, user_id=user_id)

                fields.append("updated_at = ?")
                values.append(now)

                values.append(memory_id)
                where_clause = "WHERE id = ?"
                if user_id:
                    where_clause += " AND user_id = ?"
                    values.append(user_id)

                conn.execute(f"UPDATE memories SET {', '.join(fields)} {where_clause}", values)

            uid = user_id or "default_local_user"
            self.invalidate_caches(uid)
            return self.get_memory(memory_id, user_id=user_id)
        finally:
            conn.close()

    def delete_memory(self, memory_id: int, user_id: Optional[str] = None) -> bool:
        """Permanently deletes or deactivates a memory item and invalidates caches with tenant isolation."""
        conn = self._get_connection()
        try:
            with conn:
                where_clause = "WHERE id = ?"
                params: List[Any] = [memory_id]
                if user_id:
                    where_clause += " AND user_id = ?"
                    params.append(user_id)

                cur = conn.execute(f"UPDATE memories SET is_active = 0 {where_clause}", params)
                deleted = cur.rowcount > 0
                if deleted:
                    conn.execute("DELETE FROM memory_sources WHERE memory_id = ?", (memory_id,))

            if deleted:
                self.invalidate_caches(user_id or "default_local_user")
            return deleted
        finally:
            conn.close()

    def prune_expired_memories(self, user_id: Optional[str] = None) -> int:
        """Removes expired memories whose retention period has elapsed."""
        now = datetime.now(timezone.utc).isoformat()
        conn = self._get_connection()
        try:
            with conn:
                sql = "UPDATE memories SET is_active = 0 WHERE is_active = 1 AND expires_at IS NOT NULL AND expires_at != '' AND expires_at < ?"
                params: List[Any] = [now]
                if user_id:
                    sql += " AND user_id = ?"
                    params.append(user_id)
                cur = conn.execute(sql, params)
                count = cur.rowcount

            if count > 0:
                self.invalidate_caches(user_id or "default_local_user")
            return count
        finally:
            conn.close()

    def list_memories(
        self,
        user_id: str = "default_local_user",
        domain: Optional[str] = None,
        scope: Optional[str] = None,
        memory_class: Optional[str] = None,
        provenance: Optional[str] = None,
        project_id: Optional[str] = None,
        goal_id: Optional[str] = None,
        limit: int = 100
    ) -> List[MemoryItem]:
        # Auto-prune expired items first
        self.prune_expired_memories(user_id)

        conn = self._get_connection()
        try:
            conditions = ["is_active = 1", "user_id = ?"]
            params: List[Any] = [user_id]

            if domain:
                conditions.append("domain = ?")
                params.append(domain)
            if scope:
                conditions.append("scope = ?")
                params.append(scope)
            if memory_class:
                conditions.append("(memory_class = ? OR type = ?)")
                params.extend([memory_class, memory_class])
            if provenance:
                conditions.append("(provenance = ? OR source = ?)")
                params.extend([provenance, provenance])
            if project_id:
                conditions.append("project_id = ?")
                params.append(project_id)
            if goal_id:
                conditions.append("goal_id = ?")
                params.append(goal_id)

            where_sql = " AND ".join(conditions)
            sql = f"SELECT * FROM memories WHERE {where_sql} ORDER BY importance DESC, updated_at DESC LIMIT ?"
            params.append(limit)

            rows = conn.execute(sql, params).fetchall()
            return [self._row_to_memory_item(r) for r in rows]
        finally:
            conn.close()

    def clear_project_memories(self, user_id: str, project_id: str) -> int:
        conn = self._get_connection()
        try:
            with conn:
                cur = conn.execute("""
                    UPDATE memories SET is_active = 0
                    WHERE user_id = ? AND project_id = ? AND is_active = 1
                """, (user_id, project_id))
                count = cur.rowcount
            if count > 0:
                self.invalidate_caches(user_id)
            return count
        finally:
            conn.close()

    def clear_user_memories(self, user_id: str) -> int:
        conn = self._get_connection()
        try:
            with conn:
                cur = conn.execute("UPDATE memories SET is_active = 0 WHERE user_id = ? AND is_active = 1", (user_id,))
                count = cur.rowcount
            if count > 0:
                self.invalidate_caches(user_id)
            return count
        finally:
            conn.close()

    @staticmethod
    def _row_to_memory_item(row: Any) -> MemoryItem:
        d = dict(row)
        mem_class_raw = d.get("memory_class") or d.get("type") or "USER_MEMORY"
        prov_raw = d.get("provenance") or d.get("source") or "USER_EXPLICIT"
        scope_raw = d.get("scope") or "global_user"

        return MemoryItem(
            id=d["id"],
            user_id=d["user_id"],
            memory_class=MemoryClass(mem_class_raw) if mem_class_raw in MemoryClass._value2member_map_ else MemoryClass.USER_MEMORY,
            content=d["content"],
            provenance=MemoryProvenance(prov_raw) if prov_raw in MemoryProvenance._value2member_map_ else MemoryProvenance.USER_EXPLICIT,
            confidence=float(d.get("confidence", 1.0)),
            importance=int(d.get("importance", 5)),
            scope=MemoryScope(scope_raw) if scope_raw in MemoryScope._value2member_map_ else MemoryScope.GLOBAL_USER,
            domain=d.get("domain", "general"),
            project_id=d.get("project_id"),
            goal_id=d.get("goal_id"),
            workflow_id=d.get("workflow_id"),
            conversation_id=d.get("conversation_id"),
            task_id=d.get("task_id"),
            retention_state=d.get("retention_state", "durable"),
            expires_at=d.get("expires_at"),
            created_at=d.get("created_at", ""),
            updated_at=d.get("updated_at", ""),
            last_accessed_at=d.get("last_accessed_at", ""),
            access_count=int(d.get("access_count", 0)),
            is_active=bool(d.get("is_active", 1)),
            metadata=json.loads(d.get("metadata_json") or "{}")
        )

memory_store = MemoryStore()
