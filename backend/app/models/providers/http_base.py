"""
Generic OpenAI-Compatible Async HTTP Model Provider for Saarthi.
Provides streaming, structured JSON output, tool calling, token metrics,
bounded exponential-backoff retries, and standardized error normalization.
"""

import json
import time
import asyncio
import logging
from typing import List, Dict, Any, Optional, AsyncGenerator
import httpx

from app.models.base import ModelProvider
from app.models.schema import (
    ModelResponse,
    TokenUsage,
    ModelProviderError,
    RateLimitError,
    AuthenticationError,
    ContextLengthError,
    ModelUnavailableError
)

logger = logging.getLogger("app.models.http_base")


class OpenAICompatibleHTTPProvider(ModelProvider):
    def __init__(
        self,
        model_name: str,
        provider_name: str,
        api_key: str,
        base_url: str,
        timeout: float = 30.0,
        max_retries: int = 2,
        cost_per_million_input_usd: float = 0.0,
        cost_per_million_output_usd: float = 0.0
    ):
        self.model_name = model_name
        self.provider_name = provider_name
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.cost_per_million_input_usd = cost_per_million_input_usd
        self.cost_per_million_output_usd = cost_per_million_output_usd

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Saarthi-AI-Companion/1.0"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _normalize_messages(
        self,
        prompt: str,
        history: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None
    ) -> List[Dict[str, str]]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if history:
            for msg in history:
                role = msg.get("role") or ("user" if msg.get("sender") == "user" else "assistant")
                content = msg.get("content") or msg.get("message", "")
                messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": prompt})
        return messages

    def _handle_http_error(self, response: httpx.Response, exc: Optional[Exception] = None):
        status_code = response.status_code if response is not None else 0
        error_msg = response.text if response is not None else str(exc)
        
        if status_code in (401, 403):
            raise AuthenticationError(f"[{self.provider_name}] Authentication failed: {error_msg}", provider=self.provider_name, model_id=self.model_name)
        elif status_code == 429:
            raise RateLimitError(f"[{self.provider_name}] Rate limit exceeded: {error_msg}", provider=self.provider_name, model_id=self.model_name)
        elif status_code == 400 and ("context" in error_msg.lower() or "token" in error_msg.lower()):
            raise ContextLengthError(f"[{self.provider_name}] Context length exceeded: {error_msg}", provider=self.provider_name, model_id=self.model_name)
        elif status_code >= 500:
            raise ModelUnavailableError(f"[{self.provider_name}] Service unavailable (HTTP {status_code}): {error_msg}", provider=self.provider_name, model_id=self.model_name)
        else:
            raise ModelProviderError(f"[{self.provider_name}] Request failed ({status_code}): {error_msg}", provider=self.provider_name, model_id=self.model_name)

    async def generate_response(
        self,
        prompt: str,
        history: List[Dict[str, str]] = None,
        system_prompt: str = None,
        **kwargs
    ) -> str:
        response = await self.generate_model_response(
            prompt,
            history=history,
            system_prompt=system_prompt,
            **kwargs
        )
        return response.content

    async def generate_model_response(
        self,
        prompt: str,
        history: List[Dict[str, str]] = None,
        system_prompt: str = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        json_schema: Optional[Dict[str, Any]] = None,
        temperature: Optional[float] = 0.7,
        max_tokens: Optional[int] = 2048,
        **kwargs
    ) -> ModelResponse:
        messages = self._normalize_messages(prompt, history, system_prompt)
        endpoint = f"{self.base_url}/chat/completions"
        payload: Dict[str, Any] = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        if tools:
            payload["tools"] = tools
        if json_schema:
            payload["response_format"] = {"type": "json_object"}

        start_time = time.time()
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.post(endpoint, json=payload, headers=self._get_headers())
                    if resp.status_code != 200:
                        self._handle_http_error(resp)
                    data = resp.json()
                    
                    choice = data.get("choices", [{}])[0]
                    message = choice.get("message", {})
                    content = message.get("content") or ""
                    finish_reason = choice.get("finish_reason", "stop")
                    raw_tool_calls = message.get("tool_calls")
                    
                    # Parse tool calls if present
                    tool_calls = None
                    if raw_tool_calls:
                        tool_calls = []
                        for tc in raw_tool_calls:
                            fn = tc.get("function", {})
                            tool_calls.append({
                                "id": tc.get("id"),
                                "name": fn.get("name"),
                                "arguments": json.loads(fn.get("arguments", "{}")) if isinstance(fn.get("arguments"), str) else fn.get("arguments", {})
                            })
                    
                    # Token metrics
                    usage_data = data.get("usage", {})
                    prompt_tokens = usage_data.get("prompt_tokens", len(prompt) // 4)
                    completion_tokens = usage_data.get("completion_tokens", len(content) // 4)
                    total_tokens = usage_data.get("total_tokens", prompt_tokens + completion_tokens)
                    
                    duration_ms = (time.time() - start_time) * 1000.0
                    cost = (prompt_tokens * self.cost_per_million_input_usd / 1_000_000.0) + \
                           (completion_tokens * self.cost_per_million_output_usd / 1_000_000.0)

                    # Structured JSON parsing if requested
                    structured_data = None
                    if json_schema and content:
                        try:
                            clean_text = content.strip()
                            if clean_text.startswith("```json"):
                                clean_text = clean_text[7:]
                            if clean_text.startswith("```"):
                                clean_text = clean_text[3:]
                            if clean_text.endswith("```"):
                                clean_text = clean_text[:-3]
                            structured_data = json.loads(clean_text.strip())
                        except Exception as e:
                            logger.warning(f"Could not parse structured output: {e}")

                    return ModelResponse(
                        content=content,
                        tool_calls=tool_calls,
                        structured_data=structured_data,
                        model_id=self.model_name,
                        provider=self.provider_name,
                        is_live=True,
                        execution_mode="LIVE",
                        usage=TokenUsage(
                            prompt_tokens=prompt_tokens,
                            completion_tokens=completion_tokens,
                            total_tokens=total_tokens
                        ),
                        latency_ms=round(duration_ms, 2),
                        cost_estimate_usd=round(cost, 6),
                        finish_reason=finish_reason
                    )

            except RateLimitError as e:
                last_error = e
                if attempt < self.max_retries:
                    wait_time = (2 ** attempt) + 0.5
                    logger.warning(f"Rate limited by {self.provider_name}. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    raise
            except httpx.TimeoutException as e:
                last_error = ModelUnavailableError(f"Timeout connecting to {self.provider_name} after {self.timeout}s", provider=self.provider_name, model_id=self.model_name)
                if attempt < self.max_retries:
                    await asyncio.sleep(1.0)
                else:
                    raise last_error
            except (AuthenticationError, ContextLengthError):
                raise
            except Exception as e:
                last_error = e
                if attempt < self.max_retries:
                    await asyncio.sleep(1.0)
                else:
                    raise ModelProviderError(f"[{self.provider_name}] Communication failed: {str(e)}", provider=self.provider_name, model_id=self.model_name) from e

        if last_error:
            raise last_error
        raise ModelUnavailableError(f"[{self.provider_name}] Exhausted retries", provider=self.provider_name, model_id=self.model_name)

    async def generate_stream(
        self,
        prompt: str,
        history: List[Dict[str, str]] = None,
        system_prompt: str = None,
        temperature: Optional[float] = 0.7,
        max_tokens: Optional[int] = 2048,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        messages = self._normalize_messages(prompt, history, system_prompt)
        endpoint = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream("POST", endpoint, json=payload, headers=self._get_headers()) as stream:
                if stream.status_code != 200:
                    resp_body = await stream.aread()
                    error_msg = resp_body.decode(errors="replace")
                    raise ModelProviderError(f"[{self.provider_name}] Stream error ({stream.status_code}): {error_msg}")
                
                async for line in stream.aiter_lines():
                    if not line:
                        continue
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                            delta = chunk.get("choices", [{}])[0].get("delta", {})
                            content_piece = delta.get("content")
                            if content_piece:
                                yield content_piece
                        except Exception:
                            continue

    async def health_check(self) -> bool:
        """Lightweight endpoint ping or capability check."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/models", headers=self._get_headers())
                return resp.status_code in (200, 401)  # 401 means server is reachable but needs key
        except Exception:
            return False

    async def discover_remote_models(self) -> List[str]:
        """Queries provider /models endpoint to discover live available model IDs."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(f"{self.base_url}/models", headers=self._get_headers())
                if resp.status_code == 200:
                    data = resp.json()
                    models_list = data.get("data", data.get("models", []))
                    return [m.get("id") for m in models_list if isinstance(m, dict) and m.get("id")]
        except Exception as e:
            logger.warning(f"Could not discover models from {self.provider_name}: {e}")
        return []
