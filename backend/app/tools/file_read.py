import os
from typing import Dict, Any
from app.tools.base import BaseTool
from app.security.permissions import PermissionLevel
from app.config.settings import settings

class FileReadTool(BaseTool):
    @property
    def name(self) -> str:
        return "file_read"

    @property
    def description(self) -> str:
        return "Read the text content of a file inside the allowed workspace."

    @property
    def permission_level(self) -> PermissionLevel:
        return PermissionLevel.READ_ONLY

    @property
    def risk_classification(self) -> str:
        return "LOW"

    @property
    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "string",
            "description": "The full text content of the file."
        }

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path to the text file to read."
                }
            },
            "required": ["path"]
        }

    @property
    def is_synchronous(self) -> bool:
        return True

    async def execute(self, path: str, **kwargs) -> Any:
        import asyncio
        return await asyncio.to_thread(self._execute_sync, path=path, **kwargs)

    def _execute_sync(self, path: str, **kwargs) -> Any:
        if not path:
            raise ValueError("Argument 'path' is required.")

        # Double check path permission
        from app.security.paths import is_path_allowed
        if not is_path_allowed(path, settings.ALLOWED_ROOTS):
            raise PermissionError(f"Access to path '{path}' is denied (outside allowed roots).")

        if not os.path.exists(path):
            raise FileNotFoundError(f"File '{path}' does not exist.")

        if not os.path.isfile(path):
            raise ValueError(f"Path '{path}' is not a file.")

        # Check for PDF files
        if path.lower().endswith(".pdf"):
            file_size = os.path.getsize(path)
            return {
                "path": os.path.abspath(path),
                "extension": ".pdf",
                "size_bytes": file_size,
                "mime_type": "application/pdf",
                "metadata": {
                    "info": "PDF file detected. Content extraction is not currently enabled."
                }
            }

        # Enforce size limit (max 512KB)
        MAX_SIZE = 512 * 1024
        file_size = os.path.getsize(path)
        if file_size > MAX_SIZE:
            raise ValueError(f"File '{path}' exceeds the maximum allowed size of 512KB (size: {file_size} bytes).")

        try:
            # Read first block to check for null bytes (binary file check)
            with open(path, "rb") as f:
                chunk = f.read(1024)
                if b"\x00" in chunk:
                    raise ValueError(f"File '{path}' appears to be a binary file. Reading binary files is not supported.")
                    
            # Read as text
            with open(path, "r", encoding="utf-8", errors="strict") as f:
                content = f.read()
                return content
        except UnicodeDecodeError:
            raise ValueError(f"File '{path}' could not be decoded as UTF-8 text. Only text files are supported.")
        except Exception as e:
            if not isinstance(e, (ValueError, UnicodeDecodeError)):
                raise RuntimeError(f"Failed to read file: {str(e)}")
            raise e


