"""
Database Models for Alembic Migrations

SQLAlchemy ORM models for database schema management.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

# Note: Encryption is handled at the service level for better compatibility

Base = declarative_base()


class User(Base):
    """User model for authentication and authorization."""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="user", index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    
    # Performance indexes
    __table_args__ = (
        Index('idx_users_email_active', 'email', 'is_active'),
        Index('idx_users_role_active', 'role', 'is_active'),
        Index('idx_users_created_at', 'created_at'),
        Index('idx_users_last_login', 'last_login'),
    )


class RefreshToken(Base):
    """Refresh token model for JWT token rotation."""
    __tablename__ = "refresh_tokens"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(255), nullable=False, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    is_revoked = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="refresh_tokens")
    
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
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False, index=True)
    industry_type = Column(String(50), nullable=False, default="dental", index=True)
    status = Column(String(20), nullable=False, default="pending", index=True)
    
    # Contact Information
    phone = Column(String(20), nullable=False, index=True)
    email = Column(String(100), nullable=False, index=True)
    address = Column(Text, nullable=False)
    website = Column(String(200), nullable=True)
    
    # Business Configuration
    business_hours = Column(JSON, nullable=True)
    services = Column(JSON, nullable=True)
    policies = Column(JSON, nullable=True)
    
    # AI Assistant Configuration
    vapi_assistant_id = Column(String(100), nullable=True, index=True)
    assistant_config = Column(JSON, nullable=True)
    
    # FAQ and Knowledge Base
    faq_content = Column(Text, nullable=True)
    faq_filename = Column(String(255), nullable=True)
    
    # Admin Configuration
    admin_notes = Column(Text, nullable=True)
    approved_by = Column(String, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    approver = relationship("User", foreign_keys=[approved_by])
    audit_logs = relationship("AuditLog", back_populates="clinic", cascade="all, delete-orphan")
    
    # Performance indexes
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
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(50), nullable=False, index=True)
    vapi_assistant_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    model_id = Column(String(50), nullable=False)
    voice_id = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default="active", index=True)
    config = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Performance indexes
    __table_args__ = (
        Index('idx_assistants_tenant_status', 'tenant_id', 'status'),
        Index('idx_assistants_vapi_id', 'vapi_assistant_id'),
        Index('idx_assistants_created', 'created_at'),
        Index('idx_assistants_updated_at', 'updated_at'),
        Index('idx_assistants_name', 'name'),
    )


class AuditLog(Base):
    """Audit log model for HIPAA compliance and security monitoring."""
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    clinic_id = Column(String, ForeignKey("clinics.id", ondelete="CASCADE"), nullable=True, index=True)
    action = Column(String(50), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False, index=True)
    resource_id = Column(String(100), nullable=True, index=True)
    details = Column(JSON, nullable=True)
    
    # Request Information
    ip_address = Column(String(45), nullable=True, index=True)
    user_agent = Column(Text, nullable=True)
    request_id = Column(String(100), nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    clinic = relationship("Clinic", back_populates="audit_logs")
    
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
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    clinic_id = Column(String, ForeignKey("clinics.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # File Information
    original_filename = Column(String(255), nullable=False)
    secure_filename = Column(String(255), nullable=False, unique=True, index=True)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_hash = Column(String(64), nullable=False, index=True)
    file_type = Column(String(50), nullable=False, index=True)
    mime_type = Column(String(100), nullable=False)
    
    # Upload Status
    status = Column(String(20), nullable=False, default="uploaded", index=True)
    is_quarantined = Column(Boolean, default=False, nullable=False, index=True)
    quarantine_reason = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User")
    clinic = relationship("Clinic")
    
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
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    token_hash = Column(String(255), nullable=False, unique=True, index=True)
    is_used = Column(Boolean, default=False, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('idx_csrf_tokens_user_expires', 'user_id', 'expires_at'),
        Index('idx_csrf_tokens_expires_used', 'expires_at', 'is_used'),
        Index('idx_csrf_tokens_created', 'created_at'),
    )


class RateLimit(Base):
    """Rate limit model for tracking rate limiting."""
    __tablename__ = "rate_limits"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    key = Column(String(255), nullable=False, index=True)  # IP address or user ID
    endpoint = Column(String(200), nullable=False, index=True)
    method = Column(String(10), nullable=False, index=True)
    count = Column(Integer, nullable=False, default=1)
    window_start = Column(DateTime(timezone=True), nullable=False, index=True)
    window_end = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_rate_limits_key_endpoint', 'key', 'endpoint'),
        Index('idx_rate_limits_window', 'window_start', 'window_end'),
        Index('idx_rate_limits_created', 'created_at'),
    )