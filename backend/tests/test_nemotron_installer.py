import pytest
from app.system.installer import NemotronInstallerService

@pytest.mark.asyncio
async def test_ollama_status_check():
    status = await NemotronInstallerService.get_ollama_status()
    assert "installed" in status
    assert "connected" in status
    assert "status_code" in status
