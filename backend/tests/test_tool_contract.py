import pytest
from app.tools.registry import ToolRegistry
from app.tools.base import BaseTool
from app.security.permissions import PermissionLevel

class SampleTool(BaseTool):
    @property
    def name(self) -> str:
        return "sample_tool"

    @property
    def description(self) -> str:
        return "Sample tool for contract verification"

    @property
    def permission_level(self) -> PermissionLevel:
        return PermissionLevel.SAFE

    @property
    def risk_classification(self) -> str:
        return "LOW"

    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "param": {"type": "string"}
            },
            "required": ["param"]
        }

    @property
    def output_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "result": {"type": "string"}
            }
        }

    async def execute(self, **kwargs) -> dict:
        return {"result": f"processed {kwargs.get('param')}"}

def test_tool_registry_duplicate_registration_rejection():
    registry = ToolRegistry()
    tool1 = SampleTool()
    tool2 = SampleTool()

    registry.register(tool1)
    assert registry.has("sample_tool") is True

    # Registering duplicate tool name MUST raise ValueError
    with pytest.raises(ValueError) as exc_info:
        registry.register(tool2)
    assert "Duplicate tool registration" in str(exc_info.value)

def test_tool_schema_properties():
    tool = SampleTool()
    assert tool.name == "sample_tool"
    assert tool.permission_level == PermissionLevel.SAFE
    assert "param" in tool.input_schema["properties"]
