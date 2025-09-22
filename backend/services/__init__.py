"""
Core Services Package for Healthcare Voice AI

Essential services for business logic, security, and data management.
Consolidated to remove redundancy and improve maintainability.
"""

from .security_service import security_service
from .audit_error_service import (
    centralized_error_handler, 
    health_checker, 
    audit_service
)
from .auth_service import AuthService
from .jwt_service import JWTService
from .encryption_service import EncryptionService
from .file_upload_service import FileUploadService
from .assistant_service import AssistantService
from integrations.vapi.async_vapi_service import AsyncVAPIService

__all__ = [
    # Security services
    "security_service",
    
    # Error handling and audit
    "centralized_error_handler",
    "health_checker", 
    "audit_service",
    
    # Authentication and authorization
    "AuthService",
    "JWTService",
    
    # Data security
    "EncryptionService",
    
    # File management
    "FileUploadService",
    
    # AI and voice services
    "AssistantService",
    "AsyncVAPIService"
]