import logging
from app.models.base import ModelProvider
from app.models.mock import MockModelProvider
from app.models.nemotron_service import NemotronService
from app.config.settings import settings

logger = logging.getLogger("app.models.factory")


class ModelFactory:
    @staticmethod
    def create_provider(provider_name: str, model_name: str = None, **kwargs) -> ModelProvider:
        p_name = (provider_name or "").lower()
        m_name = model_name or settings.MODEL_NAME

        if p_name in ("mock", "demo"):
            return MockModelProvider(model_name=m_name or "demo-model")
        elif p_name in ("none", "", "unavailable"):
            from app.models.schema import ModelUnavailableError
            raise ModelUnavailableError(
                "No AI model provider is configured. Live inference is unavailable.",
                provider="none",
                model_id=""
            )
        elif p_name == "ollama":
            service = NemotronService(model_name=m_name)
            return service.provider
        elif p_name == "qwen":
            from app.models.providers.qwen import QwenProvider
            return QwenProvider(model_name=m_name or "qwen-2.5-72b-instruct", **kwargs)
        elif p_name == "deepseek":
            from app.models.providers.deepseek import DeepSeekProvider
            return DeepSeekProvider(model_name=m_name or "deepseek-chat", **kwargs)
        elif p_name == "groq":
            from app.models.providers.groq import GroqProvider
            return GroqProvider(model_name=m_name or "llama-3.3-70b-versatile", **kwargs)
        elif p_name == "openrouter":
            from app.models.providers.openrouter import OpenRouterProvider
            return OpenRouterProvider(model_name=m_name or "openrouter/auto", **kwargs)
        elif p_name == "glm":
            from app.models.providers.glm import GLMProvider
            return GLMProvider(model_name=m_name or "glm-4-flash", **kwargs)
        elif p_name == "kimi":
            from app.models.providers.kimi import KimiProvider
            return KimiProvider(model_name=m_name or "moonshot-v1-128k", **kwargs)
        elif p_name == "minimax":
            from app.models.providers.minimax import MiniMaxProvider
            return MiniMaxProvider(model_name=m_name or "abab6.5s-chat", **kwargs)
        elif p_name == "llama":
            from app.models.providers.llama import LlamaProvider
            return LlamaProvider(model_name=m_name or "meta-llama-3.3-70b-instruct", **kwargs)
        else:
            is_staging_or_prod = getattr(settings, "ENVIRONMENT", "").lower() in ("staging", "production")
            if is_staging_or_prod:
                from app.models.schema import ModelUnavailableError
                raise ModelUnavailableError(
                    f"Unknown model provider requested: '{p_name}'. Silent fallback to mock is strictly prohibited in {settings.ENVIRONMENT}.",
                    provider=p_name,
                    model_id=m_name
                )
            logger.warning(f"Unknown model provider requested: {p_name}. Falling back to MockModelProvider for local testing.")
            return MockModelProvider(model_name=m_name)

    @staticmethod
    def get_provider() -> ModelProvider:
        provider_name = (settings.MODEL_PROVIDER or "").lower().strip()
        if not provider_name or provider_name in ("none", "unavailable"):
            from app.models.schema import ModelUnavailableError
            raise ModelUnavailableError(
                "No active AI model provider configured. Set MODEL_PROVIDER in environment.",
                provider="none"
            )
        return ModelFactory.create_provider(provider_name=provider_name, model_name=settings.MODEL_NAME)
