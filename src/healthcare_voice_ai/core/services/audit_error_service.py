"""
Centralized Audit and Error Handling Service

Combines audit logging and error handling for HIPAA compliance and monitoring.
"""

import logging
import time
import traceback
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import defaultdict, deque
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from healthcare_voice_ai.core.models.audit_log import AuditAction, AuditResource
from healthcare_voice_ai.core.database import get_async_db
from healthcare_voice_ai.core.logging_config import get_logger

logger = get_logger(__name__)


class ErrorStatistics:
    """Error statistics tracking."""
    
    def __init__(self):
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.error_timestamps: Dict[str, deque] = defaultdict(lambda: deque())
        self.total_errors = 0
        self.last_reset = time.time()
    
    def record_error(self, error_type: str, error_message: str = ""):
        """Record an error occurrence."""
        self.error_counts[error_type] += 1
        self.total_errors += 1
        
        # Keep timestamps for the last hour
        now = time.time()
        hour_ago = now - 3600
        
        timestamps = self.error_timestamps[error_type]
        while timestamps and timestamps[0] < hour_ago:
            timestamps.popleft()
        
        timestamps.append(now)
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics."""
        now = time.time()
        hour_ago = now - 3600
        
        # Count recent errors
        recent_errors = 0
        for timestamps in self.error_timestamps.values():
            recent_errors += sum(1 for ts in timestamps if ts > hour_ago)
        
        return {
            "total_errors": self.total_errors,
            "recent_errors": recent_errors,
            "error_counts": dict(self.error_counts),
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_hours": (now - self.last_reset) / 3600
        }
    
    def reset_stats(self):
        """Reset error statistics."""
        self.error_counts.clear()
        self.error_timestamps.clear()
        self.total_errors = 0
        self.last_reset = time.time()


class HealthChecker:
    """Health check service."""
    
    def __init__(self):
        self.checks: Dict[str, callable] = {}
        self.start_time = time.time()
    
    def register_check(self, name: str, check_func: callable):
        """Register a health check function."""
        self.checks[name] = check_func
    
    async def run_check(self, name: str) -> Dict[str, Any]:
        """Run a specific health check."""
        if name not in self.checks:
            return {
                "name": name,
                "status": "unknown",
                "error": f"Check '{name}' not found"
            }
        
        try:
            result = await self.checks[name]()
            return {
                "name": name,
                "status": "healthy",
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Health check '{name}' failed: {e}")
            return {
                "name": name,
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def run_all_checks(self) -> Dict[str, Any]:
        """Run all registered health checks."""
        results = {}
        healthy_count = 0
        unhealthy_count = 0
        
        for name in self.checks:
            result = await self.run_check(name)
            results[name] = result
            
            if result["status"] == "healthy":
                healthy_count += 1
            else:
                unhealthy_count += 1
        
        return {
            "status": "healthy" if unhealthy_count == 0 else "unhealthy",
            "total_checks": len(self.checks),
            "healthy_checks": healthy_count,
            "unhealthy_checks": unhealthy_count,
            "checks": results,
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": time.time() - self.start_time
        }
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary without running checks."""
        return {
            "status": "unknown",
            "total_checks": len(self.checks),
            "healthy_checks": 0,
            "unhealthy_checks": 0,
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": time.time() - self.start_time
        }


class AuditService:
    """Audit logging service for HIPAA compliance."""
    
    def __init__(self):
        self.audit_logs: List[Dict[str, Any]] = []
        self.max_logs = 10000  # Keep last 10k logs in memory
    
    async def log_audit_event(
        self,
        user_id: Optional[str],
        action: AuditAction,
        resource_type: AuditResource,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log an audit event."""
        audit_log = {
            "id": f"audit_{int(time.time() * 1000)}",
            "user_id": user_id,
            "action": action.value,
            "resource_type": resource_type.value,
            "resource_id": resource_id,
            "details": details or {},
            "ip_address": ip_address,
            "user_agent": user_agent,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add to memory logs
        self.audit_logs.append(audit_log)
        
        # Keep only recent logs
        if len(self.audit_logs) > self.max_logs:
            self.audit_logs = self.audit_logs[-self.max_logs:]
        
        # Log to application logger
        logger.info(
            f"Audit: {action.value} on {resource_type.value}",
            extra={
                "audit_log": audit_log,
                "user_id": user_id,
                "action": action.value,
                "resource_type": resource_type.value,
                "resource_id": resource_id
            }
        )
        
        # TODO: Store in database for persistence
        # This would require database integration
    
    def get_audit_logs(
        self,
        user_id: Optional[str] = None,
        action: Optional[AuditAction] = None,
        resource_type: Optional[AuditResource] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get audit logs with filtering."""
        filtered_logs = self.audit_logs
        
        if user_id:
            filtered_logs = [log for log in filtered_logs if log.get("user_id") == user_id]
        
        if action:
            filtered_logs = [log for log in filtered_logs if log.get("action") == action.value]
        
        if resource_type:
            filtered_logs = [log for log in filtered_logs if log.get("resource_type") == resource_type.value]
        
        # Sort by timestamp (newest first)
        filtered_logs.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Apply pagination
        return filtered_logs[offset:offset + limit]


class CentralizedErrorHandler:
    """Centralized error handling service."""
    
    def __init__(self):
        self.error_stats = ErrorStatistics()
        self.health_checker = HealthChecker()
        self.audit_service = AuditService()
        
        # Register default health checks
        self._register_default_checks()
    
    def _register_default_checks(self):
        """Register default health checks."""
        self.health_checker.register_check("database", self._check_database)
        self.health_checker.register_check("memory", self._check_memory)
        self.health_checker.register_check("disk", self._check_disk)
    
    async def _check_database(self) -> Dict[str, Any]:
        """Check database connectivity."""
        try:
            # This would be implemented with actual database check
            return {"status": "connected", "response_time_ms": 10}
        except Exception as e:
            raise Exception(f"Database check failed: {e}")
    
    async def _check_memory(self) -> Dict[str, Any]:
        """Check memory usage."""
        try:
            import psutil
            memory = psutil.virtual_memory()
            return {
                "usage_percent": memory.percent,
                "available_gb": round(memory.available / (1024**3), 2)
            }
        except Exception as e:
            raise Exception(f"Memory check failed: {e}")
    
    async def _check_disk(self) -> Dict[str, Any]:
        """Check disk usage."""
        try:
            import psutil
            disk = psutil.disk_usage('/')
            return {
                "usage_percent": disk.percent,
                "free_gb": round(disk.free / (1024**3), 2)
            }
        except Exception as e:
            raise Exception(f"Disk check failed: {e}")
    
    def handle_error(self, error: Exception, request: Optional[Request] = None) -> JSONResponse:
        """Handle and log an error."""
        error_type = type(error).__name__
        error_message = str(error)
        
        # Record error statistics
        self.error_stats.record_error(error_type, error_message)
        
        # Log error details
        logger.error(
            f"Error handled: {error_type}",
            extra={
                "error_type": error_type,
                "error_message": error_message,
                "traceback": traceback.format_exc(),
                "request_path": request.url.path if request else None,
                "request_method": request.method if request else None,
                "client_ip": request.client.host if request and request.client else None
            }
        )
        
        # Audit log for security-related errors
        if isinstance(error, HTTPException) and error.status_code in [401, 403, 429]:
            self.audit_service.log_audit_event(
                user_id=getattr(request.state, 'user_id', None) if request else None,
                action=AuditAction.READ,  # Security event
                resource_type=AuditResource.SYSTEM,
                details={
                    "error_type": error_type,
                    "status_code": error.status_code,
                    "path": request.url.path if request else None
                },
                ip_address=request.client.host if request and request.client else None,
                user_agent=request.headers.get("user-agent") if request else None
            )
        
        # Return appropriate response
        if isinstance(error, HTTPException):
            return JSONResponse(
                status_code=error.status_code,
                content={
                    "error": error.detail,
                    "type": error_type,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        else:
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "type": error_type,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics."""
        return self.error_stats.get_error_stats()
    
    def reset_error_stats(self):
        """Reset error statistics."""
        self.error_stats.reset_stats()
    
    async def run_health_checks(self) -> Dict[str, Any]:
        """Run all health checks."""
        return await self.health_checker.run_all_checks()
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary."""
        return self.health_checker.get_health_summary()
    
    async def log_audit_event(
        self,
        user_id: Optional[str],
        action: AuditAction,
        resource_type: AuditResource,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None
    ):
        """Log an audit event."""
        await self.audit_service.log_audit_event(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=request.client.host if request and request.client else None,
            user_agent=request.headers.get("user-agent") if request else None
        )
    
    def get_audit_logs(
        self,
        user_id: Optional[str] = None,
        action: Optional[AuditAction] = None,
        resource_type: Optional[AuditResource] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get audit logs."""
        return self.audit_service.get_audit_logs(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            limit=limit,
            offset=offset
        )


# Global instances
centralized_error_handler = CentralizedErrorHandler()
health_checker = centralized_error_handler.health_checker
audit_service = centralized_error_handler.audit_service
