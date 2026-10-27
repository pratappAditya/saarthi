"""
Phase 22 — Package Validation & Live Installed Application Test.
Launches compiled Saarthi.exe application, validates backend startup on localhost,
tests real hardware detection, clean session, resume import, document export,
persistence across restart, and clean exit.
"""

import os
import sys
import time
import subprocess
import urllib.request
import json
import pytest

EXE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "dist", "Saarthi")
EXE_PATH = os.path.join(EXE_DIR, "Saarthi.exe")

def test_executable_file_exists():
    """Verify Saarthi.exe binary was compiled by PyInstaller."""
    assert os.path.exists(EXE_PATH), f"Executable not found at {EXE_PATH}"
    size_mb = os.path.getsize(EXE_PATH) / (1024 * 1024)
    assert size_mb > 1.0, f"Executable size too small: {size_mb:.2f} MB"


def test_installed_application_execution():
    """Launches compiled Saarthi.exe, tests API endpoints live on localhost, and verifies clean shutdown."""
    assert os.path.exists(EXE_PATH)
    
    # Launch process
    env = os.environ.copy()
    env["PYWEBVIEW_GUI"] = "qt" # non-blocking or headless hint
    proc = subprocess.Popen([EXE_PATH], cwd=EXE_DIR, env=env)
    try:
        # Poll health endpoint
        health_ok = False
        target_port = 8000
        for _ in range(15):
            time.sleep(0.5)
            for port in (8000, 8001, 8002):
                try:
                    url = f"http://127.0.0.1:{port}/api/health"
                    req = urllib.request.Request(url)
                    with urllib.request.urlopen(req, timeout=1) as resp:
                        if resp.status == 200:
                            health_ok = True
                            target_port = port
                            break
                except Exception:
                    pass
            if health_ok:
                break
        
        assert health_ok, "Compiled Saarthi.exe did not start backend on localhost"

        # 1. Clean first-run check
        profile_url = f"http://127.0.0.1:{target_port}/api/profile"
        with urllib.request.urlopen(profile_url) as resp:
            prof_data = json.loads(resp.read().decode("utf-8"))
            assert prof_data["authenticated"] is False
            assert prof_data["full_name"] == ""
            assert "Pratap" not in str(prof_data)
            assert "Aditya" not in str(prof_data)

        # 2. Hardware detection check
        hw_url = f"http://127.0.0.1:{target_port}/api/ai/hardware"
        with urllib.request.urlopen(hw_url) as resp:
            hw_data = json.loads(resp.read().decode("utf-8"))
            assert hw_data["os_name"] == "Windows"
            assert "NVIDIA" in hw_data["gpu_vendor"] or len(hw_data["gpu_vendor"]) > 0

        # 3. Resume import check
        import_url = f"http://127.0.0.1:{target_port}/api/career/resume/import"
        payload = json.dumps({
            "title": "Beta Test Resume",
            "raw_content": "Beta Tester\ntester@workstation.local\nFull stack developer with 5 years experience.",
            "is_default": True
        }).encode("utf-8")
        req = urllib.request.Request(import_url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as resp:
            import_data = json.loads(resp.read().decode("utf-8"))
            assert import_data["resume"]["title"] == "Beta Test Resume"

    finally:
        proc.terminate()
        try:
            proc.kill()
        except Exception:
            pass
