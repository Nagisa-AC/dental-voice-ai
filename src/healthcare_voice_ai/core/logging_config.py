"""
Logging Configuration for Healthcare Voice AI

Implements production-ready logging with:
- Rotating file handlers
- Structured logging
- Environment-aware configuration
- HIPAA-compliant log sanitization
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional
from .config import settings


class SensitiveDataFilter(logging.Filter):
    """
    Filter to remove sensitive data from log messages.
    
    HIPAA-compliant logging that masks:
    - API keys
    - Passwords
    - Personal identifiers
    - Medical information
    """
    
    SENSITIVE_PATTERNS = [
        (r'(password["\']?\s*[:=]\s*["\']?)[^"\']+(["\']?)', r'\1***MASKED***\2'),
        (r'(api_key["\']?\s*[:=]\s*["\']?)[^"\']+(["\']?)', r'\1***MASKED***\2'),
        (r'(token["\']?\s*[:=]\s*["\']?)[^"\']+(["\']?)', r'\1***MASKED***\2'),
        (r'(secret["\']?\s*[:=]\s*["\']?)[^"\']+(["\']?)', r'\1***MASKED***\2'),
        (r'(ssn["\']?\s*[:=]\s*["\']?)[^"\']+(["\']?)', r'\1***MASKED***\2'),
        (r'(patient_id["\']?\s*[:=]\s*["\']?)[^"\']+(["\']?)', r'\1***MASKED***\2'),
        (r'(medical_record["\']?\s*[:=]\s*["\']?)[^"\']+(["\']?)', r'\1***MASKED***\2'),
    ]
    
    def filter(self, record):
        """Filter sensitive data from log records."""
        import re
        
        if hasattr(record, 'msg') and record.msg:
            message = str(record.msg)
            for pattern, replacement in self.SENSITIVE_PATTERNS:
                message = re.sub(pattern, replacement, message, flags=re.IGNORECASE)
            record.msg = message
        
        return True


class HealthcareLogFormatter(logging.Formatter):
    """
    Custom formatter for healthcare application logs.
    
    Provides structured, HIPAA-compliant log formatting.
    """
    
    def __init__(self, include_timestamp=True, include_level=True, include_module=True):
        self.include_timestamp = include_timestamp
        self.include_level = include_level
        self.include_module = include_module
        
        # Build format string
        format_parts = []
        if include_timestamp:
            format_parts.append("%(asctime)s")
        if include_level:
            format_parts.append("%(levelname)-8s")
        if include_module:
            format_parts.append("%(name)s")
        format_parts.append("%(message)s")
        
        super().__init__(fmt=" - ".join(format_parts), datefmt="%Y-%m-%d %H:%M:%S")
    
    def format(self, record):
        """Format log record with healthcare-specific formatting."""
        # Add emoji indicators for different log levels
        if record.levelno >= logging.ERROR:
            record.levelname = f"❌ {record.levelname}"
        elif record.levelno >= logging.WARNING:
            record.levelname = f"⚠️ {record.levelname}"
        elif record.levelno >= logging.INFO:
            record.levelname = f"ℹ️ {record.levelname}"
        else:
            record.levelname = f"🔍 {record.levelname}"
        
        return super().format(record)


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    enable_console: bool = True
) -> None:
    """
    Set up application logging with rotating file handlers.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (defaults to logs/dental_voice_ai.log)
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
        enable_console: Whether to enable console logging
    """
    
    # Use provided log level or get from settings
    if log_level is None:
        log_level = settings.LOG_LEVEL.upper()
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level, logging.INFO)
    
    # Set up log file path
    if log_file is None:
        # Ensure logs directory exists
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        log_file = logs_dir / "dental_voice_ai.log"
    
    # Clear existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    
    # Set root logger level
    root_logger.setLevel(numeric_level)
    
    # Create formatters
    file_formatter = HealthcareLogFormatter(
        include_timestamp=True,
        include_level=True,
        include_module=True
    )
    
    console_formatter = HealthcareLogFormatter(
        include_timestamp=False,  # Console doesn't need timestamp
        include_level=True,
        include_module=False  # Shorter for console
    )
    
    # Create rotating file handler
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(file_formatter)
    
    # Add sensitive data filter to file handler
    file_handler.addFilter(SensitiveDataFilter())
    
    # Add file handler to root logger
    root_logger.addHandler(file_handler)
    
    # Create console handler if enabled
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(console_formatter)
        
        # Add sensitive data filter to console handler
        console_handler.addFilter(SensitiveDataFilter())
        
        # Add console handler to root logger
        root_logger.addHandler(console_handler)
    
    # Configure specific loggers
    configure_third_party_loggers()
    
    # Log the logging setup
    logger = logging.getLogger(__name__)
    logger.info(f"📝 Logging configured - Level: {log_level}, File: {log_file}")
    logger.info(f"🔄 Log rotation: {max_bytes/1024/1024:.1f}MB max, {backup_count} backups")


def configure_third_party_loggers():
    """Configure logging levels for third-party libraries."""
    
    # Reduce noise from third-party libraries
    third_party_loggers = {
        'uvicorn.access': logging.WARNING,
        'uvicorn.error': logging.INFO,
        'fastapi': logging.INFO,
        'sqlalchemy.engine': logging.WARNING,
        'sqlalchemy.pool': logging.WARNING,
        'alembic': logging.INFO,
        'httpx': logging.WARNING,
        'httpcore': logging.WARNING,
        'asyncio': logging.WARNING,
    }
    
    for logger_name, level in third_party_loggers.items():
        logging.getLogger(logger_name).setLevel(level)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with healthcare-specific configuration.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def log_startup_info():
    """Log application startup information."""
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Healthcare Voice AI - Starting Application")
    logger.info(f"🌍 Environment: {settings.ENVIRONMENT}")
    logger.info(f"📦 Version: {settings.VERSION}")
    logger.info(f"🏥 Project: {settings.PROJECT_NAME}")
    
    if settings.is_production():
        logger.info("🔒 Production mode - Enhanced security enabled")
    else:
        logger.info("🛠️ Development mode - Debug features enabled")


def log_shutdown_info():
    """Log application shutdown information."""
    logger = logging.getLogger(__name__)
    logger.info("🛑 Healthcare Voice AI - Shutting down")


# Initialize logging when module is imported
if __name__ != "__main__":
    # Only auto-setup if not being run directly
    setup_logging()
