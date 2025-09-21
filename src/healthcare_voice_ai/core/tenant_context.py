"""
Tenant Context Management for Healthcare Voice AI

Provides thread-safe tenant context management for multi-tenant applications.
"""

import threading
from typing import Optional, Dict, Any
from contextlib import contextmanager
# Local exception class
class ValidationError(Exception):
    """Validation-related error."""
    pass


class TenantContext:
    """Thread-safe tenant context manager for multi-tenant applications."""
    
    _context = threading.local()
    
    @classmethod
    def set_tenant_id(cls, tenant_id: str) -> None:
        """Set the current tenant ID for the thread."""
        if not tenant_id or not isinstance(tenant_id, str):
            raise ValidationError("Invalid tenant_id provided")
        cls._context.tenant_id = tenant_id
        cls._context.tenant_data = {}
    
    @classmethod
    def get_tenant_id(cls) -> Optional[str]:
        """Get the current tenant ID for the thread."""
        return getattr(cls._context, 'tenant_id', None)
    
    @classmethod
    def require_tenant_id(cls) -> str:
        """Get the current tenant ID, raising an error if not set."""
        tenant_id = cls.get_tenant_id()
        if not tenant_id:
            raise ValidationError("No tenant context set. Operations must be performed within a tenant context.")
        return tenant_id
    
    @classmethod
    def clear_tenant_context(cls) -> None:
        """Clear the tenant context for the current thread."""
        if hasattr(cls._context, 'tenant_id'):
            delattr(cls._context, 'tenant_id')
        if hasattr(cls._context, 'tenant_data'):
            delattr(cls._context, 'tenant_data')
    
    @classmethod
    def set_tenant_data(cls, key: str, value: Any) -> None:
        """Set additional tenant-specific data."""
        if not hasattr(cls._context, 'tenant_data'):
            cls._context.tenant_data = {}
        cls._context.tenant_data[key] = value
    
    @classmethod
    def get_tenant_data(cls, key: str, default: Any = None) -> Any:
        """Get tenant-specific data."""
        if not hasattr(cls._context, 'tenant_data'):
            return default
        return cls._context.tenant_data.get(key, default)
    
    @classmethod
    def get_all_tenant_data(cls) -> Dict[str, Any]:
        """Get all tenant-specific data."""
        if not hasattr(cls._context, 'tenant_data'):
            return {}
        return dict(cls._context.tenant_data)
    
    @classmethod
    @contextmanager
    def tenant_context(cls, tenant_id: str):
        """Context manager for tenant operations."""
        original_tenant_id = cls.get_tenant_id()
        original_tenant_data = cls.get_all_tenant_data()
        
        try:
            cls.set_tenant_id(tenant_id)
            yield tenant_id
        finally:
            # Restore previous context
            cls.clear_tenant_context()
            if original_tenant_id:
                cls.set_tenant_id(original_tenant_id)
                for key, value in original_tenant_data.items():
                    cls.set_tenant_data(key, value)


def get_current_tenant_id() -> Optional[str]:
    """Convenience function to get current tenant ID."""
    return TenantContext.get_tenant_id()


def require_tenant_id() -> str:
    """Convenience function to require tenant ID."""
    return TenantContext.require_tenant_id()


def with_tenant_context(tenant_id: str):
    """Decorator for functions that require tenant context."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with TenantContext.tenant_context(tenant_id):
                return func(*args, **kwargs)
        return wrapper
    return decorator
