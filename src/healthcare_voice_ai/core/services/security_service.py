"""
Unified Security Service for Healthcare Voice AI

Consolidates security-related services including:
- Rate limiting
- CSRF protection
- Input sanitization
- RBAC (Role-Based Access Control)
"""

import logging
import time
import hashlib
import secrets
from typing import Dict, Any, Optional, List, Set
from datetime import datetime, timedelta
from collections import defaultdict, deque
from fastapi import Request, HTTPException, status
from starlette.responses import Response

from healthcare_voice_ai.core.config import settings
from healthcare_voice_ai.core.models.auth_models import UserRole

logger = logging.getLogger(__name__)


class RateLimitingService:
    """Rate limiting service with IP and user-based limits."""
    
    def __init__(self):
        self.ip_requests: Dict[str, deque] = defaultdict(lambda: deque())
        self.user_requests: Dict[str, deque] = defaultdict(lambda: deque())
        self.rate_limit_per_minute = getattr(settings, 'RATE_LIMIT_PER_MINUTE', 60)
        
    def is_rate_limited(self, identifier: str, is_user: bool = False) -> bool:
        """Check if identifier is rate limited."""
        now = time.time()
        minute_ago = now - 60
        
        # Get the appropriate request tracker
        requests = self.user_requests[identifier] if is_user else self.ip_requests[identifier]
        
        # Remove old requests
        while requests and requests[0] < minute_ago:
            requests.popleft()
        
        # Check if limit exceeded
        if len(requests) >= self.rate_limit_per_minute:
            return True
        
        # Add current request
        requests.append(now)
        return False
    
    def get_rate_limit_headers(self, identifier: str, is_user: bool = False) -> Dict[str, str]:
        """Get rate limit headers for response."""
        now = time.time()
        minute_ago = now - 60
        
        requests = self.user_requests[identifier] if is_user else self.ip_requests[identifier]
        
        # Remove old requests
        while requests and requests[0] < minute_ago:
            requests.popleft()
        
        remaining = max(0, self.rate_limit_per_minute - len(requests))
        
        return {
            "X-RateLimit-Limit": str(self.rate_limit_per_minute),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(int(now + 60))
        }


class CSRFService:
    """CSRF protection service."""
    
    def __init__(self):
        self.tokens: Dict[str, Dict[str, Any]] = {}
        self.token_lifetime = 3600  # 1 hour
        
    def generate_token(self, session_id: str) -> str:
        """Generate a new CSRF token for a session."""
        token = secrets.token_urlsafe(32)
        self.tokens[token] = {
            "session_id": session_id,
            "created_at": time.time(),
            "used": False
        }
        return token
    
    def validate_token(self, token: str, session_id: str) -> bool:
        """Validate a CSRF token."""
        if token not in self.tokens:
            return False
        
        token_data = self.tokens[token]
        
        # Check if token is expired
        if time.time() - token_data["created_at"] > self.token_lifetime:
            del self.tokens[token]
            return False
        
        # Check if token belongs to session
        if token_data["session_id"] != session_id:
            return False
        
        # Mark token as used
        token_data["used"] = True
        return True
    
    def cleanup_expired_tokens(self):
        """Remove expired tokens."""
        now = time.time()
        expired_tokens = [
            token for token, data in self.tokens.items()
            if now - data["created_at"] > self.token_lifetime
        ]
        for token in expired_tokens:
            del self.tokens[token]


class InputSanitizationService:
    """Input sanitization service for security."""
    
    def __init__(self):
        # Dangerous patterns to sanitize
        self.dangerous_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'vbscript:',
            r'onload\s*=',
            r'onerror\s*=',
            r'onclick\s*=',
            r'onmouseover\s*=',
            r'<iframe[^>]*>.*?</iframe>',
            r'<object[^>]*>.*?</object>',
            r'<embed[^>]*>.*?</embed>',
        ]
        
        # SQL injection patterns
        self.sql_patterns = [
            r'union\s+select',
            r'drop\s+table',
            r'delete\s+from',
            r'insert\s+into',
            r'update\s+set',
            r'--',
            r'/\*.*?\*/',
            r'xp_',
            r'sp_',
        ]
    
    def sanitize_string(self, value: str) -> str:
        """Sanitize a string value."""
        if not isinstance(value, str):
            return value
        
        import re
        
        # Remove dangerous HTML/JavaScript patterns
        for pattern in self.dangerous_patterns:
            value = re.sub(pattern, '', value, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove SQL injection patterns
        for pattern in self.sql_patterns:
            value = re.sub(pattern, '', value, flags=re.IGNORECASE)
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Trim whitespace
        value = value.strip()
        
        return value
    
    def sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize a dictionary recursively."""
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = self.sanitize_string(value)
            elif isinstance(value, dict):
                sanitized[key] = self.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = self.sanitize_list(value)
            else:
                sanitized[key] = value
        return sanitized
    
    def sanitize_list(self, data: List[Any]) -> List[Any]:
        """Sanitize a list recursively."""
        sanitized = []
        for item in data:
            if isinstance(item, str):
                sanitized.append(self.sanitize_string(item))
            elif isinstance(item, dict):
                sanitized.append(self.sanitize_dict(item))
            elif isinstance(item, list):
                sanitized.append(self.sanitize_list(item))
            else:
                sanitized.append(item)
        return sanitized


class RBACService:
    """Role-Based Access Control service."""
    
    def __init__(self):
        # Define permissions for each role
        self.role_permissions = {
            UserRole.ADMIN: {
                "clinic:read", "clinic:write", "clinic:delete",
                "user:read", "user:write", "user:delete",
                "audit:read", "system:read", "system:write",
                "assistant:read", "assistant:write", "assistant:delete"
            },
            UserRole.CLINIC_OWNER: {
                "clinic:read", "clinic:write",
                "user:read", "user:write",
                "assistant:read", "assistant:write",
                "audit:read"
            },
            UserRole.STAFF: {
                "clinic:read",
                "user:read",
                "assistant:read"
            },
            UserRole.USER: {
                "clinic:read"
            }
        }
        
        # Define resource access patterns
        self.resource_patterns = {
            "clinic": r"^/clinics(/.*)?$",
            "user": r"^/users(/.*)?$",
            "audit": r"^/audit(/.*)?$",
            "system": r"^/system(/.*)?$",
            "assistant": r"^/assistants(/.*)?$"
        }
    
    def has_permission(self, user_role: UserRole, permission: str) -> bool:
        """Check if user role has specific permission."""
        role_perms = self.role_permissions.get(user_role, set())
        return permission in role_perms
    
    def can_access_resource(self, user_role: UserRole, resource: str, action: str) -> bool:
        """Check if user can access a specific resource with an action."""
        permission = f"{resource}:{action}"
        return self.has_permission(user_role, permission)
    
    def can_access_path(self, user_role: UserRole, path: str, method: str) -> bool:
        """Check if user can access a specific path with HTTP method."""
        import re
        
        # Map HTTP methods to actions
        method_to_action = {
            "GET": "read",
            "POST": "write",
            "PUT": "write",
            "PATCH": "write",
            "DELETE": "delete"
        }
        
        action = method_to_action.get(method, "read")
        
        # Check each resource pattern
        for resource, pattern in self.resource_patterns.items():
            if re.match(pattern, path):
                return self.can_access_resource(user_role, resource, action)
        
        # Default: allow access to public endpoints
        public_paths = ["/health", "/ping", "/docs", "/redoc", "/openapi.json"]
        return any(path.startswith(public) for public in public_paths)


class SecurityService:
    """Unified security service combining all security components."""
    
    def __init__(self):
        self.rate_limiting = RateLimitingService()
        self.csrf = CSRFService()
        self.sanitization = InputSanitizationService()
        self.rbac = RBACService()
    
    def check_rate_limit(self, request: Request) -> bool:
        """Check if request is rate limited."""
        # Get identifier (IP or user ID)
        client_ip = request.client.host if request.client else "unknown"
        
        # Check if user is authenticated
        user_id = getattr(request.state, 'user_id', None)
        identifier = user_id if user_id else client_ip
        is_user = user_id is not None
        
        return self.rate_limiting.is_rate_limited(identifier, is_user)
    
    def get_rate_limit_headers(self, request: Request) -> Dict[str, str]:
        """Get rate limit headers for response."""
        client_ip = request.client.host if request.client else "unknown"
        user_id = getattr(request.state, 'user_id', None)
        identifier = user_id if user_id else client_ip
        is_user = user_id is not None
        
        return self.rate_limiting.get_rate_limit_headers(identifier, is_user)
    
    def validate_csrf_token(self, request: Request) -> bool:
        """Validate CSRF token for state-changing requests."""
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True
        
        # Get session ID from request
        session_id = request.cookies.get("session_id")
        if not session_id:
            return False
        
        # Get CSRF token from header
        csrf_token = request.headers.get("X-CSRF-Token")
        if not csrf_token:
            return False
        
        return self.csrf.validate_token(csrf_token, session_id)
    
    def sanitize_request_data(self, data: Any) -> Any:
        """Sanitize request data."""
        if isinstance(data, dict):
            return self.sanitization.sanitize_dict(data)
        elif isinstance(data, list):
            return self.sanitization.sanitize_list(data)
        elif isinstance(data, str):
            return self.sanitization.sanitize_string(data)
        else:
            return data
    
    def check_permission(self, user_role: UserRole, path: str, method: str) -> bool:
        """Check if user has permission to access path with method."""
        return self.rbac.can_access_path(user_role, path, method)
    
    def cleanup_expired_data(self):
        """Cleanup expired security data."""
        self.csrf.cleanup_expired_tokens()


# Global security service instance
security_service = SecurityService()
