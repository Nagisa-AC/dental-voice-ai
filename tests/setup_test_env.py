"""
Test environment setup script for Dental Voice AI.

This script sets up the test environment, creates test data, and ensures
all dependencies are properly configured for testing.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, Any
import json

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from healthcare_voice_ai.core.config import settings
from healthcare_voice_ai.core.database import init_database, close_database
from healthcare_voice_ai.core.cache import init_cache, close_cache
# DatabaseService removed - using direct database operations
from healthcare_voice_ai.core.services.auth_service import AuthService
from healthcare_voice_ai.core.models.database_models import Office, User, OfficeKnowledgeBase


class TestEnvironmentSetup:
    """Setup and manage test environment."""
    
    def __init__(self):
        self.db_service = None
        self.auth_service = None
        self.test_data = {}
    
    async def setup_database(self):
        """Setup test database."""
        print("🗄️ Setting up test database...")
        
        try:
            await init_database()
            self.db_service = DatabaseService()
            print("✅ Database initialized successfully")
        except Exception as e:
            print(f"❌ Database setup failed: {e}")
            raise
    
    async def setup_cache(self):
        """Setup test cache."""
        print("💾 Setting up test cache...")
        
        try:
            await init_cache()
            print("✅ Cache initialized successfully")
        except Exception as e:
            print(f"⚠️ Cache setup failed: {e}")
            # Cache failure shouldn't stop tests
    
    async def create_test_offices(self):
        """Create test offices."""
        print("🏢 Creating test offices...")
        
        test_offices = [
            {
                "tenant_id": "test_office_1",
                "name": "Test Dental Office 1",
                "email": "test1@dentaloffice.com",
                "phone": "+1234567890",
                "address": "123 Test St, Test City, TC 12345",
                "business_hours": {
                    "monday": {"start": "09:00", "end": "17:00"},
                    "tuesday": {"start": "09:00", "end": "17:00"},
                    "wednesday": {"start": "09:00", "end": "17:00"},
                    "thursday": {"start": "09:00", "end": "17:00"},
                    "friday": {"start": "09:00", "end": "17:00"},
                    "saturday": {"start": "09:00", "end": "13:00"},
                    "sunday": {"closed": True}
                },
                "services": ["General Dentistry", "Teeth Cleaning", "Cavity Fillings"],
                "timezone": "America/New_York"
            },
            {
                "tenant_id": "test_office_2",
                "name": "Test Dental Office 2",
                "email": "test2@dentaloffice.com",
                "phone": "+1234567891",
                "address": "456 Test Ave, Test City, TC 12346",
                "business_hours": {
                    "monday": {"start": "08:00", "end": "18:00"},
                    "tuesday": {"start": "08:00", "end": "18:00"},
                    "wednesday": {"start": "08:00", "end": "18:00"},
                    "thursday": {"start": "08:00", "end": "18:00"},
                    "friday": {"start": "08:00", "end": "18:00"},
                    "saturday": {"closed": True},
                    "sunday": {"closed": True}
                },
                "services": ["Orthodontics", "Cosmetic Dentistry", "Implants"],
                "timezone": "America/Los_Angeles"
            }
        ]
        
        for office_data in test_offices:
            try:
                office = await self.db_service.create_office(office_data)
                self.test_data[f"office_{office.tenant_id}"] = office
                print(f"✅ Created test office: {office.name}")
            except Exception as e:
                print(f"⚠️ Failed to create office {office_data['name']}: {e}")
    
    async def create_test_users(self):
        """Create test users."""
        print("👥 Creating test users...")
        
        self.auth_service = AuthService()
        
        test_users = [
            {
                "email": "admin@testoffice1.com",
                "password": "testpassword123",
                "role": "admin",
                "tenant_id": "test_office_1",
                "first_name": "Test",
                "last_name": "Admin"
            },
            {
                "email": "user@testoffice1.com",
                "password": "testpassword123",
                "role": "user",
                "tenant_id": "test_office_1",
                "first_name": "Test",
                "last_name": "User"
            },
            {
                "email": "admin@testoffice2.com",
                "password": "testpassword123",
                "role": "admin",
                "tenant_id": "test_office_2",
                "first_name": "Test",
                "last_name": "Admin2"
            }
        ]
        
        for user_data in test_users:
            try:
                user = await self.auth_service.create_user(user_data)
                self.test_data[f"user_{user.email}"] = user
                print(f"✅ Created test user: {user.email}")
            except Exception as e:
                print(f"⚠️ Failed to create user {user_data['email']}: {e}")
    
    async def create_test_knowledge_bases(self):
        """Create test knowledge bases."""
        print("📚 Creating test knowledge bases...")
        
        test_knowledge_bases = [
            {
                "tenant_id": "test_office_1",
                "content": """
# Test Dental Office 1 - FAQ

## General Questions

**Q: What are your office hours?**
A: We are open Monday through Friday from 9:00 AM to 5:00 PM, and Saturday from 9:00 AM to 1:00 PM. We are closed on Sundays.

**Q: Do you accept insurance?**
A: Yes, we accept most major dental insurance plans. Please call us to verify your coverage.

**Q: How do I schedule an appointment?**
A: You can schedule an appointment by calling us at (123) 456-7890 or through our online booking system.

## Services

**Q: What services do you offer?**
A: We offer general dentistry, teeth cleaning, and cavity fillings.

**Q: Do you offer emergency services?**
A: Yes, we provide emergency dental services. Please call our emergency line for urgent care.
"""
            },
            {
                "tenant_id": "test_office_2",
                "content": """
# Test Dental Office 2 - FAQ

## General Questions

**Q: What are your office hours?**
A: We are open Monday through Friday from 8:00 AM to 6:00 PM. We are closed on weekends.

**Q: Do you accept insurance?**
A: Yes, we accept most major dental insurance plans and also offer payment plans.

**Q: How do I schedule an appointment?**
A: You can schedule an appointment by calling us at (123) 456-7891 or through our online portal.

## Services

**Q: What services do you offer?**
A: We specialize in orthodontics, cosmetic dentistry, and dental implants.

**Q: Do you offer consultations?**
A: Yes, we offer free consultations for new patients. Please call to schedule.
"""
            }
        ]
        
        for kb_data in test_knowledge_bases:
            try:
                kb = await self.db_service.create_office_knowledge_base(kb_data)
                self.test_data[f"kb_{kb.tenant_id}"] = kb
                print(f"✅ Created knowledge base for: {kb.tenant_id}")
            except Exception as e:
                print(f"⚠️ Failed to create knowledge base for {kb_data['tenant_id']}: {e}")
    
    async def create_test_appointments(self):
        """Create test appointments."""
        print("📅 Creating test appointments...")
        
        test_appointments = [
            {
                "tenant_id": "test_office_1",
                "patient_name": "John Doe",
                "patient_phone": "+1234567892",
                "patient_email": "john.doe@email.com",
                "appointment_date": "2024-01-15",
                "appointment_time": "10:00",
                "service": "Teeth Cleaning",
                "duration": 60,
                "notes": "Regular cleaning appointment"
            },
            {
                "tenant_id": "test_office_1",
                "patient_name": "Jane Smith",
                "patient_phone": "+1234567893",
                "patient_email": "jane.smith@email.com",
                "appointment_date": "2024-01-16",
                "appointment_time": "14:00",
                "service": "Cavity Filling",
                "duration": 90,
                "notes": "Filling for tooth #14"
            },
            {
                "tenant_id": "test_office_2",
                "patient_name": "Bob Johnson",
                "patient_phone": "+1234567894",
                "patient_email": "bob.johnson@email.com",
                "appointment_date": "2024-01-17",
                "appointment_time": "09:00",
                "service": "Orthodontic Consultation",
                "duration": 120,
                "notes": "Initial consultation for braces"
            }
        ]
        
        for appointment_data in test_appointments:
            try:
                appointment = await self.db_service.create_appointment(appointment_data)
                self.test_data[f"appointment_{appointment.id}"] = appointment
                print(f"✅ Created test appointment: {appointment.patient_name}")
            except Exception as e:
                print(f"⚠️ Failed to create appointment for {appointment_data['patient_name']}: {e}")
    
    async def save_test_data(self):
        """Save test data for use in tests."""
        print("💾 Saving test data...")
        
        # Create results directory
        results_dir = Path("tests/results")
        results_dir.mkdir(exist_ok=True)
        
        # Save test data
        test_data_file = results_dir / "test_data.json"
        
        # Convert test data to JSON-serializable format
        serializable_data = {}
        for key, value in self.test_data.items():
            if hasattr(value, '__dict__'):
                serializable_data[key] = value.__dict__
            else:
                serializable_data[key] = str(value)
        
        with open(test_data_file, "w") as f:
            json.dump(serializable_data, f, indent=2, default=str)
        
        print(f"✅ Test data saved to {test_data_file}")
    
    async def cleanup_test_data(self):
        """Clean up test data."""
        print("🧹 Cleaning up test data...")
        
        try:
            # Clean up test data from database
            if self.db_service:
                # Delete test appointments
                for key, value in self.test_data.items():
                    if key.startswith("appointment_"):
                        try:
                            await self.db_service.delete_appointment(value.id)
                        except Exception as e:
                            print(f"⚠️ Failed to delete appointment {value.id}: {e}")
                
                # Delete test knowledge bases
                for key, value in self.test_data.items():
                    if key.startswith("kb_"):
                        try:
                            await self.db_service.delete_office_knowledge_base(value.tenant_id)
                        except Exception as e:
                            print(f"⚠️ Failed to delete knowledge base for {value.tenant_id}: {e}")
                
                # Delete test users
                for key, value in self.test_data.items():
                    if key.startswith("user_"):
                        try:
                            await self.db_service.delete_user(value.id)
                        except Exception as e:
                            print(f"⚠️ Failed to delete user {value.email}: {e}")
                
                # Delete test offices
                for key, value in self.test_data.items():
                    if key.startswith("office_"):
                        try:
                            await self.db_service.delete_office(value.tenant_id)
                        except Exception as e:
                            print(f"⚠️ Failed to delete office {value.tenant_id}: {e}")
            
            print("✅ Test data cleaned up")
        except Exception as e:
            print(f"⚠️ Cleanup failed: {e}")
    
    async def setup_complete_environment(self):
        """Setup complete test environment."""
        print("🚀 Setting up complete test environment...")
        
        try:
            # Setup infrastructure
            await self.setup_database()
            await self.setup_cache()
            
            # Create test data
            await self.create_test_offices()
            await self.create_test_users()
            await self.create_test_knowledge_bases()
            await self.create_test_appointments()
            
            # Save test data
            await self.save_test_data()
            
            print("✅ Test environment setup complete!")
            print(f"📊 Created {len(self.test_data)} test objects")
            
        except Exception as e:
            print(f"❌ Test environment setup failed: {e}")
            raise
    
    async def teardown_environment(self):
        """Teardown test environment."""
        print("🧹 Tearing down test environment...")
        
        try:
            await self.cleanup_test_data()
            await close_database()
            await close_cache()
            print("✅ Test environment torn down")
        except Exception as e:
            print(f"⚠️ Teardown failed: {e}")


async def main():
    """Main setup entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Dental Voice AI Test Environment Setup")
    parser.add_argument("--cleanup", action="store_true",
                       help="Clean up existing test data")
    parser.add_argument("--teardown", action="store_true",
                       help="Teardown test environment")
    
    args = parser.parse_args()
    
    setup = TestEnvironmentSetup()
    
    try:
        if args.teardown:
            await setup.teardown_environment()
        elif args.cleanup:
            await setup.setup_database()
            await setup.cleanup_test_data()
        else:
            await setup.setup_complete_environment()
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
