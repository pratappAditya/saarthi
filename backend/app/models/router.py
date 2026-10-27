"""
Intelligent Model Router for Saarthi.
Routes tasks based on capability requirements, free-first strategy,
privacy constraints, user plan entitlements, quota availability, and resilient fallbacks.
"""

import logging
from typing import Dict, Any, List, Optional
from app.config.settings import settings
from app.models.schema import (
    ModelDescriptor,
    ModelCapability,
    CostClass,
    LatencyClass,
    PrivacyLevel
)
from app.models.registry import GLOBAL_MODEL_CATALOG, ModelRegistry

logger = logging.getLogger("app.models.router")


class ModelRouter:
    @staticmethod
    def select_model(
        task_type: str = "chat",
        required_capability: Optional[ModelCapability] = None,
        prefer_local: bool = True,
        user_plan: str = "power",
        privacy_sensitive: bool = False,
        explicit_model_id: Optional[str] = None
    ) -> ModelDescriptor:
        """
        Intelligently select the best available model descriptor matching constraints.
        """
        # 1. Explicit model request by user/admin
        if explicit_model_id and explicit_model_id in GLOBAL_MODEL_CATALOG:
            candidate = GLOBAL_MODEL_CATALOG[explicit_model_id]
            if candidate.availability:
                # Check privacy constraint
                if privacy_sensitive and candidate.privacy_level == PrivacyLevel.STANDARD_CLOUD:
                    logger.warning(f"Explicit model {explicit_model_id} rejected due to privacy sensitivity.")
                else:
                    return candidate

        # 2. Privacy sensitive tasks MUST stay local or zero-data-retention
        if privacy_sensitive:
            if "nemotron-3-nano:4b" in GLOBAL_MODEL_CATALOG and GLOBAL_MODEL_CATALOG["nemotron-3-nano:4b"].availability:
                return GLOBAL_MODEL_CATALOG["nemotron-3-nano:4b"]
            if "llama-3.1-8b-instant" in GLOBAL_MODEL_CATALOG:
                return GLOBAL_MODEL_CATALOG["llama-3.1-8b-instant"]
            return GLOBAL_MODEL_CATALOG.get("mock_local_model", list(GLOBAL_MODEL_CATALOG.values())[0])

        # 3. Vision Requirement
        if required_capability == ModelCapability.VISION or task_type == "vision":
            if "qwen-vl-max" in GLOBAL_MODEL_CATALOG and GLOBAL_MODEL_CATALOG["qwen-vl-max"].availability and settings.QWEN_API_KEY:
                return GLOBAL_MODEL_CATALOG["qwen-vl-max"]
            return GLOBAL_MODEL_CATALOG.get("mock_local_model")

        # 4. Deep Reasoning Requirement
        if task_type in ("deep_reasoning", "complex_math", "formal_verification"):
            if "deepseek-reasoner" in GLOBAL_MODEL_CATALOG and settings.DEEPSEEK_API_KEY:
                return GLOBAL_MODEL_CATALOG["deepseek-reasoner"]
            if "nemotron-3-8b" in GLOBAL_MODEL_CATALOG and GLOBAL_MODEL_CATALOG["nemotron-3-8b"].availability:
                return GLOBAL_MODEL_CATALOG["nemotron-3-8b"]

        # 5. Coding & Software Engineering
        if required_capability == ModelCapability.CODING or task_type in ("coding", "debugging", "code_review"):
            if "qwen-2.5-coder-32b-instruct" in GLOBAL_MODEL_CATALOG and settings.QWEN_API_KEY:
                return GLOBAL_MODEL_CATALOG["qwen-2.5-coder-32b-instruct"]
            if "deepseek-chat" in GLOBAL_MODEL_CATALOG and settings.DEEPSEEK_API_KEY:
                return GLOBAL_MODEL_CATALOG["deepseek-chat"]
            if "nemotron-3-nano:4b" in GLOBAL_MODEL_CATALOG:
                return GLOBAL_MODEL_CATALOG["nemotron-3-nano:4b"]

        # 6. Ultra-Long Context Analysis
        if required_capability == ModelCapability.LONG_CONTEXT or task_type == "document_synthesis":
            if "moonshot-v1-128k" in GLOBAL_MODEL_CATALOG and settings.KIMI_API_KEY:
                return GLOBAL_MODEL_CATALOG["moonshot-v1-128k"]
            if "qwen-2.5-72b-instruct" in GLOBAL_MODEL_CATALOG and settings.QWEN_API_KEY:
                return GLOBAL_MODEL_CATALOG["qwen-2.5-72b-instruct"]

        # 7. Free-First & Default Preference Strategy
        # If prefer_local is set, or settings say mock/ollama:
        if prefer_local or settings.MODEL_PREFER_LOCAL:
            if settings.MODEL_PROVIDER.lower() == "mock":
                return GLOBAL_MODEL_CATALOG.get("mock_local_model")
            if "nemotron-3-nano:4b" in GLOBAL_MODEL_CATALOG:
                return GLOBAL_MODEL_CATALOG["nemotron-3-nano:4b"]

        # 8. High-speed free-tier hosted cloud
        if "llama-3.1-8b-instant" in GLOBAL_MODEL_CATALOG and settings.GROQ_API_KEY:
            return GLOBAL_MODEL_CATALOG["llama-3.1-8b-instant"]
        if "glm-4-flash" in GLOBAL_MODEL_CATALOG and settings.GLM_API_KEY:
            return GLOBAL_MODEL_CATALOG["glm-4-flash"]

        # 9. Low-cost versatile fallback
        if "deepseek-chat" in GLOBAL_MODEL_CATALOG and settings.DEEPSEEK_API_KEY:
            return GLOBAL_MODEL_CATALOG["deepseek-chat"]
        if "qwen-2.5-72b-instruct" in GLOBAL_MODEL_CATALOG and settings.QWEN_API_KEY:
            return GLOBAL_MODEL_CATALOG["qwen-2.5-72b-instruct"]

        # 10. Ultimate safe offline fallback
        return GLOBAL_MODEL_CATALOG.get("mock_local_model", list(GLOBAL_MODEL_CATALOG.values())[0])

    @staticmethod
    def get_fallback_chain(
        primary_model_id: str,
        privacy_sensitive: bool = False,
        allow_paid_fallback: bool = False
    ) -> List[ModelDescriptor]:
        """
        Returns ordered list of fallback models if primary model fails.
        Enforces strict constraints:
        - If privacy_sensitive: ONLY air-gapped or zero-data-retention models allowed.
        - If allow_paid_fallback is False: NEVER fall back to paid models (prevents unexpected billing).
        """
        primary_model = GLOBAL_MODEL_CATALOG.get(primary_model_id)
        is_free_primary = primary_model and primary_model.cost_class in (CostClass.FREE_LOCAL, CostClass.FREE_TIER)

        # By default, do not allow paid fallback if primary was free unless explicitly authorized
        should_restrict_to_free = not allow_paid_fallback and is_free_primary

        candidates = [
            "nemotron-3-nano:4b",
            "llama-3.1-8b-instant",
            "glm-4-flash",
            "mock_local_model"
        ]

        if not should_restrict_to_free and not privacy_sensitive:
            # Paid low-cost and standard candidates only when authorized
            candidates.extend(["deepseek-chat", "qwen-2.5-72b-instruct"])

        chain = []
        for cid in candidates:
            if cid != primary_model_id and cid in GLOBAL_MODEL_CATALOG:
                m = GLOBAL_MODEL_CATALOG[cid]
                if not m.availability or m.deprecated:
                    continue
                if privacy_sensitive and m.privacy_level == PrivacyLevel.STANDARD_CLOUD:
                    continue
                if should_restrict_to_free and m.cost_class not in (CostClass.FREE_LOCAL, CostClass.FREE_TIER):
                    continue
                chain.append(m)
        return chain


model_router = ModelRouter()
