"""
JWT Service with Refresh Token Rotation

Implements secure JWT authentication with refresh token rotation for production security.
"""

import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, and_

from healthcare_voice_ai.core.config import settings
from healthcare_voice_ai.core.models.jwt_models import (
    TokenResponse, TokenClaims, TokenValidationResult, 
    TokenType, TokenRefreshRequest
)
from healthcare_voice_ai.core.models.auth_models import User
from healthcare_voice_ai.core.auth import UserRole
from healthcare_voice_ai.core.models.refresh_token import RefreshToken
from healthcare_voice_ai.core.database import get_async_db

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class JWTService:
    """Service for JWT token management with refresh token rotation."""
    
    def __init__(self):
        """Initialize JWT service with configuration."""
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 15  # Short-lived access tokens
        self.refresh_token_expire_days = 7     # Longer-lived refresh tokens
        self.issuer = "healthcare-voice-ai"
        self.audience = "healthcare-voice-ai"
    
    def create_access_token(
        self, 
        user: User, 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token.
        
        Args:
            user: User object
            expires_delta: Custom expiration time
            
        Returns:
            JWT access token string
        """
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        # Generate unique JWT ID
        jti = secrets.token_urlsafe(32)
        
        # Create token claims
        claims = TokenClaims(
            sub=str(user.id),
            email=user.email,
            role=user.role,
            tenant_id=user.tenant_id,
            token_type=TokenType.ACCESS,
            iat=int(datetime.utcnow().timestamp()),
            exp=int(expire.timestamp()),
            jti=jti,
            iss=self.issuer,
            aud=self.audience
        )
        
        # Create JWT token
        token = jwt.encode(
            claims.dict(),
            self.secret_key,
            algorithm=self.algorithm
        )
        
        logger.debug(f"Created access token for user {user.id}")
        return token
    
    def create_refresh_token(
        self, 
        user: User, 
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> str:
        """
        Create a JWT refresh token.
        
        Args:
            user: User object
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            JWT refresh token string
        """
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        # Generate unique JWT ID
        jti = secrets.token_urlsafe(32)
        
        # Create token claims
        claims = TokenClaims(
            sub=str(user.id),
            email=user.email,
            role=user.role,
            tenant_id=user.tenant_id,
            token_type=TokenType.REFRESH,
            iat=int(datetime.utcnow().timestamp()),
            exp=int(expire.timestamp()),
            jti=jti,
            iss=self.issuer,
            aud=self.audience
        )
        
        # Create JWT token
        token = jwt.encode(
            claims.dict(),
            self.secret_key,
            algorithm=self.algorithm
        )
        
        logger.debug(f"Created refresh token for user {user.id}")
        return token, jti, expire
    
    async def create_token_pair(
        self, 
        user: User, 
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> TokenResponse:
        """
        Create both access and refresh tokens.
        
        Args:
            user: User object
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            TokenResponse with both tokens
        """
        # Create access token
        access_token = self.create_access_token(user)
        
        # Create refresh token
        refresh_token, jti, expires_at = self.create_refresh_token(user, ip_address, user_agent)
        
        # Store refresh token in database
        await self._store_refresh_token(
            jti=jti,
            user_id=str(user.id),
            tenant_id=user.tenant_id,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=self.access_token_expire_minutes * 60,
            refresh_expires_in=self.refresh_token_expire_days * 24 * 60 * 60
        )
    
    def verify_token(self, token: str) -> TokenValidationResult:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            TokenValidationResult with validation status
        """
        try:
            # Decode token
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                audience=self.audience,
                issuer=self.issuer
            )
            
            # Create claims object
            claims = TokenClaims(**payload)
            
            # Check if token is expired
            if datetime.utcnow().timestamp() > claims.exp:
                return TokenValidationResult(
                    valid=False,
                    expired=True,
                    error="Token has expired"
                )
            
            return TokenValidationResult(
                valid=True,
                claims=claims,
                expired=False
            )
            
        except JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            return TokenValidationResult(
                valid=False,
                error=f"Invalid token: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return TokenValidationResult(
                valid=False,
                error="Token verification failed"
            )
    
    async def refresh_access_token(
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
            
        Raises:
            ValueError: If refresh token is invalid or expired
        """
        # Verify refresh token
        validation_result = self.verify_token(refresh_token)
        if not validation_result.valid:
            raise ValueError(f"Invalid refresh token: {validation_result.error}")
        
        if validation_result.expired:
            raise ValueError("Refresh token has expired")
        
        claims = validation_result.claims
        if claims.token_type != TokenType.REFRESH:
            raise ValueError("Token is not a refresh token")
        
        # Check if refresh token exists in database and is not revoked
        async with get_async_db() as db:
            stmt = select(RefreshToken).where(
                and_(
                    RefreshToken.jti == claims.jti,
                    RefreshToken.user_id == claims.sub,
                    RefreshToken.tenant_id == claims.tenant_id,
                    RefreshToken.revoked == False,
                    RefreshToken.expires_at > datetime.utcnow()
                )
            )
            result = await db.execute(stmt)
            token_record = result.scalar_one_or_none()
            
            if not token_record:
                raise ValueError("Refresh token not found or revoked")
            
            # Get user from database
            user_stmt = select(User).where(User.id == claims.sub)
            user_result = await db.execute(user_stmt)
            user = user_result.scalar_one_or_none()
            
            if not user:
                raise ValueError("User not found")
            
            # Revoke old refresh token
            token_record.revoked = True
            token_record.revoked_at = datetime.utcnow()
            await db.commit()
            
            # Create new token pair (rotation)
            new_tokens = await self.create_token_pair(user, ip_address, user_agent)
            
            logger.info(f"Refreshed tokens for user {user.id}")
            return new_tokens
    
    async def revoke_refresh_token(self, jti: str) -> bool:
        """
        Revoke a specific refresh token.
        
        Args:
            jti: JWT ID of the token to revoke
            
        Returns:
            True if token was revoked, False if not found
        """
        try:
            async with get_async_db() as db:
                stmt = select(RefreshToken).where(RefreshToken.jti == jti)
                result = await db.execute(stmt)
                token_record = result.scalar_one_or_none()
                
                if token_record and not token_record.revoked:
                    token_record.revoked = True
                    token_record.revoked_at = datetime.utcnow()
                    await db.commit()
                    logger.info(f"Revoked refresh token {jti}")
                    return True
                
                return False
                
        except Exception as e:
            logger.error(f"Failed to revoke refresh token {jti}: {e}")
            return False
    
    async def revoke_all_user_tokens(self, user_id: str) -> int:
        """
        Revoke all refresh tokens for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Number of tokens revoked
        """
        try:
            async with get_async_db() as db:
                stmt = select(RefreshToken).where(
                    and_(
                        RefreshToken.user_id == user_id,
                        RefreshToken.revoked == False
                    )
                )
                result = await db.execute(stmt)
                tokens = result.scalars().all()
                
                revoked_count = 0
                for token in tokens:
                    token.revoked = True
                    token.revoked_at = datetime.utcnow()
                    revoked_count += 1
                
                await db.commit()
                logger.info(f"Revoked {revoked_count} tokens for user {user_id}")
                return revoked_count
                
        except Exception as e:
            logger.error(f"Failed to revoke all tokens for user {user_id}: {e}")
            return 0
    
    async def cleanup_expired_tokens(self) -> int:
        """
        Clean up expired refresh tokens from database.
        
        Returns:
            Number of tokens cleaned up
        """
        try:
            async with get_async_db() as db:
                stmt = delete(RefreshToken).where(
                    RefreshToken.expires_at < datetime.utcnow()
                )
                result = await db.execute(stmt)
                await db.commit()
                
                deleted_count = result.rowcount
                logger.info(f"Cleaned up {deleted_count} expired refresh tokens")
                return deleted_count
                
        except Exception as e:
            logger.error(f"Failed to cleanup expired tokens: {e}")
            return 0
    
    async def _store_refresh_token(
        self,
        jti: str,
        user_id: str,
        tenant_id: str,
        expires_at: datetime,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> None:
        """Store refresh token in database."""
        try:
            async with get_async_db() as db:
                token_record = RefreshToken(
                    jti=jti,
                    user_id=user_id,
                    tenant_id=tenant_id,
                    expires_at=expires_at,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                db.add(token_record)
                await db.commit()
                
        except Exception as e:
            logger.error(f"Failed to store refresh token: {e}")
            raise
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
