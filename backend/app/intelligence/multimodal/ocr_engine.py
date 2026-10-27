"""
OCR Engine Module.
Integrates Real OCR Provider Architecture into the Saarthi Multimodal Layer.
"""

from app.intelligence.multimodal.models import OCRResult, OCRBlock
from app.intelligence.multimodal.ocr_provider import OCRProvider, ocr_provider, RealLocalOCRProvider

# Export standard singleton
ocr_engine = ocr_provider

__all__ = ["OCRResult", "OCRBlock", "OCRProvider", "ocr_engine", "RealLocalOCRProvider"]
