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
from contextlib import asynccontextmanager
import logging
import os

from config.settings import settings
from config.database import init_db, drop_db
from api.routes import users, students, homework, payments, subscriptions, whatsapp, tutors, health
from admin.routes import api as admin_api
from utils.logger import get_logger
from services.monitoring_service import init_sentry
from middleware.monitoring import MonitoringMiddleware

logger = get_logger("main")


# Startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    # Startup
    logger.info("Starting WhatsApp Chatbot API")
    init_sentry()  # Initialize error tracking
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        logger.warning("Continuing startup - database will be initialized on first use")
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",    # Next.js dev server
        "http://localhost:8000",    # FastAPI server
        "http://localhost:8080",    # Alternative dev port
        "http://127.0.0.1:3000",    # IPv4 loopback Next.js
        os.getenv("ADMIN_ORIGIN", ""),  # Production domain from env
    ],
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
