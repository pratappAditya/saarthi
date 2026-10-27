"""
Central Production Multimodal Service.
Orchestrates:
1. File security validation (25MB max, MIME & extension verification, path sanitization)
2. Document Parsing (PDF, DOCX, TXT, MD) with scanned-page OCR fallback
3. Vision & Screenshot Analysis (layout segmentation, UI inspection, diagram classification)
4. Prompt Injection Defense (untrusted boundary wrapping & injection pattern screening)
5. Tenant Isolation & Persistence in AttachmentManager
6. Construction of normalized MultimodalContext for Saarthi Intelligence
"""

import os
import logging
from typing import Dict, Any, List, Optional, Tuple

from app.intelligence.multimodal.models import (
    MultimodalContext,
    DocumentParseResult,
    VisionAnalysisResult,
    OCRResult,
    MultimodalProcessingStatus,
    EvidenceClass
)
from app.intelligence.multimodal.security import file_security_guard, MAX_FILE_SIZE_BYTES
from app.intelligence.multimodal.injection_defense import injection_defense
from app.intelligence.multimodal.ocr_engine import ocr_engine
from app.intelligence.multimodal.vision_engine import vision_engine
from app.intelligence.multimodal.document_parsers import document_parser_router
from app.intelligence.multimodal.attachment_manager import attachment_manager, InputAttachment
from app.security.quota import QuotaManager

logger = logging.getLogger("app.intelligence.multimodal.service")


class MultimodalService:
    def process_and_save_upload(
        self,
        filename: str,
        content_bytes: bytes,
        declared_mime_type: Optional[str] = None,
        project_id: Optional[str] = None,
        user_id: str = "default_local_user",
        plan: str = "free"
    ) -> Tuple[InputAttachment, MultimodalContext]:
        """
        Processes uploaded multimodal file: validates security, extracts structured content,
        scans for injection risks, and persists attachment.
        """
        # 1. Quota check
        allowed, q_info = QuotaManager.check_and_increment_quota(user_id, plan)
        if not allowed:
            from fastapi import HTTPException
            raise HTTPException(status_code=429, detail=q_info.get("error", "Daily upload quota exceeded."))

        # 2. File Security & MIME validation
        _, safe_filename, resolved_mime = file_security_guard.validate_file(
            filename=filename,
            content_bytes=content_bytes,
            declared_mime_type=declared_mime_type
        )

        extracted_text = ""
        ocr_text = ""
        content_type = "document"
        vision_result: Optional[VisionAnalysisResult] = None
        doc_result: Optional[DocumentParseResult] = None
        pages_ctx = []
        tables = []
        confidence = 0.95
        evidence_class = EvidenceClass.SOURCE_DERIVED

        # 3. Route according to resolved MIME type
        if resolved_mime.startswith("image/"):
            content_type = "image"
            evidence_class = EvidenceClass.SOURCE_DERIVED

            # Analyze visual elements & screenshot intelligence
            vision_result = vision_engine.analyze_image(
                image_bytes=content_bytes,
                prompt=f"Inspect visual elements and structure of {safe_filename}",
                mime_type=resolved_mime
            )
            extracted_text = "\n".join(vision_result.observations)
            if vision_result.extracted_text:
                ocr_text = vision_result.extracted_text
                extracted_text += f"\n\nExtracted Text:\n{ocr_text}"

            confidence = vision_result.confidence
            tables = vision_result.tables

        elif resolved_mime == "application/pdf":
            content_type = "document"
            doc_result = document_parser_router.parse_document(
                file_bytes=content_bytes,
                filename=safe_filename,
                mime_type=resolved_mime
            )
            extracted_text = doc_result.combined_text
            pages_ctx = doc_result.pages
            tables = doc_result.tables

            # Collect any OCR fallback text
            ocr_lines = []
            for p in pages_ctx:
                if p.ocr_applied:
                    ocr_lines.append(f"[Page {p.page_number} OCR]: {p.text_content}")
            if ocr_lines:
                ocr_text = "\n".join(ocr_lines)

            confidence = 0.96 if not doc_result.has_ocr_content else 0.92

        elif "wordprocessingml" in resolved_mime or safe_filename.endswith((".docx", ".doc")):
            content_type = "document"
            doc_result = document_parser_router.parse_document(
                file_bytes=content_bytes,
                filename=safe_filename,
                mime_type=resolved_mime
            )
            extracted_text = doc_result.combined_text
            pages_ctx = doc_result.pages
            tables = doc_result.tables
            confidence = 0.98

        else:
            # Text / Markdown
            content_type = "document"
            doc_result = document_parser_router.parse_document(
                file_bytes=content_bytes,
                filename=safe_filename,
                mime_type=resolved_mime
            )
            extracted_text = doc_result.combined_text
            pages_ctx = doc_result.pages
            confidence = 0.99

        # 4. Prompt Injection Defense
        has_injection_risk, patterns = injection_defense.inspect_text(extracted_text)
        untrusted_wrapper = injection_defense.wrap_untrusted_content(
            text=extracted_text,
            filename=safe_filename,
            source_type=content_type,
            page_number=1
        )

        metadata = {
            "sanitized_filename": safe_filename,
            "resolved_mime": resolved_mime,
            "has_injection_risk": has_injection_risk,
            "injection_patterns": patterns,
            "table_count": len(tables),
            "confidence": confidence,
            "image_type": vision_result.image_type if vision_result else None
        }

        # 5. Persist to AttachmentManager with tenant isolation
        attachment = attachment_manager.save_attachment(
            filename=safe_filename,
            content_bytes=content_bytes,
            mime_type=resolved_mime,
            extracted_text=extracted_text,
            ocr_text=ocr_text,
            content_type=content_type,
            project_id=project_id,
            user_id=user_id,
            metadata=metadata
        )

        # 6. Build normalized MultimodalContext
        multimodal_context = MultimodalContext(
            attachment_id=attachment.id,
            filename=safe_filename,
            mime_type=resolved_mime,
            source_type=content_type,
            extracted_text=extracted_text,
            untrusted_content_block=untrusted_wrapper,
            vision_context=vision_result,
            document_structure=doc_result,
            page_contexts=pages_ctx,
            ocr_blocks=[],
            tables=tables,
            confidence=confidence,
            evidence_class=evidence_class,
            prompt_injection_flag=has_injection_risk,
            user_id=user_id
        )

        return attachment, multimodal_context


multimodal_service = MultimodalService()
