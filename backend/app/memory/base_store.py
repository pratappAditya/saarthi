from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseMemoryStore(ABC):
    @abstractmethod
    def create_memory(
        self,
        category: str,
        key: str,
        content: str,
        project_id: Optional[str] = None,
        importance: int = 0,
        source: str = "user",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_memory(self, memory_id: int) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def search_memories(
        self,
        query: str,
        category: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def update_memory(self, memory_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def list_memories(
        self,
        category: Optional[str] = None,
        project_id: Optional[str] = None,
        status: str = "ACTIVE"
    ) -> List[Dict[str, Any]]:
        pass
