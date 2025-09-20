"""
Core models package for Healthcare Voice AI.

Contains essential database models, Pydantic schemas, and business logic models.
Consolidated to remove duplicates and unnecessary abstractions.
"""

from .database_models import *
from .auth_models import *
from .audit_log import *
from .encrypted_fields import *
from .faq import *
from .jwt_models import *
from .refresh_token import *
from .clinic_models import *

__all__ = [
    # Database models
    "User",
    "Clinic", 
    "AuditLog",
    "RefreshToken",
    "FAQ",
    
    # Pydantic models
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "ClinicCreate",
    "ClinicUpdate", 
    "ClinicResponse",
    "AuditLogCreate",
    "AuditLogResponse",
    "FAQCreate",
    "FAQUpdate",
    "FAQResponse",
    
    # Enums
    "UserRole",
    "AuditAction",
    "AuditResource",
    "FAQCategory",
    
    # Consolidated clinic models
    "ClinicStatus",
    "HealthcareIndustry",
    "ContactInfo",
    "BusinessHours",
    "Service",
    "OfficePolicies",
    "AssistantConfig",
    "ClinicFormData",
    "ClinicSubmission",
    "AdminConfig",
    "ClinicResponse",
    "ClinicUpdate",
    "ClinicListResponse",
    "ClinicStats"
]
