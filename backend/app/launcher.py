import os
import sys
import time
import subprocess
import urllib.request
import json
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger("SaarthiLauncher")

class ServiceState:
    STOPPED = "STOPPED"
    STARTING = "STARTING"
    READY = "READY"
    FAILED = "FAILED"
    RUNNING = "RUNNING"
    STOPPING = "STOPPING"

class SaarthiLauncher:
    def __init__(self):
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.ollama_url = "http://127.0.0.1:11434"
        self.backend_url = "http://127.0.0.1:8000"
        self.target_model = "nemotron-3-nano:4b"
        self.ollama_state = ServiceState.STOPPED
        self.backend_state = ServiceState.STOPPED

    def is_ollama_online(self) -> bool:
        try:
            req = urllib.request.Request(f"{self.ollama_url}/api/tags")
            with urllib.request.urlopen(req, timeout=3) as resp:
                return resp.status == 200
        except Exception:
            return False

    def is_model_available(self) -> bool:
        try:
            req = urllib.request.Request(f"{self.ollama_url}/api/tags")
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                models = [m.get("name") for m in data.get("models", [])]
                return any(self.target_model in m for m in models)
        except Exception:
            return False

    def is_backend_online(self) -> bool:
        try:
            req = urllib.request.Request(f"{self.backend_url}/api/health")
            with urllib.request.urlopen(req, timeout=3) as resp:
                return resp.status == 200
        except Exception:
            return False

    def ensure_ollama_service(self) -> bool:
        if self.is_ollama_online():
            logger.info("Ollama service is online.")
            self.ollama_state = ServiceState.READY
            return True

        logger.info("Starting Ollama daemon service...")
        self.ollama_state = ServiceState.STARTING
        models_dir = os.path.join(self.project_root, "models")
        env = os.environ.copy()
        env["OLLAMA_MODELS"] = models_dir

        try:
            subprocess.Popen(["ollama", "serve"], env=env, creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
            for _ in range(10):
                time.sleep(1)
                if self.is_ollama_online():
                    logger.info("Ollama daemon started successfully.")
                    self.ollama_state = ServiceState.READY
                    return True
        except Exception as e:
            logger.error(f"Failed to start Ollama service: {e}")
            self.ollama_state = ServiceState.FAILED
            return False

        self.ollama_state = ServiceState.FAILED
        return False

    def ensure_backend_service(self) -> bool:
        if self.is_backend_online():
            logger.info("Saarthi FastAPI backend is online.")
            self.backend_state = ServiceState.READY
            return True

        logger.info("Starting Saarthi FastAPI backend server...")
        self.backend_state = ServiceState.STARTING
        python_exe = os.path.join(self.project_root, ".venv", "Scripts", "python.exe")
        if not os.path.exists(python_exe):
            python_exe = sys.executable

        env = os.environ.copy()
        env["PYTHONPATH"] = os.path.join(self.project_root, "backend")

        try:
            subprocess.Popen([python_exe, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"], cwd=self.project_root, env=env)
            for _ in range(10):
                time.sleep(1)
                if self.is_backend_online():
                    logger.info("Saarthi backend started successfully.")
                    self.backend_state = ServiceState.READY
                    return True
        except Exception as e:
            logger.error(f"Failed to start Saarthi backend: {e}")
            self.backend_state = ServiceState.FAILED
            return False

        self.backend_state = ServiceState.FAILED
        return False

    def get_status_summary(self) -> Dict[str, Any]:
        return {
            "ollama_state": self.ollama_state,
            "ollama_online": self.is_ollama_online(),
            "model_available": self.is_model_available(),
            "backend_state": self.backend_state,
            "backend_online": self.is_backend_online()
        }

if __name__ == "__main__":
    launcher = SaarthiLauncher()
    print("Checking Saarthi Services...")
    launcher.ensure_ollama_service()
    launcher.ensure_backend_service()
    print("Status:", json.dumps(launcher.get_status_summary(), indent=2))
