"""
Qwen Model Provider Adapter for Saarthi.
Connects to Alibaba Cloud DashScope / OpenAI compatible endpoint for Qwen 2.5 series.
"""

from app.models.providers.http_base import OpenAICompatibleHTTPProvider
from app.config.settings import settings


class QwenProvider(OpenAICompatibleHTTPProvider):
    def __init__(
        self,
        model_name: str = "qwen-2.5-72b-instruct",
        api_key: str = None,
        base_url: str = None,
        **kwargs
    ):
        super().__init__(
            model_name=model_name,
            provider_name="qwen",
            api_key=api_key or settings.QWEN_API_KEY,
            base_url=base_url or settings.QWEN_BASE_URL,
            cost_per_million_input_usd=0.40,
            cost_per_million_output_usd=1.20,
            **kwargs
        )
