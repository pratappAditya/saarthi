"""
OpenRouter Model Provider Adapter for Saarthi.
Routes across multiple models and handles unified API aggregation.
"""

from app.models.providers.http_base import OpenAICompatibleHTTPProvider
from app.config.settings import settings


class OpenRouterProvider(OpenAICompatibleHTTPProvider):
    def __init__(
        self,
        model_name: str = "meta-llama/llama-3.3-70b-instruct",
        api_key: str = None,
        base_url: str = None,
        **kwargs
    ):
        super().__init__(
            model_name=model_name,
            provider_name="openrouter",
            api_key=api_key or settings.OPENROUTER_API_KEY,
            base_url=base_url or settings.OPENROUTER_BASE_URL,
            cost_per_million_input_usd=0.40,
            cost_per_million_output_usd=0.80,
            **kwargs
        )

    def _get_headers(self):
        headers = super()._get_headers()
        headers["HTTP-Referer"] = "https://saarthi.trovanetech.com"
        headers["X-Title"] = "Saarthi AI Companion"
        return headers
