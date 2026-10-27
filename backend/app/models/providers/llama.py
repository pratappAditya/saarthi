"""
Meta Llama Model Provider Adapter for Saarthi.
Can connect to any self-hosted or endpoint-served Meta Llama 3 / 3.3 instance.
"""

from app.models.providers.http_base import OpenAICompatibleHTTPProvider
from app.config.settings import settings


class LlamaProvider(OpenAICompatibleHTTPProvider):
    def __init__(
        self,
        model_name: str = "meta-llama-3.3-70b-instruct",
        api_key: str = None,
        base_url: str = None,
        **kwargs
    ):
        super().__init__(
            model_name=model_name,
            provider_name="llama",
            api_key=api_key or settings.LLAMA_API_KEY,
            base_url=base_url or settings.LLAMA_BASE_URL or "http://127.0.0.1:8000/v1",
            cost_per_million_input_usd=0.20,
            cost_per_million_output_usd=0.40,
            **kwargs
        )
