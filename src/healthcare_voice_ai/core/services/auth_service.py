"""
Authentication service for Healthcare Voice AI.

Provides secure user authentication with proper password hashing,
user management, and session tracking using the database.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import bcrypt
import secrets

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from healthcare_voice_ai.core.database import get_async_db
from healthcare_voice_ai.core.auth import UserRole
from healthcare_voice_ai.core.models.auth_models import User
from healthcare_voice_ai.core.errors import DatabaseError, ValidationError, AuthenticationError
from healthcare_voice_ai.core.auth import AuthUser
from healthcare_voice_ai.core.services.jwt_service import JWTService
from healthcare_voice_ai.core.models.jwt_models import TokenResponse

logger = logging.getLogger(__name__)


class AuthService:
    """
    Authentication service with proper password hashing and user management.
    
    Provides secure authentication using bcrypt for password hashing,
    database-backed user management, and JWT token generation.
    """
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.jwt_service = JWTService()
    
    async def authenticate_user(self, email: str, password: str) -> Optional[AuthUser]:
        """
        Authenticate user with email and password.
        
        Args:
            email: User's email address
            password: Plain text password
            
        Returns:
            AuthUser if authentication successful, None otherwise
            
        Raises:
            AuthenticationError: If authentication fails
        """
        try:
            # Get user from database
            user = await self.get_user_by_email(email)
            if not user:
                logger.warning("Authentication failed: user not found", email=email)
                return None
            
            # Check if user is active
            if not user.is_active:
                logger.warning("Authentication failed: user inactive", email=email)
                return None
            
            # Verify password
            if not self.jwt_service.verify_password(password, user.password_hash):
                logger.warning("Authentication failed: invalid password", email=email)
                return None
            
            # Update last login
            await self.update_user_last_login(user.id)
            
            logger.info("User authenticated successfully", user_id=user.id, email=email)
            
            return AuthUser(
                user_id=user.id,
                email=user.email,
                role=user.role,
                tenant_id=user.tenant_id
            )
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    async def create_token_pair(
        self, 
        user: User, 
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> TokenResponse:
        """
        Create JWT token pair for authenticated user.
        
        Args:
            user: Authenticated user
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            TokenResponse with access and refresh tokens
        """
        return await self.jwt_service.create_token_pair(user, ip_address, user_agent)
    
    async def refresh_tokens(
        self, 
        refresh_token: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> TokenResponse:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Valid refresh token
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            New TokenResponse with rotated tokens
        """
        return await self.jwt_service.refresh_access_token(refresh_token, ip_address, user_agent)
    
    async def revoke_user_tokens(self, user_id: str) -> int:
        """
        Revoke all tokens for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Number of tokens revoked
        """
        return await self.jwt_service.revoke_all_user_tokens(user_id)
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address using ORM service."""
        try:
            from healthcare_voice_ai.core.services.orm_service import get_record_by_field
            return await get_record_by_field(User, 'email', email)
        except Exception as e:
            logger.error(f"Failed to get user by email: {e}")
            raise DatabaseError(f"Failed to get user: {str(e)}")
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID using ORM service."""
        try:
            from healthcare_voice_ai.core.services.orm_service import get_record_by_id
            return await get_record_by_id(User, user_id)
        except Exception as e:
            logger.error(f"Failed to get user by ID: {e}")
            raise DatabaseError(f"Failed to get user: {str(e)}")
    
    async def create_user(
        self, 
        email: str, 
        password: str, 
        role: UserRole = UserRole.READONLY,
        tenant_id: Optional[str] = None
    ) -> User:
        """
        Create a new user with hashed password.
        
        Args:
            email: User's email address
            password: Plain text password
            role: User role
            tenant_id: Optional tenant ID for office users
            
        Returns:
            Created User object
            
        Raises:
            ValidationError: If user already exists or validation fails
            DatabaseError: If database operation fails
        """
        try:
            # Check if user already exists
            existing_user = await self.get_user_by_email(email)
            if existing_user:
                raise ValidationError(f"User with email {email} already exists")
            
            # Hash password
            password_hash = self.jwt_service.hash_password(password)
            
            # Create user using ORM service
            from healthcare_voice_ai.core.services.orm_service import create_record
            user = await create_record(
                User,
                email=email,
                password_hash=password_hash,
                role=role,
                tenant_id=tenant_id,
                is_active=True
            )
            
            logger.info("User created successfully", user_id=user.id, email=email, role=role.value)
            return user
            
        except ValidationError:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to create user: {e}")
            raise DatabaseError(f"Failed to create user: {str(e)}")
    
    async def update_user_password(self, user_id: str, new_password: str) -> bool:
        """
        Update user password.
        
        Args:
            user_id: User ID
            new_password: New plain text password
            
        Returns:
            True if successful
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            # Hash new password
            password_hash = self.jwt_service.hash_password(new_password)
            
            # Update password
            await self.db.execute(
                update(User)
                .where(User.id == user_id)
                .values(password_hash=password_hash)
            )
            await self.db.commit()
            
            logger.info("User password updated", user_id=user_id)
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to update user password: {e}")
            raise DatabaseError(f"Failed to update password: {str(e)}")
    
    async def update_user_last_login(self, user_id: str) -> None:
        """Update user's last login timestamp."""
        try:
            await self.db.execute(
                update(User)
                .where(User.id == user_id)
                .values(last_login=datetime.utcnow())
            )
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to update user last login: {e}")
            raise DatabaseError(f"Failed to update last login: {str(e)}")
    
    async def deactivate_user(self, user_id: str) -> bool:
        """
        Deactivate a user account.
        
        Args:
            user_id: User ID to deactivate
            
        Returns:
            True if successful
        """
        try:
            await self.db.execute(
                update(User)
                .where(User.id == user_id)
                .values(is_active=False)
            )
            await self.db.commit()
            
            logger.info("User deactivated", user_id=user_id)
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to deactivate user: {e}")
            raise DatabaseError(f"Failed to deactivate user: {str(e)}")
    
    async def activate_user(self, user_id: str) -> bool:
        """
        Activate a user account.
        
        Args:
            user_id: User ID to activate
            
        Returns:
            True if successful
        """
        try:
            await self.db.execute(
                update(User)
                .where(User.id == user_id)
                .values(is_active=True)
            )
            await self.db.commit()
            
            logger.info("User activated", user_id=user_id)
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to activate user: {e}")
            raise DatabaseError(f"Failed to activate user: {str(e)}")
    
    async def change_user_role(self, user_id: str, new_role: UserRole) -> bool:
        """
        Change user role.
        
        Args:
            user_id: User ID
            new_role: New role
            
        Returns:
            True if successful
        """
        try:
            await self.db.execute(
                update(User)
                .where(User.id == user_id)
                .values(role=new_role)
            )
            await self.db.commit()
            
            logger.info("User role changed", user_id=user_id, new_role=new_role.value)
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to change user role: {e}")
            raise DatabaseError(f"Failed to change user role: {str(e)}")
    
    
    def generate_password_reset_token(self, user_id: str) -> str:
        """
        Generate password reset token.
        
        Args:
            user_id: User ID
            
        Returns:
            Password reset token
        """
        # Generate secure random token
        token = secrets.token_urlsafe(32)
        
        # In a real application, you would store this token in the database
        # with an expiration time and associate it with the user
        logger.info("Password reset token generated", user_id=user_id)
        return token
    
    async def validate_password_reset_token(self, token: str) -> Optional[str]:
        """
        Validate password reset token and return user ID.
        
        Args:
            token: Password reset token
            
        Returns:
            User ID if token is valid, None otherwise
        """
        # In a real application, you would check the token in the database
        # and verify it hasn't expired
        logger.info("Password reset token validated", token=token[:8] + "...")
        return None  # Placeholder implementation
    
    async def reset_password(self, token: str, new_password: str) -> bool:
        """
        Reset user password using reset token.
        
        Args:
            token: Password reset token
            new_password: New plain text password
            
        Returns:
            True if successful
        """
        try:
            # Validate token and get user ID
            user_id = await self.validate_password_reset_token(token)
            if not user_id:
                return False
            
            # Update password
            return await self.update_user_password(user_id, new_password)
            
        except Exception as e:
            logger.error(f"Password reset failed: {e}")
            return False


# Dependency injection for FastAPI
async def get_auth_service() -> AuthService:
    """Get authentication service instance."""
    async with get_async_db() as db:
        yield AuthService(db)
