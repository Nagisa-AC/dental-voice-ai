"""
Consolidated Database Models for Healthcare Voice AI

SQLAlchemy ORM models with proper relationships, indexes, and HIPAA compliance.
All models use a single Base class for consistency.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List

from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Text, JSON, 
    ForeignKey, Index, Numeric, LargeBinary
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID

# Single Base class for all models
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


# Enums
class UserRole(str, Enum):
    """User role enumeration."""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    CLINIC_ADMIN = "clinic_admin"
    CLINIC_USER = "clinic_user"
    READONLY = "readonly"


class ClinicStatus(str, Enum):
    """Clinic status enumeration."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"


class HealthcareIndustry(str, Enum):
    """Healthcare industry types."""
    DENTAL = "dental"
    MEDICAL = "medical"
    MENTAL_HEALTH = "mental_health"
    VETERINARY = "veterinary"
    CHIROPRACTIC = "chiropractic"
    PHYSICAL_THERAPY = "physical_therapy"
    SPECIALIST = "specialist"


class CommunicationPref(str, Enum):
    """Communication preference enumeration."""
    PHONE = "phone"
    TEXT = "text"
    EMAIL = "email"


class AuditAction(str, Enum):
    """Audit action types."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    EXPORT = "export"
    IMPORT = "import"


class AuditResource(str, Enum):
    """Audit resource types."""
    USER = "user"
    CLINIC = "clinic"
    ASSISTANT = "assistant"
    FILE = "file"
    SYSTEM = "system"
    AUDIT_LOG = "audit_log"


class FileUploadStatus(str, Enum):
    """File upload status."""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    QUARANTINED = "quarantined"


# Database Models
class User(Base):
    """User model for authentication and authorization."""
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(
        String, 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    username: Mapped[Optional[str]] = mapped_column(
        String(50), 
        unique=True, 
        nullable=True, 
        index=True
    )
    email: Mapped[str] = mapped_column(
        String(255), 
        unique=True, 
        nullable=False, 
        index=True
    )
    password_hash: Mapped[str] = mapped_column(
        String(255), 
        nullable=False
    )
    role: Mapped[str] = mapped_column(
        String(50), 
        nullable=False, 
        default=UserRole.READONLY.value,
        index=True
    )
    tenant_id: Mapped[Optional[str]] = mapped_column(
        String(50), 
        nullable=True, 
        index=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, 
        default=True, 
        nullable=False
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean, 
        default=False, 
        nullable=False
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=False
    )
    
    # Relationships
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
        "RefreshToken", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )
    file_uploads: Mapped[List["FileUpload"]] = relationship(
        "FileUpload", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )
    csrf_tokens: Mapped[List["CSRFToken"]] = relationship(
        "CSRFToken", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )
    approved_clinics: Mapped[List["Clinic"]] = relationship(
        "Clinic", 
        foreign_keys="Clinic.approved_by",
        back_populates="approved_by_user"
    )
    
    # Performance indexes
    __table_args__ = (
        Index('idx_users_email_active', 'email', 'is_active'),
        Index('idx_users_role_active', 'role', 'is_active'),
        Index('idx_users_tenant_active', 'tenant_id', 'is_active'),
        Index('idx_users_created_at', 'created_at'),
        Index('idx_users_last_login', 'last_login'),
    )


class RefreshToken(Base):
    """Refresh token model for JWT token rotation."""
    __tablename__ = "refresh_tokens"
    
    id: Mapped[str] = mapped_column(
        String, 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    token_hash: Mapped[str] = mapped_column(
        String(255), 
        nullable=False, 
        unique=True, 
        index=True
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        index=True
    )
    is_revoked: Mapped[bool] = mapped_column(
        Boolean, 
        default=False, 
        nullable=False, 
        index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )
    revoked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")
    
    # Performance indexes
    __table_args__ = (
        Index('idx_refresh_tokens_user_expires', 'user_id', 'expires_at'),
        Index('idx_refresh_tokens_expires_revoked', 'expires_at', 'is_revoked'),
        Index('idx_refresh_tokens_token_hash', 'token_hash'),
        Index('idx_refresh_tokens_created_at', 'created_at'),
    )


class Clinic(Base):
    """Clinic model for healthcare practice management."""
    __tablename__ = "clinics"
    
    id: Mapped[str] = mapped_column(
        String, 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    tenant_id: Mapped[str] = mapped_column(
        String(50), 
        unique=True, 
        nullable=False, 
        index=True
    )
    name: Mapped[str] = mapped_column(
        String(200), 
        nullable=False, 
        index=True
    )
    industry_type: Mapped[str] = mapped_column(
        String(50), 
        nullable=False, 
        default=HealthcareIndustry.DENTAL.value,
        index=True
    )
    status: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        default=ClinicStatus.PENDING.value,
        index=True
    )
    
    # Contact Information
    phone: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        index=True
    )
    email: Mapped[str] = mapped_column(
        String(255), 
        nullable=False, 
        index=True
    )
    address: Mapped[str] = mapped_column(
        Text, 
        nullable=False
    )
    website: Mapped[Optional[str]] = mapped_column(
        String(200), 
        nullable=True
    )
    
    # Business Configuration
    business_hours: Mapped[Optional[dict]] = mapped_column(
        JSON, 
        nullable=True
    )
    services: Mapped[Optional[dict]] = mapped_column(
        JSON, 
        nullable=True
    )
    policies: Mapped[Optional[dict]] = mapped_column(
        JSON, 
        nullable=True
    )
    
    # AI Assistant Configuration
    vapi_assistant_id: Mapped[Optional[str]] = mapped_column(
        String(100), 
        nullable=True, 
        index=True
    )
    assistant_config: Mapped[Optional[dict]] = mapped_column(
        JSON, 
        nullable=True
    )
    
    # FAQ and Knowledge Base
    faq_content: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True
    )
    faq_filename: Mapped[Optional[str]] = mapped_column(
        String(255), 
        nullable=True
    )
    
    # Admin Configuration
    admin_notes: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True
    )
    approved_by: Mapped[Optional[str]] = mapped_column(
        String, 
        ForeignKey("users.id"), 
        nullable=True
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=False
    )
    
    # Relationships
    approver: Mapped[Optional["User"]] = relationship(
        "User", 
        back_populates="approved_clinics", 
        foreign_keys=[approved_by]
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog", 
        back_populates="clinic", 
        cascade="all, delete-orphan"
    )
    file_uploads: Mapped[List["FileUpload"]] = relationship(
        "FileUpload", 
        back_populates="clinic", 
        cascade="all, delete-orphan"
    )
    assistants: Mapped[List["Assistant"]] = relationship(
        "Assistant", 
        back_populates="clinic", 
        cascade="all, delete-orphan"
    )
    
    # Performance indexes
    # Relationships
    approved_by_user: Mapped[Optional["User"]] = relationship("User", foreign_keys=[approved_by])
    assistants: Mapped[List["Assistant"]] = relationship("Assistant", back_populates="clinic")
    audit_logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="clinic")
    file_uploads: Mapped[List["FileUpload"]] = relationship("FileUpload", back_populates="clinic")
    appointments: Mapped[List["Appointment"]] = relationship("Appointment", back_populates="clinic")
    patients: Mapped[List["Patient"]] = relationship("Patient", back_populates="clinic")
    billing_records: Mapped[List["BillingRecord"]] = relationship("BillingRecord", back_populates="clinic")
    
    __table_args__ = (
        Index('idx_clinics_tenant_status', 'tenant_id', 'status'),
        Index('idx_clinics_industry_status', 'industry_type', 'status'),
        Index('idx_clinics_phone_email', 'phone', 'email'),
        Index('idx_clinics_created_status', 'created_at', 'status'),
        Index('idx_clinics_updated_at', 'updated_at'),
        Index('idx_clinics_approved_by', 'approved_by'),
        Index('idx_clinics_vapi_assistant_id', 'vapi_assistant_id'),
    )


class Assistant(Base):
    """AI Assistant model for VAPI integration."""
    __tablename__ = "assistants"
    
    id: Mapped[str] = mapped_column(
        String, 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    clinic_id: Mapped[str] = mapped_column(
        String, 
        ForeignKey("clinics.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    tenant_id: Mapped[str] = mapped_column(
        String(50), 
        nullable=False, 
        index=True
    )
    vapi_assistant_id: Mapped[str] = mapped_column(
        String(100), 
        unique=True, 
        nullable=False, 
        index=True
    )
    name: Mapped[str] = mapped_column(
        String(100), 
        nullable=False, 
        index=True
    )
    model_id: Mapped[str] = mapped_column(
        String(50), 
        nullable=False
    )
    voice_id: Mapped[str] = mapped_column(
        String(50), 
        nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        default="active", 
        index=True
    )
    config: Mapped[Optional[dict]] = mapped_column(
        JSON, 
        nullable=True
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=False
    )
    
    # Relationships
    clinic: Mapped["Clinic"] = relationship("Clinic", back_populates="assistants")
    
    # Performance indexes
    __table_args__ = (
        Index('idx_assistants_clinic_status', 'clinic_id', 'status'),
        Index('idx_assistants_tenant_status', 'tenant_id', 'status'),
        Index('idx_assistants_vapi_id', 'vapi_assistant_id'),
        Index('idx_assistants_created', 'created_at'),
        Index('idx_assistants_updated_at', 'updated_at'),
        Index('idx_assistants_name', 'name'),
    )


class AuditLog(Base):
    """Audit log model for HIPAA compliance and security monitoring."""
    __tablename__ = "audit_logs"
    
    id: Mapped[str] = mapped_column(
        String, 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[Optional[str]] = mapped_column(
        String, 
        ForeignKey("users.id", ondelete="SET NULL"), 
        nullable=True, 
        index=True
    )
    clinic_id: Mapped[Optional[str]] = mapped_column(
        String, 
        ForeignKey("clinics.id", ondelete="CASCADE"), 
        nullable=True, 
        index=True
    )
    action: Mapped[str] = mapped_column(
        String(50), 
        nullable=False, 
        index=True
    )
    resource_type: Mapped[str] = mapped_column(
        String(50), 
        nullable=False, 
        index=True
    )
    resource_id: Mapped[Optional[str]] = mapped_column(
        String(100), 
        nullable=True, 
        index=True
    )
    details: Mapped[Optional[dict]] = mapped_column(
        JSON, 
        nullable=True
    )
    
    # Request Information
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45), 
        nullable=True, 
        index=True
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True
    )
    request_id: Mapped[Optional[str]] = mapped_column(
        String(100), 
        nullable=True, 
        index=True
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False, 
        index=True
    )
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="audit_logs")
    clinic: Mapped[Optional["Clinic"]] = relationship("Clinic", back_populates="audit_logs")
    
    # Performance indexes for HIPAA compliance and monitoring
    __table_args__ = (
        Index('idx_audit_logs_user_action', 'user_id', 'action'),
        Index('idx_audit_logs_clinic_action', 'clinic_id', 'action'),
        Index('idx_audit_logs_resource', 'resource_type', 'resource_id'),
        Index('idx_audit_logs_created_action', 'created_at', 'action'),
        Index('idx_audit_logs_ip_created', 'ip_address', 'created_at'),
        Index('idx_audit_logs_user_created', 'user_id', 'created_at'),
        Index('idx_audit_logs_clinic_created', 'clinic_id', 'created_at'),
        Index('idx_audit_logs_action_resource', 'action', 'resource_type'),
    )


class FileUpload(Base):
    """File upload model for tracking uploaded files."""
    __tablename__ = "file_uploads"
    
    id: Mapped[str] = mapped_column(
        String, 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[Optional[str]] = mapped_column(
        String, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=True, 
        index=True
    )
    clinic_id: Mapped[Optional[str]] = mapped_column(
        String, 
        ForeignKey("clinics.id", ondelete="CASCADE"), 
        nullable=True, 
        index=True
    )
    
    # File Information
    original_filename: Mapped[str] = mapped_column(
        String(255), 
        nullable=False
    )
    secure_filename: Mapped[str] = mapped_column(
        String(255), 
        nullable=False, 
        unique=True, 
        index=True
    )
    file_path: Mapped[str] = mapped_column(
        String(500), 
        nullable=False
    )
    file_size: Mapped[int] = mapped_column(
        Integer, 
        nullable=False
    )
    file_hash: Mapped[str] = mapped_column(
        String(64), 
        nullable=False, 
        index=True
    )
    file_type: Mapped[str] = mapped_column(
        String(50), 
        nullable=False, 
        index=True
    )
    mime_type: Mapped[str] = mapped_column(
        String(100), 
        nullable=False
    )
    
    # Upload Status
    status: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        default=FileUploadStatus.UPLOADED.value,
        index=True
    )
    is_quarantined: Mapped[bool] = mapped_column(
        Boolean, 
        default=False, 
        nullable=False, 
        index=True
    )
    quarantine_reason: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=False
    )
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="file_uploads")
    clinic: Mapped[Optional["Clinic"]] = relationship("Clinic", back_populates="file_uploads")
    
    # Indexes
    __table_args__ = (
        Index('idx_file_uploads_user_status', 'user_id', 'status'),
        Index('idx_file_uploads_clinic_status', 'clinic_id', 'status'),
        Index('idx_file_uploads_hash', 'file_hash'),
        Index('idx_file_uploads_type_status', 'file_type', 'status'),
        Index('idx_file_uploads_quarantined', 'is_quarantined', 'created_at'),
    )


class CSRFToken(Base):
    """CSRF token model for tracking CSRF tokens."""
    __tablename__ = "csrf_tokens"
    
    id: Mapped[str] = mapped_column(
        String, 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[Optional[str]] = mapped_column(
        String, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=True, 
        index=True
    )
    token_hash: Mapped[str] = mapped_column(
        String(255), 
        nullable=False, 
        unique=True, 
        index=True
    )
    is_used: Mapped[bool] = mapped_column(
        Boolean, 
        default=False, 
        nullable=False, 
        index=True
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        index=True
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )
    used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="csrf_tokens")
    
    # Indexes
    __table_args__ = (
        Index('idx_csrf_tokens_user_expires', 'user_id', 'expires_at'),
        Index('idx_csrf_tokens_expires_used', 'expires_at', 'is_used'),
        Index('idx_csrf_tokens_created', 'created_at'),
    )


class RateLimit(Base):
    """Rate limit model for tracking rate limiting."""
    __tablename__ = "rate_limits"
    
    id: Mapped[str] = mapped_column(
        String, 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    key: Mapped[str] = mapped_column(
        String(255), 
        nullable=False, 
        index=True
    )  # IP address or user ID
    endpoint: Mapped[str] = mapped_column(
        String(200), 
        nullable=False, 
        index=True
    )
    method: Mapped[str] = mapped_column(
        String(10), 
        nullable=False, 
        index=True
    )
    count: Mapped[int] = mapped_column(
        Integer, 
        nullable=False, 
        default=1
    )
    window_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        index=True
    )
    window_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        index=True
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=False
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_rate_limits_key_endpoint', 'key', 'endpoint'),
        Index('idx_rate_limits_window', 'window_start', 'window_end'),
        Index('idx_rate_limits_created', 'created_at'),
    )


class Call(Base):
    """Call model for storing VAPI call data and analytics."""
    __tablename__ = "calls"
    
    id: Mapped[str] = mapped_column(
        String, 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    tenant_id: Mapped[str] = mapped_column(
        String(50), 
        nullable=False, 
        index=True
    )
    assistant_id: Mapped[Optional[str]] = mapped_column(
        String(100), 
        nullable=True, 
        index=True
    )
    vapi_call_id: Mapped[Optional[str]] = mapped_column(
        String(100), 
        nullable=True, 
        unique=True, 
        index=True
    )
    customer_phone: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        index=True
    )
    customer_name: Mapped[Optional[str]] = mapped_column(
        String(100), 
        nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        default='started',
        index=True
    )
    duration_seconds: Mapped[Optional[int]] = mapped_column(
        Integer, 
        nullable=True
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        index=True
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True, 
        index=True
    )
    transcript: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True
    )
    summary: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True
    )
    outcome: Mapped[Optional[str]] = mapped_column(
        String(50), 
        nullable=True, 
        index=True
    )  # 'appointment_booked', 'no_show', 'cancelled', etc.
    recording_url: Mapped[Optional[str]] = mapped_column(
        String(500), 
        nullable=True
    )
    cost: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 4), 
        nullable=True
    )
    currency: Mapped[str] = mapped_column(
        String(3), 
        nullable=False, 
        default='USD'
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False, 
        index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=False, 
        index=True
    )
    
    # Relationships
    assistant: Mapped[Optional["Assistant"]] = relationship("Assistant", foreign_keys=[assistant_id], primaryjoin="Call.assistant_id == Assistant.vapi_assistant_id")
    appointments: Mapped[List["Appointment"]] = relationship("Appointment", back_populates="call")
    
    # Performance indexes for call analytics
    __table_args__ = (
        Index('idx_calls_tenant_status', 'tenant_id', 'status'),
        Index('idx_calls_customer_phone', 'customer_phone'),
        Index('idx_calls_started_at', 'started_at'),
        Index('idx_calls_outcome', 'outcome'),
        Index('idx_calls_assistant_status', 'assistant_id', 'status'),
        Index('idx_calls_created_at', 'created_at'),
    )


class Appointment(Base):
    """Appointment model for managing patient appointments."""
    __tablename__ = "appointments"
    
    id: Mapped[str] = mapped_column(
        String, 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    tenant_id: Mapped[str] = mapped_column(
        String(50), 
        nullable=False, 
        index=True
    )
    clinic_id: Mapped[str] = mapped_column(
        String, 
        ForeignKey("clinics.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    patient_id: Mapped[Optional[str]] = mapped_column(
        String, 
        nullable=True, 
        index=True
    )
    assistant_id: Mapped[Optional[str]] = mapped_column(
        String(100), 
        nullable=True, 
        index=True
    )
    call_id: Mapped[Optional[str]] = mapped_column(
        String, 
        ForeignKey("calls.id", ondelete="SET NULL"), 
        nullable=True, 
        index=True
    )
    service_type: Mapped[str] = mapped_column(
        String(100), 
        nullable=False, 
        index=True
    )
    appointment_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        index=True
    )
    appointment_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        index=True
    )
    duration_minutes: Mapped[int] = mapped_column(
        Integer, 
        nullable=False, 
        default=60
    )
    status: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        default='scheduled',
        index=True
    )  # 'scheduled', 'confirmed', 'completed', 'cancelled', 'no_show'
    patient_name: Mapped[str] = mapped_column(
        String(100), 
        nullable=False
    )
    patient_phone: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        index=True
    )
    patient_email: Mapped[Optional[str]] = mapped_column(
        String(255), 
        nullable=True
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True
    )
    google_calendar_event_id: Mapped[Optional[str]] = mapped_column(
        String(200), 
        nullable=True, 
        index=True
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False, 
        index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=False, 
        index=True
    )
    
    # Relationships
    clinic: Mapped["Clinic"] = relationship("Clinic", back_populates="appointments")
    call: Mapped[Optional["Call"]] = relationship("Call", back_populates="appointments")
    
    # Performance indexes for appointment management
    __table_args__ = (
        Index('idx_appointments_clinic_date', 'clinic_id', 'appointment_date'),
        Index('idx_appointments_status_date', 'status', 'appointment_date'),
        Index('idx_appointments_patient_phone', 'patient_phone'),
        Index('idx_appointments_service_type', 'service_type'),
        Index('idx_appointments_created_at', 'created_at'),
    )


class Patient(Base):
    """Patient model for managing patient records."""
    __tablename__ = "patients"
    
    id: Mapped[str] = mapped_column(
        String, 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    tenant_id: Mapped[str] = mapped_column(
        String(50), 
        nullable=False, 
        index=True
    )
    clinic_id: Mapped[str] = mapped_column(
        String, 
        ForeignKey("clinics.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    first_name: Mapped[str] = mapped_column(
        String(100), 
        nullable=False
    )
    last_name: Mapped[str] = mapped_column(
        String(100), 
        nullable=False
    )
    phone: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        index=True
    )
    email: Mapped[Optional[str]] = mapped_column(
        String(255), 
        nullable=True, 
        index=True
    )
    date_of_birth: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )
    address: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True
    )
    insurance_provider: Mapped[Optional[str]] = mapped_column(
        String(100), 
        nullable=True
    )
    insurance_number: Mapped[Optional[str]] = mapped_column(
        String(100), 
        nullable=True
    )
    emergency_contact_name: Mapped[Optional[str]] = mapped_column(
        String(100), 
        nullable=True
    )
    emergency_contact_phone: Mapped[Optional[str]] = mapped_column(
        String(20), 
        nullable=True
    )
    preferred_communication: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        default='phone'
    )  # 'phone', 'email', 'sms'
    notes: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False, 
        index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=False, 
        index=True
    )
    
    # Relationships
    clinic: Mapped["Clinic"] = relationship("Clinic", back_populates="patients")
    
    # Performance indexes for patient management
    __table_args__ = (
        Index('idx_patients_clinic_name', 'clinic_id', 'last_name', 'first_name'),
        Index('idx_patients_phone', 'phone'),
        Index('idx_patients_email', 'email'),
        Index('idx_patients_created_at', 'created_at'),
    )


class PhoneNumber(Base):
    """Phone number model for managing VAPI phone numbers."""
    __tablename__ = "phone_numbers"
    
    id: Mapped[str] = mapped_column(
        String, 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    tenant_id: Mapped[str] = mapped_column(
        String(50), 
        nullable=False, 
        index=True
    )
    assistant_id: Mapped[Optional[str]] = mapped_column(
        String(100), 
        nullable=True, 
        index=True
    )
    phone_number: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        unique=True, 
        index=True
    )
    vapi_phone_id: Mapped[Optional[str]] = mapped_column(
        String(100), 
        nullable=True, 
        index=True
    )
    status: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        default='active',
        index=True
    )  # 'active', 'inactive', 'suspended'
    provider: Mapped[Optional[str]] = mapped_column(
        String(50), 
        nullable=True
    )  # 'vapi', 'twilio', etc.
    monthly_cost: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2), 
        nullable=True
    )
    setup_cost: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2), 
        nullable=True
    )
    activated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )
    deactivated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False, 
        index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=False, 
        index=True
    )
    
    # Relationships
    assistant: Mapped[Optional["Assistant"]] = relationship("Assistant", foreign_keys=[assistant_id], primaryjoin="PhoneNumber.assistant_id == Assistant.vapi_assistant_id")
    
    # Performance indexes for phone number management
    __table_args__ = (
        Index('idx_phone_numbers_tenant_status', 'tenant_id', 'status'),
        Index('idx_phone_numbers_assistant', 'assistant_id'),
        Index('idx_phone_numbers_created_at', 'created_at'),
    )


class BillingRecord(Base):
    """Billing record model for tracking costs and revenue."""
    __tablename__ = "billing_records"
    
    id: Mapped[str] = mapped_column(
        String, 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    tenant_id: Mapped[str] = mapped_column(
        String(50), 
        nullable=False, 
        index=True
    )
    clinic_id: Mapped[str] = mapped_column(
        String, 
        ForeignKey("clinics.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    billing_period_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        index=True
    )
    billing_period_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        index=True
    )
    total_calls: Mapped[int] = mapped_column(
        Integer, 
        nullable=False, 
        default=0
    )
    total_duration_seconds: Mapped[int] = mapped_column(
        Integer, 
        nullable=False, 
        default=0
    )
    total_cost: Mapped[float] = mapped_column(
        Numeric(10, 2), 
        nullable=False, 
        default=0.00
    )
    currency: Mapped[str] = mapped_column(
        String(3), 
        nullable=False, 
        default='USD'
    )
    vapi_cost: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2), 
        nullable=True
    )
    phone_number_cost: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2), 
        nullable=True
    )
    appointments_booked: Mapped[int] = mapped_column(
        Integer, 
        nullable=False, 
        default=0
    )
    revenue_generated: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2), 
        nullable=True
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False, 
        index=True
    )
    
    # Relationships
    clinic: Mapped["Clinic"] = relationship("Clinic", back_populates="billing_records")
    
    # Performance indexes for billing analytics
    __table_args__ = (
        Index('idx_billing_clinic_period', 'clinic_id', 'billing_period_start'),
        Index('idx_billing_period', 'billing_period_start', 'billing_period_end'),
        Index('idx_billing_created_at', 'created_at'),
    )
# Tenant model (merged from new_database_models.py)
class Tenant(Base):
    """Tenant model for multi-tenancy."""
    __tablename__ = "tenants"
    
    id: Mapped[str] = mapped_column(
        String, 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default=datetime.utcnow
    )
    
    # Relationships
    clinics: Mapped[list["Clinic"]] = relationship(
        "Clinic", back_populates="tenant", cascade="all, delete-orphan"
    )


# Integration-related models
class AssistantClinicMapping(Base):
    """Mapping between assistants and clinics for multi-tenant support."""
    __tablename__ = "assistant_clinic_mappings"
    
    id: Mapped[str] = mapped_column(
        String, 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    assistant_id: Mapped[str] = mapped_column(String, nullable=False)
    clinic_id: Mapped[str] = mapped_column(String, ForeignKey("clinics.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Relationships
    clinic: Mapped["Clinic"] = relationship("Clinic")
    
    # Constraints
    __table_args__ = (
        Index('idx_assistant_clinic_mapping', 'assistant_id', 'clinic_id'),
    )


class ClinicCalendarIntegration(Base):
    """Clinic-specific calendar integrations."""
    __tablename__ = "clinic_calendar_integrations"
    
    id: Mapped[str] = mapped_column(
        String, 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    clinic_id: Mapped[str] = mapped_column(String, ForeignKey("clinics.id"), nullable=False)
    integration_type: Mapped[str] = mapped_column(String, nullable=False)  # 'google_calendar', 'outlook', etc.
    integration_config: Mapped[dict] = mapped_column(JSON, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Relationships
    clinic: Mapped["Clinic"] = relationship("Clinic")
    
    # Constraints
    __table_args__ = (
        Index('idx_clinic_integration', 'clinic_id', 'integration_type'),
    )


class SystemAlert(Base):
    """System alerts for clinic administrators."""
    __tablename__ = "system_alerts"
    
    id: Mapped[str] = mapped_column(
        String, 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    clinic_id: Mapped[str] = mapped_column(String, ForeignKey("clinics.id"), nullable=False)
    alert_type: Mapped[str] = mapped_column(String, nullable=False)
    priority: Mapped[str] = mapped_column(String, default="medium")  # 'low', 'medium', 'high', 'critical'
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    auto_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolved_by: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow
    )
    
    # Relationships
    clinic: Mapped["Clinic"] = relationship("Clinic")
    
    # Constraints
    __table_args__ = (
        Index('idx_system_alert_clinic', 'clinic_id', 'is_resolved'),
        Index('idx_system_alert_priority', 'priority', 'created_at'),
    )


class ClinicConfiguration(Base):
    """Clinic-specific configuration settings."""
    __tablename__ = "clinic_configurations"
    
    id: Mapped[str] = mapped_column(
        String, 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    clinic_id: Mapped[str] = mapped_column(String, ForeignKey("clinics.id"), nullable=False)
    config_key: Mapped[str] = mapped_column(String, nullable=False)
    config_value: Mapped[str] = mapped_column(String, nullable=False)
    config_type: Mapped[str] = mapped_column(String, default="string")  # 'string', 'integer', 'boolean', 'json'
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Relationships
    clinic: Mapped["Clinic"] = relationship("Clinic")
    
    # Constraints
    __table_args__ = (
        Index('idx_clinic_config', 'clinic_id', 'config_key'),
    )


class IntegrationTestResult(Base):
    """Integration test results tracking."""
    __tablename__ = "integration_test_results"
    
    id: Mapped[str] = mapped_column(
        String, 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    clinic_id: Mapped[str] = mapped_column(String, ForeignKey("clinics.id"), nullable=False)
    integration_type: Mapped[str] = mapped_column(String, nullable=False)
    test_type: Mapped[str] = mapped_column(String, nullable=False)  # 'connection', 'appointment_creation', 'availability', 'full_suite'
    test_status: Mapped[str] = mapped_column(String, nullable=False)  # 'passed', 'failed', 'partial'
    test_results: Mapped[dict] = mapped_column(JSON, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    test_duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow
    )
    
    # Relationships
    clinic: Mapped["Clinic"] = relationship("Clinic")
    
    # Constraints
    __table_args__ = (
        Index('idx_integration_test', 'clinic_id', 'integration_type', 'created_at'),
    )


