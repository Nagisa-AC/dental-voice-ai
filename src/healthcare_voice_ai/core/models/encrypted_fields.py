"""
Encrypted Field Types for SQLAlchemy Models

Provides custom SQLAlchemy column types that automatically encrypt/decrypt data.
"""

import logging
from typing import Any, Optional, Type
from sqlalchemy import TypeDecorator, String, Text, JSON
from sqlalchemy.types import TypeDecorator, String, Text

from ..services.encryption_service import encryption_service

logger = logging.getLogger(__name__)


class EncryptedString(TypeDecorator):
    """
    Encrypted string field that automatically encrypts/decrypts data.
    
    Stores encrypted data as TEXT in the database but presents it as plain text
    to the application layer.
    """
    
    impl = Text
    cache_ok = True
    
    def __init__(self, length=None, **kwargs):
        # Remove SQLAlchemy column arguments that don't apply to TypeDecorator
        column_kwargs = {}
        for key, value in kwargs.items():
            if key in ['unique', 'index', 'nullable', 'default']:
                column_kwargs[key] = value
        super().__init__(**column_kwargs)
    
    def process_bind_param(self, value: Optional[str], dialect) -> Optional[str]:
        """Encrypt value before storing in database."""
        if value is None:
            return None
        
        try:
            return encryption_service.encrypt_field(value, self.name)
        except Exception as e:
            logger.error(f"Failed to encrypt field {self.name}: {e}")
            raise
    
    def process_result_value(self, value: Optional[str], dialect) -> Optional[str]:
        """Decrypt value when reading from database."""
        if value is None:
            return None
        
        try:
            return encryption_service.decrypt_field(value, self.name)
        except Exception as e:
            logger.error(f"Failed to decrypt field {self.name}: {e}")
            # Return encrypted value if decryption fails (for backward compatibility)
            return value


class EncryptedText(TypeDecorator):
    """
    Encrypted text field for longer content.
    
    Similar to EncryptedString but optimized for larger text content.
    """
    
    impl = Text
    cache_ok = True
    
    def process_bind_param(self, value: Optional[str], dialect) -> Optional[str]:
        """Encrypt value before storing in database."""
        if value is None:
            return None
        
        try:
            return encryption_service.encrypt_field(value, self.name)
        except Exception as e:
            logger.error(f"Failed to encrypt field {self.name}: {e}")
            raise
    
    def process_result_value(self, value: Optional[str], dialect) -> Optional[str]:
        """Decrypt value when reading from database."""
        if value is None:
            return None
        
        try:
            return encryption_service.decrypt_field(value, self.name)
        except Exception as e:
            logger.error(f"Failed to decrypt field {self.name}: {e}")
            # Return encrypted value if decryption fails (for backward compatibility)
            return value


class EncryptedJSON(TypeDecorator):
    """
    Encrypted JSON field that automatically encrypts/decrypts JSON data.
    
    Stores encrypted JSON as TEXT in the database but presents it as dict/list
    to the application layer.
    """
    
    impl = Text
    cache_ok = True
    
    def process_bind_param(self, value: Optional[dict], dialect) -> Optional[str]:
        """Encrypt JSON value before storing in database."""
        if value is None:
            return None
        
        try:
            return encryption_service.encrypt_json_field(value, self.name)
        except Exception as e:
            logger.error(f"Failed to encrypt JSON field {self.name}: {e}")
            raise
    
    def process_result_value(self, value: Optional[str], dialect) -> Optional[dict]:
        """Decrypt JSON value when reading from database."""
        if value is None:
            return None
        
        try:
            return encryption_service.decrypt_json_field(value, self.name)
        except Exception as e:
            logger.error(f"Failed to decrypt JSON field {self.name}: {e}")
            # Return encrypted value if decryption fails (for backward compatibility)
            return value


class EncryptedEmail(EncryptedString):
    """
    Specialized encrypted field for email addresses.
    
    Provides additional validation and formatting for email data.
    """
    
    def process_bind_param(self, value: Optional[str], dialect) -> Optional[str]:
        """Encrypt email before storing in database."""
        if value is None:
            return None
        
        # Basic email validation
        if '@' not in value or '.' not in value.split('@')[-1]:
            logger.warning(f"Invalid email format for field {self.name}: {value}")
        
        return super().process_bind_param(value, dialect)


class EncryptedPhone(EncryptedString):
    """
    Specialized encrypted field for phone numbers.
    
    Provides additional validation and formatting for phone data.
    """
    
    def process_bind_param(self, value: Optional[str], dialect) -> Optional[str]:
        """Encrypt phone number before storing in database."""
        if value is None:
            return None
        
        # Basic phone validation (digits, spaces, dashes, parentheses, plus)
        import re
        if not re.match(r'^[\d\s\-\(\)\+]+$', value):
            logger.warning(f"Invalid phone format for field {self.name}: {value}")
        
        return super().process_bind_param(value, dialect)


class EncryptedAddress(EncryptedText):
    """
    Specialized encrypted field for addresses.
    
    Optimized for longer address text content.
    """
    
    def process_bind_param(self, value: Optional[str], dialect) -> Optional[str]:
        """Encrypt address before storing in database."""
        if value is None:
            return None
        
        # Basic address validation (not empty, reasonable length)
        if len(value.strip()) < 5:
            logger.warning(f"Address too short for field {self.name}: {value}")
        
        return super().process_bind_param(value, dialect)


class EncryptedPasswordHash(EncryptedString):
    """
    Specialized encrypted field for password hashes.
    
    Provides additional security for password hash storage.
    """
    
    def process_bind_param(self, value: Optional[str], dialect) -> Optional[str]:
        """Encrypt password hash before storing in database."""
        if value is None:
            return None
        
        # Validate password hash format (bcrypt hashes start with $2b$)
        if not value.startswith('$2b$') and not value.startswith('$2a$'):
            logger.warning(f"Invalid password hash format for field {self.name}")
        
        return super().process_bind_param(value, dialect)


class EncryptedPHI(EncryptedText):
    """
    Specialized encrypted field for Protected Health Information (PHI).
    
    Provides additional security and audit logging for PHI data.
    """
    
    def process_bind_param(self, value: Optional[str], dialect) -> Optional[str]:
        """Encrypt PHI before storing in database."""
        if value is None:
            return None
        
        # Log PHI access for audit purposes
        logger.info(f"Encrypting PHI data for field {self.name}")
        
        return super().process_bind_param(value, dialect)
    
    def process_result_value(self, value: Optional[str], dialect) -> Optional[str]:
        """Decrypt PHI when reading from database."""
        if value is None:
            return None
        
        # Log PHI access for audit purposes
        logger.info(f"Decrypting PHI data for field {self.name}")
        
        return super().process_result_value(value, dialect)


# Convenience functions for creating encrypted fields
def encrypted_string(length: int = None, **kwargs) -> EncryptedString:
    """Create an encrypted string field."""
    return EncryptedString(length=length, **kwargs)


def encrypted_text(**kwargs) -> EncryptedText:
    """Create an encrypted text field."""
    return EncryptedText(**kwargs)


def encrypted_json(**kwargs) -> EncryptedJSON:
    """Create an encrypted JSON field."""
    return EncryptedJSON(**kwargs)


def encrypted_email(**kwargs) -> EncryptedEmail:
    """Create an encrypted email field."""
    return EncryptedEmail(**kwargs)


def encrypted_phone(**kwargs) -> EncryptedPhone:
    """Create an encrypted phone field."""
    return EncryptedPhone(**kwargs)


def encrypted_address(**kwargs) -> EncryptedAddress:
    """Create an encrypted address field."""
    return EncryptedAddress(**kwargs)


def encrypted_password_hash(**kwargs) -> EncryptedPasswordHash:
    """Create an encrypted password hash field."""
    return EncryptedPasswordHash(**kwargs)


def encrypted_phi(**kwargs) -> EncryptedPHI:
    """Create an encrypted PHI field."""
    return EncryptedPHI(**kwargs)
