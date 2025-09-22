"""
JWT Token Models for Secure Authentication

Implements JWT with refresh token rotation for production security.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

from core.auth import UserRole


class TokenType(str, Enum):
    """Types of JWT tokens."""
    ACCESS = "access"
    REFRESH = "refresh"


class TokenResponse(BaseModel):
    """Response model for token operations."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration time in seconds")
    refresh_expires_in: int = Field(..., description="Refresh token expiration time in seconds")


class TokenRefreshRequest(BaseModel):
    """Request model for token refresh."""
    refresh_token: str = Field(..., description="Valid refresh token")


class TokenClaims(BaseModel):
    """JWT token claims."""
    sub: str = Field(..., description="Subject (user ID)")
    email: str = Field(..., description="User email")
    role: UserRole = Field(..., description="User role")
    tenant_id: str = Field(..., description="Tenant ID for multi-tenancy")
    token_type: TokenType = Field(..., description="Token type")
    iat: int = Field(..., description="Issued at timestamp")
    exp: int = Field(..., description="Expiration timestamp")
    jti: str = Field(..., description="JWT ID for token tracking")
    iss: str = Field(default="healthcare-voice-ai", description="Issuer")
    aud: str = Field(default="healthcare-voice-ai", description="Audience")


class TokenValidationResult(BaseModel):
    """Result of token validation."""
    valid: bool = Field(..., description="Whether token is valid")
    claims: Optional[TokenClaims] = Field(None, description="Token claims if valid")
    error: Optional[str] = Field(None, description="Error message if invalid")
    expired: bool = Field(default=False, description="Whether token is expired")
    revoked: bool = Field(default=False, description="Whether token is revoked")


class RefreshTokenRecord(BaseModel):
    """Database record for refresh tokens."""
    jti: str = Field(..., description="JWT ID")
    user_id: str = Field(..., description="User ID")
    tenant_id: str = Field(..., description="Tenant ID")
    expires_at: datetime = Field(..., description="Expiration time")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation time")
    revoked: bool = Field(default=False, description="Whether token is revoked")
    revoked_at: Optional[datetime] = Field(None, description="Revocation time")
    ip_address: Optional[str] = Field(None, description="IP address when created")
    user_agent: Optional[str] = Field(None, description="User agent when created")


class TokenRevocationRequest(BaseModel):
    """Request model for token revocation."""
    token: str = Field(..., description="Token to revoke")
    revoke_all: bool = Field(default=False, description="Revoke all user tokens")


class TokenRevocationResponse(BaseModel):
    """Response model for token revocation."""
    revoked: bool = Field(..., description="Whether token was revoked")
    message: str = Field(..., description="Response message")
    revoked_count: int = Field(default=0, description="Number of tokens revoked")
