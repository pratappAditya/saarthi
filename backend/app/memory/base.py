from abc import ABC, abstractmethod
from typing import List, Dict

class MemoryProvider(ABC):
    @abstractmethod
    async def add_message(self, session_id: str, sender: str, message: str) -> None:
        pass

    @abstractmethod
    async def get_messages(self, session_id: str, limit: int = 50) -> List[Dict[str, str]]:
        pass

    @abstractmethod
    async def clear_session(self, session_id: str) -> None:
        pass
