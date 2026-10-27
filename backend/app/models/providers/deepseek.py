"""
DeepSeek Model Provider Adapter for Saarthi.
Supports DeepSeek-V3 (deepseek-chat) and DeepSeek-R1 (deepseek-reasoner).
Extracts or strips reasoning chains based on request configuration.
"""

import re
from typing import List, Dict, Optional, Any
from app.models.providers.http_base import OpenAICompatibleHTTPProvider
from app.models.schema import ModelResponse
from app.config.settings import settings


class DeepSeekProvider(OpenAICompatibleHTTPProvider):
    def __init__(
        self,
        model_name: str = "deepseek-chat",
        api_key: str = None,
        base_url: str = None,
        strip_reasoning: bool = False,
        **kwargs
    ):
        super().__init__(
            model_name=model_name,
            provider_name="deepseek",
            api_key=api_key or settings.DEEPSEEK_API_KEY,
            base_url=base_url or settings.DEEPSEEK_BASE_URL,
            cost_per_million_input_usd=0.14,
            cost_per_million_output_usd=0.28,
            **kwargs
        )
        self.strip_reasoning = strip_reasoning

    async def generate_model_response(
        self,
        prompt: str,
        history: List[Dict[str, str]] = None,
        system_prompt: str = None,
        **kwargs
    ) -> ModelResponse:
        resp = await super().generate_model_response(prompt, history=history, system_prompt=system_prompt, **kwargs)
        if self.strip_reasoning and resp.content:
            cleaned = re.sub(r'<(think|thinking)>.*?</\1>', '', resp.content, flags=re.DOTALL | re.IGNORECASE).strip()
            resp.content = cleaned
        return resp
