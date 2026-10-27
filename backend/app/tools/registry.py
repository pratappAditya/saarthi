from typing import Dict, Any
from app.tools.base import BaseTool

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        if tool.name in self._tools:
            raise ValueError(f"Duplicate tool registration: A tool with the name '{tool.name}' is already registered.")
        self._tools[tool.name] = tool

    def unregister(self, tool_name: str):
        if tool_name in self._tools:
            del self._tools[tool_name]

    def get(self, tool_name: str) -> BaseTool:
        return self._tools.get(tool_name)

    def get_tool(self, name: str) -> BaseTool:
        # Keep for backward compatibility
        return self.get(name)

    def has(self, tool_name: str) -> bool:
        return tool_name in self._tools

    def exists(self, name: str) -> bool:
        # Keep for backward compatibility
        return self.has(name)

    def list_tools(self) -> Dict[str, Dict[str, Any]]:
        return {
            name: {
                "description": tool.description,
                "permission_level": tool.permission_level,
                "risk_classification": tool.risk_classification,
                "risk_level": tool.risk_level,
                "input_schema": tool.input_schema,
                "output_schema": tool.output_schema
            }
            for name, tool in self._tools.items()
        }
