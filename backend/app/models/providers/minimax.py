"""
MiniMax Model Provider Adapter for Saarthi.
"""

from app.models.providers.http_base import OpenAICompatibleHTTPProvider
from app.config.settings import settings


class MiniMaxProvider(OpenAICompatibleHTTPProvider):
    def __init__(
        self,
        model_name: str = "abab6.5s-chat",
        api_key: str = None,
        base_url: str = None,
        **kwargs
    ):
        super().__init__(
            model_name=model_name,
            provider_name="minimax",
            api_key=api_key or settings.MINIMAX_API_KEY,
            base_url=base_url or settings.MINIMAX_BASE_URL,
            cost_per_million_input_usd=0.30,
            cost_per_million_output_usd=0.60,
            **kwargs
        )
