import pytest
from app.system.installer import NemotronInstallerService
from app.config.settings import settings

@pytest.mark.asyncio
async def test_safe_model_switch_in_mock():
    settings.MODEL_PROVIDER = "mock"
    res = await NemotronInstallerService.switch_model_safely("nemotron-mini:4b")
    assert res["success"] is True
    assert settings.MODEL_NAME == "nemotron-mini:4b"
