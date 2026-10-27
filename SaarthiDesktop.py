"""
Saarthi Windows Desktop Application Entry Point.
Launches the FastAPI backend on an available localhost port and opens a native
Windows desktop GUI window via pywebview hosting the compiled React frontend.
"""

import sys
import os
import io
import re

if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()

import time
import socket
import threading
import urllib.request
import json
import logging
from typing import Optional, Tuple, Any

# Ensure project root & backend are in sys.path for both dev and PyInstaller 6+ packaged modes
if getattr(sys, 'frozen', False):
    PROJECT_ROOT = os.path.dirname(sys.executable)
    INTERNAL_DIR = getattr(sys, '_MEIPASS', os.path.join(PROJECT_ROOT, "_internal"))
else:
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    INTERNAL_DIR = os.path.join(PROJECT_ROOT, "_internal")

possible_backend_dirs = [
    os.path.join(PROJECT_ROOT, "backend"),
    os.path.join(INTERNAL_DIR, "backend"),
    INTERNAL_DIR,
    PROJECT_ROOT,
]
for d in possible_backend_dirs:
    if os.path.exists(d) and d not in sys.path:
        sys.path.insert(0, d)

# Configure User AppData Directory for Windows Packaging
LOCAL_APPDATA = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
USER_DATA_DIR = os.path.join(LOCAL_APPDATA, "Saarthi")
LOGS_DIR = os.path.join(USER_DATA_DIR, "logs")
os.makedirs(USER_DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

if "SAARTHI_DATA_DIR" not in os.environ:
    os.environ["SAARTHI_DATA_DIR"] = USER_DATA_DIR
if "DATABASE_PATH" not in os.environ:
    os.environ["DATABASE_PATH"] = os.path.join(USER_DATA_DIR, "saarthi.db")

class SecretRedactingFormatter(logging.Formatter):
    """Redacts API keys, tokens, and authorization credentials from logs."""
    PATTERNS = [
        (re.compile(r'(?i)(?:key|token|secret|password|bearer|authorization)[:=]\s*["\']?([^"\'\s,;]+)'), r'\1'),
        (re.compile(r'sk-[a-zA-Z0-9_\-]{20,}'), '[REDACTED_API_KEY]'),
        (re.compile(r'rzp_(?:test|live)_[a-zA-Z0-9]+'), '[REDACTED_RAZORPAY_KEY]'),
        (re.compile(r'eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}'), '[REDACTED_JWT]'),
    ]

    def format(self, record):
        msg = super().format(record)
        for pattern, replacement in self.PATTERNS:
            if replacement == r'\1':
                msg = pattern.sub(lambda m: m.group(0).replace(m.group(1), "[REDACTED]"), msg)
            else:
                msg = pattern.sub(replacement, msg)
        return msg

log_file = os.path.join(LOGS_DIR, "desktop.log")
handler_file = logging.FileHandler(log_file, encoding="utf-8")
handler_file.setFormatter(SecretRedactingFormatter("[%(asctime)s] %(levelname)s - %(message)s"))

handler_stream = logging.StreamHandler(sys.stdout)
handler_stream.setFormatter(SecretRedactingFormatter("[%(asctime)s] %(levelname)s - %(message)s"))

logging.basicConfig(level=logging.INFO, handlers=[handler_file, handler_stream])
logger = logging.getLogger("SaarthiDesktop")

_active_uvicorn_server: Optional[Any] = None

def check_single_instance(mutex_name: str = "Local\\Saarthi_SingleInstance_Mutex") -> Tuple[Any, bool]:
    """
    Ensures single-instance behavior on Windows using Win32 named Mutex.
    Returns (mutex_handle, is_already_running).
    """
    if os.name != "nt":
        return None, False
    try:
        import ctypes
        from ctypes import wintypes
        kernel32 = ctypes.windll.kernel32
        CreateMutexW = kernel32.CreateMutexW
        CreateMutexW.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR]
        CreateMutexW.restype = wintypes.HANDLE
        
        GetLastError = kernel32.GetLastError
        GetLastError.restype = wintypes.DWORD
        
        ERROR_ALREADY_EXISTS = 183
        handle = CreateMutexW(None, False, mutex_name)
        if GetLastError() == ERROR_ALREADY_EXISTS:
            return handle, True
        return handle, False
    except Exception as e:
        logger.warning(f"Could not verify single-instance mutex: {e}")
        return None, False

def find_available_port(start_port: int = 8000, max_attempts: int = 50) -> int:
    """Finds an available TCP port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            result = sock.connect_ex(('127.0.0.1', port))
            if result != 0:
                return port
    return start_port

def start_backend_server(port: int):
    """Runs uvicorn FastAPI server in background thread."""
    global _active_uvicorn_server
    try:
        logger.info(f"Importing backend modules for port {port}...")
        import uvicorn
        from app.main import app
        from app.config.settings import settings
        
        settings.PORT = port
        settings.HOST = "127.0.0.1"
        logger.info(f"Starting Saarthi FastAPI backend on 127.0.0.1:{port}...")
        config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error", use_colors=False)
        _active_uvicorn_server = uvicorn.Server(config)
        _active_uvicorn_server.install_signal_handlers = lambda: None
        _active_uvicorn_server.run()
    except Exception as e:
        logger.error(f"FastAPI Backend crashed in thread: {e}", exc_info=True)

def wait_for_backend(port: int, timeout: int = 25) -> bool:
    """Polls backend health endpoint until online."""
    url = f"http://127.0.0.1:{port}/api/health"
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status == 200:
                    logger.info(f"Saarthi backend is online at http://127.0.0.1:{port}")
                    return True
        except Exception:
            time.sleep(0.3)
    return False

def shutdown_backend():
    """Signals uvicorn server to shut down cleanly."""
    global _active_uvicorn_server
    if _active_uvicorn_server is not None:
        logger.info("Signaling background FastAPI backend server to shut down...")
        _active_uvicorn_server.should_exit = True

def main():
    logger.info("Initializing Saarthi Desktop Application...")
    logger.info(f"User Data Directory: {USER_DATA_DIR}")
    
    is_smoke_test = "--smoke-test" in sys.argv or "--check" in sys.argv

    # Check Single Instance (skipped for automated smoke-tests)
    mutex_handle = None
    if not is_smoke_test:
        mutex_handle, is_already_running = check_single_instance()
        if is_already_running:
            logger.warning("Another instance of Saarthi is already active.")
            if os.name == "nt":
                import ctypes
                ctypes.windll.user32.MessageBoxW(
                    0,
                    "Saarthi is already running.\n\nPlease check your system taskbar or system tray.",
                    "Saarthi Active",
                    0x40  # MB_ICONINFORMATION
                )
            sys.exit(0)

    port = find_available_port(8000)
    
    # 1. Start backend server in daemon thread
    backend_thread = threading.Thread(target=start_backend_server, args=(port,), daemon=True)
    backend_thread.start()

    # 2. Wait for backend to become ready
    if not wait_for_backend(port):
        logger.error("Backend server failed to start within timeout.")
        if os.name == "nt":
            import ctypes
            ctypes.windll.user32.MessageBoxW(
                0,
                f"Saarthi local background service failed to start.\n\nPlease inspect logs at:\n{log_file}",
                "Saarthi Startup Error",
                0x10  # MB_ICONSTOP
            )
        sys.exit(1)

    # 3. Handle headless smoke-test
    if is_smoke_test:
        logger.info("Executing headless verification check...")
        try:
            req = urllib.request.Request(f"http://127.0.0.1:{port}/api/health")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                logger.info(f"Headless verification successful: status={resp.status}, payload={data}")
                shutdown_backend()
                print("SMOKE TEST PASSED: Saarthi Desktop backend and database initialized successfully.")
                sys.exit(0)
        except Exception as e:
            logger.error(f"Headless verification failed: {e}", exc_info=True)
            shutdown_backend()
            sys.exit(1)

    # 4. Create native Windows desktop window using pywebview
    try:
        import webview
    except ImportError as e:
        logger.error(f"Failed to import pywebview: {e}")
        if os.name == "nt":
            import ctypes
            ctypes.windll.user32.MessageBoxW(
                0,
                f"Saarthi requires Microsoft Edge WebView2 Runtime.\n\nPlease install Evergreen WebView2 Runtime from:\nhttps://developer.microsoft.com/en-us/microsoft-edge/webview2/",
                "Saarthi Dependency Missing",
                0x10
            )
        sys.exit(1)

    target_url = f"http://127.0.0.1:{port}/"
    logger.info(f"Opening Saarthi Desktop window pointing to {target_url}")

    try:
        window = webview.create_window(
            title="Saarthi — AI Career Companion (v1.0.0-beta.1)",
            url=target_url,
            width=1280,
            height=820,
            resizable=True,
            text_select=True,
            min_size=(900, 600)
        )
        webview.start(debug=False)
    except Exception as e:
        logger.error(f"Desktop GUI window error: {e}", exc_info=True)
        if os.name == "nt":
            import ctypes
            ctypes.windll.user32.MessageBoxW(
                0,
                f"Could not initialize desktop display window: {e}\n\nPlease verify Microsoft Edge WebView2 is installed.",
                "Saarthi Display Error",
                0x10
            )
    finally:
        shutdown_backend()
        logger.info("Saarthi Desktop application closed gracefully.")

if __name__ == "__main__":
    main()

