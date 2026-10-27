from abc import ABC, abstractmethod
from typing import Any, Dict
from app.security.permissions import PermissionLevel

class BaseTool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    @abstractmethod
    def permission_level(self) -> PermissionLevel:
        pass

    @property
    @abstractmethod
    def risk_classification(self) -> str:
        pass

    @property
    def risk_level(self) -> str:
        return self.risk_classification

    @property
    @abstractmethod
    def input_schema(self) -> Dict[str, Any]:
        pass

    @property
    @abstractmethod
    def output_schema(self) -> Dict[str, Any]:
        pass

    @property
    def is_synchronous(self) -> bool:
        return False

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        pass

