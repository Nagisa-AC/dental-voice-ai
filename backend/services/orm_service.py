
class DatabaseError(Exception):
    """Database-related error."""
    pass


class ValidationError(Exception):
    """Validation-related error."""
    pass


class AuthenticationError(Exception):
    """Authentication-related error."""
    pass


class EncryptionError(Exception):
    """Encryption-related error."""
    pass


class AuthorizationError(Exception):
    """Authorization-related error."""
    pass



"""
ORM Service for Database Operations

Comprehensive ORM service for all database operations using SQLAlchemy.
Replaces direct SQL queries with proper ORM usage for security and maintainability.
"""

import logging
from typing import Any, Dict, List, Optional, Type, TypeVar, Union
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, insert, and_, or_, func, text
from sqlalchemy.orm import selectinload, joinedload, subqueryload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from core.database import get_async_db
from db.models.database_models import (
    User, RefreshToken, Clinic, Assistant, AuditLog, FileUpload, CSRFToken, RateLimit
)
from core.tenant_context import TenantContext, get_current_tenant_id

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ORMService:
    """
    Comprehensive ORM service for database operations.
    
    Provides secure, type-safe database operations using SQLAlchemy ORM.
    All operations are parameterized to prevent SQL injection.
    """
    
    def __init__(self, db_session: Optional[AsyncSession] = None):
        """Initialize ORM service with database session."""
        self.db = db_session
        self.logger = logging.getLogger(__name__)
    
    async def get_session(self) -> AsyncSession:
        """Get database session."""
        if self.db:
            return self.db
        return get_async_db()
    
    # ============================================================================
    # TENANT ISOLATION HELPERS
    # ============================================================================
    
    def _has_tenant_field(self, model_class: Type) -> bool:
        """Check if model has tenant_id field."""
        return hasattr(model_class, 'tenant_id')
    
    def _apply_tenant_filter(self, query, model_class: Type, tenant_id: Optional[str] = None):
        """Apply tenant filtering to query if model supports it."""
        if not self._has_tenant_field(model_class):
            return query
        
        # Get tenant ID from parameter or current context
        current_tenant_id = tenant_id or get_current_tenant_id()
        if current_tenant_id:
            return query.where(model_class.tenant_id == current_tenant_id)
        
        return query
    
    def _ensure_tenant_context(self, model_class: Type, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure tenant_id is set in data for tenant-aware models."""
        if not self._has_tenant_field(model_class):
            return data
        
        # If tenant_id is already in data, use it
        if 'tenant_id' in data:
            return data
        
        # Get current tenant ID from context
        current_tenant_id = get_current_tenant_id()
        if current_tenant_id:
            data = data.copy()
            data['tenant_id'] = current_tenant_id
        
        return data
    
    # ============================================================================
    # GENERIC CRUD OPERATIONS
    # ============================================================================
    
    async def create(self, model_class: Type[T], **kwargs) -> T:
        """
        Create a new record.
        
        Args:
            model_class: SQLAlchemy model class
            **kwargs: Model attributes
            
        Returns:
            Created model instance
            
        Raises:
            DatabaseError: If creation fails
            ValidationError: If data validation fails
        """
        try:
            session = await self.get_session()
            
            # Apply tenant context to data
            tenant_aware_data = self._ensure_tenant_context(model_class, kwargs)
            
            # Create instance
            instance = model_class(**tenant_aware_data)
            session.add(instance)
            await session.commit()
            await session.refresh(instance)
            
            self.logger.info(f"Created {model_class.__name__} with ID: {getattr(instance, 'id', 'unknown')}")
            return instance
            
        except IntegrityError as e:
            await session.rollback()
            self.logger.error(f"Integrity error creating {model_class.__name__}: {e}")
            raise ValidationError(f"Data integrity violation: {str(e)}")
        except SQLAlchemyError as e:
            await session.rollback()
            self.logger.error(f"Database error creating {model_class.__name__}: {e}")
            raise DatabaseError(f"Failed to create {model_class.__name__}: {str(e)}")
        except Exception as e:
            await session.rollback()
            self.logger.error(f"Unexpected error creating {model_class.__name__}: {e}")
            raise DatabaseError(f"Unexpected error creating {model_class.__name__}: {str(e)}")
    
    async def get_by_id(self, model_class: Type[T], record_id: Any) -> Optional[T]:
        """
        Get record by ID.
        
        Args:
            model_class: SQLAlchemy model class
            record_id: Record ID
            
        Returns:
            Model instance or None if not found
        """
        try:
            session = await self.get_session()
            
            stmt = select(model_class).where(model_class.id == record_id)
            stmt = self._apply_tenant_filter(stmt, model_class)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
            
        except SQLAlchemyError as e:
            self.logger.error(f"Database error getting {model_class.__name__} by ID {record_id}: {e}")
            raise DatabaseError(f"Failed to get {model_class.__name__}: {str(e)}")
    
    async def get_by_field(self, model_class: Type[T], field_name: str, field_value: Any) -> Optional[T]:
        """
        Get record by field value.
        
        Args:
            model_class: SQLAlchemy model class
            field_name: Field name to search by
            field_value: Field value to search for
            
        Returns:
            Model instance or None if not found
        """
        try:
            session = await self.get_session()
            
            # Validate field exists
            if not hasattr(model_class, field_name):
                raise ValidationError(f"Field '{field_name}' does not exist in {model_class.__name__}")
            
            field = getattr(model_class, field_name)
            stmt = select(model_class).where(field == field_value)
            stmt = self._apply_tenant_filter(stmt, model_class)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
            
        except ValidationError:
            raise
        except SQLAlchemyError as e:
            self.logger.error(f"Database error getting {model_class.__name__} by {field_name}: {e}")
            raise DatabaseError(f"Failed to get {model_class.__name__}: {str(e)}")
    
    async def get_all(
        self, 
        model_class: Type[T], 
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        eager_load: Optional[List[str]] = None
    ) -> List[T]:
        """
        Get all records with optional filtering and pagination.
        
        Args:
            model_class: SQLAlchemy model class
            filters: Dictionary of field filters
            order_by: List of fields to order by
            limit: Maximum number of records
            offset: Number of records to skip
            eager_load: List of relationships to eager load
            
        Returns:
            List of model instances
        """
        try:
            session = await self.get_session()
            
            stmt = select(model_class)
            
            # Apply eager loading
            if eager_load:
                for relationship in eager_load:
                    if hasattr(model_class, relationship):
                        stmt = stmt.options(selectinload(getattr(model_class, relationship)))
            
            # Apply filters
            if filters:
                for field_name, value in filters.items():
                    if hasattr(model_class, field_name):
                        field = getattr(model_class, field_name)
                        stmt = stmt.where(field == value)
            
            # Apply ordering
            if order_by:
                for field_name in order_by:
                    if hasattr(model_class, field_name):
                        field = getattr(model_class, field_name)
                        stmt = stmt.order_by(field)
            
            # Apply tenant filtering
            stmt = self._apply_tenant_filter(stmt, model_class)
            
            # Apply pagination
            if limit:
                stmt = stmt.limit(limit)
            if offset:
                stmt = stmt.offset(offset)
            
            result = await session.execute(stmt)
            return result.scalars().all()
            
        except SQLAlchemyError as e:
            self.logger.error(f"Database error getting all {model_class.__name__}: {e}")
            raise DatabaseError(f"Failed to get {model_class.__name__} records: {str(e)}")
    
    async def update(self, model_class: Type[T], record_id: Any, **kwargs) -> Optional[T]:
        """
        Update record by ID.
        
        Args:
            model_class: SQLAlchemy model class
            record_id: Record ID to update
            **kwargs: Fields to update
            
        Returns:
            Updated model instance or None if not found
        """
        try:
            session = await self.get_session()
            
            # Get existing record with tenant filtering
            stmt = select(model_class).where(model_class.id == record_id)
            stmt = self._apply_tenant_filter(stmt, model_class)
            result = await session.execute(stmt)
            instance = result.scalar_one_or_none()
            
            if not instance:
                return None
            
            # Update fields
            for field_name, value in kwargs.items():
                if hasattr(instance, field_name):
                    setattr(instance, field_name, value)
                else:
                    self.logger.warning(f"Field '{field_name}' does not exist in {model_class.__name__}")
            
            # Add updated_at timestamp if field exists
            if hasattr(instance, 'updated_at'):
                setattr(instance, 'updated_at', datetime.utcnow())
            
            await session.commit()
            await session.refresh(instance)
            
            self.logger.info(f"Updated {model_class.__name__} with ID: {record_id}")
            return instance
            
        except IntegrityError as e:
            await session.rollback()
            self.logger.error(f"Integrity error updating {model_class.__name__} {record_id}: {e}")
            raise ValidationError(f"Data integrity violation: {str(e)}")
        except SQLAlchemyError as e:
            await session.rollback()
            self.logger.error(f"Database error updating {model_class.__name__} {record_id}: {e}")
            raise DatabaseError(f"Failed to update {model_class.__name__}: {str(e)}")
    
    async def delete(self, model_class: Type[T], record_id: Any) -> bool:
        """
        Delete record by ID.
        
        Args:
            model_class: SQLAlchemy model class
            record_id: Record ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        try:
            session = await self.get_session()
            
            stmt = delete(model_class).where(model_class.id == record_id)
            # Apply tenant filtering for delete operations
            if self._has_tenant_field(model_class):
                current_tenant_id = get_current_tenant_id()
                if current_tenant_id:
                    stmt = stmt.where(model_class.tenant_id == current_tenant_id)
            result = await session.execute(stmt)
            await session.commit()
            
            deleted = result.rowcount > 0
            if deleted:
                self.logger.info(f"Deleted {model_class.__name__} with ID: {record_id}")
            else:
                self.logger.warning(f"{model_class.__name__} with ID {record_id} not found for deletion")
            
            return deleted
            
        except SQLAlchemyError as e:
            await session.rollback()
            self.logger.error(f"Database error deleting {model_class.__name__} {record_id}: {e}")
            raise DatabaseError(f"Failed to delete {model_class.__name__}: {str(e)}")
    
    # ============================================================================
    # SEARCH AND QUERY OPERATIONS
    # ============================================================================
    
    async def search(
        self, 
        model_class: Type[T], 
        search_term: str, 
        search_fields: List[str],
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[T]:
        """
        Search records across multiple fields.
        
        Args:
            model_class: SQLAlchemy model class
            search_term: Term to search for
            search_fields: List of fields to search in
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of matching model instances
        """
        try:
            session = await self.get_session()
            
            # Validate search fields
            valid_fields = []
            for field_name in search_fields:
                if hasattr(model_class, field_name):
                    valid_fields.append(field_name)
                else:
                    self.logger.warning(f"Search field '{field_name}' does not exist in {model_class.__name__}")
            
            if not valid_fields:
                return []
            
            # Build search conditions
            search_conditions = []
            for field_name in valid_fields:
                field = getattr(model_class, field_name)
                # Use ILIKE for case-insensitive search (PostgreSQL)
                search_conditions.append(field.ilike(f"%{search_term}%"))
            
            # Create query
            stmt = select(model_class).where(or_(*search_conditions))
            
            # Apply pagination
            if limit:
                stmt = stmt.limit(limit)
            if offset:
                stmt = stmt.offset(offset)
            
            result = await session.execute(stmt)
            return result.scalars().all()
            
        except SQLAlchemyError as e:
            self.logger.error(f"Database error searching {model_class.__name__}: {e}")
            raise DatabaseError(f"Failed to search {model_class.__name__}: {str(e)}")
    
    async def count(self, model_class: Type[T], filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records with optional filters.
        
        Args:
            model_class: SQLAlchemy model class
            filters: Dictionary of field filters
            
        Returns:
            Number of matching records
        """
        try:
            session = await self.get_session()
            
            stmt = select(func.count(model_class.id))
            
            # Apply filters
            if filters:
                for field_name, value in filters.items():
                    if hasattr(model_class, field_name):
                        field = getattr(model_class, field_name)
                        stmt = stmt.where(field == value)
            
            result = await session.execute(stmt)
            return result.scalar() or 0
            
        except SQLAlchemyError as e:
            self.logger.error(f"Database error counting {model_class.__name__}: {e}")
            raise DatabaseError(f"Failed to count {model_class.__name__}: {str(e)}")
    
    # ============================================================================
    # BULK OPERATIONS
    # ============================================================================
    
    async def bulk_create(self, model_class: Type[T], data_list: List[Dict[str, Any]]) -> List[T]:
        """
        Create multiple records in bulk.
        
        Args:
            model_class: SQLAlchemy model class
            data_list: List of dictionaries with model data
            
        Returns:
            List of created model instances
        """
        try:
            session = await self.get_session()
            
            instances = []
            for data in data_list:
                instance = model_class(**data)
                instances.append(instance)
                session.add(instance)
            
            await session.commit()
            
            # Refresh all instances
            for instance in instances:
                await session.refresh(instance)
            
            self.logger.info(f"Bulk created {len(instances)} {model_class.__name__} records")
            return instances
            
        except IntegrityError as e:
            await session.rollback()
            self.logger.error(f"Integrity error bulk creating {model_class.__name__}: {e}")
            raise ValidationError(f"Data integrity violation: {str(e)}")
        except SQLAlchemyError as e:
            await session.rollback()
            self.logger.error(f"Database error bulk creating {model_class.__name__}: {e}")
            raise DatabaseError(f"Failed to bulk create {model_class.__name__}: {str(e)}")
    
    async def bulk_update(
        self, 
        model_class: Type[T], 
        updates: Dict[str, Any], 
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Update multiple records in bulk.
        
        Args:
            model_class: SQLAlchemy model class
            updates: Dictionary of fields to update
            filters: Dictionary of field filters
            
        Returns:
            Number of updated records
        """
        try:
            session = await self.get_session()
            
            stmt = update(model_class)
            
            # Apply filters
            if filters:
                for field_name, value in filters.items():
                    if hasattr(model_class, field_name):
                        field = getattr(model_class, field_name)
                        stmt = stmt.where(field == value)
            
            # Apply updates
            stmt = stmt.values(**updates)
            
            result = await session.execute(stmt)
            await session.commit()
            
            updated_count = result.rowcount
            self.logger.info(f"Bulk updated {updated_count} {model_class.__name__} records")
            return updated_count
            
        except SQLAlchemyError as e:
            await session.rollback()
            self.logger.error(f"Database error bulk updating {model_class.__name__}: {e}")
            raise DatabaseError(f"Failed to bulk update {model_class.__name__}: {str(e)}")
    
    # ============================================================================
    # TRANSACTION MANAGEMENT
    # ============================================================================
    
    async def execute_in_transaction(self, operations: List[callable]) -> Any:
        """
        Execute multiple operations in a single transaction.
        
        Args:
            operations: List of async functions to execute
            
        Returns:
            Result of the last operation
        """
        try:
            session = await self.get_session()
            
            results = []
            for operation in operations:
                result = await operation(session)
                results.append(result)
            
            await session.commit()
            return results[-1] if results else None
            
        except Exception as e:
            await session.rollback()
            self.logger.error(f"Transaction failed: {e}")
            raise DatabaseError(f"Transaction failed: {str(e)}")
    
    # ============================================================================
    # HEALTH CHECK AND UTILITIES
    # ============================================================================
    
    async def health_check(self) -> bool:
        """
        Perform database health check using ORM.
        
        Returns:
            True if database is healthy, False otherwise
        """
        try:
            session = await self.get_session()
            # Use a simple query to test database connectivity
            result = await session.execute(text("SELECT 1"))
            return result.scalar() == 1
        except Exception as e:
            self.logger.error(f"Database health check failed: {e}")
            return False
    
    async def get_database_info(self) -> Dict[str, Any]:
        """
        Get database information and statistics.
        
        Returns:
            Dictionary with database information
        """
        try:
            session = await self.get_session()
            
            # Get table counts
            table_counts = {}
            for model_class in [User, RefreshToken, Clinic, Assistant, AuditLog, FileUpload, CSRFToken, RateLimit]:
                count = await self.count(model_class)
                table_counts[model_class.__name__] = count
            
            # Get database version
            result = await session.execute(text("SELECT version()"))
            db_version = result.scalar()
            
            return {
                "database_version": db_version,
                "table_counts": table_counts,
                "checked_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get database info: {e}")
            return {"error": str(e)}


# Global ORM service instance
_orm_service = None


def get_orm_service() -> ORMService:
    """Get the global ORM service instance."""
    global _orm_service
    if _orm_service is None:
        _orm_service = ORMService()
    return _orm_service


# Convenience functions for common operations
async def create_record(model_class: Type[T], **kwargs) -> T:
    """Create a new record."""
    service = get_orm_service()
    return await service.create(model_class, **kwargs)


async def get_record_by_id(model_class: Type[T], record_id: Any) -> Optional[T]:
    """Get record by ID."""
    service = get_orm_service()
    return await service.get_by_id(model_class, record_id)


async def get_record_by_field(model_class: Type[T], field_name: str, field_value: Any) -> Optional[T]:
    """Get record by field value."""
    service = get_orm_service()
    return await service.get_by_field(model_class, field_name, field_value)


async def get_all_records(
    model_class: Type[T], 
    filters: Optional[Dict[str, Any]] = None,
    order_by: Optional[List[str]] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None
) -> List[T]:
    """Get all records with optional filtering."""
    service = get_orm_service()
    return await service.get_all(model_class, filters, order_by, limit, offset)


async def update_record(model_class: Type[T], record_id: Any, **kwargs) -> Optional[T]:
    """Update record by ID."""
    service = get_orm_service()
    return await service.update(model_class, record_id, **kwargs)


async def delete_record(model_class: Type[T], record_id: Any) -> bool:
    """Delete record by ID."""
    service = get_orm_service()
    return await service.delete(model_class, record_id)


async def search_records(
    model_class: Type[T], 
    search_term: str, 
    search_fields: List[str],
    limit: Optional[int] = None,
    offset: Optional[int] = None
) -> List[T]:
    """Search records across multiple fields."""
    service = get_orm_service()
    return await service.search(model_class, search_term, search_fields, limit, offset)


async def count_records(model_class: Type[T], filters: Optional[Dict[str, Any]] = None) -> int:
    """Count records with optional filters."""
    service = get_orm_service()
    return await service.count(model_class, filters)
