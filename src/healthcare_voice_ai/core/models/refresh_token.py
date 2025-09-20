"""
Refresh Token Database Model

SQLAlchemy model for storing refresh tokens with rotation support.
"""

from sqlalchemy import Column, String, DateTime, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from datetime import datetime

from healthcare_voice_ai.core.database import Base


class RefreshToken(Base):
    """Refresh token table for JWT token rotation."""
    __tablename__ = "refresh_tokens"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    
    # Token identification
    jti = Column(String(255), nullable=False, unique=True)  # JWT ID
    
    # User information
    user_id = Column(String(255), nullable=False)
    tenant_id = Column(String(255), nullable=False)
    
    # Token lifecycle
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked = Column(Boolean, nullable=False, default=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    
    # Security tracking
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(500), nullable=True)  # Browser/client information
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_refresh_token_jti', 'jti'),
        Index('idx_refresh_token_user_id', 'user_id'),
        Index('idx_refresh_token_tenant_id', 'tenant_id'),
        Index('idx_refresh_token_expires', 'expires_at'),
        Index('idx_refresh_token_revoked', 'revoked'),
        Index('idx_refresh_token_user_tenant', 'user_id', 'tenant_id'),
    )
