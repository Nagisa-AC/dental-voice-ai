"""
Custom exceptions for Dental Voice AI system.

Provides specific exception types for better error handling and debugging.
"""

from typing import Optional, Dict, Any


class DentalVoiceAIError(Exception):
    """Base exception for Dental Voice AI system."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class VAPIServiceError(DentalVoiceAIError):
    """Exception raised for VAPI service related errors."""
    pass


class DataServiceError(DentalVoiceAIError):
    """Exception raised for data service related errors."""
    pass


class ConfigurationError(DentalVoiceAIError):
    """Exception raised for configuration related errors."""
    pass


class ValidationError(DentalVoiceAIError):
    """Exception raised for data validation errors."""
    pass


class AuthenticationError(DentalVoiceAIError):
    """Exception raised for authentication related errors."""
    pass


class RateLimitError(DentalVoiceAIError):
    """Exception raised for rate limiting errors."""
    pass


class NetworkError(DentalVoiceAIError):
    """Exception raised for network related errors."""
    pass
