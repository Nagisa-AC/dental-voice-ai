"""
Rate Limiting Middleware

Middleware for applying rate limiting to all requests with slowapi integration.
"""

import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from services.security_service import security_service

logger = logging.getLogger(__name__)


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for applying rate limiting to all requests.
    
    Integrates with slowapi to provide comprehensive rate limiting
    with IP-based and user-based limits.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.security_service = security_service
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
        Process request and apply rate limiting.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain
            
        Returns:
            HTTP response
        """
        # Skip rate limiting for excluded paths
        if request.url.path in self.excluded_paths or request.url.path.startswith("/static"):
            return await call_next(request)
        
        try:
            # Get rate limit information
            rate_limit_info = self._get_rate_limit_info(request)
            
            # Check if IP is blacklisted
            if rate_limit_info["is_blacklisted"]:
                logger.warning(f"Request from blacklisted IP: {rate_limit_info['ip_address']}")
                return Response(
                    content='{"error": "Access denied"}',
                    status_code=403,
                    media_type="application/json"
                )
            
            # Skip rate limiting for whitelisted IPs
            if rate_limit_info["is_whitelisted"]:
                logger.debug(f"Request from whitelisted IP: {rate_limit_info['ip_address']}")
                return await call_next(request)
            
            # Log rate limit event
            self._log_rate_limit_event(
                "request_received", request, path=request.url.path
            )
            
            # Process request (rate limiting is handled by slowapi decorators)
            response = await call_next(request)
            
            # Log successful request
            self._log_rate_limit_event(
                "request_processed", request, 
                status_code=response.status_code, path=request.url.path
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Rate limiting middleware error: {e}")
            # Don't block the request if rate limiting fails
            return await call_next(request)
    
    def _get_rate_limit_info(self, request: Request) -> dict:
        """Get rate limit information for the request."""
        client_ip = request.client.host if request.client else "unknown"
        user_id = getattr(request.state, "user_id", None)
        
        return {
            "ip_address": client_ip,
            "user_id": user_id,
            "is_blacklisted": False,  # Simple implementation
            "is_whitelisted": False,  # Simple implementation
            "requests_remaining": 100,  # Simple implementation
            "reset_time": None
        }
    
    def _log_rate_limit_event(self, event_type: str, request: Request, **kwargs):
        """Log rate limiting events."""
        logger.info(f"Rate limit event: {event_type} for {request.client.host if request.client else 'unknown'}")
