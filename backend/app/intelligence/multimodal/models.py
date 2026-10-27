"""
Multimodal Data Models & Contracts for Production Multimodal 2.0.
Defines normalized structures for OCR, Vision, Document Parsing, Provenance, and Context.
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import datetime


class MultimodalProcessingStatus(str, Enum):
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    UNSUPPORTED = "UNSUPPORTED"
    FAILED = "FAILED"
    UNAVAILABLE = "UNAVAILABLE"


class EvidenceClass(str, Enum):
    FACT = "FACT"
    SOURCE_DERIVED = "SOURCE-DERIVED"
    INFERENCE = "INFERENCE"
    UNCERTAIN = "UNCERTAIN"


class OCRBlock(BaseModel):
    """Represents a discrete block of text extracted via OCR."""
    text: str
    page_number: int = 1
    confidence: float = 0.95
    bounding_box: Optional[Dict[str, int]] = None  # {x, y, width, height}
    language: str = "en"
    block_type: str = "paragraph"  # "paragraph", "heading", "table_cell", "caption"


class OCRResult(BaseModel):
    """Aggregated OCR output preserving page and block provenance."""
    extracted_text: str
    confidence: float = 0.95
    language: str = "en"
    detected_languages: List[str] = Field(default_factory=lambda: ["en"])
    page_number: int = 1
    total_pages: int = 1
    blocks: List[OCRBlock] = Field(default_factory=list)
    provider_name: str = "Local OCR Engine"
    provenance_source: str = "OCR"
    status: MultimodalProcessingStatus = MultimodalProcessingStatus.SUCCESS


class TableData(BaseModel):
    """Structured table extracted from document or visual scan."""
    title: Optional[str] = None
    headers: List[str] = Field(default_factory=list)
    rows: List[List[str]] = Field(default_factory=list)
    page_number: int = 1


class VisionAnalysisResult(BaseModel):
    """Structured visual inspection result."""
    observations: List[str] = Field(default_factory=list)
    extracted_text: str = ""
    entities: List[str] = Field(default_factory=list)
    visual_elements: List[str] = Field(default_factory=list)
    image_type: str = "general_image"  # "screenshot", "diagram", "chart", "scanned_doc", "photograph"
    dimensions: Optional[Dict[str, int]] = None  # {width, height}
    color_mode: str = "RGB"
    tables: List[TableData] = Field(default_factory=list)
    confidence: float = 0.95
    provenance: str = "Local Nemotron Vision Abstraction"
    status: MultimodalProcessingStatus = MultimodalProcessingStatus.SUCCESS
    error_message: Optional[str] = None


class PageContext(BaseModel):
    """Context for an individual page in a multi-page document."""
    page_number: int
    text_content: str = ""
    has_scanned_content: bool = False
    ocr_applied: bool = False
    ocr_confidence: Optional[float] = None
    tables: List[TableData] = Field(default_factory=list)
    character_count: int = 0


class DocumentParseResult(BaseModel):
    """Full document extraction output with structure and metadata."""
    filename: str
    mime_type: str
    total_pages: int = 1
    pages: List[PageContext] = Field(default_factory=list)
    combined_text: str = ""
    document_metadata: Dict[str, Any] = Field(default_factory=dict)
    tables: List[TableData] = Field(default_factory=list)
    has_ocr_content: bool = False
    status: MultimodalProcessingStatus = MultimodalProcessingStatus.SUCCESS
    provenance_source: str = "DOCUMENT_PARSER"
    error_message: Optional[str] = None


class MultimodalContext(BaseModel):
    """
    Normalized internal multimodal context entering the Saarthi Intelligence Core.
    Preserves origin, provenance, and untrusted-data boundary.
    """
    attachment_id: str
    filename: str
    mime_type: str
    source_type: str  # "document", "image", "screenshot", "scan"
    extracted_text: str
    untrusted_content_block: str
    vision_context: Optional[VisionAnalysisResult] = None
    document_structure: Optional[DocumentParseResult] = None
    page_contexts: List[PageContext] = Field(default_factory=list)
    ocr_blocks: List[OCRBlock] = Field(default_factory=list)
    tables: List[TableData] = Field(default_factory=list)
    confidence: float = 0.95
    evidence_class: EvidenceClass = EvidenceClass.SOURCE_DERIVED
    provenance: str = "MULTIMODAL_INGESTION"
    prompt_injection_flag: bool = False
    user_id: str = "default_local_user"
    created_at: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
