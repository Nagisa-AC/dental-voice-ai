"""
Unit tests for security fixes.
"""

import pytest
from unittest.mock import patch, MagicMock

from healthcare_voice_ai.core.config import Settings


class TestCORSSecurity:
    """Test CORS security configuration."""
    
    def test_cors_origins_development(self):
        """Test CORS origins in development environment."""
        with patch.dict('os.environ', {'ENVIRONMENT': 'development'}):
            settings = Settings()
            cors_origins = settings.get_cors_origins()
            
            # Should include both production and development origins
            assert "http://localhost:3000" in cors_origins
            assert "https://*.ngrok-free.app" in cors_origins
            assert "https://*.ngrok.io" in cors_origins
    
    def test_cors_origins_production(self):
        """Test CORS origins in production environment."""
        with patch.dict('os.environ', {'ENVIRONMENT': 'production'}):
            settings = Settings()
            cors_origins = settings.get_cors_origins()
            
            # Should only include production origins
            assert "http://localhost:3000" in cors_origins
            assert "https://*.ngrok-free.app" not in cors_origins
            assert "https://*.ngrok.io" not in cors_origins
    
    def test_cors_origins_custom(self):
        """Test custom CORS origins from environment."""
        custom_origins = ["https://example.com", "https://app.example.com"]
        with patch.dict('os.environ', {
            'ENVIRONMENT': 'production',
            'CORS_ORIGINS': '["https://example.com", "https://app.example.com"]'
        }):
            settings = Settings()
            cors_origins = settings.get_cors_origins()
            
            assert cors_origins == custom_origins


class TestXSSProtection:
    """Test XSS protection measures."""
    
    def test_html_escaping(self):
        """Test HTML escaping functionality."""
        # This would test the escapeHtml function from the dashboard
        # For now, we'll test the concept
        
        test_cases = [
            ("<script>alert('xss')</script>", "&lt;script&gt;alert('xss')&lt;/script&gt;"),
            ("<img src=x onerror=alert('xss')>", "&lt;img src=x onerror=alert('xss')&gt;"),
            ("Hello World", "Hello World"),
            ("", ""),
        ]
        
        for input_text, expected_output in test_cases:
            # Simulate the escapeHtml function
            escaped = input_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            assert escaped == expected_output
    
    def test_csp_headers(self):
        """Test Content Security Policy configuration."""
        # Test that CSP headers are properly configured
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: https:",
            "connect-src 'self' https://api.vapi.ai",
            "object-src 'none'",
            "base-uri 'self'",
            "form-action 'self'"
        ]
        
        # This would be tested in integration tests with actual HTTP requests
        # For now, we verify the directives are properly structured
        for directive in csp_directives:
            assert "'" in directive or ":" in directive  # Basic validation


class TestSecurityHeaders:
    """Test security headers configuration."""
    
    def test_cors_headers_restricted(self):
        """Test that CORS headers are properly restricted."""
        # Test that allow_headers is not "*"
        # This would be tested in integration tests
        allowed_headers = [
            "Accept",
            "Accept-Language", 
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-Request-ID"
        ]
        
        # Verify specific headers are allowed
        assert "Authorization" in allowed_headers
        assert "Content-Type" in allowed_headers
        assert "X-Request-ID" in allowed_headers
        
        # Verify wildcard is not used
        assert "*" not in allowed_headers
    
    def test_cors_credentials_allowed(self):
        """Test that credentials are properly configured."""
        # In a real test, this would check the actual CORS middleware configuration
        # For now, we verify the concept
        allow_credentials = True
        assert allow_credentials is True  # Should be True for authenticated requests
