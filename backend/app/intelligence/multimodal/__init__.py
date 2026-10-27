"""
Multimodal Intelligence Package.
Production Multimodal 2.0 with Real OCR, Vision, Document Parsing, Security, and Provenance.
"""

from .models import (
    MultimodalContext,
    MultimodalProcessingStatus,
    EvidenceClass,
    OCRBlock,
    OCRResult,
    VisionAnalysisResult,
    TableData,
    PageContext,
    DocumentParseResult
)
from .security import FileSecurityGuard, file_security_guard, MAX_FILE_SIZE_BYTES
from .injection_defense import PromptInjectionDefense, injection_defense
from .ocr_engine import ocr_engine, OCRProvider
from .vision_engine import vision_engine, VisionProvider
from .document_parsers import document_parser_router, PDFParser, DOCXParser, TextParser
from .attachment_manager import attachment_manager, InputAttachment
from .multimodal_service import multimodal_service, MultimodalService

__all__ = [
    "MultimodalContext",
    "MultimodalProcessingStatus",
    "EvidenceClass",
    "OCRBlock",
    "OCRResult",
    "VisionAnalysisResult",
    "TableData",
    "PageContext",
    "DocumentParseResult",
    "FileSecurityGuard",
    "file_security_guard",
    "MAX_FILE_SIZE_BYTES",
    "PromptInjectionDefense",
    "injection_defense",
    "ocr_engine",
    "OCRProvider",
    "vision_engine",
    "VisionProvider",
    "document_parser_router",
    "PDFParser",
    "DOCXParser",
    "TextParser",
    "attachment_manager",
    "InputAttachment",
    "multimodal_service",
    "MultimodalService"
]
