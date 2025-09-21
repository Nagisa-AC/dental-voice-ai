"""
System monitoring and health check endpoints.
Consolidates monitoring, database performance, SSL status, and system metrics.
Integrates with Prometheus for comprehensive observability.
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Query
from fastapi.responses import JSONResponse, Response
import logging
import time
import ssl
import socket
from datetime import datetime
from typing import Dict, Any, Optional
import psutil
import asyncio
import platform
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

from ...core.config import settings
from ...core.database import db_manager
from ...core.auth import get_current_user, AuthUser, require_admin
from ...core.services.security_service import security_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/system", tags=["System Monitoring"])

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Number of active connections')
DATABASE_CONNECTIONS = Gauge('database_connections', 'Number of database connections')
MEMORY_USAGE = Gauge('memory_usage_bytes', 'Memory usage in bytes')
CPU_USAGE = Gauge('cpu_usage_percent', 'CPU usage percentage')
DISK_USAGE = Gauge('disk_usage_percent', 'Disk usage percentage')


@router.get("/health")
async def health_check(
    request: Request,
    detailed: bool = Query(False, description="Get detailed health information")
) -> Dict[str, Any]:
    """
    Comprehensive system health check.
    
    Returns overall health status with optional detailed information.
    """
    health_status = {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "database": "unknown",
            "memory": "unknown",
            "disk": "unknown",
            "ssl": "unknown"
        }
    }
    
    # Check database connectivity
    try:
        db_healthy = await db_manager.health_check()
        health_status["checks"]["database"] = "healthy" if db_healthy else "unhealthy"
        if not db_healthy:
            health_status["status"] = "unhealthy"
    except Exception as e:
        health_status["checks"]["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check memory usage
    try:
        memory = psutil.virtual_memory()
        health_status["checks"]["memory"] = {
            "status": "healthy" if memory.percent < 90 else "warning",
            "usage_percent": memory.percent,
            "available_gb": round(memory.available / (1024**3), 2)
        }
        if memory.percent > 95:
            health_status["status"] = "unhealthy"
    except Exception as e:
        health_status["checks"]["memory"] = f"error: {str(e)}"
    
    # Check disk usage
    try:
        disk = psutil.disk_usage('/')
        health_status["checks"]["disk"] = {
            "status": "healthy" if disk.percent < 90 else "warning",
            "usage_percent": disk.percent,
            "free_gb": round(disk.free / (1024**3), 2)
        }
    except Exception as e:
        health_status["checks"]["disk"] = f"error: {str(e)}"
    
    # Check SSL status
    try:
        ssl_status = await check_ssl_status()
        health_status["checks"]["ssl"] = ssl_status
    except Exception as e:
        health_status["checks"]["ssl"] = f"error: {str(e)}"
    
    return health_status


@router.get("/metrics")
async def get_system_metrics(
    request: Request,
    current_user: AuthUser = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Get detailed system metrics and statistics (admin only).
    
    Returns comprehensive system information including performance metrics,
    error statistics, and system information.
    """
    try:
        logger.info("System metrics requested", user_id=current_user.user_id)
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory usage
        memory = psutil.virtual_memory()
        
        # Disk usage
        disk = psutil.disk_usage('/')
        
        # Network I/O
        network = psutil.net_io_counters()
        
        # Database performance metrics
        db_metrics = await get_database_metrics()
        
        # System information
        system_info = {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": cpu_count,
            "memory_total": memory.total,
            "memory_available": memory.available,
            "disk_usage": disk.percent,
        }
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "cpu": {
                "usage_percent": cpu_percent,
                "count": cpu_count
            },
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "usage_percent": memory.percent
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "usage_percent": disk.percent
            },
            "network": {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            },
            "database": db_metrics,
            "system_info": system_info,
            "request_info": {
                "user_id": current_user.user_id,
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent")
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system metrics")


@router.get("/status")
async def get_status(
    request: Request,
    current_user: AuthUser = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get application status information.
    
    Returns basic status information about the application including
    health summary and error statistics.
    """
    try:
        logger.info("Status requested", user_id=current_user.user_id)
        
        # Get basic health information
        health_status = {
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Check database connectivity
        try:
            db_healthy = await db_manager.health_check()
            health_status["database_status"] = "healthy" if db_healthy else "unhealthy"
        except Exception as e:
            health_status["database_status"] = f"error: {str(e)}"
        
        # Get system resource status
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            health_status["system_status"] = {
                "memory_usage_percent": memory.percent,
                "disk_usage_percent": disk.percent,
                "status": "operational" if memory.percent < 90 and disk.percent < 90 else "degraded"
            }
        except Exception as e:
            health_status["system_status"] = f"error: {str(e)}"
        
        # Determine overall status
        overall_status = "operational"
        if health_status["database_status"] != "healthy":
            overall_status = "degraded"
        if health_status["system_status"].get("status") == "degraded":
            overall_status = "degraded"
            
        health_status["status"] = overall_status
        
        return health_status
        
    except Exception as e:
        logger.error(f"Failed to get status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get status: {str(e)}"
        )


@router.get("/database/performance")
async def get_database_performance(current_user: AuthUser = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get database performance metrics.
    """
    try:
        metrics = await get_database_metrics()
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "database_performance": metrics
        }
        
    except Exception as e:
        logger.error(f"Error getting database performance: {e}")
        raise HTTPException(status_code=500, detail="Failed to get database performance")


@router.get("/ssl/status")
async def get_ssl_status(current_user: AuthUser = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get SSL/TLS certificate status.
    """
    try:
        ssl_status = await check_ssl_status()
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "ssl_status": ssl_status
        }
        
    except Exception as e:
        logger.error(f"Error getting SSL status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get SSL status")


async def get_database_metrics() -> Dict[str, Any]:
    """Get database performance metrics."""
    try:
        # This would be implemented with actual database metrics
        # For now, return basic connection info
        return {
            "connection_pool_size": getattr(db_manager, 'pool_size', 'unknown'),
            "active_connections": 'unknown',  # Would need actual implementation
            "query_performance": 'unknown'    # Would need actual implementation
        }
    except Exception as e:
        logger.error(f"Error getting database metrics: {e}")
        return {"error": str(e)}


async def check_ssl_status() -> Dict[str, Any]:
    """Check SSL certificate status."""
    try:
        # Check if we're running with SSL
        if not settings.ENFORCE_HTTPS:
            return {"status": "disabled", "reason": "HTTPS not enforced"}
        
        # This would check actual SSL certificate status
        # For now, return basic status
        return {
            "status": "enabled",
            "enforce_https": settings.ENFORCE_HTTPS,
            "hsts_enabled": True,
            "certificate_valid": True  # Would need actual certificate checking
        }
    except Exception as e:
        logger.error(f"Error checking SSL status: {e}")
        return {"status": "error", "error": str(e)}


@router.get("/metrics")
async def get_prometheus_metrics():
    """
    Prometheus metrics endpoint for monitoring.
    """
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@router.get("/status")
async def get_system_status(current_user: AuthUser = Depends(require_admin)):
    """
    Get comprehensive system status with Prometheus metrics integration.
    """
    try:
        # Update Prometheus metrics
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)
        disk = psutil.disk_usage('/')
        
        MEMORY_USAGE.set(memory.used)
        CPU_USAGE.set(cpu_percent)
        DISK_USAGE.set(disk.percent)
        
        # Get database connection count
        db_healthy = await db_manager.health_check()
        DATABASE_CONNECTIONS.set(1 if db_healthy else 0)
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "healthy" if db_healthy else "unhealthy",
            "metrics": {
                "memory_usage_percent": memory.percent,
                "cpu_usage_percent": cpu_percent,
                "disk_usage_percent": disk.percent,
                "database_healthy": db_healthy
            },
            "prometheus_metrics_available": True
        }
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system status")
