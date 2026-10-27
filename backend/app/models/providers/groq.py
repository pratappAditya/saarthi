"""
Groq Model Provider Adapter for Saarthi.
Provides ultra-low latency inference for Meta Llama and Mistral models.
"""

from app.models.providers.http_base import OpenAICompatibleHTTPProvider
from app.config.settings import settings


class GroqProvider(OpenAICompatibleHTTPProvider):
    def __init__(
        self,
        model_name: str = "llama-3.3-70b-versatile",
        api_key: str = None,
        base_url: str = None,
        **kwargs
    ):
        super().__init__(
            model_name=model_name,
            provider_name="groq",
            api_key=api_key or settings.GROQ_API_KEY,
            base_url=base_url or settings.GROQ_BASE_URL,
            cost_per_million_input_usd=0.59,
            cost_per_million_output_usd=0.79,
            **kwargs
        )
