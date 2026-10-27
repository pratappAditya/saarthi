"""
Authoritative Configuration for Saarthi NVIDIA Nemotron AI Model
"""

class NemotronConfig:
    EXACT_NEMOTRON_MODEL: str = "nemotron-3-nano:4b"
    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"
    MODEL_TEMPERATURE: float = 0.7
    MODEL_MAX_TOKENS: int = 512
    MIN_RECOMMENDED_RAM_GB: float = 8.0
    MIN_FREE_RAM_GB: float = 4.0
    ALLOW_NON_NEMOTRON: bool = False
    APPROVED_NEMOTRON_FAMILY: str = "NVIDIA Nemotron"

