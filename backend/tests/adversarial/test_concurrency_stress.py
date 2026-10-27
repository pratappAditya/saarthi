import pytest
import asyncio
from app.db.sqlite import SQLiteDatabase

CONCURRENCY_TEST_CASES = [
    (i, f"concurrent_session_{i}") for i in range(1, 51)
]

@pytest.mark.asyncio
@pytest.mark.parametrize("idx,session_id", CONCURRENCY_TEST_CASES)
async def test_fuzz_concurrent_database_writes(async_test_db, idx, session_id):
    db = async_test_db
    # Write message and memory concurrently
    await asyncio.gather(
        db.save_message(session_id=session_id, role="user", content=f"Concurrent message {idx}"),
        db.save_message(session_id=session_id, role="assistant", content=f"Concurrent response {idx}"),
        db.add_memory(content=f"Concurrent memory {idx} for ORBITAL", category="test")
    )
    messages = await db.get_messages(session_id=session_id)
    assert len(messages) == 2
