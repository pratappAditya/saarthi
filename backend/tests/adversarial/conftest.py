import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import pytest
import tempfile
import asyncio
from app.db.sqlite import SQLiteDatabase

@pytest.fixture
def temp_db_path():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    yield path
    if os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            pass

import pytest_asyncio

@pytest_asyncio.fixture
async def async_test_db(temp_db_path):
    db = SQLiteDatabase(db_path=temp_db_path)
    await db.initialize()
    yield db
    await db.close()

@pytest.fixture
def mock_ollama_provider():
    from app.models.ollama import NemotronProvider
    provider = NemotronProvider(model_name="nemotron-3-nano:4b", base_url="http://127.0.0.1:11434")
    return provider
