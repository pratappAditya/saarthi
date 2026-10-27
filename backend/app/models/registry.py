"""
Capability-Driven Model Registry for Saarthi.
Catalogs all supported models with verified capabilities, context limits,
cost classes, latency ratings, and runtime availability checks.
"""

import logging
from typing import Dict, Any, List, Optional
from app.models.schema import (
    ModelDescriptor,
    ModelCapability,
    CostClass,
    LatencyClass,
    PrivacyLevel
)

logger = logging.getLogger("app.models.registry")

GLOBAL_MODEL_CATALOG: Dict[str, ModelDescriptor] = {
    # 1. Local Nemotron via Ollama
    "nemotron-3-nano:4b": ModelDescriptor(
        id="nemotron-3-nano:4b",
        name="NVIDIA Nemotron 3 Nano (4B)",
        provider="ollama",
        is_local=True,
        capabilities=[
            ModelCapability.TEXT,
            ModelCapability.REASONING,
            ModelCapability.CODING,
            ModelCapability.TOOL_CALLING
        ],
        context_window=128000,
        cost_class=CostClass.FREE_LOCAL,
        latency_class=LatencyClass.ULTRA_FAST,
        privacy_level=PrivacyLevel.LOCAL_AIRGAPPED,
        supports_streaming=True,
        supports_structured_output=True,
        supports_tool_calling=True
    ),
    "nemotron-3-8b": ModelDescriptor(
        id="nemotron-3-8b",
        name="NVIDIA Nemotron 3 (8B)",
        provider="ollama",
        is_local=True,
        capabilities=[
            ModelCapability.TEXT,
            ModelCapability.REASONING,
            ModelCapability.CODING,
            ModelCapability.TOOL_CALLING
        ],
        context_window=128000,
        cost_class=CostClass.FREE_LOCAL,
        latency_class=LatencyClass.FAST,
        privacy_level=PrivacyLevel.LOCAL_AIRGAPPED,
        supports_streaming=True,
        supports_structured_output=True,
        supports_tool_calling=True
    ),

    # 2. Mock Offline/Testing Model
    "mock_local_model": ModelDescriptor(
        id="mock_local_model",
        name="Saarthi Mock Intelligence Engine",
        provider="mock",
        is_local=True,
        capabilities=[
            ModelCapability.TEXT,
            ModelCapability.REASONING,
            ModelCapability.CODING,
            ModelCapability.TOOL_CALLING,
            ModelCapability.VISION,
            ModelCapability.LONG_CONTEXT
        ],
        context_window=128000,
        cost_class=CostClass.FREE_LOCAL,
        latency_class=LatencyClass.INSTANT,
        privacy_level=PrivacyLevel.LOCAL_AIRGAPPED,
        supports_streaming=True,
        supports_structured_output=True,
        supports_tool_calling=True
    ),

    # 3. Groq (High Speed & Free Tier)
    "llama-3.1-8b-instant": ModelDescriptor(
        id="llama-3.1-8b-instant",
        name="Meta Llama 3.1 8B Instant (Groq)",
        provider="groq",
        is_local=False,
        capabilities=[
            ModelCapability.TEXT,
            ModelCapability.REASONING,
            ModelCapability.TOOL_CALLING
        ],
        context_window=128000,
        cost_class=CostClass.FREE_TIER,
        latency_class=LatencyClass.ULTRA_FAST,
        privacy_level=PrivacyLevel.ZERO_DATA_RETENTION,
        cost_per_million_input_usd=0.05,
        cost_per_million_output_usd=0.08
    ),
    "llama-3.3-70b-versatile": ModelDescriptor(
        id="llama-3.3-70b-versatile",
        name="Meta Llama 3.3 70B Versatile (Groq)",
        provider="groq",
        is_local=False,
        capabilities=[
            ModelCapability.TEXT,
            ModelCapability.REASONING,
            ModelCapability.CODING,
            ModelCapability.TOOL_CALLING,
            ModelCapability.LONG_CONTEXT
        ],
        context_window=128000,
        cost_class=CostClass.LOW_COST,
        latency_class=LatencyClass.ULTRA_FAST,
        privacy_level=PrivacyLevel.ZERO_DATA_RETENTION,
        cost_per_million_input_usd=0.59,
        cost_per_million_output_usd=0.79
    ),

    # 4. DeepSeek (Reasoning & Coding)
    "deepseek-chat": ModelDescriptor(
        id="deepseek-chat",
        name="DeepSeek V3 (Chat & Code)",
        provider="deepseek",
        is_local=False,
        capabilities=[
            ModelCapability.TEXT,
            ModelCapability.REASONING,
            ModelCapability.CODING,
            ModelCapability.TOOL_CALLING,
            ModelCapability.LONG_CONTEXT
        ],
        context_window=65536,
        cost_class=CostClass.LOW_COST,
        latency_class=LatencyClass.FAST,
        privacy_level=PrivacyLevel.STANDARD_CLOUD,
        cost_per_million_input_usd=0.14,
        cost_per_million_output_usd=0.28
    ),
    "deepseek-reasoner": ModelDescriptor(
        id="deepseek-reasoner",
        name="DeepSeek R1 (Deep Reasoning)",
        provider="deepseek",
        is_local=False,
        capabilities=[
            ModelCapability.TEXT,
            ModelCapability.REASONING,
            ModelCapability.CODING
        ],
        context_window=65536,
        cost_class=CostClass.HIGH_REASONING,
        latency_class=LatencyClass.MEDIUM,
        privacy_level=PrivacyLevel.STANDARD_CLOUD,
        cost_per_million_input_usd=0.55,
        cost_per_million_output_usd=2.19
    ),

    # 5. Qwen 2.5
    "qwen-2.5-72b-instruct": ModelDescriptor(
        id="qwen-2.5-72b-instruct",
        name="Qwen 2.5 72B Instruct",
        provider="qwen",
        is_local=False,
        capabilities=[
            ModelCapability.TEXT,
            ModelCapability.REASONING,
            ModelCapability.CODING,
            ModelCapability.TOOL_CALLING,
            ModelCapability.LONG_CONTEXT
        ],
        context_window=131072,
        cost_class=CostClass.STANDARD,
        latency_class=LatencyClass.FAST,
        privacy_level=PrivacyLevel.STANDARD_CLOUD,
        cost_per_million_input_usd=0.40,
        cost_per_million_output_usd=1.20
    ),
    "qwen-2.5-coder-32b-instruct": ModelDescriptor(
        id="qwen-2.5-coder-32b-instruct",
        name="Qwen 2.5 Coder 32B Instruct",
        provider="qwen",
        is_local=False,
        capabilities=[
            ModelCapability.TEXT,
            ModelCapability.CODING,
            ModelCapability.TOOL_CALLING
        ],
        context_window=131072,
        cost_class=CostClass.LOW_COST,
        latency_class=LatencyClass.FAST,
        privacy_level=PrivacyLevel.STANDARD_CLOUD,
        cost_per_million_input_usd=0.20,
        cost_per_million_output_usd=0.60
    ),
    "qwen-vl-max": ModelDescriptor(
        id="qwen-vl-max",
        name="Qwen-VL Max (Vision Language)",
        provider="qwen",
        is_local=False,
        capabilities=[
            ModelCapability.TEXT,
            ModelCapability.VISION,
            ModelCapability.REASONING
        ],
        context_window=32768,
        cost_class=CostClass.STANDARD,
        latency_class=LatencyClass.MEDIUM,
        privacy_level=PrivacyLevel.STANDARD_CLOUD,
        cost_per_million_input_usd=1.00,
        cost_per_million_output_usd=2.00
    ),

    # 6. GLM (Zhipu AI)
    "glm-4-flash": ModelDescriptor(
        id="glm-4-flash",
        name="GLM-4 Flash (Free Tier)",
        provider="glm",
        is_local=False,
        capabilities=[
            ModelCapability.TEXT,
            ModelCapability.REASONING,
            ModelCapability.CODING,
            ModelCapability.TOOL_CALLING
        ],
        context_window=128000,
        cost_class=CostClass.FREE_TIER,
        latency_class=LatencyClass.FAST,
        privacy_level=PrivacyLevel.STANDARD_CLOUD,
        cost_per_million_input_usd=0.00,
        cost_per_million_output_usd=0.00
    ),

    # 7. Kimi (Moonshot 128k Long Context)
    "moonshot-v1-128k": ModelDescriptor(
        id="moonshot-v1-128k",
        name="Moonshot Kimi (128k Context)",
        provider="kimi",
        is_local=False,
        capabilities=[
            ModelCapability.TEXT,
            ModelCapability.LONG_CONTEXT,
            ModelCapability.REASONING
        ],
        context_window=128000,
        cost_class=CostClass.STANDARD,
        latency_class=LatencyClass.MEDIUM,
        privacy_level=PrivacyLevel.STANDARD_CLOUD,
        cost_per_million_input_usd=0.85,
        cost_per_million_output_usd=0.85
    ),

    # 8. OpenRouter Aggregator
    "openrouter/auto": ModelDescriptor(
        id="openrouter/auto",
        name="OpenRouter Intelligent Auto-Router",
        provider="openrouter",
        is_local=False,
        capabilities=[
            ModelCapability.TEXT,
            ModelCapability.REASONING,
            ModelCapability.CODING,
            ModelCapability.TOOL_CALLING
        ],
        context_window=128000,
        cost_class=CostClass.LOW_COST,
        latency_class=LatencyClass.FAST,
        privacy_level=PrivacyLevel.STANDARD_CLOUD,
        cost_per_million_input_usd=0.40,
        cost_per_million_output_usd=0.80
    )
}


class ModelRegistry:
    @staticmethod
    def list_models(
        provider: Optional[str] = None,
        capability: Optional[ModelCapability] = None,
        local_only: bool = False
    ) -> List[Dict[str, Any]]:
        models = []
        for m in GLOBAL_MODEL_CATALOG.values():
            if provider and m.provider.lower() != provider.lower():
                continue
            if capability and capability not in m.capabilities:
                continue
            if local_only and not m.is_local:
                continue
            models.append(m.model_dump())
        return models

    @staticmethod
    def get_model(model_id: str) -> Optional[ModelDescriptor]:
        return GLOBAL_MODEL_CATALOG.get(model_id)

    @staticmethod
    def register_custom_model(descriptor: ModelDescriptor) -> None:
        GLOBAL_MODEL_CATALOG[descriptor.id] = descriptor
        logger.info(f"Registered custom model: {descriptor.id} ({descriptor.provider})")

    @staticmethod
    def set_availability(model_id: str, available: bool) -> None:
        if model_id in GLOBAL_MODEL_CATALOG:
            GLOBAL_MODEL_CATALOG[model_id].availability = available
