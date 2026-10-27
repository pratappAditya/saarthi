"""
Vision Engine Module.
Integrates Real Vision Provider Architecture into Saarthi Multimodal Layer.
"""

from app.intelligence.multimodal.models import VisionAnalysisResult
from app.intelligence.multimodal.vision_provider import VisionProvider, vision_provider, RealLocalVisionProvider

# Export standard singleton
vision_engine = vision_provider

__all__ = ["VisionAnalysisResult", "VisionProvider", "vision_engine", "RealLocalVisionProvider"]
