"""
Input Validation Decorators

Decorators for validating and sanitizing input data in API endpoints.
"""

import logging
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type, Union
from fastapi import HTTPException, status

from .services.sanitization_service import SanitizationService
from .utils.query_sanitizer import query_sanitizer

logger = logging.getLogger(__name__)


def validate_input(
    required_fields: Optional[List[str]] = None,
    max_length: Optional[int] = None,
    field_types: Optional[Dict[str, str]] = None
):
    """
    Decorator to validate and sanitize input data.
    
    Args:
        required_fields: List of required field names
        max_length: Maximum length for text fields
        field_types: Dictionary mapping field names to expected types
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            sanitizer = SanitizationService()
            
            # Extract request data from kwargs
            request_data = {}
            for key, value in kwargs.items():
                if key not in ['request', 'current_user', 'db', 'auth_service']:
                    request_data[key] = value
            
            # Validate required fields
            if required_fields:
                for field in required_fields:
                    if field not in request_data or request_data[field] is None:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Required field '{field}' is missing"
                        )
            
            # Sanitize and validate data
            sanitized_data = {}
            for key, value in request_data.items():
                if value is None:
                    sanitized_data[key] = None
                    continue
                
                # Get expected field type
                expected_type = field_types.get(key, 'text') if field_types else 'text'
                
                try:
                    # Sanitize based on field type
                    if expected_type == 'email':
                        sanitized_value = sanitizer.sanitize_email(str(value))
                    elif expected_type == 'phone':
                        sanitized_value = sanitizer.sanitize_phone(str(value))
                    elif expected_type == 'url':
                        sanitized_value = sanitizer.sanitize_url(str(value))
                    elif expected_type == 'uuid':
                        sanitized_value = sanitizer.sanitize_uuid(str(value))
                    elif expected_type == 'int':
                        try:
                            sanitized_value = int(value)
                        except (ValueError, TypeError):
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Field '{key}' must be an integer"
                            )
                    elif expected_type == 'float':
                        try:
                            sanitized_value = float(value)
                        except (ValueError, TypeError):
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Field '{key}' must be a number"
                            )
                    elif expected_type == 'boolean':
                        if isinstance(value, bool):
                            sanitized_value = value
                        else:
                            sanitized_value = str(value).lower() in ('true', '1', 'yes', 'on')
                    else:  # text, string, etc.
                        sanitized_value = sanitizer.sanitize_text(str(value), max_length)
                    
                    # Check for security threats
                    if isinstance(sanitized_value, str):
                        if sanitizer.detect_sql_injection(sanitized_value):
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Invalid input detected in field '{key}'"
                            )
                        if sanitizer.detect_xss(sanitized_value):
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Invalid input detected in field '{key}'"
                            )
                    
                    sanitized_data[key] = sanitized_value
                    
                except HTTPException:
                    raise
                except Exception as e:
                    logger.error(f"Input validation error for field '{key}': {e}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid input for field '{key}'"
                    )
            
            # Update kwargs with sanitized data
            for key, value in sanitized_data.items():
                kwargs[key] = value
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def validate_query_params(
    allowed_params: Optional[List[str]] = None,
    required_params: Optional[List[str]] = None
):
    """
    Decorator to validate and sanitize query parameters.
    
    Args:
        allowed_params: List of allowed parameter names
        required_params: List of required parameter names
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract query parameters from kwargs
            query_params = {}
            for key, value in kwargs.items():
                if key not in ['request', 'current_user', 'db', 'auth_service']:
                    query_params[key] = value
            
            # Check required parameters
            if required_params:
                for param in required_params:
                    if param not in query_params or query_params[param] is None:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Required query parameter '{param}' is missing"
                        )
            
            # Check allowed parameters
            if allowed_params:
                for param in query_params:
                    if param not in allowed_params:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Unknown query parameter '{param}'"
                        )
            
            # Sanitize query parameters
            sanitized_params = query_sanitizer.sanitize_query_params(query_params)
            
            # Update kwargs with sanitized parameters
            for key, value in sanitized_params.items():
                kwargs[key] = value
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def validate_search_query():
    """
    Decorator to validate and sanitize search queries.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract search query from kwargs
            search_query = kwargs.get('search_query') or kwargs.get('q') or kwargs.get('search')
            
            if search_query:
                # Sanitize search query
                sanitized_query = query_sanitizer.sanitize_search_term(str(search_query))
                
                # Update kwargs with sanitized query
                if 'search_query' in kwargs:
                    kwargs['search_query'] = sanitized_query
                elif 'q' in kwargs:
                    kwargs['q'] = sanitized_query
                elif 'search' in kwargs:
                    kwargs['search'] = sanitized_query
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def validate_pagination():
    """
    Decorator to validate and sanitize pagination parameters.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract pagination parameters
            limit = kwargs.get('limit')
            offset = kwargs.get('offset')
            
            # Sanitize pagination parameters
            sanitized_limit, sanitized_offset = query_sanitizer.sanitize_limit_offset(limit, offset)
            
            # Update kwargs with sanitized parameters
            kwargs['limit'] = sanitized_limit
            kwargs['offset'] = sanitized_offset
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def validate_file_upload(
    allowed_extensions: Optional[List[str]] = None,
    max_size: Optional[int] = None
):
    """
    Decorator to validate file uploads.
    
    Args:
        allowed_extensions: List of allowed file extensions
        max_size: Maximum file size in bytes
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract file from kwargs
            file = kwargs.get('file')
            
            if file:
                # Validate file extension
                if allowed_extensions:
                    file_extension = file.filename.split('.')[-1].lower() if file.filename else ''
                    if file_extension not in allowed_extensions:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"File extension '.{file_extension}' not allowed"
                        )
                
                # Validate file size
                if max_size:
                    file_content = await file.read()
                    if len(file_content) > max_size:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"File size exceeds maximum allowed size of {max_size} bytes"
                        )
                    # Reset file pointer
                    await file.seek(0)
                
                # Sanitize filename
                if file.filename:
                    sanitized_filename = query_sanitizer.sanitizer.sanitize_filename(file.filename)
                    if not sanitized_filename:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid filename"
                        )
                    file.filename = sanitized_filename
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator
