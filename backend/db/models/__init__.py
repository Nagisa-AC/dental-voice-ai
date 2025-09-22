"""
Core models package for Healthcare Voice AI.

Consolidated database models with proper relationships and no duplicates.
"""

# Import all models from the consolidated database_models
from .database_models import (
    Base,
    User,
    RefreshToken,
    Clinic,
    Assistant,
    AuditLog,
    FileUpload,
    CSRFToken,
    RateLimit,
)

# Import Pydantic schemas
from .pydantic_schemas import (
    # User schemas
    UserCreate,
    UserUpdate,
    UserResponse,
    UserLogin,
    
    # Clinic schemas
    ClinicCreate,
    ClinicUpdate,
    ClinicResponse,
    ClinicListResponse,
    ClinicStats,
    
    # Audit schemas
    AuditLogCreate,
    AuditLogResponse,
    
    # File upload schemas
    FileUploadResponse,
    FileUploadCreate,
    
    # Enums
    UserRole,
    ClinicStatus,
    HealthcareIndustry,
    AuditAction,
    AuditResource,
    FileUploadStatus,
)

__all__ = [
    # SQLAlchemy Models
    "Base",
    "User",
    "RefreshToken", 
    "Clinic",
    "Assistant",
    "AuditLog",
    "FileUpload",
    "CSRFToken",
    "RateLimit",
    
    # Pydantic Schemas
    "UserCreate",
    "UserUpdate", 
    "UserResponse",
    "UserLogin",
    "ClinicCreate",
    "ClinicUpdate",
    "ClinicResponse",
    "ClinicListResponse",
    "ClinicStats",
    "AuditLogCreate",
    "AuditLogResponse",
    "FileUploadResponse",
    "FileUploadCreate",
    
    # Enums
    "UserRole",
    "ClinicStatus",
    "HealthcareIndustry", 
    "AuditAction",
    "AuditResource",
    "FileUploadStatus",
]