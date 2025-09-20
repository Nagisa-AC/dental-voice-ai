"""
Authentication API endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer
import logging
from typing import Dict, Any

from healthcare_voice_ai.core.auth import (
    LoginRequest, AuthUser, get_current_user, UserRole, require_admin
)
from healthcare_voice_ai.core.rbac_dependencies import (
    require_permission, require_user_management, get_user_permissions
)
from healthcare_voice_ai.core.services.rbac_service import Permission
from healthcare_voice_ai.core.models.jwt_models import TokenResponse, TokenRefreshRequest
from healthcare_voice_ai.core.services.auth_service import AuthService
from healthcare_voice_ai.core.database import get_async_db
from healthcare_voice_ai.core.services.rate_limiting_service import (
    get_rate_limiter, rate_limit_auth, rate_limit_api
)

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()


@router.post("/login", response_model=TokenResponse)
@get_rate_limiter().limit(rate_limit_auth())
async def login(
    request: Request,
    login_data: LoginRequest,
    auth_service: AuthService = Depends(lambda: AuthService(get_async_db()))
):
    """
    Authenticate user and return JWT tokens with refresh token rotation.
    """
    try:
        # Authenticate user using database
        auth_user = await auth_service.authenticate_user(login_data.email, login_data.password)
        if not auth_user:
            logger.warning("Login failed", email=login_data.email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Get full user object for token creation
        user = await auth_service.get_user_by_id(auth_user.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Create token pair with refresh token rotation
        tokens = await auth_service.create_token_pair(user)
        
        logger.info("User logged in successfully", user_id=auth_user.user_id, role=auth_user.role.value)
        
        return tokens
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Login error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )


@router.post("/refresh", response_model=TokenResponse)
@get_rate_limiter().limit(rate_limit_auth())
async def refresh_token(
    request: Request,
    refresh_data: TokenRefreshRequest,
    auth_service: AuthService = Depends(lambda: AuthService(get_async_db()))
):
    """
    Refresh access token using refresh token with rotation.
    """
    try:
        # Refresh tokens with rotation
        tokens = await auth_service.refresh_tokens(refresh_data.refresh_token)
        
        logger.info("Tokens refreshed successfully")
        
        return tokens
        
    except ValueError as e:
        logger.warning("Token refresh failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Token refresh error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during token refresh"
        )


@router.post("/logout")
@get_rate_limiter().limit(rate_limit_api())
async def logout(
    request: Request,
    current_user: AuthUser = Depends(get_current_user),
    auth_service: AuthService = Depends(lambda: AuthService(get_async_db()))
):
    """
    Logout user and revoke all tokens.
    """
    try:
        # Revoke all user tokens
        revoked_count = await auth_service.revoke_user_tokens(current_user.user_id)
        
        logger.info("User logged out", user_id=current_user.user_id, revoked_tokens=revoked_count)
        
        return {
            "message": "Logged out successfully",
            "revoked_tokens": revoked_count
        }
        
    except Exception as e:
        logger.error("Logout error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during logout"
        )


@router.get("/me", response_model=AuthUser)
@get_rate_limiter().limit(rate_limit_api())
async def get_current_user_info(request: Request, current_user: AuthUser = Depends(get_current_user)):
    """
    Get current user information.
    """
    return current_user




@router.get("/verify")
async def verify_token(current_user: AuthUser = Depends(get_current_user)):
    """
    Verify if token is valid.
    """
    return {
        "valid": True,
        "user_id": current_user.user_id,
        "role": current_user.role.value,
        "tenant_id": current_user.tenant_id
    }


@router.post("/users", response_model=Dict[str, str])
async def create_user(
    email: str,
    password: str,
    role: UserRole = UserRole.READONLY,
    tenant_id: str = None,
    auth_service: AuthService = Depends(lambda: AuthService()),
    current_user: AuthUser = Depends(require_admin)
):
    """
    Create a new user (admin only).
    """
    try:
        user = await auth_service.create_user(
            email=email,
            password=password,
            role=role,
            tenant_id=tenant_id
        )
        
        logger.info("User created", user_id=user.id, email=email, role=role.value, created_by=current_user.user_id)
        
        return {
            "user_id": user.id,
            "email": user.email,
            "role": user.role.value,
            "message": "User created successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )


@router.put("/users/{user_id}/password")
async def change_password(
    user_id: str,
    new_password: str,
    auth_service: AuthService = Depends(lambda: AuthService()),
    current_user: AuthUser = Depends(get_current_user)
):
    """
    Change user password (own password or admin).
    """
    try:
        # Check if user can change this password
        if current_user.user_id != user_id and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to change this password"
            )
        
        success = await auth_service.update_user_password(user_id, new_password)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update password"
            )
        
        logger.info("Password changed", user_id=user_id, changed_by=current_user.user_id)
        
        return {"message": "Password updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to change password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to change password: {str(e)}"
        )


@router.put("/users/{user_id}/role")
async def change_user_role(
    user_id: str,
    new_role: UserRole,
    auth_service: AuthService = Depends(lambda: AuthService()),
    current_user: AuthUser = Depends(require_admin)
):
    """
    Change user role (admin only).
    """
    try:
        success = await auth_service.change_user_role(user_id, new_role)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to change user role"
            )
        
        logger.info("User role changed", user_id=user_id, new_role=new_role.value, changed_by=current_user.user_id)
        
        return {"message": "User role updated successfully"}
        
    except Exception as e:
        logger.error(f"Failed to change user role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to change user role: {str(e)}"
        )


@router.put("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: str,
    auth_service: AuthService = Depends(lambda: AuthService()),
    current_user: AuthUser = Depends(require_admin)
):
    """
    Deactivate user account (admin only).
    """
    try:
        success = await auth_service.deactivate_user(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to deactivate user"
            )
        
        logger.info("User deactivated", user_id=user_id, deactivated_by=current_user.user_id)
        
        return {"message": "User deactivated successfully"}
        
    except Exception as e:
        logger.error(f"Failed to deactivate user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deactivate user: {str(e)}"
        )


@router.put("/users/{user_id}/activate")
async def activate_user(
    user_id: str,
    auth_service: AuthService = Depends(lambda: AuthService()),
    current_user: AuthUser = Depends(require_admin)
):
    """
    Activate user account (admin only).
    """
    try:
        success = await auth_service.activate_user(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to activate user"
            )
        
        logger.info("User activated", user_id=user_id, activated_by=current_user.user_id)
        
        return {"message": "User activated successfully"}
        
    except Exception as e:
        logger.error(f"Failed to activate user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate user: {str(e)}"
        )


@router.get("/")
async def auth_info():
    """
    Get authentication information.
    """
    return {
        "service": "Dental Voice AI - Authentication",
        "description": "JWT-based authentication system with database backend",
        "endpoints": {
            "login": "POST /auth/login - Authenticate user",
            "refresh": "POST /auth/refresh - Refresh access token",
            "me": "GET /auth/me - Get current user info",
            "logout": "POST /auth/logout - Logout user",
            "verify": "GET /auth/verify - Verify token",
            "create_user": "POST /auth/users - Create new user (admin)",
            "change_password": "PUT /auth/users/{user_id}/password - Change password",
            "change_role": "PUT /auth/users/{user_id}/role - Change user role (admin)",
            "deactivate": "PUT /auth/users/{user_id}/deactivate - Deactivate user (admin)",
            "activate": "PUT /auth/users/{user_id}/activate - Activate user (admin)"
        },
        "security": {
            "type": "JWT Bearer Token",
            "algorithm": "HS256",
            "access_token_expiry": "30 minutes",
            "refresh_token_expiry": "7 days",
            "password_hashing": "bcrypt with 12 rounds"
        },
        "roles": {
            "admin": "Full system access",
            "office_owner": "Office management access",
            "office_staff": "Office staff access",
            "readonly": "Read-only access"
        }
    }


@router.get("/permissions", response_model=Dict[str, Any])
async def get_user_permissions_endpoint(
    request: Request,
    permissions: set = Depends(get_user_permissions),
    current_user: AuthUser = Depends(get_current_user)
):
    """
    Get current user's permissions (enhanced RBAC).
    """
    try:
        logger.info("Getting user permissions", user_id=current_user.user_id, role=current_user.role.value)
        
        return {
            "user_id": current_user.user_id,
            "role": current_user.role.value,
            "tenant_id": current_user.tenant_id,
            "permissions": [perm.value for perm in permissions],
            "total_permissions": len(permissions)
        }
        
    except Exception as e:
        logger.error(f"Failed to get user permissions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user permissions: {str(e)}"
        )


@router.get("/rbac/check", response_model=Dict[str, Any])
async def check_permission_endpoint(
    request: Request,
    permission: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """
    Check if current user has specific permission (enhanced RBAC).
    """
    try:
        from healthcare_voice_ai.core.services.rbac_service import rbac_service
        
        # Validate permission exists
        try:
            perm_enum = Permission(permission)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid permission: {permission}"
            )
        
        # Check permission
        has_perm = rbac_service.has_permission(current_user, perm_enum)
        
        logger.info(
            "Permission check", 
            user_id=current_user.user_id, 
            permission=permission,
            granted=has_perm
        )
        
        return {
            "user_id": current_user.user_id,
            "role": current_user.role.value,
            "permission": permission,
            "granted": has_perm
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to check permission: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check permission: {str(e)}"
        )
