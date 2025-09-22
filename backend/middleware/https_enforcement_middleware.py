"""
HTTPS Enforcement Middleware

Enforces HTTPS connections for all API endpoints in production.
"""

import logging
from typing import Optional
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from core.config import settings

logger = logging.getLogger(__name__)


class HTTPSEnforcementMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce HTTPS connections.
    
    Redirects HTTP requests to HTTPS in production environments.
    """
    
    def __init__(self, app: ASGIApp, enforce_https: bool = True, 
                 redirect_to_https: bool = True, https_port: int = 443):
        super().__init__(app)
        self.enforce_https = enforce_https
        self.redirect_to_https = redirect_to_https
        self.https_port = https_port
        
        # Paths that don't require HTTPS enforcement
        self.exempt_paths = {
            "/health", "/ping", "/metrics", "/docs", "/redoc", 
            "/openapi.json", "/favicon.ico"
        }
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request and enforce HTTPS if required."""
        
        # Skip HTTPS enforcement for exempt paths
        if any(request.url.path.startswith(path) for path in self.exempt_paths):
            return await call_next(request)
        
        # Skip HTTPS enforcement in development
        if not settings.is_production():
            return await call_next(request)
        
        # Check if HTTPS enforcement is enabled
        if not self.enforce_https:
            return await call_next(request)
        
        # Check if request is already HTTPS
        if self._is_https_request(request):
            return await call_next(request)
        
        # Handle non-HTTPS request
        if self.redirect_to_https:
            return self._redirect_to_https(request)
        else:
            return self._reject_http_request(request)
    
    def _is_https_request(self, request: Request) -> bool:
        """Check if the request is using HTTPS."""
        # Check the scheme
        if request.url.scheme == "https":
            return True
        
        # Check for forwarded headers (common in reverse proxy setups)
        forwarded_proto = request.headers.get("X-Forwarded-Proto")
        if forwarded_proto and forwarded_proto.lower() == "https":
            return True
        
        # Check for other common proxy headers
        forwarded_ssl = request.headers.get("X-Forwarded-Ssl")
        if forwarded_ssl and forwarded_ssl.lower() == "on":
            return True
        
        # Check for CloudFlare headers
        cf_visitor = request.headers.get("CF-Visitor")
        if cf_visitor and '"scheme":"https"' in cf_visitor:
            return True
        
        return False
    
    def _redirect_to_https(self, request: Request) -> Response:
        """Redirect HTTP request to HTTPS."""
        # Build HTTPS URL
        https_url = request.url.replace(
            scheme="https",
            port=self.https_port if self.https_port != 443 else None
        )
        
        logger.info(f"Redirecting HTTP to HTTPS: {request.url} -> {https_url}")
        
        # Return redirect response
        from fastapi.responses import RedirectResponse
        return RedirectResponse(
            url=str(https_url),
            status_code=301,  # Permanent redirect
            headers={
                "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload"
            }
        )
    
    def _reject_http_request(self, request: Request) -> Response:
        """Reject HTTP request with error message."""
        logger.warning(f"Rejected HTTP request: {request.url}")
        
        return JSONResponse(
            status_code=426,  # Upgrade Required
            content={
                "error": "HTTPS Required",
                "message": "This API requires HTTPS. Please use HTTPS to access this endpoint.",
                "upgrade": "TLS/1.2"
            },
            headers={
                "Upgrade": "TLS/1.2",
                "Connection": "Upgrade",
                "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload"
            }
        )


class HSTSHeaderMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add HTTP Strict Transport Security (HSTS) headers.
    """
    
    def __init__(self, app: ASGIApp, max_age: int = 31536000, 
                 include_subdomains: bool = True, preload: bool = True):
        super().__init__(app)
        self.max_age = max_age
        self.include_subdomains = include_subdomains
        self.preload = preload
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Add HSTS headers to response."""
        response = await call_next(request)
        
        # Only add HSTS header for HTTPS requests
        if self._is_https_request(request):
            hsts_value = f"max-age={self.max_age}"
            
            if self.include_subdomains:
                hsts_value += "; includeSubDomains"
            
            if self.preload:
                hsts_value += "; preload"
            
            response.headers["Strict-Transport-Security"] = hsts_value
        
        return response
    
    def _is_https_request(self, request: Request) -> bool:
        """Check if the request is using HTTPS."""
        # Check the scheme
        if request.url.scheme == "https":
            return True
        
        # Check for forwarded headers
        forwarded_proto = request.headers.get("X-Forwarded-Proto")
        if forwarded_proto and forwarded_proto.lower() == "https":
            return True
        
        forwarded_ssl = request.headers.get("X-Forwarded-Ssl")
        if forwarded_ssl and forwarded_ssl.lower() == "on":
            return True
        
        return False


class SSLRedirectMiddleware(BaseHTTPMiddleware):
    """
    Middleware to redirect HTTP to HTTPS with proper SSL handling.
    """
    
    def __init__(self, app: ASGIApp, ssl_redirect: bool = True, 
                 permanent: bool = True, port: int = 443):
        super().__init__(app)
        self.ssl_redirect = ssl_redirect
        self.permanent = permanent
        self.port = port
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Handle SSL redirect logic."""
        # Skip redirect for exempt paths
        exempt_paths = ["/health", "/ping", "/metrics"]
        if any(request.url.path.startswith(path) for path in exempt_paths):
            return await call_next(request)
        
        # Skip redirect in development
        if not settings.is_production():
            return await call_next(request)
        
        # Check if request is HTTPS
        if self._is_https_request(request):
            return await call_next(request)
        
        # Redirect to HTTPS
        if self.ssl_redirect:
            return self._create_redirect_response(request)
        
        return await call_next(request)
    
    def _is_https_request(self, request: Request) -> bool:
        """Check if the request is using HTTPS."""
        if request.url.scheme == "https":
            return True
        
        # Check proxy headers
        forwarded_proto = request.headers.get("X-Forwarded-Proto")
        if forwarded_proto and forwarded_proto.lower() == "https":
            return True
        
        return False
    
    def _create_redirect_response(self, request: Request) -> Response:
        """Create HTTPS redirect response."""
        # Build HTTPS URL
        https_url = request.url.replace(
            scheme="https",
            port=self.port if self.port != 443 else None
        )
        
        # Create redirect response
        from fastapi.responses import RedirectResponse
        status_code = 301 if self.permanent else 302
        
        return RedirectResponse(
            url=str(https_url),
            status_code=status_code,
            headers={
                "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload"
            }
        )
