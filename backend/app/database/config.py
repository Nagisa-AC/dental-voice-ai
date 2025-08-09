"""
Production Configuration Settings for Dental Voice AI

Manages environment variables, feature flags, and application configuration
for the multi-practice dental voice AI system with VAPI integration.
"""

import os
import logging
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """
    Application settings for production dental voice AI system.
    
    Supports multiple dental practices with intelligent FAQ matching,
    real-time intent recognition, and seamless VAPI integration.
    """
    
    # Core Application Settings
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Dental Voice AI - FAQ Processor")
    VERSION: str = "2.0.0"
    DESCRIPTION: str = "Production AI-powered voice assistant for dental practices"
    
    # Environment Configuration
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Database Configuration (Required)
    SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: Optional[str] = os.getenv("SUPABASE_KEY")
    
    # VAPI Integration (Optional)
    VAPI_API_KEY: Optional[str] = os.getenv("VAPI_API_KEY")
    WEBHOOK_SECRET: Optional[str] = os.getenv("WEBHOOK_SECRET")
    
    # Practice Identification
    TENANT_ID_METHOD: str = os.getenv("TENANT_ID_METHOD", "phone_number")
    
    # AI Configuration
    FAQ_SIMILARITY_THRESHOLD: float = float(os.getenv("FAQ_SIMILARITY_THRESHOLD", "0.7"))
    INTENT_CONFIDENCE_THRESHOLD: float = float(os.getenv("INTENT_CONFIDENCE_THRESHOLD", "0.3"))
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    RELOAD: bool = os.getenv("RELOAD", "true").lower() == "true"
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:3001"
    ]
    
    # Parse CORS origins from environment
    cors_env = os.getenv("CORS_ORIGINS")
    if cors_env:
        try:
            import json
            CORS_ORIGINS = json.loads(cors_env)
        except json.JSONDecodeError:
            CORS_ORIGINS = [origin.strip() for origin in cors_env.split(",")]
    
    # Feature Flags
    ENABLE_SEMANTIC_MATCHING: bool = os.getenv("ENABLE_SEMANTIC_MATCHING", "true").lower() == "true"
    ENABLE_ENTITY_EXTRACTION: bool = os.getenv("ENABLE_ENTITY_EXTRACTION", "true").lower() == "true"
    ENABLE_TENANT_SPECIFIC_FAQS: bool = os.getenv("ENABLE_TENANT_SPECIFIC_FAQS", "true").lower() == "true"
    
    # Performance Configuration
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "10"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    
    def validate_required_settings(self) -> bool:
        """
        Validate required environment variables.
        
        Returns:
            True if all required settings are valid
            
        Raises:
            ValueError: If required settings are missing
        """
        missing_settings = []
        
        if not self.SUPABASE_URL:
            missing_settings.append("SUPABASE_URL")
            
        if not self.SUPABASE_KEY:
            missing_settings.append("SUPABASE_KEY")
        
        if missing_settings:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_settings)}. "
                f"Please check your .env file or environment configuration."
            )
        
        return True
    
    def get_log_level(self) -> int:
        """Get the appropriate logging level based on configuration."""
        level_mapping = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        return level_mapping.get(self.LOG_LEVEL.upper(), logging.INFO)
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() == "development"
    
    def get_config_summary(self) -> dict:
        """
        Get configuration summary excluding sensitive data.
        
        Returns:
            Configuration summary for monitoring/debugging
        """
        return {
            "project_name": self.PROJECT_NAME,
            "version": self.VERSION,
            "environment": self.ENVIRONMENT,
            "debug": self.DEBUG,
            "host": self.HOST,
            "port": self.PORT,
            "tenant_id_method": self.TENANT_ID_METHOD,
            "ai_config": {
                "faq_similarity_threshold": self.FAQ_SIMILARITY_THRESHOLD,
                "intent_confidence_threshold": self.INTENT_CONFIDENCE_THRESHOLD,
                "semantic_matching": self.ENABLE_SEMANTIC_MATCHING,
                "entity_extraction": self.ENABLE_ENTITY_EXTRACTION,
                "tenant_specific_faqs": self.ENABLE_TENANT_SPECIFIC_FAQS
            },
            "database_configured": bool(self.SUPABASE_URL and self.SUPABASE_KEY),
            "vapi_configured": bool(self.VAPI_API_KEY)
        }


# Global settings instance
settings = Settings()

# Validate settings in production
if settings.is_production():
    try:
        settings.validate_required_settings()
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        raise