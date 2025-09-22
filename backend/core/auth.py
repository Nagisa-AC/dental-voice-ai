"""
Authentication and authorization for Healthcare Voice AI.
"""

import jwt
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import logging

from core.config import settings

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer(auto_error=False)


class UserRole(str, Enum):
    """User roles for authorization."""
    ADMIN = "admin"
    OFFICE_OWNER = "office_owner"
    OFFICE_STAFF = "office_staff"
    READONLY = "readonly"


class TokenData(BaseModel):
    """Token payload data."""
    user_id: str
    email: str
    role: UserRole
    tenant_id: Optional[str] = None
    exp: datetime
    iat: datetime


class AuthUser(BaseModel):
    """Authenticated user model."""
    user_id: str
    email: str
    role: UserRole
    tenant_id: Optional[str] = None


class AuthenticationError(Exception):
    """Authentication error."""
    pass


class AuthorizationError(Exception):
    """Authorization error."""
    pass


class JWTManager:
    """JWT token management."""
    
    def __init__(self):
        self.secret_key = settings.JWT_SECRET
        if not self.secret_key:
            if settings.is_production():
                raise ValueError("JWT_SECRET environment variable is required in production")
            else:
                # Use a default secret for development
                self.secret_key = "dev-secret-key-change-in-production"
                logger.warning("Using default JWT secret for development - change in production!")
        
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
    
    def create_access_token(
        self,
        user_id: str,
        email: str,
        role: UserRole,
        tenant_id: Optional[str] = None
    ) -> str:
        """Create JWT access token."""
        now = datetime.utcnow()
        expire = now + timedelta(minutes=self.access_token_expire_minutes)
        
        payload = {
            "user_id": user_id,
            "email": email,
            "role": role.value,
            "tenant_id": tenant_id,
            "exp": expire,
            "iat": now,
            "type": "access"
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        logger.info("Access token created", user_id=user_id, role=role.value)
        return token
    
    def create_refresh_token(self, user_id: str) -> str:
        """Create JWT refresh token."""
        now = datetime.utcnow()
        expire = now + timedelta(days=self.refresh_token_expire_days)
        
        payload = {
            "user_id": user_id,
            "exp": expire,
            "iat": now,
            "type": "refresh"
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        logger.info("Refresh token created", user_id=user_id)
        return token
    
    def verify_token(self, token: str) -> TokenData:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check token type
            if payload.get("type") != "access":
                raise AuthenticationError("Invalid token type")
            
            # Check expiration
            exp = datetime.fromtimestamp(payload["exp"])
            if exp < datetime.utcnow():
                raise AuthenticationError("Token expired")
            
            return TokenData(
                user_id=payload["user_id"],
                email=payload["email"],
                role=UserRole(payload["role"]),
                tenant_id=payload.get("tenant_id"),
                exp=exp,
                iat=datetime.fromtimestamp(payload["iat"])
            )
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token expired")
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f"Invalid token: {str(e)}")
        except Exception as e:
            raise AuthenticationError(f"Token verification failed: {str(e)}")
    
    def refresh_access_token(self, refresh_token: str) -> str:
        """Create new access token from refresh token."""
        try:
            payload = jwt.decode(refresh_token, self.secret_key, algorithms=[self.algorithm])
            
            if payload.get("type") != "refresh":
                raise AuthenticationError("Invalid refresh token type")
            
            user_id = payload["user_id"]
            
            # In a real application, you would fetch user data from database
            # For now, we'll create a basic token
            return self.create_access_token(
                user_id=user_id,
                email=f"user_{user_id}@example.com",
                role=UserRole.READONLY
            )
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Refresh token expired")
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f"Invalid refresh token: {str(e)}")


# Global JWT manager
jwt_manager = JWTManager()


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> AuthUser:
    """Get current authenticated user."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        token_data = jwt_manager.verify_token(credentials.credentials)
        
        return AuthUser(
            user_id=token_data.user_id,
            email=token_data.email,
            role=token_data.role,
            tenant_id=token_data.tenant_id
        )
        
    except AuthenticationError as e:
        logger.warning("Authentication failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_role(required_roles: List[UserRole]):
    """Decorator to require specific roles."""
    def role_checker(current_user: AuthUser = Depends(get_current_user)) -> AuthUser:
        if current_user.role not in required_roles:
            logger.warning(
                "Authorization failed",
                user_id=current_user.user_id,
                user_role=current_user.role.value,
                required_roles=[role.value for role in required_roles]
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {[role.value for role in required_roles]}"
            )
        return current_user
    
    return role_checker


def require_admin(current_user: AuthUser = Depends(get_current_user)) -> AuthUser:
    """Require admin role."""
    if current_user.role not in [UserRole.ADMIN]:
        logger.warning(
            "Authorization failed",
            user_id=current_user.user_id,
            user_role=current_user.role.value,
            required_roles=[UserRole.ADMIN.value]
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions. Required role: {UserRole.ADMIN.value}"
        )
    return current_user


def require_office_access(current_user: AuthUser = Depends(get_current_user)) -> AuthUser:
    """Require office owner or staff role."""
    if current_user.role not in [UserRole.OFFICE_OWNER, UserRole.OFFICE_STAFF]:
        logger.warning(
            "Authorization failed",
            user_id=current_user.user_id,
            user_role=current_user.role.value,
            required_roles=[UserRole.OFFICE_OWNER.value, UserRole.OFFICE_STAFF.value]
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions. Required roles: {[UserRole.OFFICE_OWNER.value, UserRole.OFFICE_STAFF.value]}"
        )
    return current_user


def require_tenant_access(tenant_id: str):
    """Require access to specific tenant."""
    def tenant_checker(current_user: AuthUser = Depends(get_current_user)) -> AuthUser:
        # Admin can access any tenant
        if current_user.role == UserRole.ADMIN:
            return current_user
        
        # Office users can only access their own tenant
        if current_user.tenant_id != tenant_id:
            logger.warning(
                "Tenant access denied",
                user_id=current_user.user_id,
                user_tenant=current_user.tenant_id,
                requested_tenant=tenant_id
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this office"
            )
        
        return current_user
    
    return tenant_checker


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[AuthUser]:
    """Get current user if authenticated, None otherwise."""
    if not credentials:
        return None
    
    try:
        token_data = jwt_manager.verify_token(credentials.credentials)
        return AuthUser(
            user_id=token_data.user_id,
            email=token_data.email,
            role=token_data.role,
            tenant_id=token_data.tenant_id
        )
    except AuthenticationError:
        return None


# Mock user database removed - now using real database authentication


class LoginRequest(BaseModel):
    """Login request model."""
    email: str
    password: str


class LoginResponse(BaseModel):
    """Login response model."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: AuthUser


async def authenticate_user(email: str, password: str) -> Optional[AuthUser]:
    """Authenticate user with email and password using database."""
    from services.auth_service import AuthService
    from core.database import get_async_db
    
    async with get_async_db() as db:
        auth_service = AuthService(db)
        return await auth_service.authenticate_user(email, password)


def create_login_response(user: AuthUser) -> LoginResponse:
    """Create login response with tokens."""
    access_token = jwt_manager.create_access_token(
        user_id=user.user_id,
        email=user.email,
        role=user.role,
        tenant_id=user.tenant_id
    )
    
    refresh_token = jwt_manager.create_refresh_token(user.user_id)
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=jwt_manager.access_token_expire_minutes * 60,
        user=user
    )
