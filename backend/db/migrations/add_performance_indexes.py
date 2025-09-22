"""
Migration: Add Performance Indexes

Adds performance indexes to optimize common query patterns in healthcare applications.
This migration creates additional indexes for:
- Multi-tenant queries
- Audit trail searches
- File upload tracking
- Rate limiting
- User authentication
"""

import logging
from sqlalchemy import text
from core.database import db_manager
from core.database.performance_indexes import create_performance_indexes

logger = logging.getLogger(__name__)


async def upgrade():
    """Add performance indexes to the database."""
    try:
        logger.info("🚀 Starting performance indexes migration...")
        
        # Get database engine
        engine = db_manager._sync_engine
        if not engine:
            raise Exception("Database engine not available")
        
        # Create performance indexes
        create_performance_indexes(engine)
        
        logger.info("✅ Performance indexes migration completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Performance indexes migration failed: {e}")
        raise


async def downgrade():
    """Remove performance indexes from the database."""
    try:
        logger.info("🔄 Starting performance indexes rollback...")
        
        # Get database engine
        engine = db_manager._sync_engine
        if not engine:
            raise Exception("Database engine not available")
        
        # Drop performance indexes
        from core.database.performance_indexes import drop_performance_indexes
        drop_performance_indexes(engine)
        
        logger.info("✅ Performance indexes rollback completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Performance indexes rollback failed: {e}")
        raise


# Migration metadata
MIGRATION_INFO = {
    "version": "2024.01.001",
    "description": "Add performance indexes for database optimization",
    "upgrade": upgrade,
    "downgrade": downgrade,
    "dependencies": [],
    "tags": ["performance", "indexes", "optimization"]
}

