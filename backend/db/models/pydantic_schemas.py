"""
Pydantic schemas for Healthcare Voice AI

Request/response models for API endpoints with proper validation.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator
from enum import Enum

from .database_models import (
    UserRole, ClinicStatus, HealthcareIndustry, 
    AuditAction, AuditResource, FileUploadStatus
)


# User Schemas
class UserCreate(BaseModel):
    """Schema for creating a new user."""
    username: Optional[str] = Field(None, max_length=50)
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    role: UserRole = Field(default=UserRole.READONLY)
    tenant_id: Optional[str] = Field(None, max_length=50)
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    username: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = Field(None, max_length=255)
    role: Optional[UserRole] = None
    tenant_id: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response."""
    id: str
    username: Optional[str]
    email: str
    role: str
    tenant_id: Optional[str]
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Clinic Schemas
class ContactInfo(BaseModel):
    """Contact information schema."""
    phone: str = Field(..., max_length=20)
    email: EmailStr = Field(..., max_length=255)
    address: str = Field(..., min_length=10, max_length=500)
    website: Optional[str] = Field(None, max_length=200)


class BusinessHours(BaseModel):
    """Business hours schema."""
    monday: Optional[Dict[str, str]] = None
    tuesday: Optional[Dict[str, str]] = None
    wednesday: Optional[Dict[str, str]] = None
    thursday: Optional[Dict[str, str]] = None
    friday: Optional[Dict[str, str]] = None
    saturday: Optional[Dict[str, str]] = None
    sunday: Optional[Dict[str, str]] = None


class Service(BaseModel):
    """Service schema."""
    name: str = Field(..., max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    duration_minutes: int = Field(..., ge=15, le=480)
    price: Optional[float] = Field(None, ge=0)


class ClinicPolicies(BaseModel):
    """Clinic policies schema."""
    cancellation_policy: Optional[str] = Field(None, max_length=1000)
    no_show_policy: Optional[str] = Field(None, max_length=1000)
    payment_policy: Optional[str] = Field(None, max_length=1000)
    privacy_policy: Optional[str] = Field(None, max_length=1000)


class AssistantConfig(BaseModel):
    """Assistant configuration schema."""
    voice_settings: Optional[Dict[str, Any]] = None
    conversation_style: Optional[str] = Field(None, max_length=50)
    language: str = Field(default="en", max_length=10)
    timezone: str = Field(default="America/Chicago", max_length=50)


class ClinicCreate(BaseModel):
    """Schema for creating a new clinic."""
    tenant_id: str = Field(..., max_length=50)
    name: str = Field(..., max_length=200)
    industry_type: HealthcareIndustry = Field(default=HealthcareIndustry.DENTAL)
    contact_info: ContactInfo
    business_hours: Optional[BusinessHours] = None
    services: Optional[List[Service]] = None
    policies: Optional[ClinicPolicies] = None
    assistant_config: Optional[AssistantConfig] = None
    faq_content: Optional[str] = None


class ClinicUpdate(BaseModel):
    """Schema for updating a clinic."""
    name: Optional[str] = Field(None, max_length=200)
    industry_type: Optional[HealthcareIndustry] = None
    status: Optional[ClinicStatus] = None
    contact_info: Optional[ContactInfo] = None
    business_hours: Optional[BusinessHours] = None
    services: Optional[List[Service]] = None
    policies: Optional[ClinicPolicies] = None
    assistant_config: Optional[AssistantConfig] = None
    faq_content: Optional[str] = None
    admin_notes: Optional[str] = None


class ClinicResponse(BaseModel):
    """Schema for clinic response."""
    id: str
    tenant_id: str
    name: str
    industry_type: str
    status: str
    phone: str
    email: str
    address: str
    website: Optional[str]
    business_hours: Optional[Dict[str, Any]]
    services: Optional[Dict[str, Any]]
    policies: Optional[Dict[str, Any]]
    vapi_assistant_id: Optional[str]
    assistant_config: Optional[Dict[str, Any]]
    faq_content: Optional[str]
    faq_filename: Optional[str]
    admin_notes: Optional[str]
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClinicListResponse(BaseModel):
    """Schema for clinic list response."""
    clinics: List[ClinicResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class ClinicStats(BaseModel):
    """Schema for clinic statistics."""
    total_clinics: int
    active_clinics: int
    pending_clinics: int
    approved_clinics: int
    rejected_clinics: int
    suspended_clinics: int
    clinics_by_industry: Dict[str, int]


# Audit Log Schemas
class AuditLogCreate(BaseModel):
    """Schema for creating an audit log entry."""
    user_id: Optional[str] = None
    clinic_id: Optional[str] = None
    action: AuditAction
    resource_type: AuditResource
    resource_id: Optional[str] = Field(None, max_length=100)
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = None
    request_id: Optional[str] = Field(None, max_length=100)


class AuditLogResponse(BaseModel):
    """Schema for audit log response."""
    id: str
    user_id: Optional[str]
    clinic_id: Optional[str]
    action: str
    resource_type: str
    resource_id: Optional[str]
    details: Optional[Dict[str, Any]]
    ip_address: Optional[str]
    user_agent: Optional[str]
    request_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# File Upload Schemas
class FileUploadCreate(BaseModel):
    """Schema for file upload creation."""
    original_filename: str = Field(..., max_length=255)
    file_type: str = Field(..., max_length=50)
    mime_type: str = Field(..., max_length=100)
    file_size: int = Field(..., ge=1)


class FileUploadResponse(BaseModel):
    """Schema for file upload response."""
    id: str
    user_id: Optional[str]
    clinic_id: Optional[str]
    original_filename: str
    secure_filename: str
    file_path: str
    file_size: int
    file_hash: str
    file_type: str
    mime_type: str
    status: str
    is_quarantined: bool
    quarantine_reason: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Assistant Schemas
class AssistantCreate(BaseModel):
    """Schema for creating an assistant."""
    clinic_id: str
    tenant_id: str = Field(..., max_length=50)
    vapi_assistant_id: str = Field(..., max_length=100)
    name: str = Field(..., max_length=100)
    model_id: str = Field(..., max_length=50)
    voice_id: str = Field(..., max_length=50)
    config: Optional[Dict[str, Any]] = None


class AssistantUpdate(BaseModel):
    """Schema for updating an assistant."""
    name: Optional[str] = Field(None, max_length=100)
    model_id: Optional[str] = Field(None, max_length=50)
    voice_id: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None, max_length=20)
    config: Optional[Dict[str, Any]] = None


class AssistantResponse(BaseModel):
    """Schema for assistant response."""
    id: str
    clinic_id: str
    tenant_id: str
    vapi_assistant_id: str
    name: str
    model_id: str
    voice_id: str
    status: str
    config: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Token Schemas
class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""
    refresh_token: str


# Health Check Schema
class HealthCheckResponse(BaseModel):
    """Schema for health check response."""
    status: str
    timestamp: datetime
    version: str
    environment: str
    database_status: str
    redis_status: Optional[str] = None
    uptime_seconds: float


# Error Schemas
class ErrorResponse(BaseModel):
    """Schema for error response."""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime


class ValidationErrorResponse(BaseModel):
    """Schema for validation error response."""
    error: str = "validation_error"
    message: str
    details: List[Dict[str, Any]]
    timestamp: datetime
