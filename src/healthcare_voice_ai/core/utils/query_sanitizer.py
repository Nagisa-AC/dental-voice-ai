"""
Database Query Sanitization Utilities

Utilities for sanitizing database queries and preventing SQL injection.
"""

import logging
from typing import Any, Dict, List, Optional, Union
from sqlalchemy import text, select, update, delete, insert
from sqlalchemy.orm import Query
from sqlalchemy.sql import Select, Update, Delete, Insert

from .services.sanitization_service import SanitizationService

logger = logging.getLogger(__name__)


class QuerySanitizer:
    """Utility class for sanitizing database queries."""
    
    def __init__(self):
        """Initialize query sanitizer."""
        self.sanitizer = SanitizationService()
    
    def sanitize_query_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize query parameters for database operations.
        
        Args:
            params: Dictionary of query parameters
            
        Returns:
            Sanitized parameters dictionary
        """
        sanitized_params = {}
        
        for key, value in params.items():
            # Sanitize the key
            sanitized_key = self.sanitizer.sanitize_text(key)
            
            # Sanitize the value based on its type
            if isinstance(value, str):
                sanitized_value = self.sanitizer.sanitize_text(value)
            elif isinstance(value, (int, float, bool)):
                sanitized_value = value  # Numeric and boolean values are safe
            elif isinstance(value, list):
                sanitized_value = self._sanitize_list(value)
            elif isinstance(value, dict):
                sanitized_value = self._sanitize_dict(value)
            else:
                sanitized_value = value
            
            sanitized_params[sanitized_key] = sanitized_value
        
        return sanitized_params
    
    def sanitize_where_clause(self, where_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize WHERE clause conditions.
        
        Args:
            where_conditions: Dictionary of WHERE conditions
            
        Returns:
            Sanitized WHERE conditions
        """
        sanitized_conditions = {}
        
        for column, value in where_conditions.items():
            # Sanitize column name (should be alphanumeric + underscore)
            sanitized_column = self._sanitize_column_name(column)
            
            # Sanitize value
            if isinstance(value, str):
                sanitized_value = self.sanitizer.sanitize_text(value)
            elif isinstance(value, (int, float, bool)):
                sanitized_value = value
            elif isinstance(value, list):
                sanitized_value = self._sanitize_list(value)
            else:
                sanitized_value = value
            
            sanitized_conditions[sanitized_column] = sanitized_value
        
        return sanitized_conditions
    
    def sanitize_order_by(self, order_by: Union[str, List[str]]) -> List[str]:
        """
        Sanitize ORDER BY clause.
        
        Args:
            order_by: Column name(s) for ordering
            
        Returns:
            List of sanitized column names
        """
        if isinstance(order_by, str):
            order_by = [order_by]
        
        sanitized_columns = []
        for column in order_by:
            sanitized_column = self._sanitize_column_name(column)
            if sanitized_column:
                sanitized_columns.append(sanitized_column)
        
        return sanitized_columns
    
    def sanitize_limit_offset(self, limit: Optional[int] = None, offset: Optional[int] = None) -> tuple:
        """
        Sanitize LIMIT and OFFSET values.
        
        Args:
            limit: Maximum number of rows
            offset: Number of rows to skip
            
        Returns:
            Tuple of (sanitized_limit, sanitized_offset)
        """
        # Ensure limit is positive integer
        if limit is not None:
            try:
                limit = int(limit)
                if limit < 0:
                    limit = None
                elif limit > 10000:  # Reasonable upper limit
                    limit = 10000
            except (ValueError, TypeError):
                limit = None
        
        # Ensure offset is non-negative integer
        if offset is not None:
            try:
                offset = int(offset)
                if offset < 0:
                    offset = 0
            except (ValueError, TypeError):
                offset = 0
        
        return limit, offset
    
    def sanitize_search_term(self, search_term: str) -> str:
        """
        Sanitize search term for LIKE queries.
        
        Args:
            search_term: Search term to sanitize
            
        Returns:
            Sanitized search term
        """
        if not search_term:
            return ""
        
        # Basic text sanitization
        sanitized = self.sanitizer.sanitize_text(search_term)
        
        # Escape SQL LIKE wildcards
        sanitized = sanitized.replace('%', '\\%').replace('_', '\\_')
        
        return sanitized
    
    def _sanitize_column_name(self, column_name: str) -> Optional[str]:
        """
        Sanitize database column name.
        
        Args:
            column_name: Column name to sanitize
            
        Returns:
            Sanitized column name or None if invalid
        """
        if not column_name:
            return None
        
        # Remove dangerous characters, keep only alphanumeric and underscore
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '', str(column_name))
        
        # Ensure it starts with letter or underscore
        if not re.match(r'^[a-zA-Z_]', sanitized):
            logger.warning(f"Invalid column name: {column_name}")
            return None
        
        return sanitized
    
    def _sanitize_list(self, data: list) -> list:
        """
        Sanitize list data.
        
        Args:
            data: List to sanitize
            
        Returns:
            Sanitized list
        """
        sanitized = []
        
        for item in data:
            if isinstance(item, str):
                sanitized_item = self.sanitizer.sanitize_text(item)
            elif isinstance(item, (int, float, bool)):
                sanitized_item = item
            elif isinstance(item, dict):
                sanitized_item = self._sanitize_dict(item)
            elif isinstance(item, list):
                sanitized_item = self._sanitize_list(item)
            else:
                sanitized_item = item
            
            sanitized.append(sanitized_item)
        
        return sanitized
    
    def _sanitize_dict(self, data: dict) -> dict:
        """
        Sanitize dictionary data.
        
        Args:
            data: Dictionary to sanitize
            
        Returns:
            Sanitized dictionary
        """
        sanitized = {}
        
        for key, value in data.items():
            sanitized_key = self.sanitizer.sanitize_text(key)
            
            if isinstance(value, str):
                sanitized_value = self.sanitizer.sanitize_text(value)
            elif isinstance(value, (int, float, bool)):
                sanitized_value = value
            elif isinstance(value, dict):
                sanitized_value = self._sanitize_dict(value)
            elif isinstance(value, list):
                sanitized_value = self._sanitize_list(value)
            else:
                sanitized_value = value
            
            sanitized[sanitized_key] = sanitized_value
        
        return sanitized


# Global instance for easy access
query_sanitizer = QuerySanitizer()


def sanitize_query_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to sanitize query parameters."""
    return query_sanitizer.sanitize_query_params(params)


def sanitize_where_clause(where_conditions: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to sanitize WHERE clause conditions."""
    return query_sanitizer.sanitize_where_clause(where_conditions)


def sanitize_order_by(order_by: Union[str, List[str]]) -> List[str]:
    """Convenience function to sanitize ORDER BY clause."""
    return query_sanitizer.sanitize_order_by(order_by)


def sanitize_limit_offset(limit: Optional[int] = None, offset: Optional[int] = None) -> tuple:
    """Convenience function to sanitize LIMIT and OFFSET values."""
    return query_sanitizer.sanitize_limit_offset(limit, offset)


def sanitize_search_term(search_term: str) -> str:
    """Convenience function to sanitize search terms."""
    return query_sanitizer.sanitize_search_term(search_term)

