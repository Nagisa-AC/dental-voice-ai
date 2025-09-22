"""
Tenant management API endpoints for multi-tenant healthcare practice management.

Handles tenant creation, user management, and onboarding workflows.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from db.models.database_models import Tenant
from db.models.database_models import User, UserRole
from services.tenant_service import TenantService
from services.auth_service import AuthService
from core.auth import require_admin, AuthUser, get_current_user
from core.validation import sanitize_input, validate_email
from pydantic import BaseModel, Field, EmailStr

logger = logging.getLogger(__name__)

router = APIRouter()

# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class TenantCreateRequest(BaseModel):
    """Request schema for creating a new tenant."""
    name: str = Field(..., min_length=2, max_length=100, description="Tenant name")
    admin_email: EmailStr = Field(..., description="Admin user email")
    admin_password: str = Field(..., min_length=8, description="Admin user password")
    admin_first_name: str = Field(..., min_length=1, max_length=50, description="Admin first name")
    admin_last_name: str = Field(..., min_length=1, max_length=50, description="Admin last name")
    phone_number: Optional[str] = Field(None, description="Primary phone number")
    address: Optional[str] = Field(None, description="Business address")
    website: Optional[str] = Field(None, description="Business website")

class TenantResponse(BaseModel):
    """Response schema for tenant information."""
    id: str
    name: str
    created_at: datetime
    admin_user_id: str
    admin_email: str

class TenantListResponse(BaseModel):
    """Response schema for tenant list."""
    tenants: List[TenantResponse]
    total: int

# ============================================================================
# TENANT MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    tenant_data: TenantCreateRequest,
    tenant_service: TenantService = Depends(lambda: TenantService()),
    auth_service: AuthService = Depends(lambda: AuthService())
):
    """
    Create a new tenant with an admin user.
    
    This endpoint creates:
    1. A new tenant
    2. An admin user for the tenant
    3. Sets up the tenant's initial configuration
    
    Args:
        tenant_data: Tenant creation data including admin user details
        
    Returns:
        TenantResponse with tenant and admin user information
        
    Raises:
        HTTPException: If tenant creation fails or email already exists
    """
    try:
        # Validate and sanitize input
        sanitized_data = {
            "name": sanitize_input(tenant_data.name),
            "admin_email": validate_email(tenant_data.admin_email),
            "admin_password": tenant_data.admin_password,
            "admin_first_name": sanitize_input(tenant_data.admin_first_name),
            "admin_last_name": sanitize_input(tenant_data.admin_last_name),
            "phone_number": sanitize_input(tenant_data.phone_number) if tenant_data.phone_number else None,
            "address": sanitize_input(tenant_data.address) if tenant_data.address else None,
            "website": sanitize_input(tenant_data.website) if tenant_data.website else None,
        }
        
        logger.info(f"Creating new tenant: {sanitized_data['name']}")
        
        # Create tenant with admin user
        tenant, admin_user = await tenant_service.create_tenant_with_admin(
            name=sanitized_data["name"],
            admin_email=sanitized_data["admin_email"],
            admin_password=sanitized_data["admin_password"],
            admin_first_name=sanitized_data["admin_first_name"],
            admin_last_name=sanitized_data["admin_last_name"],
            phone_number=sanitized_data["phone_number"],
            address=sanitized_data["address"],
            website=sanitized_data["website"]
        )
        
        logger.info(f"Successfully created tenant {tenant.id} with admin user {admin_user.id}")
        
        return TenantResponse(
            id=tenant.id,
            name=tenant.name,
            created_at=tenant.created_at,
            admin_user_id=admin_user.id,
            admin_email=admin_user.email
        )
        
    except ValueError as e:
        logger.error(f"Validation error creating tenant: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to create tenant: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create tenant: {str(e)}"
        )

@router.get("/", response_model=TenantListResponse)
async def list_tenants(
    current_user: AuthUser = Depends(require_admin),
    tenant_service: TenantService = Depends(lambda: TenantService())
):
    """
    List all tenants (admin only).
    
    Args:
        current_user: Current authenticated user (must be admin)
        
    Returns:
        List of all tenants with their admin users
    """
    try:
        tenants = await tenant_service.list_tenants()
        
        tenant_responses = []
        for tenant in tenants:
            # Get admin user for each tenant
            admin_user = await tenant_service.get_tenant_admin(tenant.id)
            tenant_responses.append(TenantResponse(
                id=tenant.id,
                name=tenant.name,
                created_at=tenant.created_at,
                admin_user_id=admin_user.id if admin_user else "",
                admin_email=admin_user.email if admin_user else ""
            ))
        
        return TenantListResponse(
            tenants=tenant_responses,
            total=len(tenant_responses)
        )
        
    except Exception as e:
        logger.error(f"Failed to list tenants: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list tenants: {str(e)}"
        )

@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: str,
    current_user: AuthUser = Depends(get_current_user),
    tenant_service: TenantService = Depends(lambda: TenantService())
):
    """
    Get tenant information.
    
    Args:
        tenant_id: Tenant ID
        current_user: Current authenticated user
        
    Returns:
        Tenant information with admin user details
    """
    try:
        # Check if user has access to this tenant
        if current_user.role != UserRole.SUPER_ADMIN and current_user.tenant_id != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this tenant"
            )
        
        tenant = await tenant_service.get_tenant(tenant_id)
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        admin_user = await tenant_service.get_tenant_admin(tenant_id)
        
        return TenantResponse(
            id=tenant.id,
            name=tenant.name,
            created_at=tenant.created_at,
            admin_user_id=admin_user.id if admin_user else "",
            admin_email=admin_user.email if admin_user else ""
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get tenant {tenant_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tenant: {str(e)}"
        )

@router.post("/{tenant_id}/users", response_model=Dict[str, str])
async def create_tenant_user(
    tenant_id: str,
    email: EmailStr,
    password: str,
    first_name: str,
    last_name: str,
    role: UserRole = UserRole.READONLY,
    current_user: AuthUser = Depends(get_current_user),
    auth_service: AuthService = Depends(lambda: AuthService())
):
    """
    Create a new user for a specific tenant.
    
    Args:
        tenant_id: Tenant ID
        email: User email
        password: User password
        first_name: User first name
        last_name: User last name
        role: User role
        current_user: Current authenticated user
        
    Returns:
        Created user information
    """
    try:
        # Check if user has access to this tenant
        if current_user.role != UserRole.SUPER_ADMIN and current_user.tenant_id != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this tenant"
            )
        
        # Create user for the tenant
        user = await auth_service.create_user(
            email=email,
            password=password,
            role=role,
            tenant_id=tenant_id
        )
        
        logger.info(f"Created user {user.id} for tenant {tenant_id}")
        
        return {
            "user_id": user.id,
            "email": user.email,
            "role": user.role.value,
            "tenant_id": tenant_id,
            "message": "User created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create user for tenant {tenant_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )

@router.get("/{tenant_id}/users", response_model=List[Dict[str, Any]])
async def list_tenant_users(
    tenant_id: str,
    current_user: AuthUser = Depends(get_current_user),
    tenant_service: TenantService = Depends(lambda: TenantService())
):
    """
    List all users for a specific tenant.
    
    Args:
        tenant_id: Tenant ID
        current_user: Current authenticated user
        
    Returns:
        List of users for the tenant
    """
    try:
        # Check if user has access to this tenant
        if current_user.role != UserRole.SUPER_ADMIN and current_user.tenant_id != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this tenant"
            )
        
        users = await tenant_service.list_tenant_users(tenant_id)
        
        return [
            {
                "id": user.id,
                "email": user.email,
                "role": user.role.value,
                "is_active": user.is_active,
                "created_at": user.created_at
            }
            for user in users
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list users for tenant {tenant_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list users: {str(e)}"
        )
