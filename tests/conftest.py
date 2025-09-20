"""
Pytest configuration and fixtures for Dental Voice AI tests.

Provides common test fixtures, database setup, and test utilities
for unit, integration, and end-to-end testing.
"""

import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient

from healthcare_voice_ai.main import app
from healthcare_voice_ai.core.database import Base, get_async_db
from healthcare_voice_ai.core.models.database_models import Clinic
from healthcare_voice_ai.core.models.auth_models import User
from healthcare_voice_ai.core.auth import UserRole
from healthcare_voice_ai.core.models.office import ClinicStatus
from healthcare_voice_ai.core.services.auth_service import AuthService
# DatabaseService removed - using direct database operations
from healthcare_voice_ai.core.config import settings


# Test Database Configuration
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_db_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_db_session(test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def test_auth_service(test_db_session) -> AuthService:
    """Create test auth service."""
    return AuthService(test_db_session)




@pytest_asyncio.fixture(scope="function")
async def test_user(test_auth_service) -> User:
    """Create a test user."""
    user = await test_auth_service.create_user(
        email="test@example.com",
        password="testpassword123",
        role=UserRole.ADMIN
    )
    return user


@pytest_asyncio.fixture(scope="function")
async def test_clinic(test_db_session) -> Clinic:
    """Create a test clinic."""
    from healthcare_voice_ai.core.services.orm_service import ORMService
    orm_service = ORMService(test_db_session)
    
    clinic_data = {
        "tenant_id": "test-tenant-001",
        "name": "Test Dental Office",
        "industry_type": "dental",
        "contact_info": {
            "phone": "+1234567890",
            "email": "office@testdental.com",
            "address": "123 Test Street, Test City, TC 12345"
        },
        "business_hours": {
            "monday": "9:00 AM - 5:00 PM",
            "tuesday": "9:00 AM - 5:00 PM",
            "wednesday": "9:00 AM - 5:00 PM",
            "thursday": "9:00 AM - 5:00 PM",
            "friday": "9:00 AM - 5:00 PM",
            "saturday": "Closed",
            "sunday": "Closed"
        },
        "services": ["General Dentistry", "Teeth Cleaning", "Fillings"],
        "status": "active"
    }
    
    clinic = await orm_service.create(Clinic, **clinic_data)
    return clinic


@pytest_asyncio.fixture(scope="function")
async def test_client(test_db_session) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with database override."""
    
    async def override_get_async_db():
        yield test_db_session
    
    app.dependency_overrides[get_async_db] = override_get_async_db
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def authenticated_client(test_client, test_user) -> AsyncGenerator[AsyncClient, None]:
    """Create authenticated test client."""
    # Login to get access token
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    response = await test_client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    
    token_data = response.json()
    access_token = token_data["access_token"]
    
    # Set authorization header
    test_client.headers.update({"Authorization": f"Bearer {access_token}"})
    
    yield test_client


@pytest.fixture(scope="function")
def sample_faq_content() -> str:
    """Sample FAQ content for testing."""
    return """
Q: What are your office hours?
A: We are open Monday through Friday from 9:00 AM to 5:00 PM. We are closed on weekends.

Q: Do you accept insurance?
A: Yes, we accept most major dental insurance plans. Please contact us to verify your specific plan.

Q: How much does a cleaning cost?
A: A routine cleaning typically costs between $100-$200, depending on your insurance coverage.

Q: Do you offer emergency services?
A: Yes, we provide emergency dental services. Please call our office for immediate assistance.

Q: What should I bring to my first appointment?
A: Please bring your insurance card, photo ID, and any previous dental records if available.
"""


@pytest.fixture(scope="function")
def sample_office_data() -> dict:
    """Sample office data for testing."""
    return {
        "office_name": "Test Dental Practice",
        "phone": "+1234567890",
        "email": "info@testdental.com",
        "address": "123 Main Street, Test City, TC 12345",
        "website": "https://testdental.com",
        "monday_hours": "9:00 AM - 5:00 PM",
        "tuesday_hours": "9:00 AM - 5:00 PM",
        "wednesday_hours": "9:00 AM - 5:00 PM",
        "thursday_hours": "9:00 AM - 5:00 PM",
        "friday_hours": "9:00 AM - 5:00 PM",
        "saturday_hours": "Closed",
        "sunday_hours": "Closed",
        "services": "General Dentistry,Teeth Cleaning,Fillings,Crowns",
        "preferred_voice": "cgSgspJ2msm6clMCkdW9"
    }


@pytest.fixture(scope="function")
def sample_appointment_data() -> dict:
    """Sample appointment data for testing."""
    return {
        "patient_name": "John Doe",
        "patient_phone": "+1987654321",
        "patient_email": "john.doe@example.com",
        "preferred_date": "2024-02-15",
        "preferred_time": "10:00",
        "service_type": "Teeth Cleaning",
        "duration_minutes": 60,
        "notes": "Regular cleaning appointment"
    }


# Test Utilities
class TestUtils:
    """Utility functions for testing."""
    
    @staticmethod
    def assert_valid_uuid(uuid_string: str) -> bool:
        """Assert that a string is a valid UUID."""
        import uuid
        try:
            uuid.UUID(uuid_string)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def assert_valid_email(email: str) -> bool:
        """Assert that a string is a valid email."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def assert_valid_phone(phone: str) -> bool:
        """Assert that a string is a valid phone number."""
        import re
        # Basic phone validation - can be enhanced
        pattern = r'^\+?[\d\s\-\(\)]+$'
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def assert_valid_datetime(datetime_string: str) -> bool:
        """Assert that a string is a valid ISO datetime."""
        from datetime import datetime
        try:
            datetime.fromisoformat(datetime_string.replace('Z', '+00:00'))
            return True
        except ValueError:
            return False


@pytest.fixture(scope="function")
def test_utils() -> TestUtils:
    """Provide test utilities."""
    return TestUtils()


# Mock External Services
@pytest.fixture(scope="function")
def mock_vapi_service():
    """Mock VAPI service for testing."""
    class MockVAPIService:
        def __init__(self):
            self.assistants = {}
            self.phone_numbers = {}
            self.calls = {}
            self.assistant_counter = 0
            self.phone_counter = 0
            self.call_counter = 0
        
        async def create_dental_assistant(self, name: str = "Dental Assistant") -> str:
            self.assistant_counter += 1
            assistant_id = f"assistant_{self.assistant_counter}"
            self.assistants[assistant_id] = {
                "id": assistant_id,
                "name": name,
                "created_at": "2024-01-01T00:00:00Z"
            }
            return assistant_id
        
        async def create_phone_number(self, assistant_id: str, area_code: str = "415") -> str:
            self.phone_counter += 1
            phone_id = f"phone_{self.phone_counter}"
            self.phone_numbers[phone_id] = {
                "id": phone_id,
                "assistant_id": assistant_id,
                "number": f"+1{area_code}555{self.phone_counter:04d}",
                "area_code": area_code
            }
            return phone_id
        
        async def create_call(self, assistant_id: str, phone_number_id: str, customer_phone: str) -> dict:
            self.call_counter += 1
            call_id = f"call_{self.call_counter}"
            self.calls[call_id] = {
                "id": call_id,
                "assistant_id": assistant_id,
                "phone_number_id": phone_number_id,
                "customer_phone": customer_phone,
                "status": "initiated",
                "created_at": "2024-01-01T00:00:00Z"
            }
            return self.calls[call_id]
    
    return MockVAPIService()


@pytest.fixture(scope="function")
def mock_google_calendar_service():
    """Mock Google Calendar service for testing."""
    class MockGoogleCalendarService:
        def __init__(self):
            self.events = {}
            self.event_counter = 0
        
        async def create_appointment(self, appointment_data: dict) -> dict:
            self.event_counter += 1
            event_id = f"event_{self.event_counter}"
            self.events[event_id] = {
                "id": event_id,
                "summary": appointment_data.get("service_type", "Dental Appointment"),
                "start": {"dateTime": f"{appointment_data.get('preferred_date')}T{appointment_data.get('preferred_time', '10:00')}:00Z"},
                "end": {"dateTime": f"{appointment_data.get('preferred_date')}T{appointment_data.get('preferred_time', '11:00')}:00Z"},
                "status": "confirmed"
            }
            return self.events[event_id]
        
        async def get_availability(self, start_date: str, end_date: str) -> list:
            # Return mock availability slots
            return [
                {
                    "start_time": f"{start_date}T09:00:00Z",
                    "end_time": f"{start_date}T09:30:00Z"
                },
                {
                    "start_time": f"{start_date}T10:00:00Z",
                    "end_time": f"{start_date}T10:30:00Z"
                }
            ]
    
    return MockGoogleCalendarService()


# Test Configuration
@pytest.fixture(scope="session", autouse=True)
def configure_test_settings():
    """Configure test settings."""
    # Override settings for testing
    settings.ENVIRONMENT = "testing"
    settings.DEBUG = True
    settings.LOG_LEVEL = "WARNING"  # Reduce log noise during tests
    yield
    # Reset settings after tests
    settings.ENVIRONMENT = "development"
    settings.DEBUG = False
    settings.LOG_LEVEL = "INFO"
