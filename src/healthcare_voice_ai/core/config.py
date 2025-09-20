"""
Simplified Configuration Settings for Dental Voice AI

Uses Pydantic Settings for clean, type-safe configuration management.
"""

import os
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class HealthcareIndustry(Enum):
    """Healthcare industry types supported by the platform."""
    DENTAL = "dental"
    FAMILY_MEDICINE = "family_medicine"
    INTERNAL_MEDICINE = "internal_medicine"
    DERMATOLOGY = "dermatology"
    CARDIOLOGY = "cardiology"
    ORTHOPEDICS = "orthopedics"
    CHIROPRACTIC = "chiropractic"
    MENTAL_HEALTH = "mental_health"
    THERAPY = "therapy"
    COUNSELING = "counseling"
    VETERINARY = "veterinary"


class RateLimitTier(str, Enum):
    """Rate limiting tiers for different endpoint types."""
    PUBLIC = "public"
    AUTH = "auth"
    API = "api"
    ADMIN = "admin"
    WEBHOOK = "webhook"
    UPLOAD = "upload"
    SEARCH = "search"


class Settings(BaseSettings):
    """
    Simplified application settings for dental voice AI system.
    
    Uses Pydantic for automatic validation and type conversion.
    """
    
    # Core Application Settings
    PROJECT_NAME: str = Field(default="Healthcare Voice AI", env="PROJECT_NAME")
    VERSION: str = Field(default="2.0.0", env="VERSION")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # Database Configuration
    SUPABASE_URL: Optional[str] = Field(default=None, env="SUPABASE_URL")
    SUPABASE_KEY: Optional[str] = Field(default=None, env="SUPABASE_KEY")
    
    # VAPI Integration
    VAPI_API_KEY: Optional[str] = Field(default=None, env="VAPI_API_KEY")
    WEBHOOK_SECRET: Optional[str] = Field(default=None, env="WEBHOOK_SECRET")
    
    # Healthcare Industry Configuration
    HEALTHCARE_INDUSTRY: str = Field(default="dental", env="HEALTHCARE_INDUSTRY")
    
    # Security
    JWT_SECRET: Optional[str] = Field(default=None, env="JWT_SECRET")
    
    # Encryption Configuration
    ENCRYPTION_MASTER_KEY: Optional[str] = Field(default=None, env="ENCRYPTION_MASTER_KEY")
    RSA_PRIVATE_KEY_PATH: Optional[str] = Field(default=None, env="RSA_PRIVATE_KEY_PATH")
    RSA_PUBLIC_KEY_PATH: Optional[str] = Field(default=None, env="RSA_PUBLIC_KEY_PATH")
    
    # SSL/TLS Configuration
    SSL_CERT_FILE: Optional[str] = Field(default=None, env="SSL_CERT_FILE")
    SSL_KEY_FILE: Optional[str] = Field(default=None, env="SSL_KEY_FILE")
    SSL_CA_FILE: Optional[str] = Field(default=None, env="SSL_CA_FILE")
    ENFORCE_HTTPS: bool = Field(default=True, env="ENFORCE_HTTPS")
    HTTPS_REDIRECT: bool = Field(default=True, env="HTTPS_REDIRECT")
    HSTS_MAX_AGE: int = Field(default=31536000, env="HSTS_MAX_AGE")  # 1 year
    HSTS_INCLUDE_SUBDOMAINS: bool = Field(default=True, env="HSTS_INCLUDE_SUBDOMAINS")
    HSTS_PRELOAD: bool = Field(default=True, env="HSTS_PRELOAD")
    
    # Server Configuration
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    RELOAD: bool = Field(default=True, env="RELOAD")
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:8080",
            "http://localhost:3001"
        ],
        env="CORS_ORIGINS"
    )
    
    # Development CORS Origins (for ngrok and testing)
    DEV_CORS_ORIGINS: List[str] = Field(
        default=[
            "https://*.ngrok-free.app",
            "https://*.ngrok.io"
        ],
        env="DEV_CORS_ORIGINS"
    )
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Database Performance
    DB_POOL_SIZE: int = Field(default=10, env="DB_POOL_SIZE")
    DB_MAX_OVERFLOW: int = Field(default=20, env="DB_MAX_OVERFLOW")
    DB_POOL_TIMEOUT: int = Field(default=30, env="DB_POOL_TIMEOUT")
    DB_POOL_RECYCLE: int = Field(default=3600, env="DB_POOL_RECYCLE")
    DB_POOL_PRE_PING: bool = Field(default=True, env="DB_POOL_PRE_PING")
    DB_CONNECT_TIMEOUT: int = Field(default=10, env="DB_CONNECT_TIMEOUT")
    DB_COMMAND_TIMEOUT: int = Field(default=30, env="DB_COMMAND_TIMEOUT")
    
    # Business Configuration
    DEFAULT_BUSINESS_START_HOUR: int = Field(default=9, env="DEFAULT_BUSINESS_START_HOUR")
    DEFAULT_BUSINESS_END_HOUR: int = Field(default=17, env="DEFAULT_BUSINESS_END_HOUR")
    
    # AI Configuration
    FAQ_SIMILARITY_THRESHOLD: float = Field(default=0.7, env="FAQ_SIMILARITY_THRESHOLD")
    INTENT_CONFIDENCE_THRESHOLD: float = Field(default=0.3, env="INTENT_CONFIDENCE_THRESHOLD")
    
    # Industry Configuration
    INDUSTRY_CONFIGS: Dict[HealthcareIndustry, Dict[str, Any]] = {
        HealthcareIndustry.DENTAL: {
            "name": "Dental Practice",
            "assistant_name": "Riley",
            "default_services": ["Cleaning", "Exam", "Filling", "Crown", "Root Canal"],
            "default_hours": {"monday": "9:00 AM - 5:00 PM", "tuesday": "9:00 AM - 5:00 PM", "wednesday": "9:00 AM - 5:00 PM", "thursday": "9:00 AM - 5:00 PM", "friday": "9:00 AM - 5:00 PM"}
        },
        HealthcareIndustry.FAMILY_MEDICINE: {
            "name": "Family Medicine Practice",
            "assistant_name": "Alex",
            "default_services": ["Annual Physical", "Sick Visit", "Vaccination", "Health Screening"],
            "default_hours": {"monday": "8:00 AM - 6:00 PM", "tuesday": "8:00 AM - 6:00 PM", "wednesday": "8:00 AM - 6:00 PM", "thursday": "8:00 AM - 6:00 PM", "friday": "8:00 AM - 6:00 PM"}
        },
        HealthcareIndustry.VETERINARY: {
            "name": "Veterinary Clinic",
            "assistant_name": "Max",
            "default_services": ["Wellness Exam", "Vaccination", "Surgery", "Emergency Care"],
            "default_hours": {"monday": "8:00 AM - 6:00 PM", "tuesday": "8:00 AM - 6:00 PM", "wednesday": "8:00 AM - 6:00 PM", "thursday": "8:00 AM - 6:00 PM", "friday": "8:00 AM - 6:00 PM", "saturday": "9:00 AM - 2:00 PM"}
        },
        HealthcareIndustry.MENTAL_HEALTH: {
            "name": "Mental Health Practice",
            "assistant_name": "Sage",
            "default_services": ["Individual Therapy", "Group Therapy", "Counseling", "Crisis Support"],
            "default_hours": {"monday": "9:00 AM - 7:00 PM", "tuesday": "9:00 AM - 7:00 PM", "wednesday": "9:00 AM - 7:00 PM", "thursday": "9:00 AM - 7:00 PM", "friday": "9:00 AM - 5:00 PM"}
        }
    }
    
    # Rate Limiting Configuration
    RATE_LIMITS: Dict[RateLimitTier, str] = {
        RateLimitTier.PUBLIC: "100/minute",
        RateLimitTier.AUTH: "10/minute",
        RateLimitTier.API: "60/minute",
        RateLimitTier.ADMIN: "30/minute",
        RateLimitTier.WEBHOOK: "200/minute",
        RateLimitTier.UPLOAD: "5/minute",
        RateLimitTier.SEARCH: "30/minute",
    }
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from environment variable."""
        if isinstance(v, str):
            if v.startswith("["):
                # JSON array format
                import json
                return json.loads(v)
            else:
                # Comma-separated format
                return [origin.strip() for origin in v.split(",")]
        return v
    
    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, v):
        """Parse DEBUG from string to boolean."""
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return v
    
    @field_validator("RELOAD", mode="before")
    @classmethod
    def parse_reload(cls, v):
        """Parse RELOAD from string to boolean."""
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return v
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() == "development"
    
    def get_cors_origins(self) -> List[str]:
        """Get CORS origins based on environment."""
        if self.is_development():
            return self.CORS_ORIGINS + self.DEV_CORS_ORIGINS
        return self.CORS_ORIGINS
    
    def get_log_level(self) -> int:
        """Get the appropriate logging level."""
        import logging
        level_mapping = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        return level_mapping.get(self.LOG_LEVEL.upper(), logging.INFO)
    
    def validate_required_settings(self) -> bool:
        """
        Validate required settings for production.
        
        Returns:
            True if all required settings are valid
            
        Raises:
            ValueError: If required settings are missing
        """
        if self.is_production():
            required_settings = {
                "SUPABASE_URL": self.SUPABASE_URL,
                "SUPABASE_KEY": self.SUPABASE_KEY,
                "JWT_SECRET": self.JWT_SECRET,
                "ENCRYPTION_MASTER_KEY": self.ENCRYPTION_MASTER_KEY,
            }
            
            missing = [key for key, value in required_settings.items() if not value]
            if missing:
                raise ValueError(f"Missing required settings in production: {', '.join(missing)}")
        
        return True
    
    def get_industry_config(self, industry: HealthcareIndustry) -> Dict[str, Any]:
        """Get configuration for a specific healthcare industry."""
        return self.INDUSTRY_CONFIGS.get(industry, self.INDUSTRY_CONFIGS[HealthcareIndustry.DENTAL])
    
    def get_all_industries(self) -> List[Dict[str, Any]]:
        """Get list of all available industries."""
        return [
            {
                "value": industry.value,
                "label": config["name"],
                "assistant_name": config["assistant_name"]
            }
            for industry, config in self.INDUSTRY_CONFIGS.items()
        ]
    
    def get_rate_limit_for_tier(self, tier: RateLimitTier) -> str:
        """Get rate limit for specific tier."""
        return self.RATE_LIMITS.get(tier, self.RATE_LIMITS[RateLimitTier.API])
    
    def get_config_summary(self) -> dict:
        """
        Get configuration summary for monitoring/debugging.
        
        Returns:
            Configuration summary excluding sensitive data
        """
        return {
            "project_name": self.PROJECT_NAME,
            "version": self.VERSION,
            "environment": self.ENVIRONMENT,
            "debug": self.DEBUG,
            "host": self.HOST,
            "port": self.PORT,
            "log_level": self.LOG_LEVEL,
            "database": {
                "url_configured": bool(self.SUPABASE_URL),
                "key_configured": bool(self.SUPABASE_KEY),
                "pool_size": self.DB_POOL_SIZE,
                "max_overflow": self.DB_MAX_OVERFLOW
            },
            "security": {
                "jwt_configured": bool(self.JWT_SECRET)
            },
            "vapi": {
                "api_key_configured": bool(self.VAPI_API_KEY),
                "webhook_secret_configured": bool(self.WEBHOOK_SECRET)
            },
            "cors": {
                "origins_count": len(self.CORS_ORIGINS),
                "origins": self.CORS_ORIGINS[:3] if len(self.CORS_ORIGINS) > 3 else self.CORS_ORIGINS
            },
            "business": {
                "start_hour": self.DEFAULT_BUSINESS_START_HOUR,
                "end_hour": self.DEFAULT_BUSINESS_END_HOUR
            },
            "ai": {
                "faq_similarity_threshold": self.FAQ_SIMILARITY_THRESHOLD,
                "intent_confidence_threshold": self.INTENT_CONFIDENCE_THRESHOLD
            },
            "industries": {
                "supported_count": len(self.INDUSTRY_CONFIGS),
                "supported_types": [industry.value for industry in self.INDUSTRY_CONFIGS.keys()]
            }
        }
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True
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