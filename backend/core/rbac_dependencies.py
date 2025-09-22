"""
FastAPI Dependencies for RBAC (Role-Based Access Control)

Provides FastAPI dependency functions for role and permission-based access control.
"""

from typing import List, Optional
from fastapi import Depends, HTTPException, status

from core.auth import get_current_user, AuthUser, UserRole
from services.security_service import security_service
from core.tenant_context import get_current_tenant_id


# Simple permission and resource classes
class Permission:
    """Simple permission class."""
    def __init__(self, name: str):
        self.name = name

class Resource:
    """Simple resource class."""
    def __init__(self, name: str):
        self.name = name


def require_permissions(permissions: List[Permission], 
                       resource: Optional[Resource] = None,
                       any_permission: bool = False):
    """
    FastAPI dependency to require specific permissions.
    
    Args:
        permissions: List of required permissions
        resource: Resource type for the permission check
        any_permission: If True, user needs ANY of the permissions; if False, ALL permissions
        
    Returns:
        FastAPI dependency function
    """
    def permission_checker(current_user: AuthUser = Depends(get_current_user)) -> AuthUser:
        tenant_id = get_current_tenant_id()
        
        if any_permission:
            # User needs at least one of the permissions
            has_access = any(
                rbac_service.has_permission(current_user, perm, resource, tenant_id=tenant_id)
                for perm in permissions
            )
        else:
            # User needs all permissions
            has_access = all(
                rbac_service.has_permission(current_user, perm, resource, tenant_id=tenant_id)
                for perm in permissions
            )
        
        if not has_access:
            # Audit the failed access attempt
            for perm in permissions:
                context = AccessContext(
                    user=current_user,
                    resource=resource,
                    tenant_id=tenant_id,
                    action=perm
                )
                rbac_service.audit_access_attempt(context, granted=False)
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {[p.value for p in permissions]}"
            )
        
        # Audit successful access
        for perm in permissions:
            context = AccessContext(
                user=current_user,
                resource=resource,
                tenant_id=tenant_id,
                action=perm
            )
            rbac_service.audit_access_attempt(context, granted=True)
        
        return current_user
    
    return permission_checker


def require_permission(permission: Permission, 
                      resource: Optional[Resource] = None):
    """
    FastAPI dependency to require a single permission.
    
    Args:
        permission: Required permission
        resource: Resource type for the permission check
        
    Returns:
        FastAPI dependency function
    """
    return require_permissions([permission], resource)


def require_roles(roles: List[UserRole]):
    """
    FastAPI dependency to require specific roles.
    
    Args:
        roles: List of allowed roles
        
    Returns:
        FastAPI dependency function
    """
    def role_checker(current_user: AuthUser = Depends(get_current_user)) -> AuthUser:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {[r.value for r in roles]}"
            )
        return current_user
    
    return role_checker


def require_role(role: UserRole):
    """
    FastAPI dependency to require a single role.
    
    Args:
        role: Required role
        
    Returns:
        FastAPI dependency function
    """
    return require_roles([role])


def require_admin():
    """FastAPI dependency to require admin role."""
    return require_role(UserRole.ADMIN)


def require_office_access():
    """FastAPI dependency to require office owner or staff role."""
    return require_roles([UserRole.OFFICE_OWNER, UserRole.OFFICE_STAFF])


def require_clinic_management():
    """FastAPI dependency to require clinic management permissions."""
    return require_permissions([
        Permission.READ_CLINIC, 
        Permission.UPDATE_CLINIC
    ], Resource.CLINIC)


def require_assistant_management():
    """FastAPI dependency to require assistant management permissions."""
    return require_permissions([
        Permission.READ_ASSISTANT, 
        Permission.UPDATE_ASSISTANT
    ], Resource.ASSISTANT)


def require_user_management():
    """FastAPI dependency to require user management permissions."""
    return require_permissions([
        Permission.READ_USER, 
        Permission.UPDATE_USER
    ], Resource.USER)


def require_file_upload():
    """FastAPI dependency to require file upload permissions."""
    return require_permission(Permission.UPLOAD_FILE, Resource.FILE)


def require_admin_panel():
    """FastAPI dependency to require admin panel access."""
    return require_permission(Permission.VIEW_ADMIN_PANEL, Resource.SYSTEM)


def require_audit_access():
    """FastAPI dependency to require audit log access."""
    return require_permission(Permission.VIEW_AUDIT_LOGS, Resource.SYSTEM)


def require_system_config():
    """FastAPI dependency to require system configuration access."""
    return require_permission(Permission.MANAGE_SYSTEM_CONFIG, Resource.SYSTEM)


def require_tenant_access(tenant_id: str):
    """
    FastAPI dependency to require access to specific tenant.
    
    Args:
        tenant_id: Tenant ID to check access for
        
    Returns:
        FastAPI dependency function
    """
    def tenant_checker(current_user: AuthUser = Depends(get_current_user)) -> AuthUser:
        if not rbac_service.validate_tenant_access(current_user, tenant_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied for tenant: {tenant_id}"
            )
        return current_user
    
    return tenant_checker


def require_resource_access(resource: Resource, resource_id: str, action: Permission):
    """
    FastAPI dependency to require access to specific resource.
    
    Args:
        resource: Resource type
        resource_id: Resource ID
        action: Required action/permission
        
    Returns:
        FastAPI dependency function
    """
    def resource_checker(current_user: AuthUser = Depends(get_current_user)) -> AuthUser:
        if not rbac_service.can_access_resource(current_user, resource, resource_id, action):
            context = AccessContext(
                user=current_user,
                resource=resource,
                resource_id=resource_id,
                action=action,
                tenant_id=get_current_tenant_id()
            )
            rbac_service.audit_access_attempt(context, granted=False)
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied for {resource.value} {resource_id}"
            )
        
        # Audit successful access
        context = AccessContext(
            user=current_user,
            resource=resource,
            resource_id=resource_id,
            action=action,
            tenant_id=get_current_tenant_id()
        )
        rbac_service.audit_access_attempt(context, granted=True)
        
        return current_user
    
    return resource_checker


def get_user_permissions(current_user: AuthUser = Depends(get_current_user)):
    """
    FastAPI dependency to get user permissions.
    
    Returns:
        Set of user permissions
    """
    return rbac_service.get_user_permissions(current_user)


def get_user_accessible_tenants(current_user: AuthUser = Depends(get_current_user)):
    """
    FastAPI dependency to get user's accessible tenants.
    
    Returns:
        List of tenant IDs the user can access
    """
    return rbac_service.get_accessible_tenants(current_user)
