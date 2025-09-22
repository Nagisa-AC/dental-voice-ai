"""
Tenant management service for multi-tenant healthcare practice management.

Handles tenant creation, user management, and tenant-specific operations.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from db.models.database_models import Tenant
from db.models.database_models import User, UserRole
from services.orm_service import ORMService
from services.auth_service import AuthService
from core.database import get_async_db
# Define custom exceptions for tenant service
class ValidationError(Exception):
    """Raised when validation fails."""
    pass

class DatabaseError(Exception):
    """Raised when database operations fail."""
    pass

logger = logging.getLogger(__name__)


class TenantService:
    """
    Service for managing tenants and tenant-specific operations.
    
    Provides methods for:
    - Creating tenants with admin users
    - Managing tenant users
    - Tenant-specific data operations
    """
    
    def __init__(self, db_session=None):
        """Initialize tenant service."""
        self.db_session = db_session
        self.logger = logging.getLogger(__name__)
    
    async def create_tenant_with_admin(
        self,
        name: str,
        admin_email: str,
        admin_password: str,
        admin_first_name: str,
        admin_last_name: str,
        phone_number: Optional[str] = None,
        address: Optional[str] = None,
        website: Optional[str] = None
    ) -> tuple[Tenant, User]:
        """
        Create a new tenant with an admin user.
        
        Args:
            name: Tenant name
            admin_email: Admin user email
            admin_password: Admin user password
            admin_first_name: Admin user first name
            admin_last_name: Admin user last name
            phone_number: Optional phone number
            address: Optional business address
            website: Optional business website
            
        Returns:
            Tuple of (Tenant, User) objects
            
        Raises:
            ValidationError: If tenant or user creation fails
            DatabaseError: If database operation fails
        """
        try:
            from core.database import db_manager
            from sqlalchemy import text
            
            # Get database session
            async with db_manager.get_async_session() as session:
                # Check if admin email already exists
                result = await session.execute(text("SELECT id FROM users WHERE email = :email"), {"email": admin_email})
                existing_user = result.fetchone()
                if existing_user:
                    raise ValidationError(f"User with email {admin_email} already exists")
                
                # Create tenant
                tenant_id = str(uuid.uuid4())
                await session.execute(
                    text("INSERT INTO tenants (id, name, created_at) VALUES (:id, :name, NOW())"),
                    {"id": tenant_id, "name": name}
                )
                
                # Create admin user for the tenant
                from core.security import hash_password
                password_hash = hash_password(admin_password)[0]
                
                user_id = str(uuid.uuid4())
                await session.execute(
                    text("""
                        INSERT INTO users (id, email, password_hash, role, tenant_id, is_active, created_at)
                        VALUES (:id, :email, :password_hash, :role, :tenant_id, :is_active, NOW())
                    """),
                    {
                        "id": user_id,
                        "email": admin_email,
                        "password_hash": password_hash,
                        "role": "admin",
                        "tenant_id": tenant_id,
                        "is_active": True
                    }
                )
                
                await session.commit()
                
                # Create tenant and user objects for return
                tenant = Tenant(id=tenant_id, name=name, created_at=datetime.utcnow())
                admin_user = User(
                    id=user_id,
                    email=admin_email,
                    password_hash=password_hash,
                    role=UserRole.ADMIN,
                    tenant_id=tenant_id,
                    is_active=True,
                    created_at=datetime.utcnow()
                )
            
            self.logger.info(f"Created admin user: {admin_user.id} for tenant: {tenant.id}")
            
            return tenant, admin_user
            
        except ValidationError:
            raise
        except Exception as e:
            self.logger.error(f"Error creating tenant with admin: {e}")
            raise DatabaseError(f"Failed to create tenant: {str(e)}")
    
    async def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """
        Get tenant by ID.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Tenant object or None if not found
        """
        try:
            return await self.orm_service.get_by_id(Tenant, tenant_id)
        except Exception as e:
            self.logger.error(f"Error getting tenant {tenant_id}: {e}")
            return None
    
    async def list_tenants(self) -> List[Tenant]:
        """
        List all tenants.
        
        Returns:
            List of Tenant objects
        """
        try:
            return await self.orm_service.get_all(Tenant)
        except Exception as e:
            self.logger.error(f"Error listing tenants: {e}")
            return []
    
    async def get_tenant_admin(self, tenant_id: str) -> Optional[User]:
        """
        Get the admin user for a tenant.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Admin User object or None if not found
        """
        try:
            users = await self.orm_service.get_all(User)
            for user in users:
                if user.tenant_id == tenant_id and user.role == UserRole.ADMIN:
                    return user
            return None
        except Exception as e:
            self.logger.error(f"Error getting tenant admin for {tenant_id}: {e}")
            return None
    
    async def list_tenant_users(self, tenant_id: str) -> List[User]:
        """
        List all users for a tenant.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            List of User objects for the tenant
        """
        try:
            users = await self.orm_service.get_all(User)
            return [user for user in users if user.tenant_id == tenant_id]
        except Exception as e:
            self.logger.error(f"Error listing users for tenant {tenant_id}: {e}")
            return []
    
    async def create_tenant_user(
        self,
        tenant_id: str,
        email: str,
        password: str,
        role: UserRole = UserRole.READONLY,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> User:
        """
        Create a new user for a tenant.
        
        Args:
            tenant_id: Tenant ID
            email: User email
            password: User password
            role: User role
            first_name: Optional first name
            last_name: Optional last name
            
        Returns:
            Created User object
            
        Raises:
            ValidationError: If user creation fails
            DatabaseError: If database operation fails
        """
        try:
            # Check if user already exists
            users = await self.orm_service.get_all(User)
            existing_user = next((u for u in users if u.email == email), None)
            if existing_user:
                raise ValidationError(f"User with email {email} already exists")
            
            # Create user for the tenant
            from core.security import hash_password
            password_hash = hash_password(password)[0]
            
            user = await self.orm_service.create(
                User,
                email=email,
                password_hash=password_hash,
                role=role,
                tenant_id=tenant_id,
                is_active=True
            )
            
            self.logger.info(f"Created user {user.id} for tenant {tenant_id}")
            return user
            
        except ValidationError:
            raise
        except Exception as e:
            self.logger.error(f"Error creating user for tenant {tenant_id}: {e}")
            raise DatabaseError(f"Failed to create user: {str(e)}")
    
    async def update_tenant(
        self,
        tenant_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Tenant]:
        """
        Update tenant information.
        
        Args:
            tenant_id: Tenant ID
            updates: Dictionary of fields to update
            
        Returns:
            Updated Tenant object or None if not found
        """
        try:
            tenant = await self.get_tenant(tenant_id)
            if not tenant:
                return None
            
            # Update fields
            for field, value in updates.items():
                if hasattr(tenant, field):
                    setattr(tenant, field, value)
            
            # Save changes
            updated_tenant = await self.orm_service.update(tenant)
            self.logger.info(f"Updated tenant {tenant_id}")
            return updated_tenant
            
        except Exception as e:
            self.logger.error(f"Error updating tenant {tenant_id}: {e}")
            return None
    
    async def delete_tenant(self, tenant_id: str) -> bool:
        """
        Delete a tenant and all associated data.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            # Get tenant
            tenant = await self.get_tenant(tenant_id)
            if not tenant:
                return False
            
            # Delete tenant (cascade will handle related data)
            await self.orm_service.delete(Tenant, tenant_id)
            
            self.logger.info(f"Deleted tenant {tenant_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting tenant {tenant_id}: {e}")
            return False
    
    async def get_tenant_stats(self, tenant_id: str) -> Dict[str, Any]:
        """
        Get statistics for a tenant.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Dictionary with tenant statistics
        """
        try:
            # Get tenant
            tenant = await self.get_tenant(tenant_id)
            if not tenant:
                return {}
            
            # Get user count
            users = await self.list_tenant_users(tenant_id)
            user_count = len(users)
            
            # Get clinic count (if clinics table exists)
            try:
                from db.models.database_models import Clinic
                clinics = await self.orm_service.get_all(Clinic)
                clinic_count = len([c for c in clinics if c.tenant_id == tenant_id])
            except:
                clinic_count = 0
            
            return {
                "tenant_id": tenant_id,
                "tenant_name": tenant.name,
                "user_count": user_count,
                "clinic_count": clinic_count,
                "created_at": tenant.created_at
            }
            
        except Exception as e:
            self.logger.error(f"Error getting tenant stats for {tenant_id}: {e}")
            return {}
