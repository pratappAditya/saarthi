import os
from typing import Dict, Any
from app.tools.base import BaseTool
from app.security.permissions import PermissionLevel
from app.config.settings import settings

class FileListTool(BaseTool):
    @property
    def name(self) -> str:
        return "file_list"

    @property
    def description(self) -> str:
        return "List files and directories inside an allowed workspace path."

    @property
    def permission_level(self) -> PermissionLevel:
        return PermissionLevel.READ_ONLY

    @property
    def risk_classification(self) -> str:
        return "LOW"

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The workspace sub-path or directory to list. Defaults to the root allowed path."
                },
                "recursive": {
                    "type": "boolean",
                    "description": "Whether to list files recursively."
                },
                "max_items": {
                    "type": "integer",
                    "description": "Maximum number of items to return."
                }
            }
        }

    @property
    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "path": {"type": "string"},
                    "is_directory": {"type": "boolean"},
                    "size": {"type": "integer"}
                }
            }
        }

    @property
    def is_synchronous(self) -> bool:
        return True

    async def execute(self, path: str = None, recursive: bool = False, max_items: int = 100, **kwargs) -> Any:
        import asyncio
        return await asyncio.to_thread(self._execute_sync, path=path, recursive=recursive, max_items=max_items, **kwargs)

    def _execute_sync(self, path: str = None, recursive: bool = False, max_items: int = 100, **kwargs) -> Any:
        # Resolve target path. Default to first allowed root.
        target_dir = path if path else settings.ALLOWED_ROOTS[0]
        
        # Double check path permission
        from app.security.paths import is_path_allowed
        if not is_path_allowed(target_dir, settings.ALLOWED_ROOTS):
            raise PermissionError(f"Access to path '{target_dir}' is denied (outside allowed roots).")

        if not os.path.exists(target_dir):
            raise FileNotFoundError(f"Directory '{target_dir}' does not exist.")
            
        if not os.path.isdir(target_dir):
            raise ValueError(f"Path '{target_dir}' is not a directory.")

        results = []
        try:
            if not recursive:
                with os.scandir(target_dir) as entries:
                    for entry in entries:
                        if len(results) >= max_items:
                            break
                        results.append({
                            "name": entry.name,
                            "path": entry.path,
                            "is_directory": entry.is_dir(),
                            "size": entry.stat().st_size if entry.is_file() else None
                        })
            else:
                for root, dirs, files in os.walk(target_dir):
                    # Prune common ignore directories to prevent infinite loops / bloating
                    prune_dirs = [".git", "node_modules", ".venv", "__pycache__", ".pytest_cache"]
                    dirs[:] = [d for d in dirs if d not in prune_dirs]
                    
                    # Ensure each sub-directory is within allowed root
                    dirs[:] = [d for d in dirs if is_path_allowed(os.path.join(root, d), settings.ALLOWED_ROOTS)]
                    
                    for name in dirs + files:
                        if len(results) >= max_items:
                            break
                        full_path = os.path.join(root, name)
                        if not is_path_allowed(full_path, settings.ALLOWED_ROOTS):
                            continue
                        is_dir = os.path.isdir(full_path)
                        results.append({
                            "name": name,
                            "path": full_path,
                            "is_directory": is_dir,
                            "size": os.path.getsize(full_path) if not is_dir else None
                        })
                    if len(results) >= max_items:
                        break

            # Sort directories first, then alphabetically
            results.sort(key=lambda x: (not x["is_directory"], x["name"].lower()))
            return results[:max_items]
        except Exception as e:
            if isinstance(e, (PermissionError, FileNotFoundError, ValueError)):
                raise e
            raise RuntimeError(f"Failed to list directory contents: {str(e)}")

