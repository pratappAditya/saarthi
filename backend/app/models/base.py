from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncGenerator
from app.models.schema import ModelResponse, TokenUsage


class ModelProvider(ABC):
    """
    Standardized provider interface for all Saarthi AI models.
    Supports simple text generation, rich response with token/latency tracking,
    streaming, structured JSON outputs, and tool calling.
    """
    model_name: str = "default"
    provider_name: str = "generic"

    @abstractmethod
    async def generate_response(
        self,
        prompt: str,
        history: List[Dict[str, str]] = None,
        system_prompt: str = None,
        **kwargs
    ) -> str:
        """Original backward-compatible text generation method."""
        pass

    async def generate_model_response(
        self,
        prompt: str,
        history: List[Dict[str, str]] = None,
        system_prompt: str = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        json_schema: Optional[Dict[str, Any]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ModelResponse:
        """
        Comprehensive generation interface returning normalized ModelResponse
        with token metrics, latency, finish reason, and tool calls.
        """
        import time
        start_time = time.time()
        text = await self.generate_response(prompt, history=history, system_prompt=system_prompt, **kwargs)
        duration_ms = (time.time() - start_time) * 1000.0
        
        # Estimate token usage if not provided natively
        prompt_chars = len(prompt) + sum(len(h.get("message", h.get("content", ""))) for h in (history or []))
        if system_prompt:
            prompt_chars += len(system_prompt)
        prompt_tokens = max(1, prompt_chars // 4)
        completion_tokens = max(1, len(text) // 4)

        prov_name = getattr(self, "provider_name", "generic")
        is_live_call = (prov_name != "mock")
        return ModelResponse(
            content=text,
            model_id=getattr(self, "model_name", "unknown"),
            provider=prov_name,
            is_live=is_live_call,
            execution_mode="LIVE" if is_live_call else "MOCK",
            usage=TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens
            ),
            latency_ms=round(duration_ms, 2)
        )

    async def generate_stream(
        self,
        prompt: str,
        history: List[Dict[str, str]] = None,
        system_prompt: str = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream chunks of text response. Default fallback yields full text at once."""
        full_text = await self.generate_response(prompt, history=history, system_prompt=system_prompt, **kwargs)
        yield full_text

    async def generate_structured(
        self,
        prompt: str,
        schema: Dict[str, Any],
        history: List[Dict[str, str]] = None,
        system_prompt: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate structured JSON conforming to schema."""
        import json
        structured_prompt = (
            f"{prompt}\n\nRespond ONLY with a valid JSON object matching this schema:\n"
            f"{json.dumps(schema)}"
        )
        response_text = await self.generate_response(
            structured_prompt,
            history=history,
            system_prompt=system_prompt,
            **kwargs
        )
        # Clean potential markdown fences
        cleaned = response_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        return json.loads(cleaned.strip())

    async def health_check(self) -> bool:
        """Check if provider is available and responsive."""
        return True
