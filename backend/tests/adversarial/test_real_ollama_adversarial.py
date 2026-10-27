import pytest
import urllib.request
import json
from app.models.ollama import NemotronProvider

OLLAMA_CASES = [
    (f"Test query #{i}: What is 2 + {i}?", f"{2 + i}") for i in range(1, 21)
]

def is_ollama_online():
    try:
        req = urllib.request.Request("http://127.0.0.1:11434/api/tags")
        with urllib.request.urlopen(req, timeout=2) as resp:
            return resp.status == 200
    except Exception:
        return False

@pytest.mark.asyncio
@pytest.mark.parametrize("prompt,expected_token", OLLAMA_CASES)
async def test_fuzz_real_ollama_generation_cases(prompt, expected_token):
    if not is_ollama_online():
        pytest.skip("Ollama daemon is offline")
    provider = NemotronProvider(model_name="nemotron-3-nano:4b", base_url="http://127.0.0.1:11434")
    response = await provider.generate_response(prompt=prompt)
    assert response is not None
    assert isinstance(response, str)
