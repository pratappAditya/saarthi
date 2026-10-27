import json
import time
from typing import List, Dict, Any, Optional, AsyncGenerator
from app.models.base import ModelProvider
from app.models.schema import ModelResponse, TokenUsage


class MockModelProvider(ModelProvider):
    def __init__(self, model_name: str = "mock-model"):
        self.model_name = model_name
        self.provider_name = "mock"

    async def generate_response(self, prompt: str, history: List[Dict[str, str]] = None, system_prompt: str = None, **kwargs) -> str:
        history = history or []
        
        # Check if latest history message is a tool result
        last_msg = history[-1].get("message", history[-1].get("content", "")) if history else ""
        user_query = ""
        for msg in reversed(history):
            sender = msg.get("sender", msg.get("role"))
            m_text = msg.get("message", msg.get("content", ""))
            if sender in ("user", "human") and "tool_result" not in m_text:
                try:
                    data = json.loads(m_text)
                    user_query = data.get("content", m_text)
                except Exception:
                    user_query = m_text
                break
        if not user_query:
            user_query = prompt
        
        query_lower = user_query.lower()

        # If returning from tool result
        if "tool_result" in last_msg or "file_list" in last_msg or "system_info" in last_msg or "suggest_memory" in last_msg:
            if "file_list" in last_msg:
                return "I have scanned the project workspace. The repository contains `README.md`, `SaarthiDesktop.py`, `backend/`, `frontend/`, `data/`, and `docs/`."
            elif "system_info" in last_msg:
                return "System hardware status retrieved:\n- OS: Windows 11 (AMD64)\n- Python Runtime: 3.14.6\n- Subsystem Status: Operational."
            elif "suggest_memory" in last_msg:
                return "I have stored your workflow preference into your persistent SQLite memory store."
            return "Tool action executed successfully. Here is the processed result for your workflow."

        # Trigger tool call if requested
        if any(w in query_lower for w in ["list", "file", "workspace", "dir", "folder"]):
            return (
                "I will inspect the workspace files now.\n"
                "[TOOL_CALL]\n"
                '{"tool": "file_list", "arguments": {"directory_path": "."}}\n'
                "[/TOOL_CALL]"
            )
        elif any(w in query_lower for w in ["system", "info", "spec", "hardware", "cpu"]):
            return (
                "I will retrieve your system specifications now.\n"
                "[TOOL_CALL]\n"
                '{"tool": "system_info", "arguments": {}}\n'
                "[/TOOL_CALL]"
            )
        elif any(w in query_lower for w in ["remember", "memory", "prefer", "store"]):
            return (
                "I will save this preference to your local memory store.\n"
                "[TOOL_CALL]\n"
                '{"tool": "suggest_memory", "arguments": {"category": "USER", "key": "user_preference", "content": "Prefers concise automated workflow summaries."}}\n'
                "[/TOOL_CALL]"
            )

        return (
            "Mock response: Hello! I am Saarthi, an AI Assistant for Workflows operating at TRL 3 (Proof of Concept). "
            "I can help you manage local workstation files, execute tool workflows, run hardware diagnostics, "
            "and persist context safely in your local SQLite memory store."
        )

    async def generate_model_response(
        self,
        prompt: str,
        history: List[Dict[str, str]] = None,
        system_prompt: str = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        json_schema: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> ModelResponse:
        start_time = time.time()
        text = await self.generate_response(prompt, history=history, system_prompt=system_prompt, **kwargs)
        duration_ms = (time.time() - start_time) * 1000.0

        # Parse tool calls if [TOOL_CALL] block is present
        tool_calls = None
        if "[TOOL_CALL]" in text and "[/TOOL_CALL]" in text:
            try:
                tc_raw = text.split("[TOOL_CALL]")[1].split("[/TOOL_CALL]")[0].strip()
                tc_data = json.loads(tc_raw)
                tool_calls = [{
                    "id": "mock_call_1",
                    "name": tc_data.get("tool"),
                    "arguments": tc_data.get("arguments", {})
                }]
            except Exception:
                pass

        # Structured output if requested
        structured_data = None
        if json_schema:
            structured_data = {"status": "mock_structured_success", "query": prompt, "schema_satisfied": True}

        return ModelResponse(
            content=text,
            tool_calls=tool_calls,
            structured_data=structured_data,
            model_id=self.model_name,
            provider="mock",
            usage=TokenUsage(
                prompt_tokens=max(1, len(prompt) // 4),
                completion_tokens=max(1, len(text) // 4),
                total_tokens=max(2, (len(prompt) + len(text)) // 4)
            ),
            latency_ms=round(duration_ms, 2),
            cost_estimate_usd=0.0
        )

    async def generate_stream(
        self,
        prompt: str,
        history: List[Dict[str, str]] = None,
        system_prompt: str = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        response = await self.generate_response(prompt, history=history, system_prompt=system_prompt, **kwargs)
        words = response.split(" ")
        for i, word in enumerate(words):
            yield word + (" " if i < len(words) - 1 else "")

    async def health_check(self) -> bool:
        return True
