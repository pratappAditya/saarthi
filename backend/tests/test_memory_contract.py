import pytest
from app.memory.manager import MemoryManager, memory_manager
from app.agent.core import AgentCore

def test_memory_secret_screening():
    # Attempting to store an API key should raise ValueError
    with pytest.raises(ValueError) as exc_info:
        memory_manager.create_memory(
            category="PREFERENCE",
            key="api_key",
            content="sk-proj-1234567890abcdef1234567890abcdef",
            source="user"
        )
    assert "Refusing to store potential secrets" in str(exc_info.value)

def test_memory_crud_and_relevance():
    agent = AgentCore()
    # Create test memory
    mem = memory_manager.create_memory(
        category="PREFERENCE",
        key="editor_preference",
        content="I prefer VS Code dark mode for editing code",
        source="user"
    )
    assert mem["id"] is not None

    memories = agent._get_relevant_memories("What editor mode do I prefer?")
    assert len(memories) > 0
    assert any("VS Code dark mode" in m["content"] for m in memories)

    # Cleanup
    memory_manager.delete_memory(mem["id"])
