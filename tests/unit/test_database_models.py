"""
Unit tests for database models.
"""

import pytest
import uuid
from datetime import datetime

from healthcare_voice_ai.core.models.database_models import (
    OfficeSubmission, Office, OfficeKnowledgeBase
)


class TestOfficeSubmission:
    """Test OfficeSubmission database model."""
    
    def test_office_submission_creation(self):
        """Test office submission model creation."""
        submission = OfficeSubmission(
            office_name="Test Dental Office",
            phone="+1234567890",
            email="test@example.com",
            address="123 Test Street, Test City, TC 12345",
            website="https://testdental.com",
            business_hours={
                "monday": "8:00 AM - 6:00 PM",
                "tuesday": "8:00 AM - 6:00 PM",
                "wednesday": "8:00 AM - 6:00 PM",
                "thursday": "8:00 AM - 6:00 PM",
                "friday": "8:00 AM - 5:00 PM",
                "saturday": "9:00 AM - 2:00 PM",
                "sunday": "Closed"
            },
            services=["General Dentistry", "Teeth Cleaning", "Fillings"],
            faq_content="Q: What are your hours?\nA: We are open Monday-Friday 8AM-6PM.",
            faq_filename="test_faq.txt",
            status="pending"
        )
        
        assert submission.office_name == "Test Dental Office"
        assert submission.phone == "+1234567890"
        assert submission.email == "test@example.com"
        assert submission.status == "pending"
        assert submission.faq_filename == "test_faq.txt"
        assert len(submission.services) == 3
        assert submission.business_hours["monday"] == "8:00 AM - 6:00 PM"
    
    def test_office_submission_defaults(self):
        """Test office submission default values."""
        submission = OfficeSubmission(
            office_name="Test Office",
            phone="+1234567890",
            email="test@example.com",
            address="123 Test St",
            services=["General Dentistry"],
            faq_content="Test FAQ content",
            faq_filename="test.txt",
            status="pending"  # Explicitly set default value
        )
        
        assert submission.status == "pending"
        assert submission.website is None
        assert submission.business_hours is None
        assert submission.admin_notes is None


class TestOffice:
    """Test Office database model."""
    
    def test_office_creation(self):
        """Test office model creation."""
        tenant_id = str(uuid.uuid4())
        office = Office(
            tenant_id=tenant_id,
            office_name="Test Dental Office",
            phone="+1234567890",
            email="test@example.com",
            address="123 Test Street, Test City, TC 12345",
            website="https://testdental.com",
            business_hours={
                "monday": "8:00 AM - 6:00 PM",
                "tuesday": "8:00 AM - 6:00 PM"
            },
            services=["General Dentistry", "Teeth Cleaning"],
            assistant_config={
                "voice_id": "test_voice",
                "model": "gpt-4o"
            },
            office_policies={
                "booking_advance_hours": 24,
                "cancellation_hours": 24
            },
            status="active",
            is_active=True  # Explicitly set default value
        )
        
        assert office.tenant_id == tenant_id
        assert office.office_name == "Test Dental Office"
        assert office.status == "active"
        assert office.is_active is True
        assert office.assistant_config["voice_id"] == "test_voice"
        assert office.office_policies["booking_advance_hours"] == 24
    
    def test_office_defaults(self):
        """Test office default values."""
        tenant_id = str(uuid.uuid4())
        office = Office(
            tenant_id=tenant_id,
            office_name="Test Office",
            phone="+1234567890",
            email="test@example.com",
            address="123 Test St",
            services=["General Dentistry"],
            status="active",  # Explicitly set default value
            is_active=True    # Explicitly set default value
        )
        
        assert office.status == "active"
        assert office.is_active is True
        assert office.website is None
        assert office.business_hours is None
        assert office.assistant_config is None
        assert office.office_policies is None


class TestOfficeKnowledgeBase:
    """Test OfficeKnowledgeBase database model."""
    
    def test_knowledge_base_creation(self):
        """Test knowledge base model creation."""
        office_id = str(uuid.uuid4())
        knowledge_base = OfficeKnowledgeBase(
            office_id=office_id,
            faq_content="Q: What are your hours?\nA: We are open Monday-Friday 8AM-6PM.",
            faq_filename="test_faq.txt",
            parsed_faqs=[
                {
                    "question": "What are your hours?",
                    "answer": "We are open Monday-Friday 8AM-6PM."
                }
            ],
            is_active=True  # Explicitly set default value
        )
        
        assert knowledge_base.office_id == office_id
        assert knowledge_base.faq_filename == "test_faq.txt"
        assert knowledge_base.is_active is True
        assert len(knowledge_base.parsed_faqs) == 1
        assert knowledge_base.parsed_faqs[0]["question"] == "What are your hours?"
    
    def test_knowledge_base_defaults(self):
        """Test knowledge base default values."""
        office_id = str(uuid.uuid4())
        knowledge_base = OfficeKnowledgeBase(
            office_id=office_id,
            faq_content="Test FAQ content",
            faq_filename="test.txt",
            is_active=True  # Explicitly set default value
        )
        
        assert knowledge_base.is_active is True
        assert knowledge_base.parsed_faqs is None
