import os
import glob
import pytest
from app.config.settings import project_root

def test_audit_no_private_keys_in_backend_app():
    backend_app_dir = os.path.join(project_root, "backend", "app")
    pem_files = glob.glob(os.path.join(backend_app_dir, "**", "*.pem"), recursive=True)
    
    for pem_path in pem_files:
        with open(pem_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            assert "PRIVATE KEY" not in content, f"SECURITY VIOLATION: Private key found in production client file {pem_path}"

def test_audit_no_private_keys_in_frontend():
    frontend_dir = os.path.join(project_root, "frontend")
    if os.path.exists(frontend_dir):
        pem_files = glob.glob(os.path.join(frontend_dir, "**", "*.pem"), recursive=True)
        for pem_path in pem_files:
            with open(pem_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                assert "PRIVATE KEY" not in content, f"SECURITY VIOLATION: Private key found in frontend file {pem_path}"

def test_audit_no_private_keys_in_env_example():
    env_example = os.path.join(project_root, ".env.example")
    if os.path.exists(env_example):
        with open(env_example, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            assert "PRIVATE_KEY" not in content.upper() or "BEGIN PRIVATE KEY" not in content

@pytest.mark.parametrize("source_file", [
    "backend/app/licensing/client_manager.py",
    "backend/app/licensing/middleware.py",
    "backend/app/licensing/device.py",
    "backend/app/licensing/models.py",
    "backend/app/main.py",
    "backend/app/api/routes.py"
])
def test_audit_client_modules_do_not_import_private_keys(source_file):
    full_path = os.path.join(project_root, source_file)
    if os.path.exists(full_path):
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            code = f.read()
            assert "Ed25519PrivateKey.generate()" not in code, f"Client file {source_file} must not generate private keys at runtime."
            assert "BEGIN PRIVATE KEY" not in code, f"Client file {source_file} hardcodes a private key."
