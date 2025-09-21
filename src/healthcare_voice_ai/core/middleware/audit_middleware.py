"""
Audit Middleware for HIPAA Compliance

Automatically logs API requests and responses for audit trail.
"""

import logging
import time
from typing import Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ..services.audit_error_service import audit_service
from ..models.audit_log import AuditAction, AuditResource
from ..database import get_async_db

logger = logging.getLogger(__name__)


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware for automatic audit logging of API requests.
    
    Logs all requests to track access to protected health information (PHI)
    for HIPAA compliance.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.excluded_paths = {
            "/health",
            "/ping",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/static",
            "/favicon.ico"
        }
        
        # Map HTTP methods to audit actions
        self.method_to_action = {
            "GET": AuditAction.READ,
            "POST": AuditAction.CREATE,
            "PUT": AuditAction.UPDATE,
            "PATCH": AuditAction.UPDATE,
            "DELETE": AuditAction.DELETE
        }
        
        # Map URL patterns to resource types
        self.path_to_resource = {
            "/clinics": AuditResource.CLINIC,
            "/webhooks": AuditResource.SYSTEM,
            "/auth": AuditResource.USER,
            "/monitoring": AuditResource.SYSTEM
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and log audit event.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain
            
        Returns:
            HTTP response
        """
        # Skip audit logging for excluded paths
        if request.url.path in self.excluded_paths or request.url.path.startswith("/static"):
            return await call_next(request)
        
        # Extract request information
        start_time = time.time()
        user_id = self._get_user_id(request)
        user_email = self._get_user_email(request)
        tenant_id = self._get_tenant_id(request)
        ip_address = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent")
        request_id = getattr(request.state, "request_id", None)
        
        # Determine audit action and resource type
        action = self.method_to_action.get(request.method, AuditAction.ACCESS)
        resource_type = self._get_resource_type(request.url.path)
        resource_id = self._get_resource_id(request.url.path)
        
        # Create description
        description = f"{request.method} {request.url.path}"
        
        # Process request
        try:
            response = await call_next(request)
            success = response.status_code < 400
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Log audit event
            await self._log_audit_event(
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                tenant_id=tenant_id,
                user_id=user_id,
                user_email=user_email,
                description=description,
                details={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "processing_time": processing_time,
                    "query_params": dict(request.query_params) if request.query_params else None
                },
                ip_address=ip_address,
                user_agent=user_agent,
                request_id=request_id,
                success=success
            )
            
            return response
            
        except Exception as e:
            # Log failed request
            processing_time = time.time() - start_time
            
            await self._log_audit_event(
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                tenant_id=tenant_id,
                user_id=user_id,
                user_email=user_email,
                description=f"{description} (FAILED: {str(e)})",
                details={
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e),
                    "processing_time": processing_time
                },
                ip_address=ip_address,
                user_agent=user_agent,
                request_id=request_id,
                success=False
            )
            
            raise
    
    def _get_user_id(self, request: Request) -> Optional[str]:
        """Extract user ID from request."""
        # Try to get from request state (set by auth middleware)
        user = getattr(request.state, "user", None)
        if user and hasattr(user, "id"):
            return str(user.id)
        
        # Try to get from JWT token
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # In a real implementation, you'd decode the JWT here
            # For now, we'll return None
            pass
        
        return None
    
    def _get_user_email(self, request: Request) -> Optional[str]:
        """Extract user email from request."""
        user = getattr(request.state, "user", None)
        if user and hasattr(user, "email"):
            return user.email
        return None
    
    def _get_tenant_id(self, request: Request) -> str:
        """Extract tenant ID from request."""
        # Try to get from request state (set by tenant middleware)
        tenant_id = getattr(request.state, "tenant_id", None)
        if tenant_id:
            return tenant_id
        
        # Try to get from headers
        tenant_id = request.headers.get("X-Tenant-ID")
        if tenant_id:
            return tenant_id
        
        # Default to "default" for single-tenant scenarios
        return "default"
    
    def _get_client_ip(self, request: Request) -> Optional[str]:
        """Extract client IP address from request."""
        # Check for forwarded IP (from load balancer/proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # Check for real IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to direct client IP
        if hasattr(request, "client") and request.client:
            return request.client.host
        
        return None
    
    def _get_resource_type(self, path: str) -> AuditResource:
        """Determine resource type from URL path."""
        for pattern, resource_type in self.path_to_resource.items():
            if path.startswith(pattern):
                return resource_type
        
        # Default to system for unknown paths
        return AuditResource.SYSTEM
    
    def _get_resource_id(self, path: str) -> Optional[str]:
        """Extract resource ID from URL path."""
        # Look for UUID patterns in the path
        import re
        uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        match = re.search(uuid_pattern, path, re.IGNORECASE)
        if match:
            return match.group(0)
        
        # Look for numeric IDs
        numeric_pattern = r'/(\d+)(?:/|$)'
        match = re.search(numeric_pattern, path)
        if match:
            return match.group(1)
        
        return None
    
    async def _log_audit_event(
        self,
        action: AuditAction,
        resource_type: AuditResource,
        resource_id: Optional[str],
        tenant_id: str,
        user_id: Optional[str],
        user_email: Optional[str],
        description: str,
        details: dict,
        ip_address: Optional[str],
        user_agent: Optional[str],
        request_id: Optional[str],
        success: bool
    ) -> None:
        """Log audit event to database."""
        try:
            async with get_async_db() as db:
                audit_service = AuditService(db)
                await audit_service.log_event(
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    tenant_id=tenant_id,
                    user_id=user_id,
                    user_email=user_email,
                    description=description,
                    details=details,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    request_id=request_id,
                    success=success
                )
        except Exception as e:
            # Don't let audit logging failures break the main request
            logger.error(f"Failed to log audit event: {e}")
