import os
import uuid
import datetime
from typing import Dict, Any, List, Optional
from app.config.settings import settings
from app.memory.base_store import BaseMemoryStore
from app.memory.sqlite_store import SQLiteMemoryStore

class MemoryManager:
    def __init__(self, store: BaseMemoryStore):
        self.store = store

    def create_memory(
        self,
        category: str,
        key: str,
        content: str,
        project_id: Optional[str] = None,
        importance: int = 0,
        source: str = "user",
        metadata: Optional[dict] = None
    ) -> dict:
        # Screen for secrets
        secret_keywords = ["key", "password", "token", "secret", "auth", "credential", "private"]
        content_lower = content.lower()
        key_lower = key.lower()
        if any(kw in content_lower or kw in key_lower for kw in secret_keywords):
            raise ValueError("Refusing to store potential secrets (passwords, tokens, credentials, or keys) in memory.")

        valid_categories = {
            "CONVERSATION", "USER", "PROJECT", "TASK", "SYSTEM",
            "PREFERENCE", "FACT", "INSTRUCTION", "WORKFLOW", "OTHER"
        }
        if category.upper() not in valid_categories:
            raise ValueError(f"Invalid memory category: {category}. Must be one of {valid_categories}")
        return self.store.create_memory(
            category=category.upper(),
            key=key,
            content=content,
            project_id=project_id,
            importance=importance,
            source=source,
            metadata=metadata
        )

    def get_memory(self, memory_id: int) -> Optional[dict]:
        return self.store.get_memory(memory_id)

    def search_memory(self, query: str, category: Optional[str] = None, project_id: Optional[str] = None) -> list[dict]:
        return self.store.search_memories(query, category, project_id)

    def update_memory(self, memory_id: int, **kwargs) -> Optional[dict]:
        return self.store.update_memory(memory_id, **kwargs)

    def archive_memory(self, memory_id: int) -> Optional[dict]:
        return self.store.update_memory(memory_id, status="ARCHIVED")

    def delete_memory(self, memory_id: int) -> Optional[dict]:
        return self.store.update_memory(memory_id, status="DELETED")

    def list_memories(self, category: Optional[str] = None, project_id: Optional[str] = None, status: str = "ACTIVE") -> list[dict]:
        return self.store.list_memories(category, project_id, status)


class MemoryRequest:
    def __init__(
        self,
        category: str,
        key: str,
        content: str,
        project_id: Optional[str],
        session_id: str,
        question: Optional[str] = None,
        action: str = "create"
    ):
        self.request_id = f"mem-{uuid.uuid4().hex[:8]}"
        self.category = category.upper()
        self.key = key
        self.content = content
        self.project_id = project_id
        self.session_id = session_id
        self.created_timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
        self.status = "pending"  # pending, approved, denied
        self.action = action
        if question:
            self.question = question
        elif action == "delete":
            self.question = f"Would you like me to forget this: '{content}'?"
        else:
            self.question = f"Would you like me to remember that you {content.lower().strip('.')}?"

    def to_dict(self) -> dict:
        return {
            "request_id": self.request_id,
            "category": self.category,
            "key": self.key,
            "content": self.content,
            "project_id": self.project_id,
            "session_id": self.session_id,
            "created_timestamp": self.created_timestamp,
            "status": self.status,
            "question": self.question,
            "action": self.action
        }


class MemoryRequestStore:
    def __init__(self):
        self._requests: Dict[str, MemoryRequest] = {}

    def create_request(
        self,
        category: str,
        key: str,
        content: str,
        project_id: Optional[str],
        session_id: str,
        question: Optional[str] = None,
        action: str = "create"
    ) -> MemoryRequest:
        req = MemoryRequest(category, key, content, project_id, session_id, question, action)
        self._requests[req.request_id] = req
        return req

    def get_request(self, request_id: str) -> Optional[MemoryRequest]:
        return self._requests.get(request_id)

    def get_pending(self) -> List[MemoryRequest]:
        return [req for req in self._requests.values() if req.status == "pending"]

    def clear(self):
        self._requests.clear()


class MemoryApprovalRequiredException(Exception):
    def __init__(self, memory_request: MemoryRequest):
        self.memory_request = memory_request
        super().__init__(f"Memory approval required: {memory_request.content}")


# Ensure DB path directory exists and instantiate store/manager
db_dir = os.path.dirname(settings.DATABASE_PATH)
if db_dir:
    os.makedirs(db_dir, exist_ok=True)

sqlite_store = SQLiteMemoryStore(settings.DATABASE_PATH)
memory_manager = MemoryManager(sqlite_store)
memory_request_store = MemoryRequestStore()
