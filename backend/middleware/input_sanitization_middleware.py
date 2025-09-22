"""
Input Sanitization Middleware

Automatically sanitizes all incoming request data to prevent injection attacks.
"""

import logging
from typing import Callable, Dict, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from services.security_service import security_service

logger = logging.getLogger(__name__)


class InputSanitizationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for automatic input sanitization.
    
    Sanitizes all incoming request data including:
    - Query parameters
    - Form data
    - JSON body data
    - Path parameters
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
        Process request and sanitize all input data.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain
            
        Returns:
            HTTP response
        """
        # Skip sanitization for excluded paths
        if request.url.path in self.excluded_paths or request.url.path.startswith("/static"):
            return await call_next(request)
        
        try:
            # Sanitize query parameters
            if request.query_params:
                sanitized_query_params = {}
                for key, value in request.query_params.items():
                    sanitized_key = self._sanitize_text(key)
                    sanitized_value = self._sanitize_text(value)
                    sanitized_query_params[sanitized_key] = sanitized_value
                
                # Update request with sanitized query params
                request._query_params = sanitized_query_params
            
            # Sanitize path parameters
            if hasattr(request, 'path_params') and request.path_params:
                sanitized_path_params = {}
                for key, value in request.path_params.items():
                    sanitized_key = self._sanitize_text(key)
                    sanitized_value = self._sanitize_text(value)
                    sanitized_path_params[sanitized_key] = sanitized_value
                
                request.path_params = sanitized_path_params
            
            # Sanitize form data
            if request.headers.get("content-type", "").startswith("application/x-www-form-urlencoded"):
                form_data = await request.form()
                sanitized_form_data = {}
                for key, value in form_data.items():
                    sanitized_key = self._sanitize_text(key)
                    if isinstance(value, str):
                        sanitized_value = self._sanitize_text(value)
                    else:
                        sanitized_value = value  # File uploads, etc.
                    sanitized_form_data[sanitized_key] = sanitized_value
                
                # Update request with sanitized form data
                request._form = sanitized_form_data
            
            # Sanitize JSON body
            elif request.headers.get("content-type", "").startswith("application/json"):
                try:
                    body = await request.body()
                    if body:
                        import json
                        json_data = json.loads(body.decode())
                        sanitized_json = self._sanitize_dict(json_data)
                        
                        # Update request with sanitized JSON
                        request._body = json.dumps(sanitized_json).encode()
                except (json.JSONDecodeError, UnicodeDecodeError) as e:
                    logger.warning(f"Failed to sanitize JSON body: {e}")
            
            # Process request
            response = await call_next(request)
            return response
            
        except Exception as e:
            logger.error(f"Input sanitization error: {e}")
            # Don't block the request if sanitization fails
            return await call_next(request)
    
    def _sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively sanitize dictionary data.
        
        Args:
            data: Dictionary to sanitize
            
        Returns:
            Sanitized dictionary
        """
        sanitized = {}
        
        for key, value in data.items():
            sanitized_key = self._sanitize_text(key)
            
            if isinstance(value, dict):
                sanitized_value = self._sanitize_dict(value)
            elif isinstance(value, list):
                sanitized_value = self._sanitize_list(value)
            elif isinstance(value, str):
                sanitized_value = self._sanitize_text(value)
            else:
                sanitized_value = value
            
            sanitized[sanitized_key] = sanitized_value
        
        return sanitized
    
    def _sanitize_list(self, data: list) -> list:
        """
        Recursively sanitize list data.
        
        Args:
            data: List to sanitize
            
        Returns:
            Sanitized list
        """
        sanitized = []
        
        for item in data:
            if isinstance(item, dict):
                sanitized_item = self._sanitize_dict(item)
            elif isinstance(item, list):
                sanitized_item = self._sanitize_list(item)
            elif isinstance(item, str):
                sanitized_item = self._sanitize_text(item)
            else:
                sanitized_item = item
            
            sanitized.append(sanitized_item)
        
        return sanitized
    
    def _sanitize_text(self, text: str) -> str:
        """Sanitize text input."""
        if not isinstance(text, str):
            return text
        
        # Basic HTML sanitization
        import bleach
        return bleach.clean(text, strip=True)
