import uuid
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("app.intelligence.attachment_engine")

class InputAttachment(BaseModel):
    id: str = Field(default_factory=lambda: f"att_{uuid.uuid4().hex[:8]}")
    filename: str
    mime_type: str = "application/pdf"
    content_type: str = "document"  # "document" | "image" | "audio" | "code"
    content_text: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AttachmentEngine:
    @staticmethod
    def process_attachment(filename: str, raw_text: str, mime_type: str = "text/plain") -> InputAttachment:
        content_type = "document"
        if mime_type.startswith("image/"):
            content_type = "image"
        elif mime_type.startswith("audio/"):
            content_type = "audio"
        elif "javascript" in mime_type or "python" in mime_type or filename.endswith((".py", ".ts", ".js")):
            content_type = "code"

        return InputAttachment(
            filename=filename,
            mime_type=mime_type,
            content_type=content_type,
            content_text=raw_text,
            metadata={"character_count": len(raw_text)}
        )

attachment_engine = AttachmentEngine()
