import pytest
import asyncio
from app.db.sqlite import SQLiteDatabase

SESSION_PAIRS = [
    (f"session_A_{i}", f"session_B_{i}") for i in range(1, 43)
] + [(f"tenant_{i}_sess1", f"tenant_{i}_sess2") for i in range(1, 44)]

@pytest.mark.asyncio
@pytest.mark.parametrize("session_a,session_b", SESSION_PAIRS)
async def test_cross_session_history_isolation(async_test_db, session_a, session_b):
    db = async_test_db
    await db.save_message(session_id=session_a, role="user", content=f"Secret for {session_a}")
    await db.save_message(session_id=session_b, role="user", content=f"Secret for {session_b}")

    history_a = await db.get_messages(session_id=session_a)
    history_b = await db.get_messages(session_id=session_b)

    assert len(history_a) == 1
    assert len(history_b) == 1
    assert history_a[0]["content"] == f"Secret for {session_a}"
    assert history_b[0]["content"] == f"Secret for {session_b}"
    assert session_b not in [m["content"] for m in history_a]
    assert session_a not in [m["content"] for m in history_b]
