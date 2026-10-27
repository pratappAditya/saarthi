"""
GLM (Zhipu AI) Model Provider Adapter for Saarthi.
Supports GLM-4 series including GLM-4-Flash and GLM-4-Plus.
"""

from app.models.providers.http_base import OpenAICompatibleHTTPProvider
from app.config.settings import settings


class GLMProvider(OpenAICompatibleHTTPProvider):
    def __init__(
        self,
        model_name: str = "glm-4-flash",
        api_key: str = None,
        base_url: str = None,
        **kwargs
    ):
        super().__init__(
            model_name=model_name,
            provider_name="glm",
            api_key=api_key or settings.GLM_API_KEY,
            base_url=base_url or settings.GLM_BASE_URL,
            cost_per_million_input_usd=0.01,
            cost_per_million_output_usd=0.01,
            **kwargs
        )
