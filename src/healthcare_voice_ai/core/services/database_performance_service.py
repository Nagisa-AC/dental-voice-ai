
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
Database Performance Service for Healthcare Voice AI

Service for managing database performance, monitoring, and optimization.
Provides tools for connection pool monitoring, query analysis, and performance tuning.
"""

import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy import text, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool

from ..database import db_manager
from ..core.db_utils.performance_indexes import (
    create_performance_indexes, drop_performance_indexes, 
    get_query_optimization_hints, analyze_query_performance,
    vacuum_analyze_tables, get_table_statistics
)

logger = logging.getLogger(__name__)


class DatabasePerformanceService:
    """
    Service for database performance monitoring and optimization.
    
    Provides comprehensive database performance management including:
    - Connection pool monitoring
    - Query performance analysis
    - Index management
    - Database statistics
    - Performance optimization recommendations
    """
    
    def __init__(self):
        """Initialize database performance service."""
        self.logger = logging.getLogger(__name__)
    
    async def get_connection_pool_status(self) -> Dict[str, Any]:
        """
        Get current connection pool status and statistics.
        
        Returns:
            Dict containing connection pool information
        """
        try:
            pool_status = {}
            
            # Get sync engine pool status
            if db_manager._sync_engine:
                sync_pool = db_manager._sync_engine.pool
                if isinstance(sync_pool, QueuePool):
                    pool_status["sync_pool"] = {
                        "pool_size": sync_pool.size(),
                        "checked_in": sync_pool.checkedin(),
                        "checked_out": sync_pool.checkedout(),
                        "overflow": sync_pool.overflow(),
                        "invalid": sync_pool.invalid(),
                        "total_connections": sync_pool.size() + sync_pool.overflow(),
                        "available_connections": sync_pool.checkedin(),
                        "utilization_percent": round(
                            (sync_pool.checkedout() / (sync_pool.size() + sync_pool.overflow())) * 100, 2
                        ) if (sync_pool.size() + sync_pool.overflow()) > 0 else 0
                    }
            
            # Get async engine pool status
            if db_manager._async_engine:
                async_pool = db_manager._async_engine.pool
                if isinstance(async_pool, QueuePool):
                    pool_status["async_pool"] = {
                        "pool_size": async_pool.size(),
                        "checked_in": async_pool.checkedin(),
                        "checked_out": async_pool.checkedout(),
                        "overflow": async_pool.overflow(),
                        "invalid": async_pool.invalid(),
                        "total_connections": async_pool.size() + async_pool.overflow(),
                        "available_connections": async_pool.checkedin(),
                        "utilization_percent": round(
                            (async_pool.checkedout() / (async_pool.size() + async_pool.overflow())) * 100, 2
                        ) if (async_pool.size() + async_pool.overflow()) > 0 else 0
                    }
            
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "pools": pool_status
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get connection pool status: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_database_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive database statistics.
        
        Returns:
            Dict containing database statistics
        """
        try:
            engine = db_manager._sync_engine
            if not engine:
                raise DatabaseError("Database engine not available")
            
            # Get table statistics
            table_stats = get_table_statistics(engine)
            
            # Get database size
            with engine.connect() as conn:
                db_size_result = conn.execute(text("""
                    SELECT pg_size_pretty(pg_database_size(current_database())) as database_size
                """))
                database_size = db_size_result.scalar()
                
                # Get connection count
                conn_count_result = conn.execute(text("""
                    SELECT count(*) as connection_count 
                    FROM pg_stat_activity 
                    WHERE datname = current_database()
                """))
                connection_count = conn_count_result.scalar()
                
                # Get active queries
                active_queries_result = conn.execute(text("""
                    SELECT count(*) as active_queries 
                    FROM pg_stat_activity 
                    WHERE datname = current_database() 
                    AND state = 'active'
                """))
                active_queries = active_queries_result.scalar()
            
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "database_size": database_size,
                "connection_count": connection_count,
                "active_queries": active_queries,
                "table_statistics": table_stats
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get database statistics: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def analyze_query_performance(self, query: str) -> Dict[str, Any]:
        """
        Analyze query performance using EXPLAIN ANALYZE.
        
        Args:
            query: SQL query to analyze
            
        Returns:
            Dict containing query analysis results
        """
        try:
            engine = db_manager._sync_engine
            if not engine:
                raise DatabaseError("Database engine not available")
            
            # Analyze query performance
            explain_output = analyze_query_performance(engine, query)
            
            return {
                "status": "success",
                "query": query,
                "explain_output": explain_output,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze query performance: {e}")
            return {
                "status": "error",
                "error": str(e),
                "query": query,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def create_performance_indexes(self) -> Dict[str, Any]:
        """
        Create performance indexes for database optimization.
        
        Returns:
            Dict containing index creation results
        """
        try:
            engine = db_manager._sync_engine
            if not engine:
                raise DatabaseError("Database engine not available")
            
            # Create performance indexes
            create_performance_indexes(engine)
            
            return {
                "status": "success",
                "message": "Performance indexes created successfully",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create performance indexes: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def drop_performance_indexes(self) -> Dict[str, Any]:
        """
        Drop performance indexes from the database.
        
        Returns:
            Dict containing index drop results
        """
        try:
            engine = db_manager._sync_engine
            if not engine:
                raise DatabaseError("Database engine not available")
            
            # Drop performance indexes
            drop_performance_indexes(engine)
            
            return {
                "status": "success",
                "message": "Performance indexes dropped successfully",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to drop performance indexes: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def vacuum_analyze_database(self) -> Dict[str, Any]:
        """
        Run VACUUM ANALYZE on all tables to update statistics.
        
        Returns:
            Dict containing vacuum results
        """
        try:
            engine = db_manager._sync_engine
            if not engine:
                raise DatabaseError("Database engine not available")
            
            # Run VACUUM ANALYZE
            vacuum_analyze_tables(engine)
            
            return {
                "status": "success",
                "message": "VACUUM ANALYZE completed successfully",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to run VACUUM ANALYZE: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_performance_recommendations(self) -> Dict[str, Any]:
        """
        Get performance optimization recommendations.
        
        Returns:
            Dict containing performance recommendations
        """
        try:
            # Get current pool status
            pool_status = await self.get_connection_pool_status()
            
            # Get database statistics
            db_stats = await self.get_database_statistics()
            
            recommendations = []
            
            # Analyze connection pool utilization
            if "sync_pool" in pool_status.get("pools", {}):
                sync_pool = pool_status["pools"]["sync_pool"]
                if sync_pool.get("utilization_percent", 0) > 80:
                    recommendations.append({
                        "type": "connection_pool",
                        "severity": "warning",
                        "message": "Sync connection pool utilization is high (>80%)",
                        "suggestion": "Consider increasing DB_POOL_SIZE or DB_MAX_OVERFLOW"
                    })
            
            if "async_pool" in pool_status.get("pools", {}):
                async_pool = pool_status["pools"]["async_pool"]
                if async_pool.get("utilization_percent", 0) > 80:
                    recommendations.append({
                        "type": "connection_pool",
                        "severity": "warning",
                        "message": "Async connection pool utilization is high (>80%)",
                        "suggestion": "Consider increasing DB_POOL_SIZE or DB_MAX_OVERFLOW"
                    })
            
            # Analyze table sizes
            if "table_statistics" in db_stats:
                for table_name, stats in db_stats["table_statistics"].items():
                    if "row_count" in stats and stats["row_count"] > 100000:
                        recommendations.append({
                            "type": "table_size",
                            "severity": "info",
                            "message": f"Table {table_name} has {stats['row_count']:,} rows",
                            "suggestion": "Consider partitioning or archiving old data"
                        })
            
            # Get query optimization hints
            optimization_hints = get_query_optimization_hints()
            
            return {
                "status": "success",
                "timestamp": datetime.utcnow().isoformat(),
                "recommendations": recommendations,
                "optimization_hints": optimization_hints,
                "pool_status": pool_status,
                "database_statistics": db_stats
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get performance recommendations: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def monitor_database_health(self) -> Dict[str, Any]:
        """
        Monitor overall database health and performance.
        
        Returns:
            Dict containing comprehensive database health information
        """
        try:
            start_time = time.time()
            
            # Get all performance metrics
            pool_status = await self.get_connection_pool_status()
            db_stats = await self.get_database_statistics()
            recommendations = await self.get_performance_recommendations()
            
            # Calculate response time
            response_time = round((time.time() - start_time) * 1000, 2)  # milliseconds
            
            # Determine overall health status
            health_status = "healthy"
            if pool_status.get("status") == "error" or db_stats.get("status") == "error":
                health_status = "unhealthy"
            elif recommendations.get("recommendations"):
                # Check if there are any high severity recommendations
                high_severity = any(
                    rec.get("severity") == "error" 
                    for rec in recommendations.get("recommendations", [])
                )
                if high_severity:
                    health_status = "degraded"
            
            return {
                "status": health_status,
                "timestamp": datetime.utcnow().isoformat(),
                "response_time_ms": response_time,
                "connection_pool": pool_status,
                "database_statistics": db_stats,
                "recommendations": recommendations,
                "health_checks": {
                    "connection_pool": pool_status.get("status") == "healthy",
                    "database_connectivity": db_stats.get("status") == "healthy",
                    "performance_acceptable": health_status in ["healthy", "degraded"]
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to monitor database health: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


# Global service instance
_performance_service = None


def get_database_performance_service() -> DatabasePerformanceService:
    """Get the global database performance service instance."""
    global _performance_service
    if _performance_service is None:
        _performance_service = DatabasePerformanceService()
    return _performance_service
