import pytest
from app.security.permissions import SecurityManager, SandboxViolationError

security = SecurityManager()

PATH_FUZZ_CASES = [
    # (path, should_be_allowed)
    (".", True),
    ("./backend", True),
    ("backend/app/main.py", True),
    ("README.md", True),
    ("C:\\Windows\\System32\\drivers\\etc\\hosts", False),
    ("C:/Windows/System32/cmd.exe", False),
    ("../../etc/passwd", False),
    ("..\\..\\Windows\\System32", False),
    ("E:\\Saarthi\\backend\\app\\main.py", True),
    ("E:/Saarthi/frontend/src/App.tsx", True),
    ("%2e%2e%2f%2e%2e%2fetc%2fpasswd", False),
    ("\\\\server\\share\\file.txt", False),
] + [(f"backend/app/sub_{i}/file_{i}.py", True) for i in range(1, 48)] + [(f"C:/Out_Of_Sandbox_{i}/file.txt", False) for i in range(1, 48)]

@pytest.mark.parametrize("path_str,should_be_allowed", PATH_FUZZ_CASES)
def test_fuzz_path_boundary_enforcement(path_str, should_be_allowed):
    if should_be_allowed:
        try:
            validated = security.validate_path(path_str)
            assert validated is not None
        except SandboxViolationError:
            pytest.fail(f"Path {path_str} was expected to be allowed but threw SandboxViolationError")
    else:
        with pytest.raises((SandboxViolationError, ValueError, Exception)):
            security.validate_path(path_str)
