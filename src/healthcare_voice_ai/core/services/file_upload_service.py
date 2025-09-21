
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
File Upload Security Service

Service for secure file upload validation and processing.
"""

import os
import re
import hashlib
import secrets
import logging
import mimetypes
from typing import Dict, Any, List, Optional, Tuple, Set
from pathlib import Path
from datetime import datetime
from fastapi import UploadFile, HTTPException, status
from fastapi.responses import JSONResponse

from ..config import settings
from enum import Enum


class FileType(str, Enum):
    """Supported file types for upload."""
    IMAGE = "image"
    DOCUMENT = "document"
    AUDIO = "audio"
    VIDEO = "video"
    OTHER = "other"


class FileUploadConfig:
    """Configuration for file uploads."""
    
    def __init__(self):
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.allowed_extensions = {
            '.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx',
            '.txt', '.mp3', '.wav', '.mp4', '.avi'
        }
        self.upload_dir = "uploads"
        self.quarantine_dir = "quarantine"
    
    def create_directories(self):
        """Create necessary directories."""
        Path(self.upload_dir).mkdir(exist_ok=True)
        Path(self.quarantine_dir).mkdir(exist_ok=True)
    
    @staticmethod
    def get_file_type_from_extension(extension: str) -> FileType:
        """Get file type from extension."""
        image_exts = {'.jpg', '.jpeg', '.png', '.gif'}
        doc_exts = {'.pdf', '.doc', '.docx', '.txt'}
        audio_exts = {'.mp3', '.wav'}
        video_exts = {'.mp4', '.avi'}
        
        if extension.lower() in image_exts:
            return FileType.IMAGE
        elif extension.lower() in doc_exts:
            return FileType.DOCUMENT
        elif extension.lower() in audio_exts:
            return FileType.AUDIO
        elif extension.lower() in video_exts:
            return FileType.VIDEO
        else:
            return FileType.OTHER

logger = logging.getLogger(__name__)


class FileUploadService:
    """Service for secure file upload validation and processing."""
    
    def __init__(self):
        """Initialize file upload service."""
        self.config = FileUploadConfig()
        self.config.create_directories()
        self.uploaded_files: Dict[str, Dict[str, Any]] = {}  # In production, use database
    
    def validate_file_size(self, file: UploadFile) -> bool:
        """
        Validate file size.
        
        Args:
            file: Uploaded file
            
        Returns:
            True if file size is valid, False otherwise
        """
        max_size = self.config.get_max_file_size_bytes()
        
        # Get file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        if file_size > max_size:
            logger.warning(f"File {file.filename} exceeds maximum size: {file_size} > {max_size}")
            return False
        
        return True
    
    def validate_file_extension(self, filename: str) -> Tuple[bool, Optional[FileType]]:
        """
        Validate file extension.
        
        Args:
            filename: File filename
            
        Returns:
            Tuple of (is_valid, file_type)
        """
        if not filename:
            return False, None
        
        # Get file extension
        extension = Path(filename).suffix.lower()
        
        # Check if extension is dangerous
        if extension in self.config.get_dangerous_extensions():
            logger.warning(f"Dangerous file extension detected: {extension}")
            return False, None
        
        # Check if extension is allowed
        allowed_extensions = self.config.get_all_allowed_extensions()
        if extension not in allowed_extensions:
            logger.warning(f"File extension not allowed: {extension}")
            return False, None
        
        # Get file type
        file_type = FileUploadConfig.get_file_type_from_extension(extension)
        
        return True, file_type
    
    def validate_mime_type(self, file: UploadFile, expected_file_type: FileType) -> bool:
        """
        Validate MIME type.
        
        Args:
            file: Uploaded file
            expected_file_type: Expected file type
            
        Returns:
            True if MIME type is valid, False otherwise
        """
        if not file.content_type:
            logger.warning(f"No content type provided for file {file.filename}")
            return False
        
        # Check if MIME type is dangerous
        if file.content_type in self.config.get_dangerous_mime_types():
            logger.warning(f"Dangerous MIME type detected: {file.content_type}")
            return False
        
        # Check if MIME type is allowed for file type
        allowed_mime_types = self.config.get_allowed_mime_types(expected_file_type)
        if file.content_type not in allowed_mime_types:
            logger.warning(f"MIME type not allowed for file type {expected_file_type}: {file.content_type}")
            return False
        
        return True
    
    def validate_file_content(self, file: UploadFile, file_type: FileType) -> bool:
        """
        Validate file content.
        
        Args:
            file: Uploaded file
            file_type: File type
            
        Returns:
            True if content is valid, False otherwise
        """
        if not self.config.should_validate_file_content():
            return True
        
        try:
            # Read file content
            content = file.file.read(1024)  # Read first 1KB
            file.file.seek(0)  # Reset to beginning
            
            if not content:
                return True
            
            # Check for suspicious patterns
            suspicious_patterns = self.config.get_suspicious_patterns()
            content_str = content.decode('utf-8', errors='ignore')
            
            for pattern in suspicious_patterns:
                if re.search(pattern, content_str, re.IGNORECASE):
                    logger.warning(f"Suspicious content pattern detected in file {file.filename}: {pattern}")
                    return False
            
            # File type specific validation
            if file_type == FileType.TEXT or file_type == FileType.MARKDOWN:
                return self._validate_text_content(content_str)
            elif file_type == FileType.IMAGE:
                return self._validate_image_content(content)
            elif file_type == FileType.DOCUMENT:
                return self._validate_document_content(content)
            elif file_type == FileType.ARCHIVE:
                return self._validate_archive_content(content)
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating file content for {file.filename}: {e}")
            return False
    
    def _validate_text_content(self, content: str) -> bool:
        """Validate text file content."""
        # Check for null bytes
        if '\x00' in content:
            logger.warning("Null bytes detected in text file")
            return False
        
        # Check for excessive binary content
        binary_ratio = sum(1 for c in content if ord(c) < 32 and c not in '\t\n\r') / len(content)
        if binary_ratio > 0.1:  # More than 10% binary content
            logger.warning("Excessive binary content in text file")
            return False
        
        return True
    
    def _validate_image_content(self, content: bytes) -> bool:
        """Validate image file content."""
        # Check for image file signatures
        image_signatures = {
            b'\xff\xd8\xff': 'JPEG',
            b'\x89PNG\r\n\x1a\n': 'PNG',
            b'GIF87a': 'GIF',
            b'GIF89a': 'GIF',
            b'BM': 'BMP'
        }
        
        for signature, format_name in image_signatures.items():
            if content.startswith(signature):
                return True
        
        logger.warning("Invalid image file signature")
        return False
    
    def _validate_document_content(self, content: bytes) -> bool:
        """Validate document file content."""
        # Check for document file signatures
        doc_signatures = {
            b'PK\x03\x04': 'ZIP-based (DOCX, PDF)',
            b'%PDF': 'PDF',
            b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1': 'DOC'
        }
        
        for signature, format_name in doc_signatures.items():
            if content.startswith(signature):
                return True
        
        logger.warning("Invalid document file signature")
        return False
    
    def _validate_archive_content(self, content: bytes) -> bool:
        """Validate archive file content."""
        # Check for archive file signatures
        archive_signatures = {
            b'PK\x03\x04': 'ZIP',
            b'PK\x05\x06': 'ZIP',
            b'PK\x07\x08': 'ZIP',
            b'ustar': 'TAR',
            b'\x1f\x8b': 'GZIP'
        }
        
        for signature, format_name in archive_signatures.items():
            if content.startswith(signature):
                return True
        
        logger.warning("Invalid archive file signature")
        return False
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        if not self.config.should_sanitize_filenames():
            return filename
        
        # Remove path components
        filename = Path(filename).name
        
        # Remove dangerous characters
        dangerous_chars = r'[<>:"/\\|?*\x00-\x1f]'
        filename = re.sub(dangerous_chars, '_', filename)
        
        # Remove leading/trailing dots and spaces
        filename = filename.strip('. ')
        
        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255-len(ext)] + ext
        
        return filename
    
    def generate_secure_filename(self, original_filename: str, user_id: Optional[str] = None) -> str:
        """
        Generate secure filename.
        
        Args:
            original_filename: Original filename
            user_id: Optional user ID
            
        Returns:
            Secure filename
        """
        if not self.config.should_generate_secure_filenames():
            return self.sanitize_filename(original_filename)
        
        # Get file extension
        extension = Path(original_filename).suffix.lower()
        
        # Generate secure name
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        random_part = secrets.token_hex(8)
        
        if user_id:
            secure_name = f"{user_id}_{timestamp}_{random_part}{extension}"
        else:
            secure_name = f"{timestamp}_{random_part}{extension}"
        
        return secure_name
    
    def calculate_file_hash(self, file: UploadFile) -> str:
        """
        Calculate file hash.
        
        Args:
            file: Uploaded file
            
        Returns:
            File hash
        """
        hasher = hashlib.sha256()
        
        # Read file in chunks
        chunk_size = 8192
        file.file.seek(0)
        
        while chunk := file.file.read(chunk_size):
            hasher.update(chunk)
        
        file.file.seek(0)  # Reset to beginning
        return hasher.hexdigest()
    
    def scan_for_malware(self, file: UploadFile) -> bool:
        """
        Scan file for malware.
        
        Args:
            file: Uploaded file
            
        Returns:
            True if file is clean, False if malware detected
        """
        if not self.config.should_scan_for_malware():
            return True
        
        # In a real implementation, you would integrate with a malware scanning service
        # For now, we'll do basic heuristic checks
        
        try:
            # Check file size (very large files might be suspicious)
            file.file.seek(0, 2)
            file_size = file.file.tell()
            file.file.seek(0)
            
            if file_size > 100 * 1024 * 1024:  # 100MB
                logger.warning(f"File {file.filename} is unusually large: {file_size} bytes")
                return False
            
            # Check for suspicious content patterns
            content = file.file.read(1024)
            file.file.seek(0)
            
            if content:
                content_str = content.decode('utf-8', errors='ignore')
                
                # Check for common malware signatures
                malware_signatures = [
                    "eval(",
                    "document.write",
                    "window.location",
                    "document.cookie",
                    "innerHTML",
                    "outerHTML"
                ]
                
                for signature in malware_signatures:
                    if signature in content_str:
                        logger.warning(f"Potential malware signature detected in file {file.filename}: {signature}")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error scanning file {file.filename} for malware: {e}")
            return False
    
    def quarantine_file(self, file: UploadFile, reason: str) -> str:
        """
        Quarantine suspicious file.
        
        Args:
            file: Uploaded file
            reason: Reason for quarantine
            
        Returns:
            Quarantine file path
        """
        quarantine_dir = self.config.get_quarantine_directory()
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        quarantine_filename = f"quarantine_{timestamp}_{file.filename}"
        quarantine_path = os.path.join(quarantine_dir, quarantine_filename)
        
        # Save file to quarantine
        with open(quarantine_path, "wb") as f:
            file.file.seek(0)
            f.write(file.file.read())
        
        file.file.seek(0)  # Reset to beginning
        
        logger.warning(f"File {file.filename} quarantined: {reason}")
        return quarantine_path
    
    def validate_file_upload(self, file: UploadFile, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate file upload.
        
        Args:
            file: Uploaded file
            user_id: Optional user ID
            
        Returns:
            Validation result dictionary
        """
        result = {
            "valid": False,
            "file_type": None,
            "secure_filename": None,
            "file_hash": None,
            "file_size": 0,
            "errors": [],
            "warnings": []
        }
        
        try:
            # Validate file size
            if not self.validate_file_size(file):
                result["errors"].append(f"File size exceeds maximum allowed size")
                return result
            
            # Validate file extension
            is_valid_ext, file_type = self.validate_file_extension(file.filename)
            if not is_valid_ext:
                result["errors"].append(f"File extension not allowed")
                return result
            
            result["file_type"] = file_type
            
            # Validate MIME type
            if not self.validate_mime_type(file, file_type):
                result["errors"].append(f"MIME type not allowed for file type {file_type}")
                return result
            
            # Validate file content
            if not self.validate_file_content(file, file_type):
                result["errors"].append("File content validation failed")
                return result
            
            # Scan for malware
            if not self.scan_for_malware(file):
                result["errors"].append("Malware detected in file")
                if self.config.should_quarantine_suspicious_files():
                    quarantine_path = self.quarantine_file(file, "Malware detected")
                    result["quarantine_path"] = quarantine_path
                return result
            
            # Generate secure filename
            secure_filename = self.generate_secure_filename(file.filename, user_id)
            result["secure_filename"] = secure_filename
            
            # Calculate file hash
            file_hash = self.calculate_file_hash(file)
            result["file_hash"] = file_hash
            
            # Get file size
            file.file.seek(0, 2)
            file_size = file.file.tell()
            file.file.seek(0)
            result["file_size"] = file_size
            
            result["valid"] = True
            
            logger.info(f"File {file.filename} validated successfully")
            
        except Exception as e:
            logger.error(f"Error validating file {file.filename}: {e}")
            result["errors"].append(f"Validation error: {str(e)}")
        
        return result
    
    def save_uploaded_file(self, file: UploadFile, secure_filename: str, user_id: Optional[str] = None) -> str:
        """
        Save uploaded file to secure location.
        
        Args:
            file: Uploaded file
            secure_filename: Secure filename
            user_id: Optional user ID
            
        Returns:
            Saved file path
        """
        upload_dir = self.config.get_upload_directory()
        
        # Create user-specific subdirectory if user_id provided
        if user_id:
            user_dir = os.path.join(upload_dir, user_id)
            os.makedirs(user_dir, exist_ok=True)
            file_path = os.path.join(user_dir, secure_filename)
        else:
            file_path = os.path.join(upload_dir, secure_filename)
        
        # Save file
        with open(file_path, "wb") as f:
            file.file.seek(0)
            f.write(file.file.read())
        
        file.file.seek(0)  # Reset to beginning
        
        logger.info(f"File saved to: {file_path}")
        return file_path
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get file information.
        
        Args:
            file_path: File path
            
        Returns:
            File information dictionary
        """
        if not os.path.exists(file_path):
            return {}
        
        stat = os.stat(file_path)
        
        return {
            "path": file_path,
            "size": stat.st_size,
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "mime_type": mimetypes.guess_type(file_path)[0]
        }


# Global file upload service instance
file_upload_service = FileUploadService()


def get_file_upload_service() -> FileUploadService:
    """Get the global file upload service instance."""
    return file_upload_service


def validate_file_upload(file: UploadFile, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Validate file upload."""
    return file_upload_service.validate_file_upload(file, user_id)


def save_uploaded_file(file: UploadFile, secure_filename: str, user_id: Optional[str] = None) -> str:
    """Save uploaded file."""
    return file_upload_service.save_uploaded_file(file, secure_filename, user_id)
