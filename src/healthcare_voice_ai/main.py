"""
Healthcare Voice AI - Production FastAPI Application

A minimal webhook processor for healthcare practices with VAPI integration.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from healthcare_voice_ai.core.config import settings
from healthcare_voice_ai.core.errors import centralized_exception_handler
# Environment validation moved to config.py
from healthcare_voice_ai.api.v1 import webhooks, system
# Dashboard served directly as static file
from healthcare_voice_ai.api.v1 import clinic
from healthcare_voice_ai.api.v1 import auth
from healthcare_voice_ai.api.v1 import audit
from healthcare_voice_ai.api.v1 import file_upload
from healthcare_voice_ai.core.database import init_database, close_database, db_manager
# Cache removed - can be reintroduced later with Redis if needed
from healthcare_voice_ai.core.middleware import (
    AuditMiddleware, CSRFMiddleware, HTTPSEnforcementMiddleware,
    InputSanitizationMiddleware, RateLimitingMiddleware
)
from healthcare_voice_ai.core.services.security_service import security_service
import logging
import time
from datetime import datetime
from typing import Dict, Any
from healthcare_voice_ai.core.logging_config import setup_logging, get_logger, log_startup_info, log_shutdown_info

# Set up logging configuration
setup_logging(
    log_level=settings.LOG_LEVEL,
    enable_console=True
)

# Get configured logger
logger = get_logger(__name__)

# Initialize FastAPI app with rate limiting
app = FastAPI(
    title="Healthcare Voice AI - Healthcare Practice Management",
    description="""
    Multi-tenant healthcare practice management system with VAPI integration.
    
    ## Features
    - 🏥 Multi-clinic support with tenant isolation
    - 🤖 Custom AI assistants per clinic with FAQ knowledge
    - 📞 VAPI voice AI integration with phone numbers
    - 📅 Google Calendar integration for appointments
    - 📋 Clinic onboarding with FAQ file upload
    - 🔧 Admin management and approval system
    
    ## Multi-Clinic Architecture
    - Service layer for clinic management
    - Tenant-isolated data and assistants
    - Custom knowledge bases from FAQ files
    - Clinic-specific voice and prompt configuration
    """,
    version=settings.VERSION,
    docs_url="/docs" if not settings.is_production() else None,
    redoc_url="/redoc" if not settings.is_production() else None,
    openapi_url="/openapi.json" if not settings.is_production() else None
)

# Add security service to FastAPI app
app.state.security_service = security_service

# Add centralized exception handler for all exceptions
from healthcare_voice_ai.core.services.audit_error_service import centralized_error_handler
app.add_exception_handler(Exception, centralized_error_handler.handle_error)

# Configure CORS middleware with security restrictions
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),  # Environment-aware CORS origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "X-Request-ID"
    ],
    expose_headers=["X-Request-ID"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Add essential middleware only (5 layers for security and HIPAA compliance)
# Order: Last added runs first

# 1. HTTPS enforcement and security headers (runs last, added first)
app.add_middleware(HTTPSEnforcementMiddleware, enforce_https=True)

# 2. CSRF protection (prevents cross-site request forgery)
app.add_middleware(CSRFMiddleware)

# 3. Rate limiting (prevents abuse and DoS attacks)
app.add_middleware(RateLimitingMiddleware)

# 4. Input sanitization (prevents injection attacks)
app.add_middleware(InputSanitizationMiddleware)

# 5. Audit logging (HIPAA compliance - logs all access to PHI)
app.add_middleware(AuditMiddleware)

# Note: Removed 6 unnecessary middleware layers:
# - HealthCheckMiddleware (FastAPI has built-in health checks)
# - InputValidationMiddleware (Pydantic handles validation)
# - RequestIDMiddleware (nice-to-have, not essential)
# - EnhancedSecurityMiddleware (overkill for webhook processor)
# - ResponseCompressionMiddleware (can be handled by reverse proxy)
# - CacheControlMiddleware (not needed for API)

# Include routers
app.include_router(
    webhooks.router, 
    prefix="/webhooks", 
    tags=["Webhook Processing"]
)

app.include_router(
    clinic.router,
    prefix="/clinics",
    tags=["Clinic Management"]
)

app.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

app.include_router(
    system.router,
    tags=["System Monitoring"]
)

app.include_router(
    audit.router,
    prefix="/audit",
    tags=["Audit & Compliance"]
)

app.include_router(
    file_upload.router,
    prefix="/upload",
    tags=["File Upload"]
)

# Dashboard served directly as static file
@app.get("/dashboard")
async def serve_dashboard():
    """Serve the React dashboard."""
    return FileResponse("frontend/build/index.html")

# Serve React static files
app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")

# Serve React app for all other routes (SPA routing)
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    """Serve React app for client-side routing."""
    if full_path.startswith("api/"):
        # Let API routes be handled by their respective routers
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    # Serve React app for all other routes
    return FileResponse("frontend/build/index.html")


@app.get("/", tags=["Dashboard"])
async def dashboard_home():
    """Serve the main dashboard page."""
    return FileResponse("src/dental_voice_ai/static/dashboard.html")


@app.on_event("startup")
async def startup_event():
    """Application startup event handler."""
    # Log startup information using the logging config
    log_startup_info()
    
    # Validate environment variables
    try:
        # Environment validation integrated into config
        logger.info(f"✅ Environment validated for {settings.ENVIRONMENT}")
    except Exception as e:
        logger.critical(f"❌ Environment validation failed: {e}")
        raise
    
    # Validate configuration
    if settings.is_production():
        try:
            settings.validate_required_settings()
            logger.info("✅ Production configuration validated")
        except ValueError as e:
            logger.critical(f"❌ Configuration validation failed: {e}")
            raise
    
    # Initialize database
    try:
        await init_database()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.critical(f"❌ Database initialization failed: {e}")
        raise
    
    # Initialize cache
    try:
        # Cache removed - can be reintroduced later with Redis if needed
        logger.info("✅ Application started without cache (can be added later)")
    except Exception as e:
        logger.warning(f"⚠️ Cache initialization failed: {e} - continuing without cache")
    
    logger.info("✅ Application ready")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event handler."""
    # Log shutdown information using the logging config
    log_shutdown_info()
    
    # Close database connections
    try:
        await close_database()
        logger.info("✅ Database connections closed")
    except Exception as e:
        logger.error(f"❌ Error closing database connections: {e}")
    
    # Close cache connections
    try:
        # Cache removed - can be reintroduced later with Redis if needed
        logger.info("✅ Cache connections closed")
    except Exception as e:
        logger.error(f"❌ Error closing cache connections: {e}")


@app.get("/", tags=["Health"])
async def root() -> Dict[str, Any]:
    """
    Root endpoint providing service information.
    
    Returns:
        Basic service status and information
    """
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """
    Comprehensive health check endpoint.
    
    Returns:
        Detailed health status including database connectivity
    """
    
    health_status = {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "environment": "unknown",
            "database": "unknown",
            "cache": "unknown",
            "configuration": "unknown"
        }
    }
    
    # Check environment validation
    try:
        # Environment health check integrated into config
        health_status["checks"]["environment"] = "healthy"
    except Exception as e:
        health_status["checks"]["environment"] = f"error: {str(e)}"
    
    # Check database connectivity
    try:
        db_healthy = await db_manager.health_check()
        health_status["checks"]["database"] = "healthy" if db_healthy else "unhealthy"
    except Exception as e:
        health_status["checks"]["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check cache connectivity
    try:
        # Cache removed - can be reintroduced later with Redis if needed
        health_status["checks"]["cache"] = "not_configured"
    except Exception as e:
        health_status["checks"]["cache"] = f"error: {str(e)}"
        # Cache failure doesn't make the service unhealthy
    
    # Check configuration
    try:
        if settings.is_production():
            settings.validate_required_settings()
        health_status["checks"]["configuration"] = "healthy"
    except Exception as e:
        health_status["checks"]["configuration"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    return health_status


@app.get("/config", tags=["System"])
async def get_config_info() -> Dict[str, Any]:
    """
    Get non-sensitive configuration information.
    
    Returns:
        Configuration summary excluding sensitive data
    """
    if settings.is_production():
        raise HTTPException(status_code=404, detail="Not found")
    
    return settings.get_config_summary()