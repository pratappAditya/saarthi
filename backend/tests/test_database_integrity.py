import pytest
import sqlite3
import tempfile
import os
import asyncio
from app.memory.sqlite_store import SQLiteMemoryStore
from app.memory.sqlite import SQLiteMemoryProvider

@pytest.fixture
def temp_db():
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_saarthi.db")
    yield db_path
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass

def test_database_creation_schema_and_indexes(temp_db):
    store = SQLiteMemoryStore(temp_db)
    provider = SQLiteMemoryProvider(temp_db)

    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()

    # Verify tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    assert "memories" in tables
    assert "chat_history" in tables

    conn.close()

@pytest.mark.anyio
async def test_database_concurrent_writes(temp_db):
    provider = SQLiteMemoryProvider(temp_db)
    session_id = "concurrent-db-test"

    async def write_turn(idx):
        await provider.add_message(session_id, "user", f"Message {idx}")

    # Write 20 messages concurrently
    tasks = [write_turn(i) for i in range(20)]
    await asyncio.gather(*tasks)

    messages = await provider.get_messages(session_id)
    assert len(messages) == 20
