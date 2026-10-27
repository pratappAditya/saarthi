"""
Kimi (Moonshot AI) Model Provider Adapter for Saarthi.
Specializes in ultra-long context window (128k - 256k tokens).
"""

from app.models.providers.http_base import OpenAICompatibleHTTPProvider
from app.config.settings import settings


class KimiProvider(OpenAICompatibleHTTPProvider):
    def __init__(
        self,
        model_name: str = "moonshot-v1-128k",
        api_key: str = None,
        base_url: str = None,
        **kwargs
    ):
        super().__init__(
            model_name=model_name,
            provider_name="kimi",
            api_key=api_key or settings.KIMI_API_KEY,
            base_url=base_url or settings.KIMI_BASE_URL,
            cost_per_million_input_usd=0.85,
            cost_per_million_output_usd=0.85,
            **kwargs
        )
