"""
Unit tests for AuthService.

Tests user authentication, password hashing, and user management functionality.
"""

import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from healthcare_voice_ai.core.services.auth_service import AuthService
from healthcare_voice_ai.core.models.database_models import User, UserRole
from healthcare_voice_ai.core.exceptions import AuthenticationError, UserNotFoundError


class TestAuthService:
    """Test cases for AuthService."""
    
    @pytest_asyncio.fixture
    async def auth_service(self, test_db_session: AsyncSession) -> AuthService:
        """Create AuthService instance for testing."""
        return AuthService(test_db_session)
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, auth_service: AuthService):
        """Test successful user creation."""
        # Act
        user = await auth_service.create_user(
            email="test@example.com",
            password="testpassword123",
            role=UserRole.ADMIN
        )
        
        # Assert
        assert user is not None
        assert user.email == "test@example.com"
        assert user.role == UserRole.ADMIN
        assert user.is_active is True
        assert user.password_hash != "testpassword123"  # Should be hashed
        assert user.created_at is not None
        assert user.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, auth_service: AuthService):
        """Test user creation with duplicate email fails."""
        # Arrange
        await auth_service.create_user(
            email="test@example.com",
            password="testpassword123",
            role=UserRole.ADMIN
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="User with email test@example.com already exists"):
            await auth_service.create_user(
                email="test@example.com",
                password="anotherpassword",
                role=UserRole.USER
            )
    
    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, auth_service: AuthService):
        """Test successful user authentication."""
        # Arrange
        await auth_service.create_user(
            email="test@example.com",
            password="testpassword123",
            role=UserRole.ADMIN
        )
        
        # Act
        user = await auth_service.authenticate_user("test@example.com", "testpassword123")
        
        # Assert
        assert user is not None
        assert user.email == "test@example.com"
        assert user.role == UserRole.ADMIN
    
    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_email(self, auth_service: AuthService):
        """Test authentication with invalid email."""
        # Act & Assert
        with pytest.raises(AuthenticationError, match="Invalid email or password"):
            await auth_service.authenticate_user("nonexistent@example.com", "password")
    
    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_password(self, auth_service: AuthService):
        """Test authentication with invalid password."""
        # Arrange
        await auth_service.create_user(
            email="test@example.com",
            password="correctpassword",
            role=UserRole.ADMIN
        )
        
        # Act & Assert
        with pytest.raises(AuthenticationError, match="Invalid email or password"):
            await auth_service.authenticate_user("test@example.com", "wrongpassword")
    
    @pytest.mark.asyncio
    async def test_authenticate_user_inactive_user(self, auth_service: AuthService):
        """Test authentication with inactive user."""
        # Arrange
        user = await auth_service.create_user(
            email="test@example.com",
            password="testpassword123",
            role=UserRole.ADMIN
        )
        await auth_service.deactivate_user(user.id)
        
        # Act & Assert
        with pytest.raises(AuthenticationError, match="User account is inactive"):
            await auth_service.authenticate_user("test@example.com", "testpassword123")
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self, auth_service: AuthService):
        """Test successful user retrieval by ID."""
        # Arrange
        created_user = await auth_service.create_user(
            email="test@example.com",
            password="testpassword123",
            role=UserRole.ADMIN
        )
        
        # Act
        user = await auth_service.get_user_by_id(created_user.id)
        
        # Assert
        assert user is not None
        assert user.id == created_user.id
        assert user.email == "test@example.com"
        assert user.role == UserRole.ADMIN
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, auth_service: AuthService):
        """Test user retrieval with non-existent ID."""
        # Act & Assert
        with pytest.raises(UserNotFoundError, match="User not found"):
            await auth_service.get_user_by_id("nonexistent-id")
    
    @pytest.mark.asyncio
    async def test_get_user_by_email_success(self, auth_service: AuthService):
        """Test successful user retrieval by email."""
        # Arrange
        await auth_service.create_user(
            email="test@example.com",
            password="testpassword123",
            role=UserRole.ADMIN
        )
        
        # Act
        user = await auth_service.get_user_by_email("test@example.com")
        
        # Assert
        assert user is not None
        assert user.email == "test@example.com"
        assert user.role == UserRole.ADMIN
    
    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, auth_service: AuthService):
        """Test user retrieval with non-existent email."""
        # Act & Assert
        with pytest.raises(UserNotFoundError, match="User not found"):
            await auth_service.get_user_by_email("nonexistent@example.com")
    
    @pytest.mark.asyncio
    async def test_change_password_success(self, auth_service: AuthService):
        """Test successful password change."""
        # Arrange
        user = await auth_service.create_user(
            email="test@example.com",
            password="oldpassword",
            role=UserRole.ADMIN
        )
        old_hash = user.password_hash
        
        # Act
        await auth_service.change_password(user.id, "oldpassword", "newpassword123")
        
        # Assert
        updated_user = await auth_service.get_user_by_id(user.id)
        assert updated_user.password_hash != old_hash
        
        # Verify new password works
        authenticated_user = await auth_service.authenticate_user("test@example.com", "newpassword123")
        assert authenticated_user is not None
    
    @pytest.mark.asyncio
    async def test_change_password_invalid_old_password(self, auth_service: AuthService):
        """Test password change with invalid old password."""
        # Arrange
        user = await auth_service.create_user(
            email="test@example.com",
            password="correctpassword",
            role=UserRole.ADMIN
        )
        
        # Act & Assert
        with pytest.raises(AuthenticationError, match="Invalid current password"):
            await auth_service.change_password(user.id, "wrongpassword", "newpassword123")
    
    @pytest.mark.asyncio
    async def test_change_user_role_success(self, auth_service: AuthService):
        """Test successful user role change."""
        # Arrange
        user = await auth_service.create_user(
            email="test@example.com",
            password="testpassword123",
            role=UserRole.USER
        )
        
        # Act
        await auth_service.change_user_role(user.id, UserRole.ADMIN)
        
        # Assert
        updated_user = await auth_service.get_user_by_id(user.id)
        assert updated_user.role == UserRole.ADMIN
    
    @pytest.mark.asyncio
    async def test_deactivate_user_success(self, auth_service: AuthService):
        """Test successful user deactivation."""
        # Arrange
        user = await auth_service.create_user(
            email="test@example.com",
            password="testpassword123",
            role=UserRole.ADMIN
        )
        
        # Act
        await auth_service.deactivate_user(user.id)
        
        # Assert
        updated_user = await auth_service.get_user_by_id(user.id)
        assert updated_user.is_active is False
    
    @pytest.mark.asyncio
    async def test_activate_user_success(self, auth_service: AuthService):
        """Test successful user activation."""
        # Arrange
        user = await auth_service.create_user(
            email="test@example.com",
            password="testpassword123",
            role=UserRole.ADMIN
        )
        await auth_service.deactivate_user(user.id)
        
        # Act
        await auth_service.activate_user(user.id)
        
        # Assert
        updated_user = await auth_service.get_user_by_id(user.id)
        assert updated_user.is_active is True
    
    @pytest.mark.asyncio
    async def test_list_users_success(self, auth_service: AuthService):
        """Test successful user listing."""
        # Arrange
        await auth_service.create_user(
            email="user1@example.com",
            password="password1",
            role=UserRole.USER
        )
        await auth_service.create_user(
            email="user2@example.com",
            password="password2",
            role=UserRole.ADMIN
        )
        
        # Act
        users = await auth_service.list_users()
        
        # Assert
        assert len(users) == 2
        emails = [user.email for user in users]
        assert "user1@example.com" in emails
        assert "user2@example.com" in emails
    
    @pytest.mark.asyncio
    async def test_password_hashing_security(self, auth_service: AuthService):
        """Test that password hashing is secure."""
        # Arrange
        password = "testpassword123"
        
        # Act
        user1 = await auth_service.create_user(
            email="user1@example.com",
            password=password,
            role=UserRole.USER
        )
        user2 = await auth_service.create_user(
            email="user2@example.com",
            password=password,
            role=UserRole.USER
        )
        
        # Assert
        # Same password should produce different hashes (due to salt)
        assert user1.password_hash != user2.password_hash
        assert user1.password_hash != password
        assert user2.password_hash != password
        
        # Both should authenticate successfully
        auth1 = await auth_service.authenticate_user("user1@example.com", password)
        auth2 = await auth_service.authenticate_user("user2@example.com", password)
        assert auth1 is not None
        assert auth2 is not None
    
    @pytest.mark.asyncio
    async def test_user_creation_timestamps(self, auth_service: AuthService):
        """Test that user creation sets proper timestamps."""
        # Act
        user = await auth_service.create_user(
            email="test@example.com",
            password="testpassword123",
            role=UserRole.ADMIN
        )
        
        # Assert
        assert user.created_at is not None
        assert user.updated_at is not None
        assert user.created_at == user.updated_at  # Should be same on creation
    
    @pytest.mark.asyncio
    async def test_user_update_timestamps(self, auth_service: AuthService):
        """Test that user updates modify the updated_at timestamp."""
        # Arrange
        user = await auth_service.create_user(
            email="test@example.com",
            password="testpassword123",
            role=UserRole.USER
        )
        original_updated_at = user.updated_at
        
        # Act
        await auth_service.change_user_role(user.id, UserRole.ADMIN)
        
        # Assert
        updated_user = await auth_service.get_user_by_id(user.id)
        assert updated_user.updated_at > original_updated_at
        assert updated_user.created_at == user.created_at  # Should not change
