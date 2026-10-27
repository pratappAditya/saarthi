import os
import uuid
import time
import logging
from typing import Dict, List, Tuple
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.telemetry import telemetry

logger = logging.getLogger("app.core.middleware")

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        req_id = request.headers.get("X-Request-ID") or f"req_{uuid.uuid4().hex[:12]}"
        request.state.request_id = req_id
        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = req_id
        return response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(self), geolocation=()"
        return response

class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        telemetry.increment_active_requests()
        client_ip = request.client.host if request.client else "unknown"
        req_id = getattr(request.state, "request_id", "unknown")

        try:
            response: Response = await call_next(request)
            latency_ms = round((time.time() - start_time) * 1000, 2)
            telemetry.record_request(response.status_code, latency_ms)
            
            logger.info(
                f"[{req_id}] {request.method} {request.url.path} -> {response.status_code} ({latency_ms}ms) IP={client_ip}"
            )
            response.headers["X-Response-Time-MS"] = str(latency_ms)
            return response
        except Exception as exc:
            latency_ms = round((time.time() - start_time) * 1000, 2)
            telemetry.record_request(500, latency_ms)
            logger.error(f"[{req_id}] {request.method} {request.url.path} FAILED: {exc} ({latency_ms}ms)", exc_info=True)
            raise exc
        finally:
            telemetry.decrement_active_requests()

class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    In-memory rate limiter protecting sensitive API routes.
    Limits auth requests to 20/min and unified chat/intelligence to 90/min per IP.
    """
    def __init__(self, app):
        super().__init__(app)
        self.ip_buckets: Dict[str, List[float]] = {}
        self.auth_limits = (20, 60.0)  # 20 requests per 60s
        self.general_limits = (90, 60.0)  # 90 requests per 60s

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if not path.startswith("/api/"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "127.0.0.1"
        is_prod = os.getenv("ENVIRONMENT", "development").lower() == "production"
        if not is_prod and (client_ip == "testclient" or os.getenv("PYTEST_CURRENT_TEST")):
            if path != "/api/auth/verify":
                return await call_next(request)

        now = time.time()

        max_reqs, window_sec = self.auth_limits if "/auth/" in path else self.general_limits
        bucket_key = f"{client_ip}:{ 'auth' if '/auth/' in path else 'gen' }"

        timestamps = self.ip_buckets.get(bucket_key, [])
        valid_timestamps = [t for t in timestamps if now - t < window_sec]

        if len(valid_timestamps) >= max_reqs:
            logger.warning(f"Rate limit exceeded for IP={client_ip} on path={path}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "status": "error",
                    "code": "RATE_LIMIT_EXCEEDED",
                    "detail": "Too many requests. Please slow down and try again shortly.",
                    "retry_after_seconds": int(window_sec - (now - valid_timestamps[0]))
                },
                headers={"Retry-After": str(int(window_sec - (now - valid_timestamps[0])))}
            )

        valid_timestamps.append(now)
        self.ip_buckets[bucket_key] = valid_timestamps
        return await call_next(request)

async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler catching unhandled server 500 exceptions.
    Returns sanitized JSON without exposing python tracebacks to clients.
    """
    req_id = getattr(request.state, "request_id", "unknown")
    logger.error(f"Global Exception Handler caught unhandled error [{req_id}]: {exc}", exc_info=True)
    
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"status": "error", "detail": exc.detail, "request_id": req_id}
        )

    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "code": "INTERNAL_SERVER_ERROR",
            "detail": "An internal operational error occurred. The incident has been recorded.",
            "request_id": req_id
        }
    )
