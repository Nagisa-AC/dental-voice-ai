"""
Dental Voice AI - Production FastAPI Application

A minimal webhook processor for dental practices with VAPI integration.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dental_voice_ai.core.config import settings
from dental_voice_ai.api.v1 import dental
import logging
import time
from datetime import datetime
from typing import Dict, Any

# Configure production logging
logging.basicConfig(
    level=settings.get_log_level(),
    format=settings.LOG_FORMAT,
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Dental Voice AI - Webhook Processor",
    description="""
    Minimal webhook processor for dental practices with VAPI integration.
    
    ## Features
    - 🎯 VAPI webhook availability checking
    - 🏥 Practice-specific webhook endpoints
    - 🔧 Production-grade error handling
    
    ## Integration
    - Compatible with VAPI voice AI platform
    - Minimal footprint for maximum performance
    """,
    version=settings.VERSION,
    docs_url="/docs" if not settings.is_production() else None,
    redoc_url="/redoc" if not settings.is_production() else None,
    openapi_url="/openapi.json" if not settings.is_production() else None
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.is_development() else settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    dental.router, 
    prefix="/dental", 
    tags=["Dental Voice AI"]
)


@app.on_event("startup")
async def startup_event():
    """Application startup event handler."""
    logger.info(f"🚀 Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"🌍 Environment: {settings.ENVIRONMENT}")
    
    # Validate configuration
    if settings.is_production():
        try:
            settings.validate_required_settings()
            logger.info("✅ Production configuration validated")
        except ValueError as e:
            logger.critical(f"❌ Configuration validation failed: {e}")
            raise
    
    logger.info("✅ Webhook processor ready")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event handler."""
    logger.info(f"🛑 Shutting down {settings.PROJECT_NAME}")


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