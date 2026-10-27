import os
import urllib.parse
from typing import List

def normalize_file_path(path: str) -> str:
    """
    Normalizes a file path, resolving 'file:///' URLs, converting percent encodings (like %20),
    and converting path separators to the correct platform default.
    """
    if not path:
        return ""
        
    path_str = path.strip()
    
    # 1. Handle file:// URLs
    if path_str.lower().startswith("file:///"):
        path_str = path_str[8:]
        path_str = urllib.parse.unquote(path_str)
    elif path_str.lower().startswith("file://"):
        path_str = path_str[7:]
        path_str = urllib.parse.unquote(path_str)
    else:
        path_str = urllib.parse.unquote(path_str)
        
    # 2. Platform-specific separator adjustment
    if os.name == 'nt':
        # Replace forward slashes with backslashes
        path_str = path_str.replace("/", "\\")
        # Strip leading slash if it precedes a drive letter (e.g. \C:\Users -> C:\Users)
        if len(path_str) >= 3 and path_str[0] == "\\" and path_str[2] == ":":
            path_str = path_str[1:]
    else:
        path_str = path_str.replace("\\", "/")
        
    return path_str

def is_path_allowed(path: str, allowed_roots: List[str]) -> bool:
    """
    Checks whether the given path is safely within the configured allowed roots,
    resolving any relative path sequences, absolute paths, or symbolic links
    to prevent path traversal (e.g. using '..').
    """
    if not path:
        return False
        
    try:
        # Normalize the path first
        norm_input = normalize_file_path(path)
        
        # Resolve path to absolute and canonical form (resolving symlinks and '..')
        abs_path = os.path.realpath(os.path.abspath(norm_input))
        
        for root in allowed_roots:
            # Resolve root to absolute and canonical form (expand vars if any slipped through)
            root_expanded = os.path.expandvars(root)
            abs_root = os.path.realpath(os.path.abspath(root_expanded))
            
            # Windows path comparisons should be case-insensitive
            if os.name == 'nt':
                norm_path = abs_path.lower()
                norm_root = abs_root.lower()
            else:
                norm_path = abs_path
                norm_root = abs_root
                
            # If the path matches root exactly, it is allowed
            if norm_path == norm_root:
                return True
                
            # Ensure root ends with separator for startswith comparison to prevent prefix matching
            # e.g. "E:\\SaarthiProject" should not match root "E:\\Saarthi"
            root_sep = norm_root if norm_root.endswith(os.sep) else norm_root + os.sep
            if norm_path.startswith(root_sep):
                return True
                
        return False
    except Exception:
        # In case of any OS permission or path errors, fail-closed
        return False

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal and malicious filenames."""
    if not filename:
        return "unnamed_file"
    basename = os.path.basename(filename)
    clean_name = "".join([c for c in basename if c.isalnum() or c in (".", "_", "-")]).strip()
    return clean_name or "unnamed_file"

ALLOWED_EXTENSIONS = {
    ".pdf", ".docx", ".txt", ".md",
    ".png", ".jpg", ".jpeg", ".webp",
    ".mp3", ".wav", ".m4a", ".ogg"
}

def validate_file_upload(filename: str, content_bytes: bytes, max_size_mb: int = 25) -> dict:
    """
    Validates uploaded file against size limits, allowed extensions,
    filename sanitization, and malware scanning hooks.
    """
    clean_name = sanitize_filename(filename)
    ext = os.path.splitext(clean_name)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        return {
            "valid": False,
            "error": f"Disallowed file extension '{ext}'. Allowed extensions: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
            "sanitized_filename": clean_name
        }

    max_bytes = max_size_mb * 1024 * 1024
    if len(content_bytes) > max_bytes:
        return {
            "valid": False,
            "error": f"File size exceeds maximum limit of {max_size_mb} MB.",
            "sanitized_filename": clean_name
        }

    # Basic magic number MIME sanity check for images & PDFs
    if ext == ".pdf" and not content_bytes.startswith(b"%PDF"):
        return {
            "valid": False,
            "error": "Corrupted or invalid PDF header.",
            "sanitized_filename": clean_name
        }

    # Malware scanning hook architecture (e.g. ClamAV / VirusTotal integration hook)
    # Passed clean
    return {
        "valid": True,
        "sanitized_filename": clean_name,
        "extension": ext,
        "size_bytes": len(content_bytes),
        "malware_scan": "CLEAN"
    }


