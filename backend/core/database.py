"""
Database configuration and connection management for Dental Voice AI.

Provides SQLAlchemy setup with proper connection pooling, session management,
and database initialization for the multi-tenant dental practice system.
"""

import logging
from typing import AsyncGenerator, Optional, Dict, Any
from contextlib import asynccontextmanager

from sqlalchemy import create_engine, MetaData, event, Index
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy.engine import Engine

from core.config import settings


class DatabaseError(Exception):
    """Database-related error."""
    pass

logger = logging.getLogger(__name__)


# Import the consolidated Base class from models
# Import new clean models - use as primary
from db.models.database_models import Base as NewBase


class DatabaseManager:
    """
    Database connection manager with proper connection pooling and session management.
    
    Handles both sync and async database operations with connection pooling,
    retry logic, and proper error handling.
    """
    
    def __init__(self):
        self._sync_engine: Optional[Engine] = None
        self._async_engine: Optional[Engine] = None
        self._async_session_factory: Optional[async_sessionmaker] = None
        self._sync_session_factory: Optional[sessionmaker] = None
        self._initialized = False
        
    def _get_database_url(self, async_driver: bool = False) -> str:
        """
        Get database URL based on configuration.
    
    Args:
            async_driver: Whether to use async driver (asyncpg for PostgreSQL)
    
    Returns:
            Database URL string
            
        Raises:
            DatabaseError: If database configuration is invalid
        """
        # Check if DATABASE_URL is set (for development with SQLite)
        if hasattr(settings, 'DATABASE_URL') and settings.DATABASE_URL:
            if settings.DATABASE_URL.startswith("sqlite"):
                if async_driver:
                    # Handle both sqlite:// and sqlite+aiosqlite:// formats
                    if "sqlite+aiosqlite://" in settings.DATABASE_URL:
                        return settings.DATABASE_URL
                    else:
                        return settings.DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")
                return settings.DATABASE_URL
        
        # Check if SUPABASE_URL is a PostgreSQL connection string
        if settings.SUPABASE_URL and settings.SUPABASE_URL.startswith("postgresql://"):
            if async_driver:
                # Replace postgresql:// with postgresql+asyncpg:// for async operations
                return settings.SUPABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
            return settings.SUPABASE_URL
        
        # For development, use SQLite if no valid database URL is configured
        sqlite_url = "sqlite:///./dental_voice_ai.db"
        if async_driver:
            return sqlite_url.replace("sqlite://", "sqlite+aiosqlite://")
        return sqlite_url
    
    def initialize(self) -> None:
        """
        Initialize database engines and session factories.
        
        Raises:
            DatabaseError: If database initialization fails
        """
        try:
            # Create sync engine with connection pooling
            sync_url = self._get_database_url(async_driver=False)
            self._sync_engine = create_engine(
                sync_url,
                poolclass=QueuePool,
                pool_size=settings.DB_POOL_SIZE,
                max_overflow=settings.DB_MAX_OVERFLOW,
                pool_timeout=settings.DB_POOL_TIMEOUT,
                pool_pre_ping=settings.DB_POOL_PRE_PING,  # Verify connections before use
                pool_recycle=settings.DB_POOL_RECYCLE,   # Recycle connections periodically
                echo=settings.DEBUG,  # Log SQL queries in debug mode
                connect_args={
                    "connect_timeout": settings.DB_CONNECT_TIMEOUT,
                    "application_name": "healthcare_voice_ai"
                }
            )
        
            # Create async engine with connection pooling
            async_url = self._get_database_url(async_driver=True)
            
            # Use appropriate pool class based on database type
            if async_url.startswith("sqlite"):
                # SQLite doesn't support connection pooling, use NullPool
                from sqlalchemy.pool import NullPool
                pool_class = NullPool
                pool_kwargs = {}
            else:
                # PostgreSQL supports connection pooling
                pool_class = QueuePool
                pool_kwargs = {
                    "pool_size": settings.DB_POOL_SIZE,
                    "max_overflow": settings.DB_MAX_OVERFLOW,
                    "pool_timeout": settings.DB_POOL_TIMEOUT,
                    "pool_pre_ping": settings.DB_POOL_PRE_PING,
                    "pool_recycle": settings.DB_POOL_RECYCLE,
                }
            
            # Set up connect_args based on database type
            if async_url.startswith("sqlite"):
                # SQLite-specific connect args
                connect_args = {
                    "check_same_thread": False,
                    "timeout": 30
                }
            else:
                # PostgreSQL-specific connect args
                connect_args = {
                    "command_timeout": settings.DB_COMMAND_TIMEOUT,
                    "server_settings": {
                        "application_name": "healthcare_voice_ai_async"
                    }
                }
            
            self._async_engine = create_async_engine(
                async_url,
                poolclass=pool_class,
                echo=settings.DEBUG,
                **pool_kwargs,
                connect_args=connect_args
            )
        
            # Create session factories
            self._sync_session_factory = sessionmaker(
                bind=self._sync_engine,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False
            )
            
            self._async_session_factory = async_sessionmaker(
                bind=self._async_engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False
            )
        
            # Add connection event listeners
            self._setup_connection_listeners()
            
            self._initialized = True
            logger.info("✅ Database engines and session factories initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize database: {e}")
            raise DatabaseError(f"Database initialization failed: {str(e)}")
    
    def _setup_connection_listeners(self) -> None:
        """Setup database connection event listeners for monitoring."""
        
        @event.listens_for(self._sync_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """Set connection-level settings for PostgreSQL."""
            if "postgresql" in str(self._sync_engine.url):
                with dbapi_connection.cursor() as cursor:
                    # Set timezone to UTC
                    cursor.execute("SET timezone TO 'UTC'")
                    # Set statement timeout
                    cursor.execute("SET statement_timeout = '30s'")
        
        @event.listens_for(self._sync_engine, "checkout")
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            """Log connection checkout for monitoring."""
            logger.debug("Database connection checked out")
        
        @event.listens_for(self._sync_engine, "checkin")
        def receive_checkin(dbapi_connection, connection_record):
            """Log connection checkin for monitoring."""
            logger.debug("Database connection checked in")
    
    @property
    def sync_engine(self) -> Engine:
        """Get sync database engine."""
        if not self._initialized:
            raise DatabaseError("Database not initialized. Call initialize() first.")
        return self._sync_engine
    
    @property
    def async_engine(self) -> Engine:
        """Get async database engine."""
        if not self._initialized:
            raise DatabaseError("Database not initialized. Call initialize() first.")
        return self._async_engine
    
    def get_sync_session(self):
        """Get sync database session."""
        if not self._sync_session_factory:
            raise DatabaseError("Sync session factory not initialized")
        return self._sync_session_factory()
    
    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get async database session with proper cleanup.
        
        Yields:
            AsyncSession: Database session for async operations
        """
        if not self._async_session_factory:
            raise DatabaseError("Async session factory not initialized")
        
        async with self._async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def create_tables(self) -> None:
        """
        Create all database tables.
        
        Raises:
            DatabaseError: If table creation fails
        """
        try:
            async with self._async_engine.begin() as conn:
                await conn.run_sync(NewBase.metadata.create_all)
            logger.info("✅ Database tables created successfully")
        except Exception as e:
            logger.error(f"❌ Failed to create database tables: {e}")
            raise DatabaseError(f"Table creation failed: {str(e)}")
    
    async def drop_tables(self) -> None:
        """
        Drop all database tables (use with caution!).
        
        Raises:
            DatabaseError: If table dropping fails
        """
        try:
            async with self._async_engine.begin() as conn:
                await conn.run_sync(NewBase.metadata.drop_all)
            logger.info("✅ Database tables dropped successfully")
        except Exception as e:
            logger.error(f"❌ Failed to drop database tables: {e}")
            raise DatabaseError(f"Table dropping failed: {str(e)}")
    
    async def health_check(self) -> bool:
        """
        Perform database health check using ORM.
    
    Returns:
            bool: True if database is healthy, False otherwise
        """
        try:
            from sqlalchemy import text
            async with self.get_async_session() as session:
                # Use SQLAlchemy text() for safe raw SQL when needed
                await session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"❌ Database health check failed: {e}")
            return False
    
    async def close(self) -> None:
        """Close all database connections."""
        try:
            if self._async_engine:
                await self._async_engine.dispose()
            if self._sync_engine:
                self._sync_engine.dispose()
            logger.info("✅ Database connections closed")
        except Exception as e:
            logger.error(f"❌ Error closing database connections: {e}")


# Global database manager instance
db_manager = DatabaseManager()


# Database operations will be handled by ORMService
# This class is kept for backward compatibility but delegates to ORMService

class DatabaseOperations:
    """
    Database operations for CRUD operations.
    
    Now uses the comprehensive ORMService for all operations.
    Provides backward compatibility while delegating to ORMService.
    """
    
    def __init__(self, db_session: AsyncSession):
        """Initialize database operations with ORM service."""
        self.db = db_session
        self.logger = logging.getLogger(__name__)
        # Import ORM service for enhanced operations
        from services.orm_service import ORMService
        self.orm_service = ORMService(db_session)
    
    # Office Submission Operations
    async def create_office_submission(self, **kwargs):
        """Create a new office submission using ORM service."""
        from db.models.database_models import Clinic
        
        # Ensure industry_type has a default value
        if 'industry_type' not in kwargs:
            kwargs['industry_type'] = 'dental'
        
        # Use ORM service for creation
        return await self.orm_service.create(Clinic, **kwargs)
    
    async def get_office_submission(self, submission_id: str):
        """Get office submission by ID using ORM service."""
        from db.models.database_models import Clinic
        
        # Use ORM service for retrieval
        return await self.orm_service.get_by_id(Clinic, submission_id)
    
    async def get_all_office_submissions(self, status: str = None, limit: int = None, offset: int = None):
        """Get all office submissions with optional filtering using ORM service."""
        from db.models.database_models import Clinic
        
        # Build filters
        filters = {}
        if status:
            filters['status'] = status
        
        # Use ORM service for retrieval
        return await self.orm_service.get_all(Clinic, filters=filters, limit=limit, offset=offset)
    
    async def update_office_submission(self, submission_id: str, **kwargs):
        """Update office submission using ORM service."""
        from db.models.database_models import Clinic
        
        # Use ORM service for update
        return await self.orm_service.update(Clinic, submission_id, **kwargs)
    
    # Office Operations
    async def create_office(self, **kwargs):
        """Create a new office using ORM service."""
        from db.models.database_models import Clinic
        
        # Ensure industry_type has a default value
        if 'industry_type' not in kwargs:
            kwargs['industry_type'] = 'dental'
        
        # Use ORM service for creation
        return await self.orm_service.create(Clinic, **kwargs)
    
    async def get_office_by_tenant_id(self, tenant_id: str):
        """Get office by tenant ID using ORM service."""
        from db.models.database_models import Clinic
        
        # Use ORM service for retrieval
        return await self.orm_service.get_by_field(Clinic, 'tenant_id', tenant_id)
    
    async def get_office_by_id(self, office_id: str):
        """Get office by ID using ORM service."""
        from db.models.database_models import Clinic
        
        # Use ORM service for retrieval
        return await self.orm_service.get_by_id(Clinic, office_id)
    
    async def get_all_offices(self, status: str = None, limit: int = None, offset: int = None):
        """Get all offices with optional filtering using ORM service."""
        from db.models.database_models import Clinic
        
        # Build filters
        filters = {}
        if status:
            filters['status'] = status
        
        # Use ORM service for retrieval
        return await self.orm_service.get_all(Clinic, filters=filters, limit=limit, offset=offset)
    
    async def update_office(self, office_id: str, **kwargs):
        """Update office using ORM service."""
        from db.models.database_models import Clinic
        
        # Use ORM service for update
        return await self.orm_service.update(Clinic, office_id, **kwargs)
    
    # Knowledge Base Operations (Note: Knowledge base is now part of Clinic model)
    async def create_knowledge_base(self, **kwargs):
        """Create a new knowledge base using ORM service."""
        # Knowledge base is now stored as part of the Clinic model
        # This method is kept for backward compatibility
        self.logger.warning("create_knowledge_base is deprecated. Use Clinic model directly.")
        return None
    
    async def get_knowledge_base_by_office_id(self, office_id: str):
        """Get knowledge base by office ID using ORM service."""
        # Knowledge base is now stored as part of the Clinic model
        # This method is kept for backward compatibility
        self.logger.warning("get_knowledge_base_by_office_id is deprecated. Use Clinic model directly.")
        return None


async def get_db_operations() -> DatabaseOperations:
    """Get database operations instance."""
    async for db in get_async_db():
        yield DatabaseOperations(db)


# Dependency injection for FastAPI
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for getting async database session.
    
    Yields:
        AsyncSession: Database session for async operations
    """
    async with db_manager.get_async_session() as session:
        yield session


def get_sync_db():
    """
    Get sync database session (for non-async operations).
    
    Returns:
        Session: Database session for sync operations
    """
    return db_manager.get_sync_session()


# Database initialization function
async def init_database() -> None:
    """
    Initialize database connection and create tables.
    
    This function should be called during application startup.
    """
    try:
        db_manager.initialize()
        await db_manager.create_tables()
        
        # Perform health check
        if await db_manager.health_check():
            logger.info("✅ Database initialized and healthy")
        else:
            raise DatabaseError("Database health check failed")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise


# Database cleanup function
async def close_database() -> None:
    """
    Close database connections.
    
    This function should be called during application shutdown.
    """
    await db_manager.close()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get a database session.
    
    This function provides a database session for dependency injection
    in FastAPI endpoints and other async functions.
    
    Yields:
        AsyncSession: Database session
    """
    async with db_manager.get_async_session() as session:
        yield session


# Duplicate DatabaseOperations class removed - using the one defined above


async def get_db_operations() -> DatabaseOperations:
    """Get database operations instance."""
    async for db in get_async_db():
        yield DatabaseOperations(db)


# Performance indexes for database optimization
PERFORMANCE_INDEXES = [
    # User authentication and authorization indexes
    Index('idx_users_email_role_active', 'users', 'email', 'role', 'is_active'),
    Index('idx_users_last_login', 'users', 'last_login'),
    Index('idx_users_created_active', 'users', 'created_at', 'is_active'),
    
    # Clinic management indexes
    Index('idx_clinics_name_industry', 'clinics', 'name', 'industry_type'),
    Index('idx_clinics_approved_status', 'clinics', 'approved_at', 'status'),
    Index('idx_clinics_vapi_assistant', 'clinics', 'vapi_assistant_id'),
    Index('idx_clinics_updated_status', 'clinics', 'updated_at', 'status'),
    
    # Assistant management indexes
    Index('idx_assistants_tenant_name', 'assistants', 'tenant_id', 'name'),
    Index('idx_assistants_model_voice', 'assistants', 'model_id', 'voice_id'),
    Index('idx_assistants_updated_status', 'assistants', 'updated_at', 'status'),
    
    # Audit log performance indexes
    Index('idx_audit_logs_user_created', 'audit_logs', 'user_id', 'created_at'),
    Index('idx_audit_logs_clinic_created', 'audit_logs', 'clinic_id', 'created_at'),
    Index('idx_audit_logs_action_created', 'audit_logs', 'action', 'created_at'),
    Index('idx_audit_logs_ip_created', 'audit_logs', 'ip_address', 'created_at'),
    Index('idx_audit_logs_request_id', 'audit_logs', 'request_id'),
]


async def create_performance_indexes() -> None:
    """Create performance indexes on the database."""
    try:
        async with db_manager.get_async_session() as session:
            for index in PERFORMANCE_INDEXES:
                try:
                    # Create index with IF NOT EXISTS to avoid errors on re-runs
                    index_name = index.name
                    table_name = index.table.name
                    columns = ', '.join([f'"{col.name}"' for col in index.columns])
                    
                    create_sql = f"""
                    CREATE INDEX IF NOT EXISTS "{index_name}" 
                    ON "{table_name}" ({columns})
                    """
                    
                    await session.execute(text(create_sql))
                    await session.commit()
                    logger.info(f"✅ Created performance index: {index_name}")
                    
                except Exception as e:
                    logger.warning(f"⚠️  Could not create index {index_name}: {e}")
                    # Continue with other indexes even if one fails
                    
    except Exception as e:
        logger.error(f"❌ Failed to create performance indexes: {e}")


async def get_table_statistics() -> Dict[str, Any]:
    """Get table statistics for performance monitoring."""
    tables = [
        "users", "refresh_tokens", "clinics", "assistants", 
        "audit_logs", "file_uploads", "csrf_tokens", "rate_limits"
    ]
    
    stats = {}
    
    try:
        async with db_manager.get_async_session() as session:
            for table in tables:
                try:
                    # Get row count
                    count_result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    row_count = count_result.scalar()
                    
                    # Get table size (PostgreSQL specific)
                    size_result = await session.execute(text(f"""
                        SELECT pg_size_pretty(pg_total_relation_size('{table}')) as size
                    """))
                    table_size = size_result.scalar()
                    
                    stats[table] = {
                        "row_count": row_count,
                        "table_size": table_size
                    }
                    
                except Exception as e:
                    stats[table] = {"error": str(e)}
                    
    except Exception as e:
        logger.error(f"❌ Failed to get table statistics: {e}")
        return {"error": str(e)}
    
    return stats
