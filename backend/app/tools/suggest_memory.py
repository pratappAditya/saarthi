from typing import Dict, Any, Optional
from app.tools.base import BaseTool
from app.security.permissions import PermissionLevel
from app.memory.manager import memory_request_store, MemoryApprovalRequiredException

class SuggestMemoryTool(BaseTool):
    @property
    def name(self) -> str:
        return "suggest_memory"

    @property
    def description(self) -> str:
        return "Suggest a piece of information to remember permanently about the user, a project, or a task. Use this when the user shares useful preference, project, or task information that should be persisted across sessions. The user will be prompted to approve or deny this."

    @property
    def permission_level(self) -> PermissionLevel:
        return PermissionLevel.SAFE

    @property
    def risk_classification(self) -> str:
        return "LOW"

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": ["USER", "PROJECT", "TASK", "SYSTEM"],
                    "description": "The category of the memory (e.g. USER, PROJECT, TASK, SYSTEM)."
                },
                "key": {
                    "type": "string",
                    "description": "A short, snake_case key identifying the topic of this memory (e.g., preferred_language)."
                },
                "content": {
                    "type": "string",
                    "description": "The detailed memory content to store (e.g., Prefers TypeScript for frontend projects)."
                },
                "project_id": {
                    "type": "string",
                    "description": "The project ID/name this memory is associated with. Required if category is PROJECT."
                },
                "question": {
                    "type": "string",
                    "description": "The natural language question to ask the user to approve the memory (e.g., Would you like me to remember that you prefer TypeScript for frontend projects?)."
                }
            },
            "required": ["category", "key", "content"]
        }

    @property
    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "request_id": {"type": "string"}
            }
        }

    @property
    def is_synchronous(self) -> bool:
        return True

    async def execute(self, **kwargs) -> Any:
        import asyncio
        return await asyncio.to_thread(self._execute_sync, **kwargs)

    def _execute_sync(self, **kwargs) -> Any:
        category = kwargs.get("category")
        key = kwargs.get("key")
        content = kwargs.get("content")
        project_id = kwargs.get("project_id")
        question = kwargs.get("question")
        session_id = kwargs.get("session_id", "default_session")

        # Create a pending memory request
        req = memory_request_store.create_request(
            category=category,
            key=key,
            content=content,
            project_id=project_id,
            session_id=session_id,
            question=question
        )

        raise MemoryApprovalRequiredException(req)

