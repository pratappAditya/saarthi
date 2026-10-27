"""
Multimodal Attachment Persistence & Tenant Isolation Manager.
Stores metadata, extracted text, OCR results, and file provenance in database
with per-user tenant isolation.
"""

import sqlite3
import os
import json
import hashlib
import uuid
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from app.db.connection import get_db_connection
from app.config.settings import settings

logger = logging.getLogger("app.intelligence.attachment_manager")


class InputAttachment(BaseModel):
    id: str
    filename: str
    mime_type: str
    source: str = "user_upload"
    size_bytes: int = 0
    file_hash: str = ""
    content_type: str = "document"  # "document" | "image" | "audio" | "code"
    extraction_status: str = "completed"  # "pending" | "completed" | "failed"
    extracted_text: str = ""
    ocr_text: Optional[str] = ""
    page_count: Optional[int] = 1
    image_dimensions: Optional[Dict[str, int]] = None
    audio_duration_seconds: Optional[float] = None
    transcription: Optional[str] = None
    project_id: Optional[str] = None
    user_id: str = "default_local_user"
    created_at: Optional[str] = None
    metadata_json: Dict[str, Any] = Field(default_factory=dict)


class AttachmentManager:
    def __init__(self, db_path: Optional[str] = None):
        self._db_path = db_path
        self._init_tables()

    @property
    def db_path(self) -> str:
        return self._db_path or settings.DATABASE_PATH

    @db_path.setter
    def db_path(self, val: str):
        self._db_path = val

    def _get_connection(self):
        return get_db_connection(self.db_path)

    def _init_tables(self):
        conn = self._get_connection()
        try:
            with conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS multimodal_attachments (
                        id TEXT PRIMARY KEY,
                        filename TEXT NOT NULL,
                        mime_type TEXT NOT NULL,
                        source TEXT NOT NULL,
                        size_bytes INTEGER NOT NULL,
                        file_hash TEXT NOT NULL,
                        content_type TEXT NOT NULL,
                        extraction_status TEXT NOT NULL,
                        extracted_text TEXT,
                        ocr_text TEXT,
                        page_count INTEGER,
                        transcription TEXT,
                        project_id TEXT,
                        user_id TEXT DEFAULT 'default_local_user',
                        created_at TEXT NOT NULL,
                        metadata_json TEXT NOT NULL
                    );
                """)
                # Safe migration check: add user_id column if table pre-existed without it
                try:
                    conn.execute("ALTER TABLE multimodal_attachments ADD COLUMN user_id TEXT DEFAULT 'default_local_user';")
                except Exception:
                    pass  # Column already exists
        finally:
            conn.close()

    def compute_hash(self, content_bytes: bytes) -> str:
        return hashlib.sha256(content_bytes).hexdigest()

    def save_attachment(
        self,
        filename: str,
        content_bytes: bytes,
        mime_type: str,
        extracted_text: str = "",
        ocr_text: str = "",
        content_type: str = "document",
        project_id: Optional[str] = None,
        user_id: str = "default_local_user",
        metadata: Optional[Dict[str, Any]] = None
    ) -> InputAttachment:
        import datetime
        att_id = f"att_{uuid.uuid4().hex[:8]}"
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        f_hash = self.compute_hash(content_bytes)
        size = len(content_bytes)

        att = InputAttachment(
            id=att_id,
            filename=filename,
            mime_type=mime_type,
            source="user_upload",
            size_bytes=size,
            file_hash=f_hash,
            content_type=content_type,
            extraction_status="completed",
            extracted_text=extracted_text,
            ocr_text=ocr_text,
            project_id=project_id,
            user_id=user_id,
            created_at=now,
            metadata_json=metadata or {}
        )

        conn = self._get_connection()
        try:
            with conn:
                conn.execute("""
                    INSERT OR REPLACE INTO multimodal_attachments
                    (id, filename, mime_type, source, size_bytes, file_hash, content_type, extraction_status, extracted_text, ocr_text, page_count, transcription, project_id, user_id, created_at, metadata_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    att.id, att.filename, att.mime_type, att.source, att.size_bytes,
                    att.file_hash, att.content_type, att.extraction_status,
                    att.extracted_text, att.ocr_text, att.page_count,
                    att.transcription, att.project_id, att.user_id, att.created_at, json.dumps(att.metadata_json)
                ))
            return att
        finally:
            conn.close()

    def get_attachment(self, att_id: str, user_id: Optional[str] = None) -> Optional[InputAttachment]:
        """Retrieves attachment, enforcing user tenant isolation if user_id is provided."""
        conn = self._get_connection()
        try:
            if user_id:
                row = conn.execute(
                    "SELECT * FROM multimodal_attachments WHERE id = ? AND (user_id = ? OR user_id = 'default_local_user')",
                    (att_id, user_id)
                ).fetchone()
            else:
                row = conn.execute("SELECT * FROM multimodal_attachments WHERE id = ?", (att_id,)).fetchone()

            if not row:
                return None
            d = dict(row)
            d["metadata_json"] = json.loads(d["metadata_json"])
            return InputAttachment(**d)
        finally:
            conn.close()

    def list_attachments(
        self,
        project_id: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 50
    ) -> List[InputAttachment]:
        """Lists attachments filtered by user_id and optional project_id."""
        conn = self._get_connection()
        try:
            params = []
            clauses = []
            if user_id:
                clauses.append("(user_id = ? OR user_id = 'default_local_user')")
                params.append(user_id)
            if project_id:
                clauses.append("project_id = ?")
                params.append(project_id)

            where_str = f"WHERE {' AND '.join(clauses)}" if clauses else ""
            params.append(limit)

            query = f"SELECT * FROM multimodal_attachments {where_str} ORDER BY created_at DESC LIMIT ?"
            rows = conn.execute(query, tuple(params)).fetchall()

            results = []
            for r in rows:
                d = dict(r)
                d["metadata_json"] = json.loads(d["metadata_json"])
                results.append(InputAttachment(**d))
            return results
        finally:
            conn.close()

    def delete_attachment(self, att_id: str, user_id: Optional[str] = None) -> bool:
        """Deletes attachment, enforcing user tenant isolation if user_id is provided."""
        conn = self._get_connection()
        try:
            with conn:
                if user_id:
                    cur = conn.execute(
                        "DELETE FROM multimodal_attachments WHERE id = ? AND (user_id = ? OR user_id = 'default_local_user')",
                        (att_id, user_id)
                    )
                else:
                    cur = conn.execute("DELETE FROM multimodal_attachments WHERE id = ?", (att_id,))
                return cur.rowcount > 0
        finally:
            conn.close()


attachment_manager = AttachmentManager()
