"""
Integration tests for database operations.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

from healthcare_voice_ai.core.database import DatabaseOperations
from healthcare_voice_ai.core.models.database_models import OfficeSubmission, Office


class TestDatabaseOperations:
    """Test DatabaseOperations class."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        session = AsyncMock()
        session.add = MagicMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        session.execute = AsyncMock()
        return session
    
    @pytest.fixture
    def db_operations(self, mock_db_session):
        """Database operations instance with mocked session."""
        return DatabaseOperations(mock_db_session)
    
    @pytest.mark.asyncio
    async def test_create_office_submission(self, db_operations, mock_db_session):
        """Test creating office submission."""
        # Mock the database model
        mock_submission = OfficeSubmission(
            id="test-id",
            office_name="Test Office",
            phone="+1234567890",
            email="test@example.com",
            address="123 Test St",
            services=["General Dentistry"],
            faq_content="Test FAQ",
            faq_filename="test.txt",
            status="pending"
        )
        
        # Mock the database operations
        mock_db_session.add.return_value = None
        mock_db_session.refresh.return_value = None
        
        # Test data
        submission_data = {
            'office_name': 'Test Office',
            'phone': '+1234567890',
            'email': 'test@example.com',
            'address': '123 Test St',
            'services': ['General Dentistry'],
            'faq_content': 'Test FAQ',
            'faq_filename': 'test.txt',
            'status': 'pending'
        }
        
        # Mock the import and model creation
        with pytest.MonkeyPatch().context() as m:
            m.setattr('dental_voice_ai.core.models.database_models.OfficeSubmission', 
                     lambda **kwargs: mock_submission)
            
            result = await db_operations.create_office_submission(**submission_data)
            
            # Verify database operations were called
            mock_db_session.add.assert_called_once()
            mock_db_session.commit.assert_called_once()
            mock_db_session.refresh.assert_called_once()
            
            assert result == mock_submission
    
    @pytest.mark.asyncio
    async def test_get_office_submission(self, db_operations, mock_db_session):
        """Test getting office submission by ID."""
        # Mock the database result
        mock_submission = OfficeSubmission(
            id="test-id",
            office_name="Test Office",
            phone="+1234567890",
            email="test@example.com",
            address="123 Test St",
            services=["General Dentistry"],
            faq_content="Test FAQ",
            faq_filename="test.txt",
            status="pending"
        )
        
        # Mock the database query result
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_submission
        mock_db_session.execute.return_value = mock_result
        
        # Test getting submission
        result = await db_operations.get_office_submission("test-id")
        
        # Verify database operations were called
        mock_db_session.execute.assert_called_once()
        assert result == mock_submission
    
    @pytest.mark.asyncio
    async def test_get_office_submission_not_found(self, db_operations, mock_db_session):
        """Test getting non-existent office submission."""
        # Mock the database query result (not found)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        # Test getting non-existent submission
        result = await db_operations.get_office_submission("non-existent-id")
        
        # Verify database operations were called
        mock_db_session.execute.assert_called_once()
        assert result is None
    
    @pytest.mark.asyncio
    async def test_create_office(self, db_operations, mock_db_session):
        """Test creating office."""
        # Mock the database model
        mock_office = Office(
            id="test-id",
            tenant_id="tenant-123",
            office_name="Test Office",
            phone="+1234567890",
            email="test@example.com",
            address="123 Test St",
            services=["General Dentistry"],
            status="active"
        )
        
        # Mock the database operations
        mock_db_session.add.return_value = None
        mock_db_session.refresh.return_value = None
        
        # Test data
        office_data = {
            'tenant_id': 'tenant-123',
            'office_name': 'Test Office',
            'phone': '+1234567890',
            'email': 'test@example.com',
            'address': '123 Test St',
            'services': ['General Dentistry'],
            'status': 'active'
        }
        
        # Mock the import and model creation
        with pytest.MonkeyPatch().context() as m:
            m.setattr('dental_voice_ai.core.models.database_models.Office', 
                     lambda **kwargs: mock_office)
            
            result = await db_operations.create_office(**office_data)
            
            # Verify database operations were called
            mock_db_session.add.assert_called_once()
            mock_db_session.commit.assert_called_once()
            mock_db_session.refresh.assert_called_once()
            
            assert result == mock_office
    
    @pytest.mark.asyncio
    async def test_get_office_by_tenant_id(self, db_operations, mock_db_session):
        """Test getting office by tenant ID."""
        # Mock the database result
        mock_office = Office(
            id="test-id",
            tenant_id="tenant-123",
            office_name="Test Office",
            phone="+1234567890",
            email="test@example.com",
            address="123 Test St",
            services=["General Dentistry"],
            status="active"
        )
        
        # Mock the database query result
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_office
        mock_db_session.execute.return_value = mock_result
        
        # Test getting office by tenant ID
        result = await db_operations.get_office_by_tenant_id("tenant-123")
        
        # Verify database operations were called
        mock_db_session.execute.assert_called_once()
        assert result == mock_office
