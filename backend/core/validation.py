"""
Simplified Input Validation for Healthcare Voice AI

Basic validation utilities without over-engineering.
"""

import re
import html
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


def sanitize_input(data: Any) -> Any:
    """
    Sanitize input data to prevent XSS and injection attacks.
    
    Args:
        data: Input data to sanitize
        
    Returns:
        Sanitized data
    """
    if isinstance(data, str):
        # HTML escape and strip
        return html.escape(data.strip())
    elif isinstance(data, dict):
        return {key: sanitize_input(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    else:
        return data


def validate_phone_number(phone: str) -> str:
    """
    Validate and format phone number.
    
    Args:
        phone: Phone number to validate
        
    Returns:
        Formatted phone number
        
    Raises:
        ValueError: If phone number is invalid
    """
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Check if it's a valid length (10-15 digits)
    if len(digits) < 10 or len(digits) > 15:
        raise ValueError("Phone number must be 10-15 digits")
    
    # Format as E.164 (add +1 for US numbers if needed)
    if len(digits) == 10:
        return f"+1{digits}"
    elif len(digits) == 11 and digits.startswith('1'):
        return f"+{digits}"
    else:
        return f"+{digits}"


def validate_email(email: str) -> str:
    """
    Validate email address.
    
    Args:
        email: Email to validate
        
    Returns:
        Validated email
        
    Raises:
        ValueError: If email is invalid
    """
    email = email.strip().lower()
    
    # Basic email regex
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        raise ValueError("Invalid email format")
    
    return email


def validate_office_name(name: str) -> str:
    """
    Validate office name.
    
    Args:
        name: Office name to validate
        
    Returns:
        Validated office name
        
    Raises:
        ValueError: If name is invalid
    """
    name = name.strip()
    
    if not name or len(name) < 2:
        raise ValueError("Office name must be at least 2 characters")
    
    if len(name) > 100:
        raise ValueError("Office name must be less than 100 characters")
    
    # Remove HTML tags and check for suspicious characters
    cleaned = re.sub(r'<[^>]+>', '', name)
    if re.search(r'[<>"\']', cleaned):
        raise ValueError("Office name contains invalid characters")
    
    return cleaned


# Simple validation models for common use cases
class BasicValidation:
    """Basic validation utilities."""
    
    @staticmethod
    def validate_required(value: Any, field_name: str) -> Any:
        """Validate that a required field is not empty."""
        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValueError(f"{field_name} is required")
        return value
    
    @staticmethod
    def validate_length(value: str, field_name: str, min_length: int = 1, max_length: int = 255) -> str:
        """Validate string length."""
        if len(value) < min_length:
            raise ValueError(f"{field_name} must be at least {min_length} characters")
        if len(value) > max_length:
            raise ValueError(f"{field_name} must be less than {max_length} characters")
        return value
    
    @staticmethod
    def validate_choices(value: str, field_name: str, choices: List[str]) -> str:
        """Validate that value is in allowed choices."""
        if value not in choices:
            raise ValueError(f"{field_name} must be one of: {', '.join(choices)}")
        return value