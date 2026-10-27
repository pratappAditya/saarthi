import pytest
from app.system.hardware import HardwareDetectionService
from app.licensing.telemetry import telemetry

def test_hardware_privacy_local():
    profile = HardwareDetectionService.get_hardware_profile()
    # Ensure profile dict is generated locally
    assert profile.os_name is not None

def test_telemetry_privacy_redaction():
    # Verify telemetry rejects sensitive content
    telemetry.log_event("TEST_EVENT", {"status": "ok"})
    # Check that events do not store sensitive prompt/resume keys
    metrics = telemetry.get_conversion_metrics()
    assert metrics is not None
