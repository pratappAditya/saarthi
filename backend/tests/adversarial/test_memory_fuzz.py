import pytest
import asyncio
from app.db.sqlite import SQLiteDatabase

MEMORY_TEST_CASES = [
    ("User prefers dark mode UI", True),
    ("Favorite test keyword is ORBITAL", True),
    ("User password is SuperSecret123!", False),
    ("API Key sk-proj-1234567890abcdef", False),
    ("Bearer token eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9", False),
] + [(f"Memory item {i}: User setting preference #{i}", True) for i in range(1, 96)]

@pytest.mark.asyncio
@pytest.mark.parametrize("content,should_store", MEMORY_TEST_CASES)
async def test_fuzz_memory_storage_and_screening(async_test_db, content, should_store):
    db = async_test_db
    if should_store:
        item = await db.add_memory(content=content, category="user_preference")
        assert item["id"] is not None
        all_memories = await db.get_memories()
        assert any(m["content"] == content for m in all_memories)
    else:
        # Credential pattern memory store attempt must throw ValueError or be rejected
        with pytest.raises((ValueError, Exception)):
            await db.add_memory(content=content, category="user_preference")
