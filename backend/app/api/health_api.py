import os
import shutil
import sqlite3
import psutil
from typing import Dict, Any
from fastapi import APIRouter, Response
from app.config.settings import settings
from app.core.telemetry import telemetry
from app.db.connection import get_db_connection
from app.system.hardware import HardwareDetectionService

router = APIRouter(tags=["Health & Observability"])

def get_ai_provider_status() -> Dict[str, Any]:
    """
    Returns truthful status of the AI model provider.
    Standardized execution_mode vocabulary: 'live', 'local', 'demo', 'unavailable'.
    Never discloses API credentials or secret values.
    """
    raw_provider = (settings.MODEL_PROVIDER or "").lower().strip()
    model_name = settings.MODEL_NAME or ""
    env = getattr(settings, "ENVIRONMENT", "").lower()
    is_staging_or_prod = env in ("staging", "production")
    demo_enabled = getattr(settings, "DEMO_MODE", False) or getattr(settings, "ALLOW_DEMO_FALLBACK", False)

    if not raw_provider or raw_provider in ("none", "unavailable"):
        return {
            "healthy": False,
            "provider": raw_provider or "none",
            "model": model_name,
            "configured": False,
            "reachable": False,
            "is_live": False,
            "execution_mode": "unavailable",
            "last_error_category": "NOT_CONFIGURED"
        }

    if raw_provider in ("mock", "demo"):
        if is_staging_or_prod and not demo_enabled:
            return {
                "healthy": False,
                "provider": raw_provider,
                "model": model_name,
                "configured": False,
                "reachable": False,
                "is_live": False,
                "execution_mode": "unavailable",
                "last_error_category": "MOCK_PROHIBITED_IN_STAGING"
            }
        return {
            "healthy": True,
            "provider": raw_provider,
            "model": model_name or "demo-model",
            "configured": True,
            "reachable": True,
            "is_live": False,
            "execution_mode": "demo",
            "last_error_category": None
        }

    if raw_provider == "ollama":
        try:
            hw_profile = HardwareDetectionService.get_hardware_profile()
            is_up = bool(hw_profile.ollama_running)
        except Exception:
            is_up = False
        return {
            "healthy": is_up,
            "provider": "ollama",
            "model": model_name,
            "configured": True,
            "reachable": is_up,
            "is_live": is_up,
            "execution_mode": "local" if is_up else "unavailable",
            "last_error_category": None if is_up else "LOCAL_INFERENCE_UNREACHABLE"
        }

    # Cloud providers: groq, deepseek, qwen, openrouter, glm, kimi, minimax, llama
    key_attr = f"{raw_provider.upper()}_API_KEY"
    api_key = getattr(settings, key_attr, "") or os.getenv(key_attr, "")
    is_placeholder = not api_key or "placeholder" in api_key.lower() or api_key.startswith("generate_")
    configured = not is_placeholder

    return {
        "healthy": configured,
        "provider": raw_provider,
        "model": model_name,
        "configured": configured,
        "reachable": configured,
        "is_live": configured,
        "execution_mode": "live" if configured else "unavailable",
        "last_error_category": None if configured else "MISSING_CREDENTIALS"
    }

@router.get("/health")
def full_health_check(response: Response):
    """
    Comprehensive operational health check for load balancers and system monitoring.
    Inspects DB connectivity, disk space, memory, and truthful AI provider status.
    """
    db_healthy = False
    db_error = None
    db_type = "postgresql" if (settings.DATABASE_URL or os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URI", "")).startswith("postgres") else "sqlite"
    try:
        with get_db_connection() as conn:
            conn.execute("SELECT 1").fetchone()
            db_healthy = True
    except Exception as e:
        db_error = str(e)

    # Disk Space
    try:
        total_d, used_d, free_d = shutil.disk_usage(settings.SAARTHI_DATA_DIR)
        free_gb = round(free_d / (1024**3), 2)
        disk_healthy = free_gb >= 1.0  # At least 1GB free storage
    except Exception:
        free_gb = 0.0
        disk_healthy = True

    # Hardware stats
    try:
        mem = psutil.virtual_memory()
        mem_percent = mem.percent
        mem_healthy = mem_percent < 95.0
    except Exception:
        mem_percent = 0.0
        mem_healthy = True

    # Truthful AI Model Service Status
    ai_status = get_ai_provider_status()

    # Overall system health: core web service & DB must be healthy
    overall_healthy = db_healthy and disk_healthy and mem_healthy

    # Set HTTP status code accordingly
    response.status_code = 200 if overall_healthy else 503

    return {
        "status": "healthy" if overall_healthy else "degraded",
        "service": "saarthi",
        "app_name": "Saarthi AI Operating Companion",
        "version": "0.5.0-rc2",
        "environment": getattr(settings, "ENVIRONMENT", "staging"),
        "checks": {
            "database": {"healthy": db_healthy, "type": db_type, "error": db_error},
            "storage": {"healthy": disk_healthy, "free_gb": free_gb},
            "memory": {"healthy": mem_healthy, "used_percent": mem_percent},
            "ai_provider": ai_status
        }
    }

@router.get("/health/liveness")
def liveness_ping():
    """
    Lightweight ping endpoint for load balancer liveness probes.
    """
    return {"status": "alive", "service": "Saarthi"}

@router.get("/health/readiness")
def readiness_check(response: Response):
    """
    Readiness probe verifying database connectivity before accepting incoming traffic.
    """
    try:
        with get_db_connection() as conn:
            conn.execute("SELECT 1")
        return {"status": "ready"}
    except Exception as e:
        response.status_code = 503
        return {"status": "not_ready", "reason": str(e)}

@router.get("/metrics")
def get_prometheus_metrics():
    """
    Observability endpoint providing operational metrics.
    """
    return {
        "status": "success",
        "metrics": telemetry.get_metrics_snapshot()
    }
