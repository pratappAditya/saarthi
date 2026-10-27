"""
Unified Model Gateway for Saarthi.
Provides provider-independent text generation, streaming, structured JSON output,
tool calling, automatic fallback handling, latency and cost tracking, and audit logging.
"""

import time
import logging
from typing import Dict, Any, List, Optional, AsyncGenerator

from app.models.base import ModelProvider
from app.models.schema import (
    ModelResponse,
    ModelDescriptor,
    ModelCapability,
    TokenUsage,
    ModelProviderError
)
from app.models.router import ModelRouter, model_router
from app.models.registry import GLOBAL_MODEL_CATALOG, ModelRegistry
from app.config.settings import settings

logger = logging.getLogger("app.models.gateway")


class ModelGateway:
    def __init__(self):
        self._provider_cache: Dict[str, ModelProvider] = {}
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_estimated_cost_usd = 0.0

    def get_provider_for_descriptor(self, descriptor: ModelDescriptor) -> ModelProvider:
        cache_key = f"{descriptor.provider}:{descriptor.id}"
        if cache_key in self._provider_cache:
            return self._provider_cache[cache_key]

        from app.models.factory import ModelFactory
        provider = ModelFactory.create_provider(
            provider_name=descriptor.provider,
            model_name=descriptor.id
        )
        self._provider_cache[cache_key] = provider
        return provider

    async def generate(
        self,
        prompt: str,
        history: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None,
        task_type: str = "chat",
        required_capability: Optional[ModelCapability] = None,
        prefer_local: bool = True,
        user_plan: str = "power",
        privacy_sensitive: bool = False,
        explicit_model_id: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        json_schema: Optional[Dict[str, Any]] = None,
        temperature: Optional[float] = 0.7,
        max_tokens: Optional[int] = 2048,
        **kwargs
    ) -> ModelResponse:
        """
        Execute generation with intelligent routing and automatic fallback chain.
        """
        # Select target model
        target_model = model_router.select_model(
            task_type=task_type,
            required_capability=required_capability,
            prefer_local=prefer_local,
            user_plan=user_plan,
            privacy_sensitive=privacy_sensitive,
            explicit_model_id=explicit_model_id
        )

        allow_paid = kwargs.get("allow_paid_fallback", False)
        candidates = [target_model] + model_router.get_fallback_chain(
            target_model.id,
            privacy_sensitive=privacy_sensitive,
            allow_paid_fallback=allow_paid
        )
        last_error = None

        for idx, candidate in enumerate(candidates):
            try:
                provider = self.get_provider_for_descriptor(candidate)
                response = await provider.generate_model_response(
                    prompt=prompt,
                    history=history,
                    system_prompt=system_prompt,
                    tools=tools,
                    json_schema=json_schema,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )

                if idx > 0:
                    if response.execution_mode == "LIVE":
                        response.execution_mode = "FALLBACK"
                    elif response.provider == "mock":
                        is_staging_or_prod = getattr(settings, "ENVIRONMENT", "").lower() in ("staging", "production")
                        if is_staging_or_prod:
                            response.execution_mode = "DEMO_FALLBACK"
                            err_str = f"Live model '{candidates[0].id}' failed"
                            if not response.content.startswith("[DEMO RESULT"):
                                response.content = f"[DEMO RESULT / OFFLINE FALLBACK — {err_str}]\n{response.content}"

                # Track metrics
                self.total_prompt_tokens += response.usage.prompt_tokens
                self.total_completion_tokens += response.usage.completion_tokens
                self.total_estimated_cost_usd += response.cost_estimate_usd

                return response

            except Exception as e:
                logger.warning(
                    f"Model {candidate.id} ({candidate.provider}) failed: {e}. Attempting fallback..."
                )
                last_error = e
                continue

        # If all candidates failed, check if demo fallback is explicitly permitted
        is_staging_or_prod = getattr(settings, "ENVIRONMENT", "").lower() in ("staging", "production")
        demo_allowed = getattr(settings, "DEMO_MODE", False) or getattr(settings, "ALLOW_DEMO_FALLBACK", False)

        if is_staging_or_prod and not demo_allowed:
            logger.error(f"All model candidates failed in {settings.ENVIRONMENT}. Refusing silent mock fallback: {last_error}")
            raise ModelProviderError(
                f"All configured AI model candidates failed in {settings.ENVIRONMENT}. "
                f"Silent mock fallback is strictly disabled without explicit DEMO_MODE. Last error: {last_error}",
                provider="gateway",
                retryable=False
            )

        logger.warning(f"All model candidates failed. Engaging explicit demo mode fallback: {last_error}")
        from app.models.mock import MockModelProvider
        mock = MockModelProvider()
        fallback_resp = await mock.generate_model_response(
            prompt=prompt,
            history=history,
            system_prompt=system_prompt,
            tools=tools,
            json_schema=json_schema,
            **kwargs
        )
        fallback_resp.is_live = False
        if is_staging_or_prod:
            fallback_resp.execution_mode = "DEMO_FALLBACK"
            err_msg = str(last_error) if last_error else "Provider unavailable"
            fallback_resp.content = f"[DEMO RESULT / OFFLINE FALLBACK — LIVE PROVIDER UNAVAILABLE: {err_msg}]\n{fallback_resp.content}"
        else:
            fallback_resp.execution_mode = "MOCK"
        return fallback_resp

    async def stream(
        self,
        prompt: str,
        history: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None,
        task_type: str = "chat",
        required_capability: Optional[ModelCapability] = None,
        prefer_local: bool = True,
        user_plan: str = "power",
        explicit_model_id: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream chunks from the routed model."""
        target_model = model_router.select_model(
            task_type=task_type,
            required_capability=required_capability,
            prefer_local=prefer_local,
            user_plan=user_plan,
            explicit_model_id=explicit_model_id
        )
        provider = self.get_provider_for_descriptor(target_model)
        try:
            async for chunk in provider.generate_stream(
                prompt=prompt,
                history=history,
                system_prompt=system_prompt,
                **kwargs
            ):
                yield chunk
        except Exception as e:
            logger.warning(f"Streaming failed on {target_model.id}: {e}.")
            is_staging_or_prod = getattr(settings, "ENVIRONMENT", "").lower() in ("staging", "production")
            demo_allowed = getattr(settings, "DEMO_MODE", False) or getattr(settings, "ALLOW_DEMO_FALLBACK", False)
            if is_staging_or_prod and not demo_allowed:
                raise ModelProviderError(
                    f"Streaming failed on {target_model.id} and mock fallback is prohibited in {settings.ENVIRONMENT}: {e}",
                    provider="gateway"
                )
            from app.models.mock import MockModelProvider
            mock = MockModelProvider()
            async for chunk in mock.generate_stream(prompt, history=history, system_prompt=system_prompt):
                yield chunk

    def get_metrics(self) -> Dict[str, Any]:
        return {
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "total_tokens": self.total_prompt_tokens + self.total_completion_tokens,
            "total_estimated_cost_usd": round(self.total_estimated_cost_usd, 4),
            "cached_providers": list(self._provider_cache.keys())
        }

    async def discover_and_refresh_models(self, provider_name: str) -> List[str]:
        """Discovers live available models from provider and dynamically updates catalogue."""
        from app.models.factory import ModelFactory
        provider = ModelFactory.create_provider(provider_name=provider_name)
        if hasattr(provider, "discover_remote_models"):
            remote_ids = await provider.discover_remote_models()
            for mid in remote_ids:
                if mid not in GLOBAL_MODEL_CATALOG:
                    from app.models.schema import ModelCapability, CostClass, LatencyClass, PrivacyLevel
                    ModelRegistry.register_custom_model(ModelDescriptor(
                        id=mid,
                        name=f"{mid} ({provider_name.capitalize()})",
                        provider=provider_name,
                        capabilities=[ModelCapability.TEXT, ModelCapability.REASONING],
                        cost_class=CostClass.LOW_COST,
                        latency_class=LatencyClass.FAST,
                        privacy_level=PrivacyLevel.STANDARD_CLOUD
                    ))
            return remote_ids
        return []


model_gateway = ModelGateway()
