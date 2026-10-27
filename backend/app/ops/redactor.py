"""
Saarthi Ops Security Redactor.
Performs deterministic, recursive redaction of secrets, tokens, credentials, and sensitive patterns.
"""

import re
from typing import Any, Dict, List, Union
from app.ops.config import SENSITIVE_KEY_SUBSTRINGS

# Precompiled regex patterns for sensitive data redaction in free text and log lines
_PATTERNS = [
    # Database connection strings with credentials (e.g. postgresql://user:pass@host:port/db)
    (re.compile(r'(?i)([a-z0-9_]+://[^:\s]+:)([^@\s]+)(@[^\s]+)'), r'\1[REDACTED]\3'),
    # Bearer tokens in headers or logs
    (re.compile(r'(?i)(bearer\s+)([a-zA-Z0-9_\-\.]{8,})'), r'\1[REDACTED]'),
    # Generic authorization / token headers
    (re.compile(r'(?i)(authorization:\s*)([^\r\n]+)'), r'\1[REDACTED]'),
    # PEM Private keys
    (re.compile(r'-----BEGIN [A-Z\s]+PRIVATE KEY-----[\s\S]+?-----END [A-Z\s]+PRIVATE KEY-----'), '[REDACTED_PRIVATE_KEY]'),
    # OpenSSH private / public key lines
    (re.compile(r'ssh-(?:rsa|ed25519|dss)\s+[A-Za-z0-9+/=]+'), '[REDACTED_SSH_KEY]'),
    # JWT tokens (3-part base64url)
    (re.compile(r'eyJ[A-Za-z0-9_\-]{8,}\.eyJ[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}'), '[REDACTED_JWT]'),
    # Sensitive URL query parameters (e.g. ?secret=xyz, &token=xyz, &key=xyz, &password=xyz)
    (re.compile(r'(?i)([?&](?:password|secret|token|key|api_key|admin_key)=)([^&\s]+)'), r'\1[REDACTED]'),
    # Windows absolute user path sanitization (C:\Users\<user>\...)
    (re.compile(r'(?i)[a-z]:\\users\\[^\\]+\\', re.IGNORECASE), r'C:\\Users\\[REDACTED]\\'),
    # Linux absolute user home path sanitization (/home/<user>/...)
    (re.compile(r'/home/[^/]+/', re.IGNORECASE), r'/home/[REDACTED]/'),
]

class OpsRedactor:
    """Thread-safe, multi-pass redaction engine for Ops monitoring data."""

    @classmethod
    def redact_text(cls, text: str) -> str:
        """Applies all regex redaction patterns to a raw text string."""
        if not text or not isinstance(text, str):
            return str(text) if text is not None else ""
        
        redacted = text
        for pattern, replacement in _PATTERNS:
            redacted = pattern.sub(replacement, redacted)
        return redacted

    @classmethod
    def redact_data(cls, data: Any) -> Any:
        """
        Recursively traverses dictionaries, lists, and primitives.
        Redacts sensitive dictionary keys and patterns within string values.
        """
        if isinstance(data, dict):
            clean_dict = {}
            for k, v in data.items():
                k_str = str(k).lower()
                if any(sub in k_str for sub in SENSITIVE_KEY_SUBSTRINGS):
                    clean_dict[k] = "[REDACTED]"
                else:
                    clean_dict[k] = cls.redact_data(v)
            return clean_dict
        elif isinstance(data, (list, tuple, set)):
            return [cls.redact_data(item) for item in data]
        elif isinstance(data, str):
            return cls.redact_text(data)
        else:
            return data

ops_redactor = OpsRedactor()
