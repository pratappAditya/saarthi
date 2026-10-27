import httpx
import time
import logging
import re
from typing import List, Dict, Optional
from app.models.base import ModelProvider
from app.config.settings import settings

def clean_reasoning(text: str) -> str:
    if not text:
        return ""
    # Strip <think>...</think> and <thinking>...</thinking> blocks
    cleaned = re.sub(r'<(think|thinking)>.*?</\1>', '', text, flags=re.DOTALL | re.IGNORECASE)
    # Strip "Thinking..." to "...done thinking." blocks
    cleaned = re.sub(r'Thinking\.\.\..*?\.\.\.done thinking\.', '', cleaned, flags=re.DOTALL | re.IGNORECASE)
    # Handle unclosed tags at the end of text
    for tag in ["<think>", "<thinking>"]:
        idx = cleaned.lower().find(tag)
        if idx != -1:
            cleaned = cleaned[:idx]
    return cleaned.strip()

logger = logging.getLogger("app.models.ollama")

class NemotronProvider(ModelProvider):
    def __init__(
        self,
        model_name: str = None,
        base_url: str = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ):
        self.model_name = model_name or settings.MODEL_NAME
        resolved_url = base_url or settings.OLLAMA_BASE_URL
        import os
        if os.path.exists("/.dockerenv") and any(h in resolved_url for h in ("127.0.0.1", "localhost")):
            host_candidate = os.getenv("OLLAMA_HOST_URL", "http://host.docker.internal:11434")
            logger.info(f"Container environment detected: resolving Ollama host gateway at {host_candidate}")
            resolved_url = host_candidate
        self.base_url = resolved_url
        self.provider_name = "ollama"
        self.temperature = temperature if temperature is not None else settings.MODEL_TEMPERATURE
        self.max_tokens = max_tokens if max_tokens is not None else settings.MODEL_MAX_TOKENS

    async def generate_response(self, prompt: str, history: List[Dict[str, str]] = None, system_prompt: str = None) -> str:
        # Use provided system prompt or fallback to default
        system_content = system_prompt if system_prompt else (
            "You are Saarthi, a personal AI agent currently being developed by your user. "
            "You are currently in an early development stage. You must not pretend to have "
            "abilities that you do not yet have. For example, you cannot execute commands, "
            "open files, browse the web, or control the computer, as those capabilities are not yet enabled."
        )
        
        messages = [{"role": "system", "content": system_content}]
        
        # Calculate sizes for system prompt
        system_chars = len(system_content)
        system_tokens = system_chars // 4
        
        history_chars = 0
        history_tokens = 0
        
        # Convert history format {"sender": "user"|"assistant", "message": "..."} to Ollama format {"role": "...", "content": "..."}
        if history:
            limit_msgs = settings.MAX_HISTORY_MESSAGES
            max_chars = settings.MAX_HISTORY_CHARS
            
            # Select most recent messages
            limited_history = history[-limit_msgs:]
            
            # Limit characters starting from the most recent
            selected_msgs = []
            current_chars = 0
            for msg in reversed(limited_history):
                content = msg.get("message", "")
                if current_chars + len(content) <= max_chars:
                    selected_msgs.append(msg)
                    current_chars += len(content)
                else:
                    break
            selected_msgs.reverse()
            
            for msg in selected_msgs:
                role = "user" if msg.get("sender") == "user" else "assistant"
                content_str = msg.get("message", "")
                messages.append({"role": role, "content": content_str})
                history_chars += len(content_str)
            
            history_tokens = history_chars // 4
        else:
            messages.append({"role": "user", "content": prompt})
            history_chars = len(prompt)
            history_tokens = history_chars // 4

        total_prompt_chars = system_chars + history_chars
        total_prompt_tokens = total_prompt_chars // 4
        
        start_time = time.time()

        # Request payload
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "think": settings.OLLAMA_THINK,
            "options": {}
        }
        
        payload["options"]["num_ctx"] = 4096
        if self.temperature is not None:
            payload["options"]["temperature"] = self.temperature
        if self.max_tokens is not None:
            payload["options"]["num_predict"] = self.max_tokens

        try:
            # Set a generous timeout (e.g., 180 seconds) for local CPU inference
            timeout = httpx.Timeout(180.0, connect=5.0)
            async with httpx.AsyncClient(timeout=timeout) as client:
                url = f"{self.base_url.rstrip('/')}/api/chat"
                response = await client.post(url, json=payload)
                
                # Check for HTTP status errors
                if response.status_code == 404:
                    raise RuntimeError(
                        f"Model '{self.model_name}' was not found. Please pull it first using 'ollama pull {self.model_name}'."
                    )
                elif response.status_code != 200:
                    try:
                        err_detail = response.json().get("error", response.text)
                    except Exception:
                        err_detail = response.text
                    raise RuntimeError(f"Ollama returned error status {response.status_code}: {err_detail}")
                
                try:
                    result_json = response.json()
                except Exception as e:
                    raise RuntimeError(f"Failed to parse JSON response from local model: {str(e)}")
                
                if not isinstance(result_json, dict):
                    raise RuntimeError("Ollama response was not a JSON object.")
                
                message_content = result_json.get("message", {}).get("content", "")
                if not message_content:
                    # Fallback to thinking trace if main content is empty
                    message_content = result_json.get("message", {}).get("thinking", "")
                    
                if not message_content:
                    raise RuntimeError("Received empty response from local model.")
                
                return clean_reasoning(message_content)
                
        except (httpx.ConnectError, httpx.ConnectTimeout) as e:
            raise ConnectionError(
                f"Cannot connect to Ollama service at {self.base_url}. Please ensure the Ollama service is running. Details: {str(e)}"
            )
        except httpx.TimeoutException as e:
            raise TimeoutError(f"Ollama request timed out. Details: {str(e)}")
        except Exception as e:
            if not isinstance(e, (ConnectionError, TimeoutError, RuntimeError)):
                raise RuntimeError(f"Unexpected error communicating with local LLM: {str(e)}")
            raise e
