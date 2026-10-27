import pytest
from app.system.installer import NemotronInstallerService
from app.config.settings import settings
from unittest.mock import patch

@pytest.mark.asyncio
async def test_automatic_rollback_on_failed_health_check():
    settings.MODEL_PROVIDER = "ollama"
    settings.MODEL_NAME = "nemotron-3-nano:4b"

    # Mock health check to fail
    with patch.object(NemotronInstallerService, "verify_model_health", return_value={"success": False, "message": "Corrupted weights"}):
        res = await NemotronInstallerService.switch_model_safely("nemotron-3-8b")
        assert res["success"] is False
        assert res["active_model"] == "nemotron-3-nano:4b"
        assert settings.MODEL_NAME == "nemotron-3-nano:4b"
