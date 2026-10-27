import os
from typing import Dict, Any, List
from app.tools.base import BaseTool
from app.security.permissions import PermissionLevel
from app.config.settings import settings

class FileSearchTool(BaseTool):
    @property
    def name(self) -> str:
        return "file_search"

    @property
    def description(self) -> str:
        return "Search for files by name or containing specific text inside allowed workspace directories."

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
                "query": {
                    "type": "string",
                    "description": "The search query (file name snippet or text content)."
                },
                "path": {
                    "type": "string",
                    "description": "The directory to search within. Defaults to the first allowed root."
                },
                "root_path": {
                    "type": "string",
                    "description": "Alternative key for the directory to search within."
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of search results to return."
                },
                "file_pattern": {
                    "type": "string",
                    "description": "Optional file pattern to filter search (e.g. *.py)."
                }
            },
            "required": ["query"]
        }

    @property
    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "matches": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "type": {"type": "string"},
                            "line": {"type": "integer"},
                            "snippet": {"type": "string"}
                        }
                    }
                },
                "scanned_files": {"type": "integer"},
                "limit_reached": {"type": "boolean"}
            }
        }

    @property
    def is_synchronous(self) -> bool:
        return True

    async def execute(self, query: str, path: str = None, root_path: str = None, max_results: int = 100, file_pattern: str = None, **kwargs) -> Any:
        import asyncio
        return await asyncio.to_thread(
            self._execute_sync,
            query=query,
            path=path,
            root_path=root_path,
            max_results=max_results,
            file_pattern=file_pattern,
            **kwargs
        )

    def _execute_sync(self, query: str, path: str = None, root_path: str = None, max_results: int = 100, file_pattern: str = None, **kwargs) -> Any:
        if not query:
            raise ValueError("Argument 'query' is required.")

        search_dir = root_path or path or settings.ALLOWED_ROOTS[0]

        # Double check path permission
        from app.security.paths import is_path_allowed
        if not is_path_allowed(search_dir, settings.ALLOWED_ROOTS):
            raise PermissionError(f"Access to path '{search_dir}' is denied (outside allowed roots).")

        if not os.path.exists(search_dir):
            raise FileNotFoundError(f"Search directory '{search_dir}' does not exist.")

        if not os.path.isdir(search_dir):
            raise ValueError(f"Path '{search_dir}' is not a directory.")

        matches = []
        max_scanned_files = 1000
        scanned_count = 0

        try:
            for root, dirs, files in os.walk(search_dir):
                # Prune node_modules, git, venv to speed up and avoid scanning endless files
                prune_dirs = [".git", "node_modules", ".venv", "__pycache__", ".pytest_cache"]
                dirs[:] = [d for d in dirs if d not in prune_dirs]

                # Security check on subdirectories (just in case directory structure has symlink loops or escapes)
                # Filter dirs list in-place so walk doesn't descend into unauthorized roots
                dirs[:] = [d for d in dirs if is_path_allowed(os.path.join(root, d), settings.ALLOWED_ROOTS)]

                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Ensure path is allowed
                    if not is_path_allowed(file_path, settings.ALLOWED_ROOTS):
                        continue

                    # If file_pattern is specified, filter files using fnmatch
                    if file_pattern:
                        import fnmatch
                        if not fnmatch.fnmatch(file.lower(), file_pattern.lower()):
                            continue

                    scanned_count += 1
                    if scanned_count > max_scanned_files:
                        # Return what we found so far and indicate limits were reached
                        break

                    # 1. Match file name
                    if query.lower() in file.lower():
                        matches.append({
                            "path": file_path,
                            "type": "filename_match",
                            "line": None,
                            "snippet": None
                        })
                        if len(matches) >= max_results:
                            break
                        continue

                    # 2. Match content (only for text files under a certain size)
                    try:
                        # Limit to text files less than 128KB for search to prevent slowing down
                        if os.path.getsize(file_path) < 128 * 1024:
                            # Read first block to check for null bytes
                            with open(file_path, "rb") as f:
                                if b"\x00" in f.read(1024):
                                    continue # skip binary

                            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                                for line_num, line in enumerate(f, 1):
                                    if query.lower() in line.lower():
                                        matches.append({
                                            "path": file_path,
                                            "type": "content_match",
                                            "line": line_num,
                                            "snippet": line.strip()
                                        })
                                        if len(matches) >= max_results:
                                            break
                            if len(matches) >= max_results:
                                break
                    except Exception:
                        pass # Ignore reading errors during search walk

                if scanned_count > max_scanned_files or len(matches) >= max_results:
                    break

            return {
                "matches": matches,
                "scanned_files": scanned_count,
                "limit_reached": scanned_count > max_scanned_files
            }
        except Exception as e:
            raise RuntimeError(f"Search failed: {str(e)}")

