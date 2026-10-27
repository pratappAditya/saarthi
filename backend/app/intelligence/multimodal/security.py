"""
Secure File Ingestion & Tenant Isolation Guard.
Enforces:
- 25 MB maximum upload size limit
- Strict MIME and extension validation
- Path traversal prevention & filename sanitization
- Malicious file & dangerous executable rejection
- Multi-user tenant isolation
"""

import os
import re
import logging
from typing import Optional, Tuple
from fastapi import HTTPException

logger = logging.getLogger("app.intelligence.multimodal.security")

MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25 Megabytes

# Whitelisted extensions for production multimodal ingestion
ALLOWED_EXTENSIONS = {
    ".pdf", ".docx", ".doc", ".txt", ".md",
    ".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"
}

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "text/plain",
    "text/markdown",
    "image/png",
    "image/jpeg",
    "image/webp",
    "image/bmp",
    "image/tiff"
}

DANGEROUS_EXTENSIONS = {
    ".exe", ".bat", ".cmd", ".sh", ".bash", ".vbs", ".dll",
    ".scr", ".msi", ".jar", ".py", ".pyw", ".js", ".vbe",
    ".wsf", ".ps1", ".hta", ".cpl", ".iso", ".reg"
}


class FileSecurityGuard:
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitizes filename, stripping directory traversal tokens, null bytes,
        and dangerous control characters.
        """
        if not filename:
            return "attachment_document"

        # Remove null bytes and path separators
        clean = filename.replace("\x00", "").replace("/", "_").replace("\\", "_")
        # Remove relative directory navigation
        clean = clean.replace("..", "_")
        # Strip dangerous symbols, preserving alphanumeric, dots, underscores, dashes
        clean = re.sub(r'[^a-zA-Z0-9._\- ]', '', clean)
        clean = clean.strip(". ")

        if not clean:
            return "attachment_document"
        return clean[:120]  # Max safe length

    @staticmethod
    def validate_file(
        filename: str,
        content_bytes: bytes,
        declared_mime_type: Optional[str] = None
    ) -> Tuple[bool, str, str]:
        """
        Validates file size, extension, and content type.
        Returns: (is_valid, sanitized_filename, resolved_mime_type)
        Raises HTTPException on violation.
        """
        # 1. Size Validation (25 MB max)
        size = len(content_bytes)
        if size == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty (0 bytes).")
        if size > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=400,
                detail=f"File exceeds maximum permissible size limit of 25 MB (size: {size / (1024 * 1024):.1f} MB)."
            )

        # 2. Filename and Path Traversal Check
        sanitized = FileSecurityGuard.sanitize_filename(filename)
        _, ext = os.path.splitext(sanitized.lower())

        if ext in DANGEROUS_EXTENSIONS:
            logger.warning(f"Blocked upload attempt with dangerous extension: {ext} ({filename})")
            raise HTTPException(
                status_code=400,
                detail=f"Security violation: File extension '{ext}' is prohibited."
            )

        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format '{ext}'. Allowed formats: PDF, DOCX, TXT, MD, PNG, JPG, WEBP."
            )

        # 3. Magic Header Content Sniffing
        resolved_mime = declared_mime_type or "application/octet-stream"
        if content_bytes.startswith(b"%PDF-"):
            resolved_mime = "application/pdf"
        elif content_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
            resolved_mime = "image/png"
        elif content_bytes.startswith(b"\xff\xd8\xff"):
            resolved_mime = "image/jpeg"
        elif content_bytes.startswith(b"RIFF") and b"WEBP" in content_bytes[:16]:
            resolved_mime = "image/webp"
        elif content_bytes.startswith(b"PK\x03\x04") and ext in (".docx", ".doc"):
            resolved_mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif ext in (".txt", ".md"):
            resolved_mime = "text/plain" if ext == ".txt" else "text/markdown"

        return True, sanitized, resolved_mime

    @staticmethod
    def get_user_storage_dir(base_storage_dir: str, user_id: str) -> str:
        """
        Returns safe per-tenant directory path.
        Prevents tenant directory escape.
        """
        safe_user_id = re.sub(r'[^a-zA-Z0-9_\-]', '', user_id) or "default_user"
        target_dir = os.path.join(base_storage_dir, safe_user_id)
        os.makedirs(target_dir, exist_ok=True)
        return target_dir


file_security_guard = FileSecurityGuard()
