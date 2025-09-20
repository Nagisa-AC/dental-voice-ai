"""
Unit tests for environment validation.

Tests the environment validation system to ensure proper configuration
validation and error handling.
"""

import pytest
import os
from unittest.mock import patch
from healthcare_voice_ai.core.environment_validation import (
    EnvironmentConfig, EnvironmentValidator, validate_environment,
    check_environment_health, get_environment_summary
)


class TestEnvironmentConfig:
    """Test EnvironmentConfig model validation."""
    
    def test_valid_config(self):
        """Test valid environment configuration."""
        config_data = {
            "JWT_SECRET": "test_secret_key_that_is_long_enough_for_validation",
            "SUPABASE_URL": "postgresql://user:pass@localhost:5432/db",
            "VAPI_API_KEY": "vapi_test_key_12345",
            "ENVIRONMENT": "development",
            "DEBUG": False,
            "LOG_LEVEL": "INFO",
            "REDIS_HOST": "localhost",
            "REDIS_PORT": 6379,
            "REDIS_DB": 0,
            "CORS_ORIGINS": ["*"],
            "RATE_LIMIT_ENABLED": True,
            "MAX_REQUEST_SIZE": 10485760,
            "LOG_FORMAT": "json"
        }
        
        config = EnvironmentConfig(**config_data)
        assert config.ENVIRONMENT == "development"
        assert config.DEBUG is False
        assert config.LOG_LEVEL == "INFO"
        assert config.REDIS_HOST == "localhost"
        assert config.REDIS_PORT == 6379
    
    def test_invalid_jwt_secret_too_short(self):
        """Test JWT secret validation - too short."""
        config_data = {
            "JWT_SECRET": "short",
            "SUPABASE_URL": "postgresql://user:pass@localhost:5432/db",
            "VAPI_API_KEY": "vapi_test_key_12345"
        }
        
        with pytest.raises(ValueError, match="JWT_SECRET must be at least 32 characters"):
            EnvironmentConfig(**config_data)
    
    def test_invalid_jwt_secret_weak(self):
        """Test JWT secret validation - weak secret."""
        config_data = {
            "JWT_SECRET": "test" + "x" * 28,  # 32 chars but starts with 'test'
            "SUPABASE_URL": "postgresql://user:pass@localhost:5432/db",
            "VAPI_API_KEY": "vapi_test_key_12345"
        }
        
        with pytest.raises(ValueError, match="JWT_SECRET appears to be a weak"):
            EnvironmentConfig(**config_data)
    
    def test_invalid_environment(self):
        """Test invalid environment value."""
        config_data = {
            "JWT_SECRET": "test_secret_key_that_is_long_enough_for_validation",
            "SUPABASE_URL": "postgresql://user:pass@localhost:5432/db",
            "VAPI_API_KEY": "vapi_test_key_12345",
            "ENVIRONMENT": "invalid"
        }
        
        with pytest.raises(ValueError, match="ENVIRONMENT must be one of"):
            EnvironmentConfig(**config_data)
    
    def test_invalid_supabase_url(self):
        """Test invalid Supabase URL."""
        config_data = {
            "JWT_SECRET": "test_secret_key_that_is_long_enough_for_validation",
            "SUPABASE_URL": "invalid-url",
            "VAPI_API_KEY": "vapi_test_key_12345"
        }
        
        with pytest.raises(ValueError, match="SUPABASE_URL must be a valid"):
            EnvironmentConfig(**config_data)
    
    def test_invalid_redis_host(self):
        """Test invalid Redis host."""
        config_data = {
            "JWT_SECRET": "test_secret_key_that_is_long_enough_for_validation",
            "SUPABASE_URL": "postgresql://user:pass@localhost:5432/db",
            "VAPI_API_KEY": "vapi_test_key_12345",
            "REDIS_HOST": ""
        }
        
        with pytest.raises(ValueError, match="REDIS_HOST cannot be empty"):
            EnvironmentConfig(**config_data)
    
    def test_invalid_redis_port(self):
        """Test invalid Redis port."""
        config_data = {
            "JWT_SECRET": "test_secret_key_that_is_long_enough_for_validation",
            "SUPABASE_URL": "postgresql://user:pass@localhost:5432/db",
            "VAPI_API_KEY": "vapi_test_key_12345",
            "REDIS_PORT": 70000  # Invalid port
        }
        
        with pytest.raises(ValueError, match="ensure this value is less than or equal to 65535"):
            EnvironmentConfig(**config_data)
    
    def test_invalid_cors_origins(self):
        """Test invalid CORS origins."""
        config_data = {
            "JWT_SECRET": "test_secret_key_that_is_long_enough_for_validation",
            "SUPABASE_URL": "postgresql://user:pass@localhost:5432/db",
            "VAPI_API_KEY": "vapi_test_key_12345",
            "CORS_ORIGINS": ["invalid-origin"]
        }
        
        with pytest.raises(ValueError, match="Invalid CORS origin"):
            EnvironmentConfig(**config_data)
    
    def test_log_level_validation(self):
        """Test log level validation."""
        config_data = {
            "JWT_SECRET": "test_secret_key_that_is_long_enough_for_validation",
            "SUPABASE_URL": "postgresql://user:pass@localhost:5432/db",
            "VAPI_API_KEY": "vapi_test_key_12345",
            "LOG_LEVEL": "invalid"
        }
        
        with pytest.raises(ValueError, match="LOG_LEVEL must be one of"):
            EnvironmentConfig(**config_data)
    
    def test_log_format_validation(self):
        """Test log format validation."""
        config_data = {
            "JWT_SECRET": "test_secret_key_that_is_long_enough_for_validation",
            "SUPABASE_URL": "postgresql://user:pass@localhost:5432/db",
            "VAPI_API_KEY": "vapi_test_key_12345",
            "LOG_FORMAT": "invalid"
        }
        
        with pytest.raises(ValueError, match="LOG_FORMAT must be one of"):
            EnvironmentConfig(**config_data)


class TestEnvironmentValidator:
    """Test EnvironmentValidator class."""
    
    def test_validator_initialization(self):
        """Test validator initialization."""
        validator = EnvironmentValidator()
        assert validator.config is None
        assert validator.validation_errors == []
    
    @patch.dict(os.environ, {
        'JWT_SECRET': 'test_secret_key_that_is_long_enough_for_validation',
        'SUPABASE_URL': 'postgresql://user:pass@localhost:5432/db',
        'VAPI_API_KEY': 'vapi_test_key_12345'
    })
    def test_validate_environment_success(self):
        """Test successful environment validation."""
        validator = EnvironmentValidator()
        config = validator.validate_environment()
        
        assert config is not None
        assert config.ENVIRONMENT == "development"
        assert config.JWT_SECRET == "test_secret_key_that_is_long_enough_for_validation"
        assert config.SUPABASE_URL == "postgresql://user:pass@localhost:5432/db"
        assert config.VAPI_API_KEY == "vapi_test_key_12345"
    
    @patch.dict(os.environ, {
        'JWT_SECRET': 'short',
        'SUPABASE_URL': 'postgresql://user:pass@localhost:5432/db',
        'VAPI_API_KEY': 'vapi_test_key_12345'
    }, clear=True)
    def test_validate_environment_failure(self):
        """Test environment validation failure."""
        validator = EnvironmentValidator()
        
        with pytest.raises(EnvironmentError, match="Environment validation failed"):
            validator.validate_environment()
    
    @patch.dict(os.environ, {
        'JWT_SECRET': 'test_secret_key_that_is_long_enough_for_validation',
        'SUPABASE_URL': 'postgresql://user:pass@localhost:5432/db',
        'VAPI_API_KEY': 'vapi_test_key_12345',
        'ENVIRONMENT': 'production',
        'DEBUG': 'false',
        'CORS_ORIGINS': 'https://example.com,https://app.example.com'
    })
    def test_production_validation(self):
        """Test production environment validation."""
        validator = EnvironmentValidator()
        config = validator.validate_environment()
        
        assert config.ENVIRONMENT == "production"
        assert config.DEBUG is False
        assert config.CORS_ORIGINS == ["https://example.com", "https://app.example.com"]
    
    @patch.dict(os.environ, {
        'JWT_SECRET': 'test_secret_key_that_is_long_enough_for_validation',
        'SUPABASE_URL': 'postgresql://user:pass@localhost:5432/db',
        'VAPI_API_KEY': 'vapi_test_key_12345',
        'ENVIRONMENT': 'production',
        'DEBUG': 'true'  # Debug should be false in production
    })
    def test_production_validation_failure(self):
        """Test production environment validation failure."""
        validator = EnvironmentValidator()
        
        with pytest.raises(EnvironmentError, match="Production validation failed"):
            validator.validate_environment()
    
    def test_get_config_summary_not_validated(self):
        """Test config summary when not validated."""
        validator = EnvironmentValidator()
        summary = validator.get_config_summary()
        
        assert summary["status"] == "not_validated"
    
    @patch.dict(os.environ, {
        'JWT_SECRET': 'test_secret_key_that_is_long_enough_for_validation',
        'SUPABASE_URL': 'postgresql://user:pass@localhost:5432/db',
        'VAPI_API_KEY': 'vapi_test_key_12345',
        'SUPABASE_KEY': 'test_key',
        'SENTRY_DSN': 'https://test@sentry.io/test'
    })
    def test_get_config_summary_validated(self):
        """Test config summary when validated."""
        validator = EnvironmentValidator()
        validator.validate_environment()
        summary = validator.get_config_summary()
        
        assert summary["status"] == "validated"
        assert summary["environment"] == "development"
        assert summary["has_supabase_key"] is True
        assert summary["has_sentry"] is True


class TestEnvironmentValidationFunctions:
    """Test environment validation utility functions."""
    
    @patch.dict(os.environ, {
        'JWT_SECRET': 'test_secret_key_that_is_long_enough_for_validation',
        'SUPABASE_URL': 'postgresql://user:pass@localhost:5432/db',
        'VAPI_API_KEY': 'vapi_test_key_12345'
    })
    def test_validate_environment_function(self):
        """Test validate_environment function."""
        config = validate_environment()
        assert config.ENVIRONMENT == "development"
        assert config.JWT_SECRET == "test_secret_key_that_is_long_enough_for_validation"
    
    @patch.dict(os.environ, {
        'JWT_SECRET': 'test_secret_key_that_is_long_enough_for_validation',
        'SUPABASE_URL': 'postgresql://user:pass@localhost:5432/db',
        'VAPI_API_KEY': 'vapi_test_key_12345'
    })
    def test_check_environment_health_healthy(self):
        """Test environment health check - healthy."""
        health = check_environment_health()
        
        assert health["status"] == "healthy"
        assert health["environment"] == "development"
        assert health["validation_errors"] == []
        assert health["warnings"] == []
    
    @patch.dict(os.environ, {
        'JWT_SECRET': 'short',
        'SUPABASE_URL': 'postgresql://user:pass@localhost:5432/db',
        'VAPI_API_KEY': 'vapi_test_key_12345'
    }, clear=True)
    def test_check_environment_health_unhealthy(self):
        """Test environment health check - unhealthy."""
        health = check_environment_health()
        
        assert health["status"] == "unhealthy"
        assert health["environment"] == "unknown"
        assert len(health["validation_errors"]) > 0
    
    @patch.dict(os.environ, {
        'JWT_SECRET': 'test_secret_key_that_is_long_enough_for_validation',
        'SUPABASE_URL': 'postgresql://user:pass@localhost:5432/db',
        'VAPI_API_KEY': 'vapi_test_key_12345'
    })
    def test_get_environment_summary(self):
        """Test get environment summary."""
        summary = get_environment_summary()
        
        assert summary["status"] == "validated"
        assert summary["environment"] == "development"
        assert "redis_host" in summary
        assert "log_level" in summary


class TestEnvironmentValidationIntegration:
    """Integration tests for environment validation."""
    
    @patch.dict(os.environ, {
        'JWT_SECRET': 'test_secret_key_that_is_long_enough_for_validation',
        'SUPABASE_URL': 'postgresql://user:pass@localhost:5432/db',
        'VAPI_API_KEY': 'vapi_test_key_12345',
        'ENVIRONMENT': 'production',
        'DEBUG': 'false',
        'LOG_LEVEL': 'WARNING',
        'CORS_ORIGINS': 'https://example.com',
        'REDIS_HOST': 'redis.example.com',
        'REDIS_PORT': '6379',
        'REDIS_DB': '1',
        'RATE_LIMIT_ENABLED': 'true',
        'MAX_REQUEST_SIZE': '20971520',
        'LOG_FORMAT': 'json'
    })
    def test_full_production_config(self):
        """Test full production configuration."""
        config = validate_environment()
        
        assert config.ENVIRONMENT == "production"
        assert config.DEBUG is False
        assert config.LOG_LEVEL == "WARNING"
        assert config.CORS_ORIGINS == ["https://example.com"]
        assert config.REDIS_HOST == "redis.example.com"
        assert config.REDIS_PORT == 6379
        assert config.REDIS_DB == 1
        assert config.RATE_LIMIT_ENABLED is True
        assert config.MAX_REQUEST_SIZE == 20971520
        assert config.LOG_FORMAT == "json"
    
    @patch.dict(os.environ, {
        'JWT_SECRET': 'test_secret_key_that_is_long_enough_for_validation',
        'SUPABASE_URL': 'postgresql://user:pass@localhost:5432/db',
        'VAPI_API_KEY': 'vapi_test_key_12345',
        'ENVIRONMENT': 'development',
        'DEBUG': 'true',
        'LOG_LEVEL': 'DEBUG',
        'CORS_ORIGINS': '*',
        'REDIS_HOST': 'localhost',
        'REDIS_PORT': '6379',
        'REDIS_DB': '0',
        'RATE_LIMIT_ENABLED': 'false',
        'MAX_REQUEST_SIZE': '10485760',
        'LOG_FORMAT': 'text'
    })
    def test_full_development_config(self):
        """Test full development configuration."""
        config = validate_environment()
        
        assert config.ENVIRONMENT == "development"
        assert config.DEBUG is True
        assert config.LOG_LEVEL == "DEBUG"
        assert config.CORS_ORIGINS == ["*"]
        assert config.REDIS_HOST == "localhost"
        assert config.REDIS_PORT == 6379
        assert config.REDIS_DB == 0
        assert config.RATE_LIMIT_ENABLED is False
        assert config.MAX_REQUEST_SIZE == 10485760
        assert config.LOG_FORMAT == "text"
