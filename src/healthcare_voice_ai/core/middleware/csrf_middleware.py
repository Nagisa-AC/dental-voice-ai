"""
CSRF Protection Middleware

Middleware for automatic CSRF protection on all requests.
"""

import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from healthcare_voice_ai.core.services.csrf_service import (
    csrf_service, should_protect_request, get_csrf_token_from_request,
    create_csrf_error_response, get_csrf_cookie
)
from healthcare_voice_ai.core.configs.csrf import CSRFConfig

logger = logging.getLogger(__name__)


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    Middleware for automatic CSRF protection.
    
    Validates CSRF tokens on all protected requests and sets
    CSRF cookies for client-side token access.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.csrf_service = csrf_service
        self.config = CSRFConfig()
        self.excluded_paths = {
            "/health",
            "/ping",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/static"
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
            if not self.csrf_service.should_protect_request(request):
                return await call_next(request)
            
            # Get user ID from request state (set by auth middleware)
            user_id = getattr(request.state, "user_id", None)
            
            # Get CSRF token from request
            csrf_token = get_csrf_token_from_request(request)
            
            if not csrf_token:
                logger.warning(f"CSRF token missing for protected request: {request.method} {request.url.path}")
                return create_csrf_error_response("CSRF token is required")
            
            # Validate CSRF token
            if not self.csrf_service.validate_token(csrf_token, user_id):
                logger.warning(f"CSRF token validation failed for request: {request.method} {request.url.path}")
                return create_csrf_error_response("Invalid CSRF token")
            
            # Log successful CSRF validation
            logger.debug(f"CSRF token validated successfully for request: {request.method} {request.url.path}")
            
            # Process request
            response = await call_next(request)
            
            # Set CSRF cookie for future requests (if not already set)
            if not get_csrf_cookie(request):
                new_token, _ = self.csrf_service.generate_token(user_id)
                self.csrf_service.set_csrf_cookie(response, new_token)
            
            return response
            
        except Exception as e:
            logger.error(f"CSRF middleware error: {e}")
            # Don't block the request if CSRF validation fails due to system error
            # In production, you might want to be more strict
            return await call_next(request)
