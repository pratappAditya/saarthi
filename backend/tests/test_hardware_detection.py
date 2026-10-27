import pytest
from app.system.hardware import HardwareDetectionService, HardwareProfile

def test_hardware_detection_profile():
    profile = HardwareDetectionService.get_hardware_profile()
    assert isinstance(profile, HardwareProfile)
    assert profile.total_ram_gb > 0
    assert profile.available_ram_gb >= 0
    assert profile.cpu_cores > 0
    assert profile.free_storage_gb >= 0
    assert isinstance(profile.gpu_vendor, str)
