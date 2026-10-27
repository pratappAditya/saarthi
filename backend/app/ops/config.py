"""
Saarthi Ops Subsystem Configuration.
Enforces strict allowlists, data boundaries, and redaction rules.
"""

from typing import Set

# Strictly allowlisted Saarthi services. Never discover or query arbitrary or MKS ERP services.
ALLOWED_OPS_SERVICES: Set[str] = frozenset([
    "saarthi-backend",
    "saarthi-db",
    "saarthi-frontend",
    "saarthi-admin",
    "ollama"
])

# Strict bounds on query windows, response sizes, and log volume
MAX_ERROR_LOGS_LIMIT: int = 50
DEFAULT_ERROR_LOGS_LIMIT: int = 20
MAX_SNAPSHOTS_STORED: int = 50
MAX_AUDIT_EVENTS_LIMIT: int = 50
DEFAULT_AUDIT_EVENTS_LIMIT: int = 25

# Redaction blocklist keywords (case-insensitive substring match on dictionary keys)
SENSITIVE_KEY_SUBSTRINGS = (
    "password", "secret", "token", "key", "authorization", "bearer",
    "cookie", "credential", "private", "cert", "hash", "salt",
    "dsn", "connection_string", "uri", "ssh", "auth", "admin_key"
)
