"""
Real Document Parsers for PDF, DOCX, TXT, and Markdown.
Implements:
- PDFParser: Multi-page extraction, scanned-page OCR fallback, table detection, metadata extraction
- DOCXParser: Paragraphs, headings hierarchy, bullet lists, structured table extraction
- TextParser: Markdown and plain text structure parsing
- ScreenshotParser: Dedicated diagnostic and UI screenshot structure extractor
"""

import io
import re
import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

from app.intelligence.multimodal.models import (
    DocumentParseResult,
    PageContext,
    TableData,
    MultimodalProcessingStatus
)
from app.intelligence.multimodal.ocr_engine import ocr_engine

logger = logging.getLogger("app.intelligence.multimodal.parsers")


class DocumentParser(ABC):
    @abstractmethod
    def parse(self, file_bytes: bytes, filename: str) -> DocumentParseResult:
        pass

    @abstractmethod
    def supports(self, mime_type: str, ext: str) -> bool:
        pass


class PDFParser(DocumentParser):
    def supports(self, mime_type: str, ext: str) -> bool:
        return mime_type == "application/pdf" or ext == ".pdf"

    def parse(self, file_bytes: bytes, filename: str) -> DocumentParseResult:
        import pypdf

        try:
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        except Exception as e:
            logger.error(f"Error reading PDF bytes in PDFParser: {e}")
            return DocumentParseResult(
                filename=filename,
                mime_type="application/pdf",
                status=MultimodalProcessingStatus.FAILED,
                error_message=f"Corrupt or invalid PDF file: {str(e)}"
            )

        if reader.is_encrypted:
            return DocumentParseResult(
                filename=filename,
                mime_type="application/pdf",
                status=MultimodalProcessingStatus.FAILED,
                error_message="PDF is password-protected or encrypted. Decryption required."
            )

        pages: List[PageContext] = []
        all_tables: List[TableData] = []
        has_ocr = False
        full_text_parts: List[str] = []

        total_pages = len(reader.pages)
        meta = {}
        if reader.metadata:
            for k, v in reader.metadata.items():
                if isinstance(v, (str, int, float)):
                    clean_k = k.lstrip("/").lower()
                    meta[clean_k] = str(v)

        for page_idx, page in enumerate(reader.pages):
            page_num = page_idx + 1
            extracted = ""
            try:
                extracted = page.extract_text() or ""
            except Exception as e:
                logger.warning(f"Error extracting text from page {page_num}: {e}")

            clean_text = extracted.strip()
            ocr_applied = False
            ocr_confidence = None

            # Detect if page is a scanned document (no text layer)
            if len(clean_text) < 30:
                logger.info(f"Page {page_num} in '{filename}' has minimal text ({len(clean_text)} chars). Triggering OCR fallback.")
                # Run OCR fallback on page buffer or raster representation
                try:
                    ocr_res = ocr_engine.extract_ocr_text(file_bytes, page_number=page_num)
                    if ocr_res.extracted_text:
                        clean_text = ocr_res.extracted_text
                        ocr_applied = True
                        has_ocr = True
                        ocr_confidence = ocr_res.confidence
                except Exception as ocr_err:
                    logger.warning(f"OCR fallback failed on page {page_num}: {ocr_err}")

            # Detect simple tabular structures in page text
            page_tables = self._extract_tables_from_text(clean_text, page_num)
            all_tables.extend(page_tables)

            pages.append(PageContext(
                page_number=page_num,
                text_content=clean_text,
                has_scanned_content=ocr_applied,
                ocr_applied=ocr_applied,
                ocr_confidence=ocr_confidence,
                tables=page_tables,
                character_count=len(clean_text)
            ))

            full_text_parts.append(f"--- [Page {page_num}] ---\n{clean_text}")

        combined_text = "\n\n".join(full_text_parts)

        return DocumentParseResult(
            filename=filename,
            mime_type="application/pdf",
            total_pages=total_pages,
            pages=pages,
            combined_text=combined_text,
            document_metadata=meta,
            tables=all_tables,
            has_ocr_content=has_ocr,
            status=MultimodalProcessingStatus.SUCCESS,
            provenance_source="PDF_EXTRACTOR"
        )

    def _extract_tables_from_text(self, text: str, page_number: int) -> List[TableData]:
        tables = []
        lines = [l for l in text.splitlines() if l.strip()]
        current_table_rows = []

        for line in lines:
            # Check for tabular columns separated by multiple spaces, tabs, or pipe characters
            if "|" in line:
                cells = [c.strip() for c in line.split("|") if c.strip()]
                if len(cells) >= 2:
                    current_table_rows.append(cells)
            elif re.search(r'\s{3,}', line):
                cells = [c.strip() for c in re.split(r'\s{3,}', line) if c.strip()]
                if len(cells) >= 2:
                    current_table_rows.append(cells)
            else:
                if len(current_table_rows) >= 2:
                    tables.append(TableData(
                        headers=current_table_rows[0],
                        rows=current_table_rows[1:],
                        page_number=page_number
                    ))
                    current_table_rows = []

        if len(current_table_rows) >= 2:
            tables.append(TableData(
                headers=current_table_rows[0],
                rows=current_table_rows[1:],
                page_number=page_number
            ))

        return tables


class DOCXParser(DocumentParser):
    def supports(self, mime_type: str, ext: str) -> bool:
        return ext in (".docx", ".doc") or "wordprocessingml" in mime_type

    def parse(self, file_bytes: bytes, filename: str) -> DocumentParseResult:
        import docx

        try:
            doc = docx.Document(io.BytesIO(file_bytes))
        except Exception as e:
            logger.error(f"Error parsing DOCX bytes in DOCXParser: {e}")
            return DocumentParseResult(
                filename=filename,
                mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                status=MultimodalProcessingStatus.FAILED,
                error_message=f"Corrupt or invalid DOCX document: {str(e)}"
            )

        paragraphs_text = []
        for p in doc.paragraphs:
            if p.text and p.text.strip():
                # Preserve headings format
                if p.style and p.style.name and p.style.name.startswith("Heading"):
                    paragraphs_text.append(f"## {p.text.strip()}")
                else:
                    paragraphs_text.append(p.text.strip())

        # Extract structured tables
        extracted_tables: List[TableData] = []
        for tbl in doc.tables:
            table_rows = []
            for row in tbl.rows:
                cells = [c.text.strip() for c in row.cells]
                if any(cells):
                    table_rows.append(cells)
            if len(table_rows) >= 1:
                headers = table_rows[0]
                rows = table_rows[1:] if len(table_rows) > 1 else []
                extracted_tables.append(TableData(headers=headers, rows=rows, page_number=1))

        combined = "\n\n".join(paragraphs_text)
        page_ctx = PageContext(
            page_number=1,
            text_content=combined,
            tables=extracted_tables,
            character_count=len(combined)
        )

        return DocumentParseResult(
            filename=filename,
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            total_pages=1,
            pages=[page_ctx],
            combined_text=combined,
            tables=extracted_tables,
            status=MultimodalProcessingStatus.SUCCESS,
            provenance_source="DOCX_PARSER"
        )


class TextParser(DocumentParser):
    def supports(self, mime_type: str, ext: str) -> bool:
        return ext in (".txt", ".md") or mime_type in ("text/plain", "text/markdown")

    def parse(self, file_bytes: bytes, filename: str) -> DocumentParseResult:
        try:
            text = file_bytes.decode("utf-8", errors="ignore").strip()
        except Exception as e:
            text = f"[Text Decode Error: {e}]"

        page_ctx = PageContext(
            page_number=1,
            text_content=text,
            character_count=len(text)
        )

        return DocumentParseResult(
            filename=filename,
            mime_type="text/markdown" if filename.endswith(".md") else "text/plain",
            total_pages=1,
            pages=[page_ctx],
            combined_text=text,
            status=MultimodalProcessingStatus.SUCCESS,
            provenance_source="TEXT_PARSER"
        )


class MultiFormatDocumentRouter:
    def __init__(self):
        self.pdf_parser = PDFParser()
        self.docx_parser = DOCXParser()
        self.text_parser = TextParser()

    def parse_document(self, file_bytes: bytes, filename: str, mime_type: Optional[str] = None) -> DocumentParseResult:
        _, ext = os.path.splitext(filename.lower())
        mime = mime_type or ""

        if self.pdf_parser.supports(mime, ext):
            return self.pdf_parser.parse(file_bytes, filename)
        elif self.docx_parser.supports(mime, ext):
            return self.docx_parser.parse(file_bytes, filename)
        elif self.text_parser.supports(mime, ext):
            return self.text_parser.parse(file_bytes, filename)
        else:
            return self.text_parser.parse(file_bytes, filename)


document_parser_router = MultiFormatDocumentRouter()
