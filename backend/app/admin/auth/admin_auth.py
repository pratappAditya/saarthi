import hashlib
import hmac
import logging
import os
from typing import Optional, Dict, Any, List, Callable
from fastapi import Request, Header, HTTPException, Depends
from app.config.settings import settings
from app.db.auth import AuthRepository
from app.admin.repositories.admin_repository import AdminRepository

logger = logging.getLogger("app.admin.auth")

# Explicit list of revoked/forbidden fallback keys and insecure placeholders that must NEVER be accepted
REVOKED_ADMIN_KEYS = frozenset([
    "SAARTHI_SECRET_ADMIN_KEY_2026",
    "saarthi_admin_secret_key_2026",
    "saarthi_vendor_secret_key_change_in_production",
    "dev_admin_key",
    "change_in_production",
    "admin",
    "password",
    "secret",
    "default_secret",
    "changeme",
    "generate_fresh_random_staging_admin_key_64chars",
    "generate_fresh_random_staging_jwt_secret_64chars",
])

def is_insecure_placeholder(secret: Optional[str]) -> bool:
    if not secret or not isinstance(secret, str):
        return True
    s = secret.strip().lower()
    if not s:
        return True
    if s in {k.lower() for k in REVOKED_ADMIN_KEYS}:
        return True
    placeholder_substrings = ["placeholder", "generate_", "changeme", "example", "your_secret", "change_in_production"]
    return any(p in s for p in placeholder_substrings)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

def get_configured_admin_key() -> Optional[str]:
    """
    Retrieves the configured admin key from environment or settings.
    Enforces strict configuration precedence:
      1. Explicit environment variables (VENDOR_ADMIN_KEY, ADMIN_SECRET_KEY)
      2. Settings attributes (settings.VENDOR_ADMIN_KEY, settings.ADMIN_SECRET_KEY)
    Discards any empty, whitespace, or known insecure placeholder/revoked keys at every step,
    preventing a default or placeholder from silently masking an environment secret or granting access.
    Fails closed (returns None) if unconfigured, empty, or using an insecure placeholder.
    Never returns a hardcoded default secret.
    """
    candidates = [
        os.getenv("VENDOR_ADMIN_KEY"),
        os.getenv("ADMIN_SECRET_KEY"),
        getattr(settings, "VENDOR_ADMIN_KEY", None),
        getattr(settings, "ADMIN_SECRET_KEY", None),
    ]
    for key in candidates:
        if not key or not isinstance(key, str):
            continue
        key_clean = key.strip()
        if not key_clean or is_insecure_placeholder(key_clean):
            continue
        return key_clean
    return None

def validate_admin_security_configuration(is_prod: Optional[bool] = None) -> bool:
    """
    Explicit environment/configuration validation.
    In production/staging, fails closed by raising RuntimeError if admin secret or JWT secret is absent, insecure placeholder, or has insufficient entropy.
    """
    if is_prod is None:
        is_prod = os.getenv("ENVIRONMENT", "development").lower() in ("production", "staging")

    key = get_configured_admin_key()
    if is_prod:
        if not key:
            raise RuntimeError(
                "FATAL: Production security check failed: VENDOR_ADMIN_KEY / ADMIN_SECRET_KEY "
                "is absent, empty, or configured with an insecure placeholder. System failed closed."
            )
        if len(key) < 32:
            raise RuntimeError(
                "FATAL: Production security check failed: VENDOR_ADMIN_KEY / ADMIN_SECRET_KEY "
                "has insufficient entropy (< 32 characters). System failed closed."
            )

        # Validate JWT_SECRET as well
        jwt_sec = os.getenv("JWT_SECRET") or getattr(settings, "JWT_SECRET", None)
        if not jwt_sec or is_insecure_placeholder(jwt_sec):
            raise RuntimeError(
                "FATAL: Production security check failed: JWT_SECRET is absent or contains an insecure placeholder. System failed closed."
            )
        if len(jwt_sec.strip()) < 32:
            raise RuntimeError(
                "FATAL: Production security check failed: JWT_SECRET has insufficient entropy (< 32 characters). System failed closed."
            )

    return bool(key)

def verify_admin_key(candidate_key: Optional[str]) -> bool:
    """
    Verifies that candidate_key matches the configured admin secret using constant-time comparison.
    Fails closed if candidate_key or configured key is missing/invalid.
    Explicitly rejects revoked fallback keys and insecure placeholders.
    """
    if not candidate_key or not isinstance(candidate_key, str):
        return False
    candidate_clean = candidate_key.strip()
    if not candidate_clean or candidate_clean.lower() in {k.lower() for k in REVOKED_ADMIN_KEYS}:
        return False

    configured_key = get_configured_admin_key()
    if not configured_key:
        return False

    return hmac.compare_digest(candidate_clean, configured_key)

def verify_admin_access(
    request: Request,
    x_admin_key: Optional[str] = Header(None),
    x_vendor_admin_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None)
) -> Dict[str, Any]:
    """
    Server-side admin authentication and authorization dependency.
    Checks:
    1. X-Admin-Key / X-Vendor-Admin-Key matching configured admin secret -> returns SUPER_ADMIN admin context.
    2. Bearer session_token matching AdminSession -> returns AdminUser context.
    3. Bearer session_token matching Saarthi User with role in ['ADMIN', 'SUPER_ADMIN', 'SUPPORT', 'ANALYST'].
    Rejects unauthorized access with HTTP 403.
    """
    # 1. Header Admin Key
    header_key = x_admin_key if isinstance(x_admin_key, str) else (x_vendor_admin_key if isinstance(x_vendor_admin_key, str) else None)
    if header_key:
        clean_key = header_key.strip()
        if clean_key.lower() in {k.lower() for k in REVOKED_ADMIN_KEYS}:
            client_ip = request.client.host if request.client else "127.0.0.1"
            logger.warning(f"Unauthorized admin access attempt with revoked/placeholder key from IP: {client_ip}")
            raise HTTPException(status_code=403, detail="Unauthorized admin access: Revoked or placeholder admin key rejected.")
        if verify_admin_key(clean_key):
            return {
                "admin_id": "SYSTEM_KEY_ADMIN",
                "email": "admin@saarthi.local",
                "role": "SUPER_ADMIN",
                "full_name": "System Super Admin",
                "auth_method": "ADMIN_KEY"
            }

    # 2. Authorization Header Token
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]

        # Check AdminSession repository
        admin_sess = AdminRepository.get_session(token)
        if admin_sess:
            if admin_sess.get("admin_id") == "SYSTEM_KEY_ADMIN":
                return {
                    "admin_id": "SYSTEM_KEY_ADMIN",
                    "email": "admin@saarthi.local",
                    "role": "SUPER_ADMIN",
                    "full_name": "System Super Admin",
                    "auth_method": "ADMIN_SESSION"
                }
            admin_user = AdminRepository.get_admin_by_id(admin_sess["admin_id"])
            if admin_user and admin_user.get("status") == "ACTIVE":
                return {
                    "admin_id": admin_user["admin_id"],
                    "email": admin_user["email"],
                    "role": admin_user["role"],
                    "full_name": admin_user.get("full_name", ""),
                    "auth_method": "ADMIN_SESSION"
                }

        # Check standard user sessions with elevated admin role
        user_sess = AuthRepository.get_session(token)
        if user_sess:
            user = AuthRepository.get_user_by_id(user_sess["user_id"])
            if user and user.get("role") in ["ADMIN", "SUPER_ADMIN", "SUPPORT", "ANALYST"]:
                return {
                    "admin_id": user["user_id"],
                    "email": user["email"],
                    "role": user["role"],
                    "full_name": user.get("full_name", ""),
                    "auth_method": "USER_SESSION"
                }

    client_ip = request.client.host if request.client else "127.0.0.1"
    logger.warning(f"Unauthorized admin access attempt from IP: {client_ip}")
    raise HTTPException(status_code=403, detail="Unauthorized admin access.")

def require_admin_role(allowed_roles: List[str]):
    """
    Dependency factory to enforce explicit role permissions on endpoints.
    Supported roles: SUPER_ADMIN, ADMIN, SUPPORT, ANALYST.
    SUPER_ADMIN always passes.
    ANALYST is restricted to read-only endpoints.
    """
    def role_checker(admin: Dict[str, Any] = Depends(verify_admin_access)) -> Dict[str, Any]:
        user_role = admin.get("role", "").upper()

        if user_role == "SUPER_ADMIN":
            return admin

        if user_role in [r.upper() for r in allowed_roles]:
            return admin

        raise HTTPException(
            status_code=403,
            detail=f"Role '{user_role}' is not authorized to perform this operation. Required: {allowed_roles}"
        )
    return role_checker
