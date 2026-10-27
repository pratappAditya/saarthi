import sys
import os
from contextlib import asynccontextmanager

# Ensure both backend/app and backend are in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import router as api_router
from app.api.health_api import router as health_router
from app.api.beta_api import router as beta_router
from app.api.desktop_api import router as desktop_router
from app.api.admin import router as admin_router
from app.api.mcp_api import router as mcp_router
from app.ops import ops_router
from app.config.settings import settings
from app.core.middleware import (
    RequestIDMiddleware,
    SecurityHeadersMiddleware,
    StructuredLoggingMiddleware,
    RateLimiterMiddleware,
    global_exception_handler
)

from app.db.admin_db import init_admin_tables
from app.db.billing_db import init_billing_tables
from app.db.postgres_schema import init_postgres_tables
from app.mcp.request_state import init_request_state_table

import logging

logger = logging.getLogger("app.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup procedure
    is_prod = os.getenv("ENVIRONMENT", "development").lower() in ("production", "staging")
    try:
        init_postgres_tables()
        init_admin_tables()
        init_billing_tables()
        init_request_state_table()
        from app.db.career import init_career_tables
        init_career_tables()
        if is_prod:
            from app.admin.auth.admin_auth import validate_admin_security_configuration
            validate_admin_security_configuration(is_prod=True)
        logger.info("Application database initialization completed successfully.")
    except Exception as e:
        logger.error(f"Database initialization failure during startup: {e}", exc_info=True)
        if is_prod:
            raise RuntimeError(f"FATAL: Application failed to start due to configuration/database error: {e}")
    yield
    # Shutdown procedure
    try:
        from app.db.connection import close_pg_pool
        close_pg_pool()
        logger.info("Application shutdown completed successfully.")
    except Exception as e:
        logger.warning(f"Error during application shutdown: {e}")

app = FastAPI(
    title="Saarthi API",
    version="0.5.0-rc2",
    description="Saarthi Universal AI Operating Companion Operational API",
    lifespan=lifespan
)

# Global Exception Shield
app.add_exception_handler(Exception, global_exception_handler)

# Compression Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Custom Operational Middlewares (Execution order is bottom-up in Starlette stack)
app.add_middleware(RateLimiterMiddleware)
app.add_middleware(StructuredLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestIDMiddleware)

# CORS Policy — Exact Staging & Production Allowed Origins (No Wildcards)
ALLOWED_ORIGINS = [
    "http://staging.saarthi.trovanetech.com",
    "https://staging.saarthi.trovanetech.com",
    "http://admin-staging.saarthi.trovanetech.com",
    "https://admin-staging.saarthi.trovanetech.com",
    "http://api-staging.saarthi.trovanetech.com",
    "https://api-staging.saarthi.trovanetech.com",
    "http://staging.saarthi.trovanetech.com:8000",
    "http://admin-staging.saarthi.trovanetech.com:8000",
    "http://staging.saarthi.trovanetech.com:8080",
    "http://admin-staging.saarthi.trovanetech.com:8080",
    "http://staging.saarthi.trovanetech.com:3000",
    "http://admin-staging.saarthi.trovanetech.com:3001",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:8000",
    "http://localhost:8080",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8080",
]

env_cors = os.getenv("CORS_ALLOWED_ORIGINS", "")
if env_cors:
    for orig in env_cors.split(","):
        orig = orig.strip()
        if orig and orig not in ALLOWED_ORIGINS:
            ALLOWED_ORIGINS.append(orig)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Response-Time-MS"],
)

# Include API Routers
app.include_router(health_router)
app.include_router(health_router, prefix="/api")
app.include_router(beta_router, prefix="/api")
app.include_router(desktop_router, prefix="/api")
app.include_router(api_router, prefix="/api")
app.include_router(mcp_router, prefix="/api")
app.include_router(ops_router, prefix="/api")
app.include_router(ops_router, prefix="/admin")
app.include_router(admin_router)

# Mount production frontend build if available
app_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(app_dir)
root_dir = os.path.dirname(backend_dir)
meipass_dir = getattr(sys, '_MEIPASS', root_dir)
exe_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else root_dir

possible_frontend_dirs = [
    os.path.join(meipass_dir, "frontend", "dist"),
    os.path.join(exe_dir, "_internal", "frontend", "dist"),
    os.path.join(exe_dir, "frontend", "dist"),
    os.path.join(root_dir, "frontend", "dist"),
    os.path.join(root_dir, "_internal", "frontend", "dist"),
    os.path.join(app_dir, "..", "..", "frontend", "dist"),
]

frontend_dist = None
for f_dir in possible_frontend_dirs:
    norm_dir = os.path.normpath(f_dir)
    if os.path.exists(norm_dir) and os.path.isdir(norm_dir):
        frontend_dist = norm_dir
        break

if frontend_dist:
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static_frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=False)
