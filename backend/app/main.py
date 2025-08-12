"""
Dental Voice AI - Production FastAPI Application

A production-ready voice AI system for dental practices with VAPI integration,
intelligent FAQ matching, and comprehensive call analytics.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import supabase
from app.core.config import settings
from app.api.v1 import dental
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
    title="Dental Voice AI - FAQ Processor",
    description="""
    Production-ready AI-powered voice assistant for dental practices.
    
    ## Features
    - 🎯 VAPI webhook processing for dental calls
    - 🧠 Intelligent FAQ matching with semantic similarity  
    - 🏥 Practice-specific response generation
    - 📊 Real-time call analysis and logging
    - 🔍 Advanced dental intent recognition
    
    ## Integration
    - Compatible with VAPI voice AI platform
    - Supabase database for multi-practice data
    - Production-grade error handling and monitoring
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
    
    # Log database status
    db_status = "✅ Connected" if supabase else "❌ Not available"
    logger.info(f"📊 Database status: {db_status}")


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


@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """
    Comprehensive health check endpoint.
    
    Returns:
        Detailed system health information including database connectivity
        
    Raises:
        HTTPException: If critical system components are unavailable
    """
    health_check_id = int(time.time() * 1000)
    
    try:
        # Database connectivity check
        db_status = "unknown"
        db_response_time = None
        
        if supabase is None:
            db_status = "unavailable"
            logger.warning(f"[{health_check_id}] Database client not available")
        else:
            try:
                start_time = time.time()
                supabase.table("calls").select("id").limit(1).execute()
                db_response_time = round((time.time() - start_time) * 1000, 2)
                db_status = "connected"
            except Exception as e:
                db_status = "error"
                logger.error(f"[{health_check_id}] Database health check failed: {e}")
        
        # Determine overall status
        overall_status = "healthy" if db_status == "connected" else "degraded"
        
        health_response = {
            "status": overall_status,
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "timestamp": datetime.utcnow().isoformat(),
            "health_check_id": health_check_id,
            "components": {
                "database": {
                    "status": db_status,
                    "response_time_ms": db_response_time
                },
                "webhook_handler": {
                    "status": "available",
                    "endpoint": "/dental/incoming_call"
                },
                "appointment_webhook": {
                    "status": "available",
                    "endpoints": ["/appointments/appointment_change", "/appointments/availability_change"]
                },
                "api": {
                    "status": "available",
                    "docs_enabled": not settings.is_production()
                }
            }
        }
        
        # Return appropriate status code
        status_code = 200 if overall_status == "healthy" else 503
        if status_code != 200:
            raise HTTPException(status_code=status_code, detail=health_response)
        
        return health_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{health_check_id}] Health check system error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "status": "unhealthy",
                "service": settings.PROJECT_NAME,
                "timestamp": datetime.utcnow().isoformat(),
                "health_check_id": health_check_id,
                "error": "Health check system failure"
            }
        )


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