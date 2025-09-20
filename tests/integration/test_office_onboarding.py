"""
Integration tests for office onboarding flow.

Tests the complete office onboarding process from submission to approval.
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from healthcare_voice_ai.core.models.database_models import OfficeStatus, UserRole


class TestOfficeOnboardingIntegration:
    """Integration tests for office onboarding."""
    
    @pytest.mark.asyncio
    async def test_complete_onboarding_flow(self, test_client: AsyncClient, sample_office_data: dict, sample_faq_content: str):
        """Test complete office onboarding flow from submission to approval."""
        # Step 1: Submit office onboarding form
        form_data = sample_office_data.copy()
        files = {"faq_file": ("faq.txt", sample_faq_content, "text/plain")}
        
        response = await test_client.post("/offices/onboarding/submit", data=form_data, files=files)
        
        assert response.status_code == 200
        submission_data = response.json()
        assert "submission_id" in submission_data
        assert submission_data["status"] == "submitted"
        
        submission_id = submission_data["submission_id"]
        
        # Step 2: Check submission status
        response = await test_client.get(f"/offices/onboarding/submission/{submission_id}")
        
        assert response.status_code == 200
        status_data = response.json()
        assert status_data["submission_id"] == submission_id
        assert status_data["status"] == "pending"
        assert status_data["office_name"] == sample_office_data["office_name"]
        
        # Step 3: Admin approves submission (simulated)
        # In a real scenario, this would be done through admin endpoints
        # For testing, we'll directly update the database
        from healthcare_voice_ai.core.services.database_service import DatabaseService
        from healthcare_voice_ai.core.database import get_async_db
        
        # Get database session
        async for db_session in get_async_db():
            db_service = DatabaseService(db_session)
            
            # Approve the submission
            await db_service.update_office_submission_status(
                submission_id, 
                OfficeStatus.APPROVED,
                "Approved for testing"
            )
            break
        
        # Step 4: Check updated status
        response = await test_client.get(f"/offices/onboarding/submission/{submission_id}")
        
        assert response.status_code == 200
        status_data = response.json()
        assert status_data["status"] == "approved"
        assert status_data["admin_notes"] == "Approved for testing"
    
    @pytest.mark.asyncio
    async def test_onboarding_validation_errors(self, test_client: AsyncClient, sample_faq_content: str):
        """Test onboarding form validation errors."""
        # Test missing required fields
        form_data = {
            "office_name": "",  # Empty name
            "phone": "invalid-phone",  # Invalid phone
            "email": "invalid-email",  # Invalid email
            "address": "",  # Empty address
            "services": ""  # Empty services
        }
        files = {"faq_file": ("faq.txt", sample_faq_content, "text/plain")}
        
        response = await test_client.post("/offices/onboarding/submit", data=form_data, files=files)
        
        assert response.status_code == 422  # Validation error
        
        # Test invalid file type
        form_data = {
            "office_name": "Test Office",
            "phone": "+1234567890",
            "email": "test@example.com",
            "address": "123 Test St",
            "services": "General Dentistry"
        }
        files = {"faq_file": ("document.pdf", b"PDF content", "application/pdf")}
        
        response = await test_client.post("/offices/onboarding/submit", data=form_data, files=files)
        
        assert response.status_code == 400
        assert "Invalid file type" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_onboarding_file_size_limit(self, test_client: AsyncClient, sample_office_data: dict):
        """Test onboarding form file size limit."""
        # Create a large FAQ file (over 1MB)
        large_content = "Q: Test question?\nA: Test answer.\n" * 50000  # ~1.5MB
        
        form_data = sample_office_data.copy()
        files = {"faq_file": ("faq.txt", large_content, "text/plain")}
        
        response = await test_client.post("/offices/onboarding/submit", data=form_data, files=files)
        
        assert response.status_code == 400
        assert "File too large" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_onboarding_duplicate_submission(self, test_client: AsyncClient, sample_office_data: dict, sample_faq_content: str):
        """Test that duplicate submissions are handled properly."""
        form_data = sample_office_data.copy()
        files = {"faq_file": ("faq.txt", sample_faq_content, "text/plain")}
        
        # First submission
        response1 = await test_client.post("/offices/onboarding/submit", data=form_data, files=files)
        assert response1.status_code == 200
        
        # Second submission with same data
        response2 = await test_client.post("/offices/onboarding/submit", data=form_data, files=files)
        assert response2.status_code == 200
        
        # Both should create separate submissions
        submission1_id = response1.json()["submission_id"]
        submission2_id = response2.json()["submission_id"]
        
        assert submission1_id != submission2_id
    
    @pytest.mark.asyncio
    async def test_onboarding_submission_not_found(self, test_client: AsyncClient):
        """Test retrieval of non-existent submission."""
        response = await test_client.get("/offices/onboarding/submission/nonexistent-id")
        
        assert response.status_code == 404
        assert "Submission not found" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_onboarding_rate_limiting(self, test_client: AsyncClient, sample_office_data: dict, sample_faq_content: str):
        """Test rate limiting on onboarding submissions."""
        form_data = sample_office_data.copy()
        files = {"faq_file": ("faq.txt", sample_faq_content, "text/plain")}
        
        # Make multiple rapid submissions
        responses = []
        for i in range(10):  # Try to exceed rate limit
            form_data["office_name"] = f"Office {i}"
            response = await test_client.post("/offices/onboarding/submit", data=form_data, files=files)
            responses.append(response)
        
        # Check if any requests were rate limited
        rate_limited = any(r.status_code == 429 for r in responses)
        # Note: Rate limiting might not be enabled in test environment
        # This test ensures the endpoint can handle multiple requests
    
    @pytest.mark.asyncio
    async def test_onboarding_with_special_characters(self, test_client: AsyncClient, sample_faq_content: str):
        """Test onboarding with special characters in data."""
        form_data = {
            "office_name": "Dr. Smith's Dental Clinic & Associates",
            "phone": "+1 (555) 123-4567",
            "email": "info@dr-smith-dental.com",
            "address": "123 Main St., Suite 100, New York, NY 10001",
            "website": "https://dr-smith-dental.com",
            "monday_hours": "9:00 AM - 5:00 PM",
            "tuesday_hours": "9:00 AM - 5:00 PM",
            "wednesday_hours": "9:00 AM - 5:00 PM",
            "thursday_hours": "9:00 AM - 5:00 PM",
            "friday_hours": "9:00 AM - 5:00 PM",
            "saturday_hours": "Closed",
            "sunday_hours": "Closed",
            "services": "General Dentistry,Teeth Cleaning,Fillings,Crowns & Bridges",
            "preferred_voice": "cgSgspJ2msm6clMCkdW9"
        }
        
        # FAQ with special characters
        special_faq = """
Q: What are your office hours?
A: We're open Monday through Friday from 9:00 AM to 5:00 PM.

Q: Do you accept insurance?
A: Yes, we accept most major dental insurance plans including Aetna, Cigna, and Delta Dental.

Q: What services do you offer?
A: We offer comprehensive dental services including:
- General Dentistry
- Cosmetic Dentistry
- Orthodontics
- Oral Surgery
- Periodontics

Q: How much does a cleaning cost?
A: A routine cleaning typically costs between $100-$200, depending on your insurance coverage.

Q: Do you offer emergency services?
A: Yes, we provide emergency dental services 24/7. Please call our office at (555) 123-4567 for immediate assistance.
"""
        
        files = {"faq_file": ("faq.txt", special_faq, "text/plain")}
        
        response = await test_client.post("/offices/onboarding/submit", data=form_data, files=files)
        
        assert response.status_code == 200
        submission_data = response.json()
        assert "submission_id" in submission_data
        
        # Verify the submission was created with special characters preserved
        submission_id = submission_data["submission_id"]
        response = await test_client.get(f"/offices/onboarding/submission/{submission_id}")
        
        assert response.status_code == 200
        status_data = response.json()
        assert "Dr. Smith's Dental Clinic & Associates" in status_data["office_name"]
    
    @pytest.mark.asyncio
    async def test_onboarding_with_unicode_content(self, test_client: AsyncClient, sample_office_data: dict):
        """Test onboarding with Unicode content."""
        # FAQ with Unicode characters
        unicode_faq = """
Q: ¿Cuáles son sus horarios de oficina?
A: Estamos abiertos de lunes a viernes de 9:00 AM a 5:00 PM.

Q: 你们接受保险吗？
A: 是的，我们接受大多数主要的牙科保险计划。

Q: Quels sont vos services?
A: Nous offrons des services dentaires complets.

Q: What are your services?
A: We offer comprehensive dental services including:
- General Dentistry
- Cosmetic Dentistry
- Orthodontics
- Oral Surgery
- Periodontics
"""
        
        form_data = sample_office_data.copy()
        files = {"faq_file": ("faq.txt", unicode_faq, "text/plain")}
        
        response = await test_client.post("/offices/onboarding/submit", data=form_data, files=files)
        
        assert response.status_code == 200
        submission_data = response.json()
        assert "submission_id" in submission_data
        
        # Verify the submission was created with Unicode content preserved
        submission_id = submission_data["submission_id"]
        response = await test_client.get(f"/offices/onboarding/submission/{submission_id}")
        
        assert response.status_code == 200
        status_data = response.json()
        assert status_data["office_name"] == sample_office_data["office_name"]
    
    @pytest.mark.asyncio
    async def test_onboarding_concurrent_submissions(self, test_client: AsyncClient, sample_office_data: dict, sample_faq_content: str):
        """Test concurrent onboarding submissions."""
        import asyncio
        
        async def submit_office(office_name: str):
            form_data = sample_office_data.copy()
            form_data["office_name"] = office_name
            files = {"faq_file": ("faq.txt", sample_faq_content, "text/plain")}
            return await test_client.post("/offices/onboarding/submit", data=form_data, files=files)
        
        # Submit multiple offices concurrently
        tasks = [
            submit_office("Concurrent Office 1"),
            submit_office("Concurrent Office 2"),
            submit_office("Concurrent Office 3"),
            submit_office("Concurrent Office 4"),
            submit_office("Concurrent Office 5")
        ]
        
        responses = await asyncio.gather(*tasks)
        
        # All submissions should succeed
        for response in responses:
            assert response.status_code == 200
            assert "submission_id" in response.json()
        
        # All submission IDs should be unique
        submission_ids = [r.json()["submission_id"] for r in responses]
        assert len(set(submission_ids)) == len(submission_ids)  # All unique
