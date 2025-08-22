"""
Production Database Operations for Dental Voice AI

Handles Supabase client creation, error handling, and database operations
with comprehensive logging and error recovery for production environments.
"""

from supabase import create_client, Client
from dental_voice_ai.core.config import settings
import logging
from typing import Dict, Any, Optional, List
from fastapi import HTTPException

logger = logging.getLogger(__name__)


def create_supabase_client() -> Client:
    """
    Create and configure Supabase client with production error handling.
    
    Returns:
        Configured Supabase client
        
    Raises:
        RuntimeError: If client creation fails
    """
    try:
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            raise ValueError(
                "Missing Supabase configuration. Please check SUPABASE_URL and "
                "SUPABASE_KEY environment variables."
            )
        
        client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        logger.info("✅ Supabase client initialized successfully")
        return client
        
    except Exception as e:
        logger.error(f"❌ Failed to create Supabase client: {e}")
        raise RuntimeError(f"Database connection failed: {str(e)}")


def handle_supabase_error(
    error: Exception, 
    operation: str, 
    request_id: Optional[str] = None
) -> HTTPException:
    """
    Handle Supabase errors with structured logging and appropriate HTTP responses.
    
    Args:
        error: The exception that occurred
        operation: Description of the operation that failed
        request_id: Optional request identifier for tracking
    
    Returns:
        HTTPException with appropriate status code and message
    """
    request_prefix = f"[{request_id}] " if request_id else ""
    error_str = str(error).lower()
    
    logger.error(f"🔴 {request_prefix}Supabase {operation} failed: {error}")
    
    # Categorize errors and return appropriate HTTP responses
    if "connection" in error_str or "network" in error_str:
        return HTTPException(
            status_code=503, 
            detail="Database temporarily unavailable - please try again later"
        )
    
    elif "timeout" in error_str:
        return HTTPException(
            status_code=504, 
            detail="Database operation timed out - please try again"
        )
    
    elif "constraint" in error_str or "unique" in error_str:
        return HTTPException(
            status_code=409, 
            detail="Data validation error - duplicate or invalid data"
        )
    
    elif "permission" in error_str or "unauthorized" in error_str:
        return HTTPException(
            status_code=403, 
            detail="Database permission error"
        )
    
    elif "not found" in error_str or "does not exist" in error_str:
        return HTTPException(
            status_code=404, 
            detail="Database resource not found"
        )
    
    else:
        return HTTPException(
            status_code=500, 
            detail="Database operation failed"
        )


def safe_supabase_insert(
    table_name: str, 
    data: Dict[str, Any], 
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Safely insert data into Supabase with comprehensive error handling.
    
    Args:
        table_name: Name of the table to insert into
        data: Data to insert
        request_id: Optional request identifier for tracking
    
    Returns:
        The inserted record data
        
    Raises:
        HTTPException: If the operation fails
    """
    if supabase is None:
        request_prefix = f"[{request_id}] " if request_id else ""
        logger.error(f"🔴 {request_prefix}Supabase client not initialized")
        raise HTTPException(status_code=500, detail="Database not available")
    
    try:
        request_prefix = f"[{request_id}] " if request_id else ""
        logger.info(f"💾 {request_prefix}Inserting into {table_name}")
        
        response = supabase.table(table_name).insert(data).execute()
        
        if not response.data:
            logger.error(f"🔴 {request_prefix}Insert into {table_name} returned empty data")
            raise HTTPException(status_code=500, detail="Database insert failed")
        
        inserted_record = response.data[0]
        record_id = inserted_record.get('id', 'unknown')
        logger.info(f"✅ {request_prefix}Successfully inserted into {table_name} - ID: {record_id}")
        
        return inserted_record
        
    except HTTPException:
        raise
    except Exception as e:
        raise handle_supabase_error(e, f"insert into {table_name}", request_id)


def safe_supabase_select(
    table_name: str,
    columns: str = "*",
    filters: Optional[Dict[str, Any]] = None,
    limit: Optional[int] = None,
    request_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Safely select data from Supabase with error handling.
    
    Args:
        table_name: Name of the table to select from
        columns: Columns to select (default: "*")
        filters: Optional filters to apply
        limit: Optional limit on results
        request_id: Optional request identifier for tracking
    
    Returns:
        List of selected records
        
    Raises:
        HTTPException: If the operation fails
    """
    if supabase is None:
        request_prefix = f"[{request_id}] " if request_id else ""
        logger.error(f"🔴 {request_prefix}Supabase client not initialized")
        raise HTTPException(status_code=500, detail="Database not available")
    
    try:
        request_prefix = f"[{request_id}] " if request_id else ""
        logger.debug(f"🔍 {request_prefix}Selecting from {table_name}")
        
        query = supabase.table(table_name).select(columns)
        
        # Apply filters if provided
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        
        # Apply limit if provided
        if limit:
            query = query.limit(limit)
        
        response = query.execute()
        
        logger.debug(f"✅ {request_prefix}Selected {len(response.data)} records from {table_name}")
        return response.data
        
    except Exception as e:
        raise handle_supabase_error(e, f"select from {table_name}", request_id)


# Initialize the Supabase client
try:
    supabase = create_supabase_client()
except Exception as e:
    logger.error(f"❌ Failed to initialize Supabase client: {e}")
    supabase = None