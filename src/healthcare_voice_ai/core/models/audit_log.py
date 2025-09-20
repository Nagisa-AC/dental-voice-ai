"""
Audit Log Models for HIPAA Compliance

Lightweight audit logging to track access to protected health information (PHI).
"""

from sqlalchemy import Column, String, DateTime, Text, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

from healthcare_voice_ai.core.database import Base


class AuditAction(str, Enum):
    """Types of actions that can be audited."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    ACCESS = "access"
    EXPORT = "export"
    SHARE = "share"


class AuditResource(str, Enum):
    """Types of resources that can be audited."""
    PATIENT = "patient"
    APPOINTMENT = "appointment"
    CLINIC = "clinic"
    ASSISTANT = "assistant"
    KNOWLEDGE_BASE = "knowledge_base"
    USER = "user"
    SYSTEM = "system"


class AuditLog(Base):
    """Audit log table for HIPAA compliance."""
    __tablename__ = "audit_logs"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    
    # Audit details
    timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    action = Column(String(50), nullable=False)  # AuditAction
    resource_type = Column(String(50), nullable=False)  # AuditResource
    resource_id = Column(String(255), nullable=True)  # ID of the resource being accessed
    
    # User information
    user_id = Column(String(255), nullable=True)  # User who performed the action
    user_email = Column(String(255), nullable=True)  # User email for identification
    tenant_id = Column(String(255), nullable=False)  # Multi-tenant isolation
    
    # Request details
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(Text, nullable=True)  # Browser/client information
    request_id = Column(String(255), nullable=True)  # Request correlation ID
    
    # Action details
    description = Column(Text, nullable=True)  # Human-readable description
    details = Column(Text, nullable=True)  # JSON string with additional details
    success = Column(String(10), nullable=False, default="true")  # "true" or "false"
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_audit_timestamp', 'timestamp'),
        Index('idx_audit_user_id', 'user_id'),
        Index('idx_audit_tenant_id', 'tenant_id'),
        Index('idx_audit_action', 'action'),
        Index('idx_audit_resource', 'resource_type', 'resource_id'),
        Index('idx_audit_ip', 'ip_address'),
    )


# Pydantic models for API responses
class AuditLogEntry(BaseModel):
    """Audit log entry for API responses."""
    id: str
    timestamp: datetime
    action: AuditAction
    resource_type: AuditResource
    resource_id: Optional[str] = None
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    tenant_id: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_id: Optional[str] = None
    description: Optional[str] = None
    details: Optional[str] = None
    success: str = "true"
    
    class Config:
        from_attributes = True


class AuditLogQuery(BaseModel):
    """Query parameters for audit log searches."""
    tenant_id: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    user_id: Optional[str] = None
    action: Optional[AuditAction] = None
    resource_type: Optional[AuditResource] = None
    resource_id: Optional[str] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class AuditLogResponse(BaseModel):
    """Response model for audit log queries."""
    entries: list[AuditLogEntry]
    total: int
    limit: int
    offset: int
    has_more: bool
