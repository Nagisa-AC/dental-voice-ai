"""
Simplified Monitoring System for Healthcare Voice AI

Provides essential monitoring, metrics, health checks, and application constants.
Consolidates functionality from monitoring/, analytics/, observability, and constants modules.
"""

import logging
import time
import asyncio
import psutil
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json

logger = logging.getLogger(__name__)


# ============================================================================
# APPLICATION CONSTANTS
# ============================================================================

class AppConstants:
    """Application-wide constants."""
    
    # Version and Metadata
    VERSION = "2.0.0"
    PROJECT_NAME = "Dental Voice AI - Dental Practice Management"
    
    # Default Timeouts (in seconds)
    DEFAULT_REQUEST_TIMEOUT = 30
    DEFAULT_DATABASE_TIMEOUT = 10
    DEFAULT_CACHE_TIMEOUT = 5
    DEFAULT_HTTP_TIMEOUT = 30
    
    # Retry Configuration
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_RETRY_DELAY = 1.0
    DEFAULT_MAX_RETRY_DELAY = 60.0
    DEFAULT_RETRY_BACKOFF_FACTOR = 2.0
    
    # Rate Limiting
    DEFAULT_RATE_LIMIT_PER_MINUTE = 100
    LOGIN_RATE_LIMIT_PER_MINUTE = 10
    UPLOAD_RATE_LIMIT_PER_MINUTE = 5
    
    # Cache TTL (in seconds)
    CACHE_TTL_SHORT = 300      # 5 minutes
    CACHE_TTL_MEDIUM = 1800    # 30 minutes
    CACHE_TTL_LONG = 3600      # 1 hour
    CACHE_TTL_VERY_LONG = 7200 # 2 hours
    
    # JWT Configuration
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7
    JWT_ALGORITHM = "HS256"
    
    # Password Hashing
    BCRYPT_ROUNDS = 12
    
    # File Upload Limits
    MAX_FILE_SIZE_MB = 10
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
    ALLOWED_FILE_EXTENSIONS = [".txt", ".md", ".doc", ".docx"]
    
    # Health Check
    HEALTH_CHECK_TIMEOUT = 5
    HEALTH_CHECK_INTERVAL = 30


class BusinessConstants:
    """Business-specific constants."""
    
    # Office Status
    OFFICE_STATUS_PENDING = "pending"
    OFFICE_STATUS_APPROVED = "approved"
    OFFICE_STATUS_REJECTED = "rejected"
    OFFICE_STATUS_ACTIVE = "active"
    OFFICE_STATUS_INACTIVE = "inactive"
    
    # User Roles
    USER_ROLE_ADMIN = "admin"
    USER_ROLE_OFFICE_OWNER = "office_owner"
    USER_ROLE_OFFICE_STAFF = "office_staff"
    USER_ROLE_READONLY = "readonly"
    
    # Default Services
    DEFAULT_DENTAL_SERVICES = [
        "General Dentistry",
        "Teeth Cleaning",
        "Fillings",
        "Crowns",
        "Root Canal",
        "Extractions",
        "Teeth Whitening",
        "Orthodontics",
        "Periodontics",
        "Oral Surgery"
    ]
    
    # Default Business Hours
    DEFAULT_BUSINESS_HOURS = {
        "monday": "9:00 AM - 5:00 PM",
        "tuesday": "9:00 AM - 5:00 PM",
        "wednesday": "9:00 AM - 5:00 PM",
        "thursday": "9:00 AM - 5:00 PM",
        "friday": "9:00 AM - 5:00 PM",
        "saturday": "Closed",
        "sunday": "Closed"
    }


# ============================================================================
# MONITORING SYSTEM
# ============================================================================


class AlertSeverity(Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Metric:
    """Simple metric data structure."""
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = {}


@dataclass
class HealthCheck:
    """Health check result."""
    name: str
    status: str  # "healthy", "degraded", "unhealthy"
    message: str
    timestamp: datetime
    details: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}


class MonitoringService:
    """Simplified monitoring service for dental practice operations."""
    
    def __init__(self):
        self.start_time = time.time()
        self.metrics: Dict[str, List[Metric]] = {}
        self.health_checks: Dict[str, HealthCheck] = {}
        self.alerts: List[Dict[str, Any]] = []
        
    def record_metric(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a metric value."""
        if name not in self.metrics:
            self.metrics[name] = []
        
        metric = Metric(
            name=name,
            value=value,
            timestamp=datetime.utcnow(),
            tags=tags or {}
        )
        
        self.metrics[name].append(metric)
        
        # Keep only last 1000 metrics per name
        if len(self.metrics[name]) > 1000:
            self.metrics[name] = self.metrics[name][-1000:]
    
    def get_metric_summary(self, name: str, minutes: int = 60) -> Dict[str, Any]:
        """Get metric summary for the last N minutes."""
        if name not in self.metrics:
            return {"error": "Metric not found"}
        
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        recent_metrics = [
            m for m in self.metrics[name] 
            if m.timestamp >= cutoff
        ]
        
        if not recent_metrics:
            return {"error": "No recent data"}
        
        values = [m.value for m in recent_metrics]
        
        return {
            "name": name,
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "latest": values[-1] if values else None,
            "period_minutes": minutes
        }
    
    def add_health_check(self, name: str, status: str, message: str, details: Dict[str, Any] = None):
        """Add or update a health check."""
        self.health_checks[name] = HealthCheck(
            name=name,
            status=status,
            message=message,
            timestamp=datetime.utcnow(),
            details=details or {}
        )
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # Uptime
            uptime_seconds = time.time() - self.start_time
            
            # Overall health status
            overall_status = "healthy"
            if cpu_percent > 80 or memory.percent > 80 or disk.percent > 90:
                overall_status = "degraded"
            if cpu_percent > 95 or memory.percent > 95 or disk.percent > 95:
                overall_status = "unhealthy"
            
            return {
                "status": overall_status,
                "timestamp": datetime.utcnow().isoformat(),
                "uptime_seconds": uptime_seconds,
                "system": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available_gb": memory.available / (1024**3),
                    "disk_percent": disk.percent,
                    "disk_free_gb": disk.free / (1024**3)
                },
                "health_checks": {
                    name: {
                        "status": hc.status,
                        "message": hc.message,
                        "timestamp": hc.timestamp.isoformat(),
                        "details": hc.details
                    }
                    for name, hc in self.health_checks.items()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics."""
        summary = {}
        
        for name, metrics in self.metrics.items():
            if metrics:
                values = [m.value for m in metrics]
                summary[name] = {
                    "count": len(values),
                    "latest": values[-1],
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values)
                }
        
        return summary
    
    def add_alert(self, severity: AlertSeverity, message: str, details: Dict[str, Any] = None):
        """Add an alert."""
        alert = {
            "id": f"alert_{int(time.time())}",
            "severity": severity.value,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {}
        }
        
        self.alerts.append(alert)
        
        # Keep only last 100 alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
        
        logger.warning(f"Alert [{severity.value}]: {message}")
    
    def get_recent_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent alerts."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        return [
            alert for alert in self.alerts
            if datetime.fromisoformat(alert["timestamp"]) >= cutoff
        ]


# Global monitoring service instance
monitoring_service = MonitoringService()


# Convenience functions
def record_metric(name: str, value: float, tags: Dict[str, str] = None):
    """Record a metric value."""
    monitoring_service.record_metric(name, value, tags)


def add_health_check(name: str, status: str, message: str, details: Dict[str, Any] = None):
    """Add or update a health check."""
    monitoring_service.add_health_check(name, status, message, details)


def add_alert(severity: AlertSeverity, message: str, details: Dict[str, Any] = None):
    """Add an alert."""
    monitoring_service.add_alert(severity, message, details)


def get_system_health() -> Dict[str, Any]:
    """Get overall system health."""
    return monitoring_service.get_system_health()


def get_metrics_summary() -> Dict[str, Any]:
    """Get metrics summary."""
    return monitoring_service.get_metrics_summary()


def get_recent_alerts(hours: int = 24) -> List[Dict[str, Any]]:
    """Get recent alerts."""
    return monitoring_service.get_recent_alerts(hours)
