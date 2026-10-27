import os
import json
import pytest
import shutil
import tempfile
from app.config.settings import settings
from app.security.permissions import SecurityManager, PermissionLevel
from app.security.paths import is_path_allowed
from app.tools.registry import ToolRegistry
from app.tools.executor import ToolExecutor
from app.tools.file_list import FileListTool
from app.tools.file_read import FileReadTool
from app.tools.file_search import FileSearchTool
from app.tools.system_info import SystemInfoTool

@pytest.fixture
def temp_workspace():
    # Setup temporary allowed workspace
    temp_dir = tempfile.mkdtemp()
    
    # Create test files
    with open(os.path.join(temp_dir, "test.txt"), "w", encoding="utf-8") as f:
        f.write("Hello World! This is a test file.")
        
    with open(os.path.join(temp_dir, "large.txt"), "w", encoding="utf-8") as f:
        f.write("A" * 600 * 1024) # 600KB file (exceeds 512KB)
        
    with open(os.path.join(temp_dir, "binary.bin"), "wb") as f:
        f.write(b"Hello \x00 Binary \x01 World!")
        
    # Sub-directory
    sub_dir = os.path.join(temp_dir, "subdir")
    os.makedirs(sub_dir, exist_ok=True)
    with open(os.path.join(sub_dir, "subtest.txt"), "w", encoding="utf-8") as f:
        f.write("Finding matching content query inside subdirectory file.")
        
    # Backup allowed roots
    original_roots = settings.ALLOWED_ROOTS
    settings.ALLOWED_ROOTS = [temp_dir]
    
    yield temp_dir
    
    # Restore and cleanup
    settings.ALLOWED_ROOTS = original_roots
    shutil.rmtree(temp_dir)

def test_path_validation_boundary(temp_workspace):
    # Test path allowed inside workspace
    assert is_path_allowed(temp_workspace, settings.ALLOWED_ROOTS) is True
    assert is_path_allowed(os.path.join(temp_workspace, "test.txt"), settings.ALLOWED_ROOTS) is True
    assert is_path_allowed(os.path.join(temp_workspace, "subdir", "subtest.txt"), settings.ALLOWED_ROOTS) is True
    
    # Test path traversal attempts
    assert is_path_allowed(os.path.join(temp_workspace, ".."), settings.ALLOWED_ROOTS) is False
    assert is_path_allowed(os.path.join(temp_workspace, "subdir", "..", ".."), settings.ALLOWED_ROOTS) is False
    
    # Test outside allowed roots
    assert is_path_allowed("C:/Windows", settings.ALLOWED_ROOTS) is False
    assert is_path_allowed("/", settings.ALLOWED_ROOTS) is False

@pytest.mark.anyio
async def test_file_list_tool(temp_workspace):
    tool = FileListTool()
    
    # Test valid directory listing
    res = await tool.execute()
    assert len(res) == 4 # test.txt, large.txt, binary.bin, subdir
    assert any(x["name"] == "subdir" and x["is_directory"] for x in res)
    assert any(x["name"] == "test.txt" and not x["is_directory"] for x in res)
    
    # Test sub-path
    res_sub = await tool.execute(path=os.path.join(temp_workspace, "subdir"))
    assert len(res_sub) == 1
    assert res_sub[0]["name"] == "subtest.txt"
    
    # Test path traversal protection
    with pytest.raises(PermissionError):
        await tool.execute(path=os.path.join(temp_workspace, ".."))
        
    # Test non-existent path
    with pytest.raises(FileNotFoundError):
        await tool.execute(path=os.path.join(temp_workspace, "nonexistent"))

@pytest.mark.anyio
async def test_file_read_tool(temp_workspace):
    tool = FileReadTool()
    
    # Test valid file read
    content = await tool.execute(path=os.path.join(temp_workspace, "test.txt"))
    assert content == "Hello World! This is a test file."
    
    # Test oversized file (600KB > 512KB)
    with pytest.raises(ValueError) as exc:
        await tool.execute(path=os.path.join(temp_workspace, "large.txt"))
    assert "exceeds the maximum" in str(exc.value)
    
    # Test binary file rejection
    with pytest.raises(ValueError) as exc:
        await tool.execute(path=os.path.join(temp_workspace, "binary.bin"))
    assert "binary file" in str(exc.value)
    
    # Test path traversal protection
    with pytest.raises(PermissionError):
        await tool.execute(path=os.path.join(temp_workspace, "../some_other_folder/file.txt"))

@pytest.mark.anyio
async def test_file_search_tool(temp_workspace):
    tool = FileSearchTool()
    
    # Test search by name
    res = await tool.execute(query="subtest")
    assert len(res["matches"]) == 1
    assert res["matches"][0]["type"] == "filename_match"
    assert "subtest.txt" in res["matches"][0]["path"]
    
    # Test search by content
    res_content = await tool.execute(query="matching content query")
    assert len(res_content["matches"]) == 1
    assert res_content["matches"][0]["type"] == "content_match"
    assert res_content["matches"][0]["line"] == 1
    assert "inside subdirectory file" in res_content["matches"][0]["snippet"]
    
    # Test traversal attempt during search
    with pytest.raises(PermissionError):
        await tool.execute(query="test", path=os.path.join(temp_workspace, ".."))

@pytest.mark.anyio
async def test_system_info_tool():
    tool = SystemInfoTool()
    res = await tool.execute()
    
    # Verify expected structure
    assert "os" in res
    assert "cpu" in res
    assert "python_version" in res
    
    # Ensure no environment secrets or tokens are exposed
    for key in res.keys():
        assert not any(x in key.lower() for x in ["password", "token", "secret", "key"])

def test_security_manager_hierarchy():
    # Test READ_ONLY
    sm_ro = SecurityManager(PermissionLevel.READ_ONLY)
    assert sm_ro.is_allowed(PermissionLevel.READ_ONLY) is True
    assert sm_ro.is_allowed(PermissionLevel.USER_CONFIRMATION) is False
    
    # Test PRIVILEGED
    sm_priv = SecurityManager(PermissionLevel.PRIVILEGED)
    assert sm_priv.is_allowed(PermissionLevel.READ_ONLY) is True
    assert sm_priv.is_allowed(PermissionLevel.USER_CONFIRMATION) is True
    assert sm_priv.is_allowed(PermissionLevel.PRIVILEGED) is True

@pytest.mark.anyio
async def test_tool_executor(temp_workspace):
    # Registry setup
    registry = ToolRegistry()
    registry.register(FileListTool())
    registry.register(FileReadTool())
    
    # Security Setup
    security_manager = SecurityManager(PermissionLevel.USER_CONFIRMATION)
    
    # Executor Setup
    log_file = os.path.join(temp_workspace, "tools.log")
    executor = ToolExecutor(
        registry=registry,
        security_manager=security_manager,
        allowed_roots=settings.ALLOWED_ROOTS,
        log_path=log_file
    )
    
    # Test execute valid tool
    res = await executor.execute_tool("file_list", {"path": temp_workspace})
    assert res["success"] is True
    assert res["tool"] == "file_list"
    assert len(res["data"]) == 4
    
    # Test path traversal parameter protection inside executor
    res_traversal = await executor.execute_tool("file_read", {"path": os.path.join(temp_workspace, "..", "escaped.txt")})
    assert res_traversal["success"] is False
    assert res_traversal["error"]["code"] == "PATH_TRAVERSAL_DENIED"
    
    # Test unregistered tool lookup failure
    res_unreg = await executor.execute_tool("unregistered_tool", {})
    assert res_unreg["success"] is False
    assert res_unreg["error"]["code"] == "TOOL_NOT_FOUND"
    
    # Test logs verification
    assert os.path.exists(log_file) is True
    with open(log_file, "r") as f:
        log_lines = [json.loads(line) for line in f.read().splitlines() if line.strip()]
    assert len(log_lines) >= 2
    assert log_lines[0]["tool"] == "file_list"
    assert log_lines[0]["status"] == "success"
    assert log_lines[1]["tool"] == "file_read"
    assert log_lines[1]["status"] == "failure"
    assert log_lines[1]["error_code"] == "PATH_TRAVERSAL_DENIED"
