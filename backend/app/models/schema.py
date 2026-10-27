"""
Unified Model Platform Schemas and Data Models for Saarthi.
Defines capability taxonomy, response structures, token usage metrics,
model descriptors, cost classes, and standardized exceptions.
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ModelCapability(str, Enum):
    TEXT = "text"
    REASONING = "reasoning"
    CODING = "coding"
    TOOL_CALLING = "tool_calling"
    VISION = "vision"
    AUDIO = "audio"
    EMBEDDINGS = "embeddings"
    LONG_CONTEXT = "long_context"


class CostClass(str, Enum):
    FREE_LOCAL = "FREE_LOCAL"
    FREE_TIER = "FREE_TIER"
    LOW_COST = "LOW_COST"
    STANDARD = "STANDARD"
    HIGH_REASONING = "HIGH_REASONING"


class LatencyClass(str, Enum):
    INSTANT = "INSTANT"
    ULTRA_FAST = "ULTRA_FAST"
    FAST = "FAST"
    MEDIUM = "MEDIUM"
    SLOW = "SLOW"


class PrivacyLevel(str, Enum):
    LOCAL_AIRGAPPED = "LOCAL_AIRGAPPED"
    ZERO_DATA_RETENTION = "ZERO_DATA_RETENTION"
    STANDARD_CLOUD = "STANDARD_CLOUD"


class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ModelResponse(BaseModel):
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    structured_data: Optional[Dict[str, Any]] = None
    model_id: str
    provider: str
    is_live: bool = False
    execution_mode: str = "MOCK"  # "LIVE" | "MOCK" | "FALLBACK"
    usage: TokenUsage = Field(default_factory=TokenUsage)
    latency_ms: float = 0.0
    cost_estimate_usd: float = 0.0
    finish_reason: str = "stop"
    cached: bool = False


class ModelDescriptor(BaseModel):
    id: str
    name: str
    provider: str  # "ollama", "mock", "qwen", "deepseek", "groq", "openrouter", "glm", "kimi", "minimax", "llama"
    is_local: bool = False
    capabilities: List[ModelCapability] = Field(default_factory=list)
    context_window: int = 128000
    cost_class: CostClass = CostClass.FREE_TIER
    latency_class: LatencyClass = LatencyClass.FAST
    privacy_level: PrivacyLevel = PrivacyLevel.STANDARD_CLOUD
    max_output_tokens: int = 4096
    availability: bool = True
    deprecated: bool = False
    supports_streaming: bool = True
    supports_structured_output: bool = True
    supports_tool_calling: bool = True
    cost_per_million_input_usd: float = 0.0
    cost_per_million_output_usd: float = 0.0


class ProviderQuota(BaseModel):
    provider: str
    daily_token_limit: int = 1_000_000
    daily_tokens_used: int = 0
    daily_cost_ceiling_usd: float = 1.0
    daily_cost_used_usd: float = 0.0
    is_exhausted: bool = False


class ModelProviderError(Exception):
    """Base exception for model provider errors."""
    def __init__(self, message: str, provider: str = "", model_id: str = "", retryable: bool = False):
        super().__init__(message)
        self.message = message
        self.provider = provider
        self.model_id = model_id
        self.retryable = retryable


class RateLimitError(ModelProviderError):
    def __init__(self, message: str, provider: str = "", model_id: str = ""):
        super().__init__(message, provider=provider, model_id=model_id, retryable=True)


class AuthenticationError(ModelProviderError):
    def __init__(self, message: str, provider: str = "", model_id: str = ""):
        super().__init__(message, provider=provider, model_id=model_id, retryable=False)


class ContextLengthError(ModelProviderError):
    def __init__(self, message: str, provider: str = "", model_id: str = ""):
        super().__init__(message, provider=provider, model_id=model_id, retryable=False)


class ModelUnavailableError(ModelProviderError):
    def __init__(self, message: str, provider: str = "", model_id: str = ""):
        super().__init__(message, provider=provider, model_id=model_id, retryable=True)
