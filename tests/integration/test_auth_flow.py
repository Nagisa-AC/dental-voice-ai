"""
Integration tests for authentication flow.

Tests the complete authentication process including login, token validation, and user management.
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from healthcare_voice_ai.core.models.database_models import UserRole
from healthcare_voice_ai.core.services.auth_service import AuthService


class TestAuthFlowIntegration:
    """Integration tests for authentication flow."""
    
    @pytest.mark.asyncio
    async def test_complete_auth_flow(self, test_client: AsyncClient, test_auth_service: AuthService):
        """Test complete authentication flow from user creation to login."""
        # Step 1: Create a user
        user = await test_auth_service.create_user(
            email="test@example.com",
            password="testpassword123",
            role=UserRole.ADMIN
        )
        
        # Step 2: Login with correct credentials
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        response = await test_client.post("/auth/login", json=login_data)
        
        assert response.status_code == 200
        token_data = response.json()
        assert "access_token" in token_data
        assert "token_type" in token_data
        assert token_data["token_type"] == "bearer"
        assert "expires_in" in token_data
        
        access_token = token_data["access_token"]
        
        # Step 3: Use token to access protected endpoint
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await test_client.get("/auth/me", headers=headers)
        
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["email"] == "test@example.com"
        assert user_data["role"] == "admin"
        assert user_data["is_active"] is True
    
    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, test_client: AsyncClient, test_auth_service: AuthService):
        """Test login with invalid credentials."""
        # Create a user
        await test_auth_service.create_user(
            email="test@example.com",
            password="correctpassword",
            role=UserRole.USER
        )
        
        # Test invalid email
        login_data = {
            "email": "wrong@example.com",
            "password": "correctpassword"
        }
        
        response = await test_client.post("/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]
        
        # Test invalid password
        login_data = {
            "email": "test@example.com",
            "password": "wrongpassword"
        }
        
        response = await test_client.post("/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_login_inactive_user(self, test_client: AsyncClient, test_auth_service: AuthService):
        """Test login with inactive user."""
        # Create and deactivate user
        user = await test_auth_service.create_user(
            email="test@example.com",
            password="testpassword123",
            role=UserRole.USER
        )
        await test_auth_service.deactivate_user(user.id)
        
        # Try to login
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        response = await test_client.post("/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "User account is inactive" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_token_validation(self, test_client: AsyncClient, test_auth_service: AuthService):
        """Test token validation and expiration."""
        # Create user and login
        await test_auth_service.create_user(
            email="test@example.com",
            password="testpassword123",
            role=UserRole.USER
        )
        
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        response = await test_client.post("/auth/login", json=login_data)
        token_data = response.json()
        access_token = token_data["access_token"]
        
        # Test valid token
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await test_client.get("/auth/me", headers=headers)
        
        assert response.status_code == 200
        
        # Test invalid token
        headers = {"Authorization": "Bearer invalid-token"}
        response = await test_client.get("/auth/me", headers=headers)
        
        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]
        
        # Test missing token
        response = await test_client.get("/auth/me")
        
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]
        
        # Test malformed token
        headers = {"Authorization": "InvalidFormat token"}
        response = await test_client.get("/auth/me", headers=headers)
        
        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_user_management_endpoints(self, test_client: AsyncClient, test_auth_service: AuthService):
        """Test user management endpoints."""
        # Create admin user
        admin = await test_auth_service.create_user(
            email="admin@example.com",
            password="adminpassword123",
            role=UserRole.ADMIN
        )
        
        # Login as admin
        login_data = {
            "email": "admin@example.com",
            "password": "adminpassword123"
        }
        
        response = await test_client.post("/auth/login", json=login_data)
        token_data = response.json()
        access_token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Test create user endpoint
        new_user_data = {
            "email": "newuser@example.com",
            "password": "newpassword123",
            "role": "user"
        }
        
        response = await test_client.post("/auth/users", json=new_user_data, headers=headers)
        
        assert response.status_code == 201
        user_data = response.json()
        assert user_data["email"] == "newuser@example.com"
        assert user_data["role"] == "user"
        assert user_data["is_active"] is True
        
        new_user_id = user_data["id"]
        
        # Test change user role
        role_change_data = {"role": "admin"}
        
        response = await test_client.put(f"/auth/users/{new_user_id}/role", json=role_change_data, headers=headers)
        
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["role"] == "admin"
        
        # Test deactivate user
        response = await test_client.put(f"/auth/users/{new_user_id}/deactivate", headers=headers)
        
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["is_active"] is False
        
        # Test activate user
        response = await test_client.put(f"/auth/users/{new_user_id}/activate", headers=headers)
        
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["is_active"] is True
        
        # Test list users
        response = await test_client.get("/auth/users", headers=headers)
        
        assert response.status_code == 200
        users_data = response.json()
        assert len(users_data) >= 2  # At least admin and new user
        emails = [user["email"] for user in users_data]
        assert "admin@example.com" in emails
        assert "newuser@example.com" in emails
    
    @pytest.mark.asyncio
    async def test_self_service_password_change(self, test_client: AsyncClient, test_auth_service: AuthService):
        """Test self-service password change."""
        # Create user
        user = await test_auth_service.create_user(
            email="test@example.com",
            password="oldpassword123",
            role=UserRole.USER
        )
        
        # Login
        login_data = {
            "email": "test@example.com",
            "password": "oldpassword123"
        }
        
        response = await test_client.post("/auth/login", json=login_data)
        token_data = response.json()
        access_token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Change password
        password_change_data = {
            "current_password": "oldpassword123",
            "new_password": "newpassword123"
        }
        
        response = await test_client.put("/auth/change-password", json=password_change_data, headers=headers)
        
        assert response.status_code == 200
        assert "Password changed successfully" in response.json()["message"]
        
        # Verify old password no longer works
        login_data = {
            "email": "test@example.com",
            "password": "oldpassword123"
        }
        
        response = await test_client.post("/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]
        
        # Verify new password works
        login_data = {
            "email": "test@example.com",
            "password": "newpassword123"
        }
        
        response = await test_client.post("/auth/login", json=login_data)
        
        assert response.status_code == 200
        assert "access_token" in response.json()
    
    @pytest.mark.asyncio
    async def test_password_change_invalid_current_password(self, test_client: AsyncClient, test_auth_service: AuthService):
        """Test password change with invalid current password."""
        # Create user and login
        await test_auth_service.create_user(
            email="test@example.com",
            password="correctpassword",
            role=UserRole.USER
        )
        
        login_data = {
            "email": "test@example.com",
            "password": "correctpassword"
        }
        
        response = await test_client.post("/auth/login", json=login_data)
        token_data = response.json()
        access_token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Try to change password with wrong current password
        password_change_data = {
            "current_password": "wrongpassword",
            "new_password": "newpassword123"
        }
        
        response = await test_client.put("/auth/change-password", json=password_change_data, headers=headers)
        
        assert response.status_code == 400
        assert "Invalid current password" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_unauthorized_access(self, test_client: AsyncClient, test_auth_service: AuthService):
        """Test unauthorized access to protected endpoints."""
        # Create regular user
        await test_auth_service.create_user(
            email="user@example.com",
            password="userpassword123",
            role=UserRole.USER
        )
        
        # Login as regular user
        login_data = {
            "email": "user@example.com",
            "password": "userpassword123"
        }
        
        response = await test_client.post("/auth/login", json=login_data)
        token_data = response.json()
        access_token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Try to access admin-only endpoint
        response = await test_client.get("/auth/users", headers=headers)
        
        assert response.status_code == 403
        assert "Insufficient permissions" in response.json()["detail"]
        
        # Try to create user without admin role
        new_user_data = {
            "email": "newuser@example.com",
            "password": "newpassword123",
            "role": "user"
        }
        
        response = await test_client.post("/auth/users", json=new_user_data, headers=headers)
        
        assert response.status_code == 403
        assert "Insufficient permissions" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_concurrent_login_attempts(self, test_client: AsyncClient, test_auth_service: AuthService):
        """Test concurrent login attempts."""
        # Create user
        await test_auth_service.create_user(
            email="test@example.com",
            password="testpassword123",
            role=UserRole.USER
        )
        
        # Make concurrent login attempts
        import asyncio
        
        async def login():
            login_data = {
                "email": "test@example.com",
                "password": "testpassword123"
            }
            return await test_client.post("/auth/login", json=login_data)
        
        tasks = [login() for _ in range(5)]
        responses = await asyncio.gather(*tasks)
        
        # All login attempts should succeed
        for response in responses:
            assert response.status_code == 200
            assert "access_token" in response.json()
        
        # All tokens should be valid
        for response in responses:
            token_data = response.json()
            access_token = token_data["access_token"]
            headers = {"Authorization": f"Bearer {access_token}"}
            
            me_response = await test_client.get("/auth/me", headers=headers)
            assert me_response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_user_creation_validation(self, test_client: AsyncClient, test_auth_service: AuthService):
        """Test user creation validation."""
        # Create admin user
        await test_auth_service.create_user(
            email="admin@example.com",
            password="adminpassword123",
            role=UserRole.ADMIN
        )
        
        # Login as admin
        login_data = {
            "email": "admin@example.com",
            "password": "adminpassword123"
        }
        
        response = await test_client.post("/auth/login", json=login_data)
        token_data = response.json()
        access_token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Test invalid email format
        invalid_user_data = {
            "email": "invalid-email",
            "password": "password123",
            "role": "user"
        }
        
        response = await test_client.post("/auth/users", json=invalid_user_data, headers=headers)
        
        assert response.status_code == 422  # Validation error
        
        # Test weak password
        weak_password_data = {
            "email": "user@example.com",
            "password": "123",  # Too short
            "role": "user"
        }
        
        response = await test_client.post("/auth/users", json=weak_password_data, headers=headers)
        
        assert response.status_code == 422  # Validation error
        
        # Test invalid role
        invalid_role_data = {
            "email": "user@example.com",
            "password": "password123",
            "role": "invalid_role"
        }
        
        response = await test_client.post("/auth/users", json=invalid_role_data, headers=headers)
        
        assert response.status_code == 422  # Validation error
        
        # Test duplicate email
        duplicate_email_data = {
            "email": "admin@example.com",  # Already exists
            "password": "password123",
            "role": "user"
        }
        
        response = await test_client.post("/auth/users", json=duplicate_email_data, headers=headers)
        
        assert response.status_code == 400
        assert "User with email admin@example.com already exists" in response.json()["detail"]
