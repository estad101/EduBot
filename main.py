"""
FastAPI application - WhatsApp Chatbot Backend.

Production-grade chatbot system for homework submission and payments.
Integrates with WhatsApp Cloud API and Paystack.
Includes native WhatsApp message handling (no n8n required).
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from contextlib import asynccontextmanager
import logging
import os

from config.settings import settings
from config.database import init_db, drop_db, SessionLocal
from api.routes import users, students, homework, payments, subscriptions, whatsapp, tutors, health
from admin.routes import api as admin_api
from utils.logger import get_logger
from services.monitoring_service import init_sentry
from services.settings_service import init_settings_from_db
from middleware.monitoring import MonitoringMiddleware

logger = get_logger("main")


# Startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    # Startup
    logger.info("Starting WhatsApp Chatbot API")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Database URL: {settings.database_url.split('@')[0]}...{settings.database_url.split('/')[-1] if '/' in settings.database_url else 'invalid'}")
    
    # Initialize Sentry for error tracking (non-blocking)
    try:
        init_sentry()
    except Exception as e:
        logger.warning(f"Sentry initialization failed: {e}")
    
    # Initialize database in background - DON'T WAIT
    try:
        import asyncio
        db_task = asyncio.create_task(
            asyncio.to_thread(init_db)
        )
        logger.info("Database initialization started in background")
    except Exception as e:
        logger.warning(f"Could not start database initialization: {e}")
    
    # Initialize settings from database in background - DON'T WAIT
    # App will use environment variables as fallback until settings load
    try:
        import asyncio
        async def load_settings_async():
            try:
                from threading import Thread
                def load_settings():
                    try:
                        db = SessionLocal()
                        try:
                            if init_settings_from_db(db):
                                logger.info("WhatsApp settings loaded from database")
                            else:
                                logger.info("Using environment variables as fallback for settings")
                        finally:
                            db.close()
                    except Exception as e:
                        logger.warning(f"Settings load failed, using env vars: {e}")
                
                thread = Thread(target=load_settings, daemon=True)
                thread.start()
            except Exception as e:
                logger.warning(f"Could not start settings load: {e}")
        
        asyncio.create_task(load_settings_async())
        logger.info("Settings initialization started in background")
    except Exception as e:
        logger.warning(f"Could not start settings initialization: {e}")
    
    logger.info("=== APPLICATION READY ===")
    yield
    # Shutdown
    logger.info("Shutting down WhatsApp Chatbot API")


# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="Production-grade WhatsApp chatbot for homework submission with Paystack integration",
    lifespan=lifespan,
)

# Security middleware - add security headers
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        # Enable XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # Content Security Policy for admin panel
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' cdn.tailwindcss.com cdn.jsdelivr.net cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' cdnjs.cloudflare.com cdn.tailwindcss.com; img-src 'self' data: https:; font-src 'self' cdnjs.cloudflare.com"
        return response

# Add monitoring middleware (must be before security headers)
app.add_middleware(MonitoringMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

# CORS middleware - restrict origins in production
# Includes Next.js dev server (localhost:3000) and production domains
# Build allowed origins list dynamically
cors_allowed_origins = [
    "http://localhost:3000",    # Next.js dev server
    "http://localhost:8000",    # FastAPI server
    "http://localhost:8080",    # Alternative dev port
    "http://127.0.0.1:3000",    # IPv4 loopback Next.js
    "https://nurturing-exploration-production.up.railway.app",  # Current Railway frontend
    "https://proactive-insight-production-6462.up.railway.app",  # Old Railway frontend (legacy)
    "https://edubot-production-cf26.up.railway.app",  # Backend service (for admin status checks)
]

# Add environment-configured origins
if settings.allow_origins:
    extra_origins = [o.strip() for o in settings.allow_origins.split(",") if o.strip()]
    cors_allowed_origins.extend(extra_origins)

# Remove duplicates and empty strings
cors_allowed_origins = list(set(o for o in cors_allowed_origins if o))

logger.info(f"CORS allowed origins: {cors_allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-CSRF-Token"],
)

# Session middleware for admin panel
from starlette.middleware.sessions import SessionMiddleware
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key, https_only=False, same_site="strict")


# Custom exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    logger.error(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
            "error_code": "HTTP_ERROR",
        },
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle validation errors."""
    logger.error(f"Validation error: {str(exc)}")
    return JSONResponse(
        status_code=422,
        content={
            "status": "validation_error",
            "message": str(exc),
            "error_code": "VALIDATION_ERROR",
        },
    )


# Include routers
app.include_router(users.router)
app.include_router(students.router)
app.include_router(homework.router)
app.include_router(payments.router)
app.include_router(subscriptions.router)
app.include_router(whatsapp.router)  # WhatsApp webhook endpoint
app.include_router(health.router)  # Health check endpoints
app.include_router(tutors.router)  # Tutor endpoints

# Include admin routers
app.include_router(admin_api.router)

# Mount static files for admin panel
admin_static_path = os.path.join(os.path.dirname(__file__), "admin", "static")
if os.path.exists(admin_static_path):
    app.mount("/admin/static", StaticFiles(directory=admin_static_path), name="admin_static")

# Mount uploads directory for homework file access
# Try Railway volume path first, fallback to local
uploads_path = None
railway_uploads = "/app/uploads"
local_uploads = os.path.join(os.path.dirname(__file__), "uploads")

# On Railway, use persistent volume path
if os.path.exists(railway_uploads):
    uploads_path = railway_uploads
    logger.info(f"Using Railway persistent volume: {uploads_path}")
else:
    uploads_path = local_uploads
    logger.info(f"Using local uploads directory: {uploads_path}")

# Ensure directory exists
os.makedirs(uploads_path, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_path), name="uploads")


# File serving endpoint with security
@app.get("/files/{file_path:path}")
async def get_file(file_path: str):
    """
    Serve uploaded files with security checks.
    Prevents directory traversal attacks.
    Works with Railway persistent volume and local uploads.
    """
    # Security: prevent directory traversal
    if ".." in file_path or file_path.startswith("/"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Try to find file in Railway volume or local directory
    railway_uploads = "/app/uploads"
    local_uploads = os.path.join(os.path.dirname(__file__), "uploads")
    
    # Construct full file path - try Railway first
    full_path = os.path.join(railway_uploads, file_path) if os.path.exists(railway_uploads) else os.path.join(local_uploads, file_path)
    
    # Verify file exists and is within appropriate uploads directory
    abs_path = os.path.abspath(full_path)
    
    # Check against both possible upload directories
    railway_abs = os.path.abspath(railway_uploads)
    local_abs = os.path.abspath(local_uploads)
    
    if not (abs_path.startswith(railway_abs) or abs_path.startswith(local_abs)):
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not os.path.exists(abs_path):
        logger.warning(f"File not found: {full_path} (abs: {abs_path})")
        raise HTTPException(status_code=404, detail="File not found")
    
    logger.info(f"Serving file: {abs_path}")
    return FileResponse(abs_path)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": settings.api_title,
        "version": settings.api_version,
    }


# API documentation
@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "docs": "/docs",
        "openapi": "/openapi.json",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting {settings.api_title} on port {settings.api_port}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.api_port,
        log_level=settings.log_level.lower(),
    )
