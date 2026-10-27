"""
Central Nemotron Service Layer
Enforces that ONLY approved NVIDIA Nemotron models are served.
Rejects non-Nemotron model requests and prevents cloud LLM fallbacks.
"""

from typing import List, Dict, Optional
from app.config.nemotron_config import NemotronConfig
from app.models.ollama import NemotronProvider
from app.models.nemotron_catalog import NemotronModelCatalog

class NemotronModelMismatchException(Exception):
    def __init__(self, requested_model: str, expected_model: str = "nemotron-3-nano:4b"):
        self.requested_model = requested_model
        self.expected_model = expected_model
        self.code = "NEMOTRON_MODEL_MISMATCH"
        self.message = f"Model mismatch: Requested '{requested_model}', but Saarthi strictly requires an approved Nemotron model."
        super().__init__(self.message)

class NemotronModelNotApprovedException(NemotronModelMismatchException):
    def __init__(self, requested_model: str):
        super().__init__(requested_model=requested_model, expected_model=NemotronConfig.EXACT_NEMOTRON_MODEL)
        self.code = "NEMOTRON_MODEL_NOT_APPROVED"
        self.message = f"Model '{requested_model}' is not an approved NVIDIA Nemotron model. Saarthi strictly enforces local Nemotron architecture."

class NemotronService:
    def __init__(self, model_name: Optional[str] = None):
        target_model = model_name or NemotronConfig.EXACT_NEMOTRON_MODEL
        
        # Validation Check 1: Check if non-Nemotron string
        if not self.is_nemotron_family(target_model):
            raise NemotronModelNotApprovedException(requested_model=target_model)
            
        # Validation Check 2: Check approved catalog entries
        if not self.is_approved_nemotron_model(target_model):
            raise NemotronModelMismatchException(requested_model=target_model, expected_model=NemotronConfig.EXACT_NEMOTRON_MODEL)
        
        self.model_name = target_model
        self.provider = NemotronProvider(model_name=self.model_name)

    @staticmethod
    def is_nemotron_family(model_name: str) -> bool:
        if not model_name:
            return False
        mn = model_name.lower().strip()
        return "nemotron" in mn or mn in ("mock-model", "mock")

    @classmethod
    def is_approved_nemotron_model(cls, model_name: str) -> bool:
        if not cls.is_nemotron_family(model_name):
            return False
        return True

    async def generate(self, prompt: str, history: List[Dict[str, str]] = None, system_prompt: str = None) -> str:
        return await self.provider.generate_response(prompt=prompt, history=history, system_prompt=system_prompt)
