import sys
import os
# Ensure both backend/app and backend are in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app"))

import json
import pytest
import shutil
import tempfile
from unittest.mock import AsyncMock, patch
from app.config.settings import settings
from app.security.permissions import PermissionLevel, SecurityManager, PermissionRequiredException
from app.security.paths import is_path_allowed, normalize_file_path
from app.tools.registry import ToolRegistry
from app.tools.executor import ToolExecutor
from app.tools.file_read import FileReadTool
from app.tools.terminal import TerminalTool
from app.agent.core import AgentCore, validate_arguments

# 1. Test URL and Path Normalization
def test_path_normalization():
    # Windows style file URLs
    url = "file:///C:/Users/prata/OneDrive/Desktop/Suresh%20Mistry.pdf"
    norm = normalize_file_path(url)
    if os.name == 'nt':
        assert norm == "C:\\Users\\prata\\OneDrive\\Desktop\\Suresh Mistry.pdf"
    else:
        assert "Suresh Mistry.pdf" in norm

    # Normal path check
    normal = "C:\\Users\\prata\\OneDrive\\Desktop\\file.pdf"
    assert normalize_file_path(normal) == normal

    # Space encoding URL check
    encoded_url = "file:///E:/My%20Folder/Sub%20Folder/text.txt"
    norm_encoded = normalize_file_path(encoded_url)
    if os.name == 'nt':
        assert norm_encoded == "E:\\My Folder\\Sub Folder\\text.txt"
    else:
        assert "My Folder/Sub Folder/text.txt" in norm_encoded

# 2. Test Path Traversal and Prefix Protection
def test_traversal_and_prefix_protection():
    allowed_roots = ["E:\\Saarthi", "C:\\Users\\prata\\Downloads"]

    # Valid path matching root exactly
    assert is_path_allowed("E:\\Saarthi", allowed_roots) is True
    assert is_path_allowed("C:\\Users\\prata\\Downloads\\test.txt", allowed_roots) is True

    # Traversal escape
    assert is_path_allowed("E:\\Saarthi\\..\\Windows", allowed_roots) is False
    assert is_path_allowed("C:\\Users\\prata\\Downloads\\..\\..\\Windows", allowed_roots) is False

    # Prefix match attempt
    assert is_path_allowed("E:\\SaarthiProject", allowed_roots) is False
    assert is_path_allowed("E:\\SaarthiEvil\\file.txt", allowed_roots) is False
    assert is_path_allowed("C:\\Users\\prata\\DownloadsProject", allowed_roots) is False

# 3. Test PDF Metadata in FileReadTool
@pytest.mark.anyio
async def test_pdf_metadata():
    tool = FileReadTool()
    
    # Create temp directory inside allowed roots
    temp_dir = tempfile.mkdtemp()
    original_roots = settings.ALLOWED_ROOTS
    settings.ALLOWED_ROOTS = [temp_dir]
    
    try:
        # Create a dummy pdf file
        pdf_path = os.path.join(temp_dir, "Suresh Mistry.pdf")
        with open(pdf_path, "wb") as f:
            f.write(b"%PDF-1.4 mock pdf data")
            
        result = await tool.execute(path=pdf_path)
        assert isinstance(result, dict)
        assert result["extension"] == ".pdf"
        assert result["size_bytes"] > 0
        assert result["mime_type"] == "application/pdf"
        assert "PDF file detected" in result["metadata"]["info"]
    finally:
        settings.ALLOWED_ROOTS = original_roots
        shutil.rmtree(temp_dir)

# 4. Test Deletion Safety Response in TerminalTool
def test_terminal_deletion_safety():
    tool = TerminalTool()
    
    # Verify safety exception for rm, del, erase etc.
    with pytest.raises(PermissionError) as exc:
        tool.validate_command("rm -Force file.txt")
    assert "File deletion is not currently enabled" in str(exc.value)

    with pytest.raises(PermissionError) as exc:
        tool.validate_command("del file.txt")
    assert "File deletion is not currently enabled" in str(exc.value)

    with pytest.raises(PermissionError) as exc:
        tool.validate_command("remove-item file.txt")
    assert "File deletion is not currently enabled" in str(exc.value)

    # Check non-destructive is validated correctly
    # (should not raise deletion safety exception, though might raise privileged error)
    try:
        tool.validate_command("dir")
    except Exception as e:
        # It's fine if dir command raises PermissionError if it checks privileged,
        # but it shouldn't raise the "File deletion is not currently enabled" message.
        assert "File deletion is not currently enabled" not in str(e)

# 5. Test Argument Schema Validation
def test_argument_validation():
    schema = {
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "recursive": {"type": "boolean"},
            "limit": {"type": "integer"}
        },
        "required": ["path"]
    }
    
    # Valid arguments
    validate_arguments(schema, {"path": "E:\\Saarthi", "recursive": True, "limit": 10})
    
    # Missing required argument
    with pytest.raises(ValueError) as exc:
        validate_arguments(schema, {"recursive": True})
    assert "Missing required argument" in str(exc.value)
    
    # Wrong types
    with pytest.raises(ValueError) as exc:
        validate_arguments(schema, {"path": 123})
    assert "must be a string" in str(exc.value)
    
    # Wrong types type check
    with pytest.raises(ValueError) as exc:
        validate_arguments(schema, {"path": "E:\\Saarthi", "recursive": "yes"})
    assert "must be a boolean" in str(exc.value)

# 6. Test Unknown Tool Call Recovery (UNKNOWN_TOOL)
@pytest.mark.anyio
async def test_unknown_tool_call():
    agent = AgentCore()
    await agent.memory.clear_session("sess_unknown")
    
    # Mock model to return unknown tool first, then normal response
    mock_responses = [
        '[TOOL_CALL] {"tool": "file_look", "arguments": {"path": "dummy"}} [/TOOL_CALL]',
        'I cannot find that tool, but here is my normal answer.'
    ]
    
    with patch.object(agent.model, 'generate_response', AsyncMock()) as mock_gen:
        mock_gen.side_effect = mock_responses
        
        res = await agent.handle_message("sess_unknown", "Hello")
        
        # Should loop through unknown tool call, get error, and finally return clean response
        assert mock_gen.call_count == 2
        history = await agent.memory.get_messages("sess_unknown")
        
        # Verify database history contains structured JSON messages
        assert len(history) >= 4  # User message, tool call (assistant), tool result error (user), final response (assistant)
        
        # Verify intermediate tool call structure is saved
        t_call = json.loads(history[1]["message"])
        assert t_call["type"] == "tool_call"
        assert t_call["tool"] == "file_look"
        
        # Verify UNKNOWN_TOOL error result is stored
        t_res = json.loads(history[2]["message"])
        assert t_res["type"] == "tool_result"
        assert t_res["success"] is False
        assert t_res["error"]["type"] == "UNKNOWN_TOOL"

# 7. Test Malformed Tool Call Handling
@pytest.mark.anyio
async def test_malformed_tool_call():
    agent = AgentCore()
    await agent.memory.clear_session("sess_malformed")
    
    # Mock model to output invalid json inside tool call tag
    mock_responses = [
        '[TOOL_CALL] {invalid json} [/TOOL_CALL]',
        'Sorry, let me talk normally.'
    ]
    
    with patch.object(agent.model, 'generate_response', AsyncMock()) as mock_gen:
        mock_gen.side_effect = mock_responses
        
        res = await agent.handle_message("sess_malformed", "Hello")
        
        assert mock_gen.call_count == 2
        history = await agent.memory.get_messages("sess_malformed")
        
        # Verify parsing error structure is stored
        t_res = json.loads(history[2]["message"])
        assert t_res["type"] == "tool_result"
        assert t_res["success"] is False
        assert t_res["error"]["type"] == "MALFORMED_TOOL_CALL"

# 8. Test E2E Agent Tool Loop Execution
@pytest.mark.anyio
async def test_successful_tool_loop():
    # Create temp workspace
    temp_dir = tempfile.mkdtemp()
    original_roots = settings.ALLOWED_ROOTS
    settings.ALLOWED_ROOTS = [temp_dir]
    
    try:
        # Instantiate agent AFTER settings.ALLOWED_ROOTS is set
        agent = AgentCore()
        await agent.memory.clear_session("sess_loop_e2e")
        
        # 1. Ask agent to read a file
        file_path = os.path.join(temp_dir, "test.txt")
        with open(file_path, "w") as f:
            f.write("Hello Saarthi!")
            
        mock_responses = [
            f'[TOOL_CALL] {{"tool": "file_read", "arguments": {{"path": "{file_path.replace(os.sep, "/")}"}}}} [/TOOL_CALL]',
            'File read successfully. The content is: Hello Saarthi!'
        ]
        
        with patch.object(agent.model, 'generate_response', AsyncMock()) as mock_gen:
            mock_gen.side_effect = mock_responses
            
            res_json = await agent.handle_message("sess_loop_e2e", "Read test.txt please")
            
            # Verify final text response is returned inside structured format
            res_data = json.loads(res_json)
            assert res_data["type"] == "text"
            assert "Hello Saarthi!" in res_data["content"]
            
            # Verify tool execution succeeded
            history = await agent.memory.get_messages("sess_loop_e2e")
            tool_res_msg = json.loads(history[2]["message"])
            assert tool_res_msg["type"] == "tool_result"
            assert tool_res_msg["success"] is True
            assert tool_res_msg["result"] == "Hello Saarthi!"
            
    finally:
        settings.ALLOWED_ROOTS = original_roots
        shutil.rmtree(temp_dir)

# 9. Test Tool-Specific Tag parsing (e.g. [TOOL_FILE_READ])
@pytest.mark.anyio
async def test_tool_specific_tags_parsing():
    # Create temp workspace
    temp_dir = tempfile.mkdtemp()
    original_roots = settings.ALLOWED_ROOTS
    settings.ALLOWED_ROOTS = [temp_dir]
    
    try:
        agent = AgentCore()
        await agent.memory.clear_session("sess_specific_tags")
        
        file_path = os.path.join(temp_dir, "test.txt")
        with open(file_path, "w") as f:
            f.write("Tag content read!")
            
        # Model outputs [TOOL_FILE_READ] without specifying 'tool' in JSON
        mock_responses = [
            f'[TOOL_FILE_READ] {{"path": "{file_path.replace(os.sep, "/")}"}} [/TOOL_FILE_READ]',
            'Completed reading using custom tags.'
        ]
        
        with patch.object(agent.model, 'generate_response', AsyncMock()) as mock_gen:
            mock_gen.side_effect = mock_responses
            
            res_json = await agent.handle_message("sess_specific_tags", "Read test.txt please")
            res_data = json.loads(res_json)
            assert res_data["type"] == "text"
            
            # Verify tool execution succeeded with correct tool name parsed from tag
            history = await agent.memory.get_messages("sess_specific_tags")
            tool_res_msg = json.loads(history[2]["message"])
            assert tool_res_msg["type"] == "tool_result"
            assert tool_res_msg["tool"] == "file_read"
            assert tool_res_msg["success"] is True
            assert tool_res_msg["result"] == "Tag content read!"
            
    finally:
        settings.ALLOWED_ROOTS = original_roots
        shutil.rmtree(temp_dir)



