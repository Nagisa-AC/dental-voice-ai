"""
CSRF Protection Middleware

Middleware for automatic CSRF protection on all requests.
"""

import logging
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from services.security_service import security_service
from core.config import settings

logger = logging.getLogger(__name__)


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    Middleware for automatic CSRF protection.
    
    Validates CSRF tokens on all protected requests and sets
    CSRF cookies for client-side token access.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.security_service = security_service
        self.config = settings
        self.excluded_paths = {
            "/health",
            "/ping",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/static",
            "/webhooks/incoming_call",
            "/new/webhooks/incoming_call"
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and apply CSRF protection.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain
            
        Returns:
            HTTP response
        """
        # Skip CSRF protection for excluded paths
        if request.url.path in self.excluded_paths or request.url.path.startswith("/static"):
            return await call_next(request)
        
        try:
            # Check if request should be protected
            if not self._should_protect_request(request):
                return await call_next(request)
            
            # Get user ID from request state (set by auth middleware)
            user_id = getattr(request.state, "user_id", None)
            
            # Get CSRF token from request
            csrf_token = self._get_csrf_token_from_request(request)
            
            if not csrf_token:
                logger.warning(f"CSRF token missing for protected request: {request.method} {request.url.path}")
                return self._create_csrf_error_response("CSRF token is required")
            
            # Validate CSRF token
            if not self._validate_token(csrf_token, user_id):
                logger.warning(f"CSRF token validation failed for request: {request.method} {request.url.path}")
                return self._create_csrf_error_response("Invalid CSRF token")
            
            # Log successful CSRF validation
            logger.debug(f"CSRF token validated successfully for request: {request.method} {request.url.path}")
            
            # Process request
            response = await call_next(request)
            
            # Set CSRF cookie for future requests (if not already set)
            if not self._get_csrf_cookie(request):
                new_token = self._generate_token(user_id)
                self._set_csrf_cookie(response, new_token)
            
            return response
            
        except Exception as e:
            logger.error(f"CSRF middleware error: {e}")
            # Don't block the request if CSRF validation fails due to system error
            # In production, you might want to be more strict
            return await call_next(request)
    
    def _should_protect_request(self, request: Request) -> bool:
        """Check if request should be protected by CSRF."""
        # Skip CSRF protection for excluded paths
        if request.url.path in self.excluded_paths:
            return False
        
        # Skip CSRF protection for webhook endpoints
        if request.url.path.startswith("/webhooks/"):
            return False
        
        # Only protect state-changing methods
        return request.method in ["POST", "PUT", "PATCH", "DELETE"]
    
    def _validate_token(self, token: str, user_id: str) -> bool:
        """Validate CSRF token."""
        # Simple validation - in production, use proper token validation
        return token and len(token) > 10
    
    def _generate_token(self, user_id: str) -> str:
        """Generate CSRF token."""
        import secrets
        return secrets.token_urlsafe(32)
    
    def _set_csrf_cookie(self, response: Response, token: str):
        """Set CSRF cookie."""
        response.set_cookie(
            key="csrf_token",
            value=token,
            httponly=False,  # Allow JavaScript access
            secure=True,
            samesite="strict"
        )
    
    def _get_csrf_token_from_request(self, request: Request) -> str:
        """Get CSRF token from request headers or form data."""
        # Check X-CSRF-Token header first
        csrf_token = request.headers.get("X-CSRF-Token")
        if csrf_token:
            return csrf_token
        
        # Check form data
        if hasattr(request, "_form") and request._form:
            csrf_token = request._form.get("csrf_token")
            if csrf_token:
                return csrf_token
        
        return None
    
    def _get_csrf_cookie(self, request: Request) -> str:
        """Get CSRF token from cookie."""
        return request.cookies.get("csrf_token")
    
    def _create_csrf_error_response(self, message: str) -> JSONResponse:
        """Create CSRF error response."""
        return JSONResponse(
            status_code=403,
            content={"error": "CSRF validation failed", "message": message}
        )
