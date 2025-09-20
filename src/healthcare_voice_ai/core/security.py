"""
Simplified Security Module for Healthcare Voice AI

Provides essential security features for healthcare practice applications:
- Data encryption/decryption
- Input validation and sanitization
- Basic security utilities
"""

import hashlib
import secrets
import re
from typing import Any, Dict, Optional
from cryptography.fernet import Fernet
import logging

logger = logging.getLogger(__name__)


class SecurityService:
    """Simplified security service for dental practice applications."""
    
    def __init__(self, encryption_key: Optional[str] = None):
        """Initialize security service."""
        if encryption_key:
            self.fernet = Fernet(encryption_key.encode())
        else:
            # Generate a key for development (in production, use proper key management)
            key = Fernet.generate_key()
            self.fernet = Fernet(key)
            logger.warning("Using generated encryption key - not suitable for production")
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data."""
        try:
            encrypted_data = self.fernet.encrypt(data.encode())
            return encrypted_data.decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        try:
            decrypted_data = self.fernet.decrypt(encrypted_data.encode())
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
    
    def hash_password(self, password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """Hash password with salt."""
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Use PBKDF2 for password hashing
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # iterations
        )
        
        return password_hash.hex(), salt
    
    def verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        """Verify password against stored hash."""
        try:
            password_hash, _ = self.hash_password(password, salt)
            return password_hash == stored_hash
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False
    
    def sanitize_input(self, input_data: str) -> str:
        """Sanitize user input to prevent injection attacks."""
        if not isinstance(input_data, str):
            return str(input_data)
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\';\\]', '', input_data)
        
        # Trim whitespace
        sanitized = sanitized.strip()
        
        return sanitized
    
    def validate_email(self, email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def validate_phone(self, phone: str) -> bool:
        """Validate phone number format (E.164)."""
        pattern = r'^\+[1-9]\d{1,14}$'
        return bool(re.match(pattern, phone))
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate a secure random token."""
        return secrets.token_urlsafe(length)
    
    def mask_sensitive_data(self, data: str, visible_chars: int = 4) -> str:
        """Mask sensitive data for logging."""
        if len(data) <= visible_chars:
            return "*" * len(data)
        
        return data[:visible_chars] + "*" * (len(data) - visible_chars)


# Global security service instance
security_service = SecurityService()


# Convenience functions
def encrypt_data(data: str) -> str:
    """Encrypt sensitive data."""
    return security_service.encrypt_data(data)


def decrypt_data(encrypted_data: str) -> str:
    """Decrypt sensitive data."""
    return security_service.decrypt_data(encrypted_data)


def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """Hash password with salt."""
    return security_service.hash_password(password, salt)


def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    """Verify password against stored hash."""
    return security_service.verify_password(password, stored_hash, salt)


def sanitize_input(input_data: str) -> str:
    """Sanitize user input."""
    return security_service.sanitize_input(input_data)


def validate_email(email: str) -> bool:
    """Validate email format."""
    return security_service.validate_email(email)


def validate_phone(phone: str) -> bool:
    """Validate phone number format."""
    return security_service.validate_phone(phone)


def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token."""
    return security_service.generate_secure_token(length)


def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """Mask sensitive data for logging."""
    return security_service.mask_sensitive_data(data, visible_chars)
