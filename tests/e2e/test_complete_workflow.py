"""
End-to-end tests for complete application workflow.

Tests the entire application flow from office onboarding to assistant creation and call management.
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from healthcare_voice_ai.core.models.database_models import UserRole, OfficeStatus


class TestCompleteWorkflow:
    """End-to-end tests for complete application workflow."""
    
    @pytest.mark.asyncio
    async def test_complete_office_setup_workflow(
        self, 
        test_client: AsyncClient, 
        test_auth_service, 
        sample_office_data: dict, 
        sample_faq_content: str,
        mock_vapi_service
    ):
        """Test complete workflow from office onboarding to assistant creation."""
        # Step 1: Create admin user
        admin = await test_auth_service.create_user(
            email="admin@dentalvoiceai.com",
            password="adminpassword123",
            role=UserRole.ADMIN
        )
        
        # Step 2: Login as admin
        login_data = {
            "email": "admin@dentalvoiceai.com",
            "password": "adminpassword123"
        }
        
        response = await test_client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        token_data = response.json()
        access_token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Step 3: Office submits onboarding form
        form_data = sample_office_data.copy()
        files = {"faq_file": ("faq.txt", sample_faq_content, "text/plain")}
        
        response = await test_client.post("/offices/onboarding/submit", data=form_data, files=files)
        assert response.status_code == 200
        submission_data = response.json()
        submission_id = submission_data["submission_id"]
        
        # Step 4: Admin reviews and approves submission
        # Get submission details
        response = await test_client.get(f"/offices/onboarding/submission/{submission_id}")
        assert response.status_code == 200
        submission_details = response.json()
        assert submission_details["status"] == "pending"
        
        # Approve submission (simulated admin action)
        from healthcare_voice_ai.core.services.database_service import DatabaseService
        from healthcare_voice_ai.core.database import get_async_db
        
        async for db_session in get_async_db():
            db_service = DatabaseService(db_session)
            await db_service.update_office_submission_status(
                submission_id, 
                OfficeStatus.APPROVED,
                "Approved for production use"
            )
            break
        
        # Step 5: Create office from approved submission
        # This would typically be done through admin endpoints
        # For testing, we'll simulate the office creation
        async for db_session in get_async_db():
            db_service = DatabaseService(db_session)
            
            # Get the approved submission
            submission = await db_service.get_office_submission(submission_id)
            
            # Create office
            office = await db_service.create_office(
                tenant_id=f"tenant-{submission_id[:8]}",
                name=submission.form_data["office_name"],
                phone=submission.form_data["contact_info"]["phone"],
                email=submission.form_data["contact_info"]["email"],
                address=submission.form_data["contact_info"]["address"],
                business_hours=submission.form_data.get("business_hours", {}),
                services=submission.form_data.get("services", [])
            )
            
            # Create knowledge base
            await db_service.create_office_knowledge_base(
                office_id=office.id,
                faq_items=[
                    {"question": "What are your hours?", "answer": "9 AM to 5 PM"},
                    {"question": "Do you accept insurance?", "answer": "Yes, we accept most plans"}
                ]
            )
            break
        
        # Step 6: Create VAPI assistant for the office
        # This would typically be done through the VAPI service
        # For testing, we'll use the mock service
        assistant_id = await mock_vapi_service.create_dental_assistant(
            name=f"{submission.form_data['office_name']} Assistant"
        )
        
        # Step 7: Create phone number for the assistant
        phone_number_id = await mock_vapi_service.create_phone_number(
            assistant_id=assistant_id,
            area_code="415"
        )
        
        # Step 8: Verify the complete setup
        # Check that office exists
        async for db_session in get_async_db():
            db_service = DatabaseService(db_session)
            office = await db_service.get_office_by_tenant_id(f"tenant-{submission_id[:8]}")
            assert office is not None
            assert office.name == submission.form_data["office_name"]
            assert office.is_active is True
            
            # Check knowledge base exists
            kb = await db_service.get_office_knowledge_base(office.id)
            assert kb is not None
            assert len(kb.faq_items) == 2
            break
        
        # Check VAPI assistant and phone number
        assert assistant_id in mock_vapi_service.assistants
        assert phone_number_id in mock_vapi_service.phone_numbers
        assert mock_vapi_service.phone_numbers[phone_number_id]["assistant_id"] == assistant_id
        
        # Step 9: Test call creation
        call_data = await mock_vapi_service.create_call(
            assistant_id=assistant_id,
            phone_number_id=phone_number_id,
            customer_phone="+1234567890"
        )
        
        assert call_data is not None
        assert call_data["assistant_id"] == assistant_id
        assert call_data["phone_number_id"] == phone_number_id
        assert call_data["customer_phone"] == "+1234567890"
        assert call_data["status"] == "initiated"
    
    @pytest.mark.asyncio
    async def test_multi_office_workflow(
        self, 
        test_client: AsyncClient, 
        test_auth_service, 
        sample_office_data: dict, 
        sample_faq_content: str,
        mock_vapi_service
    ):
        """Test workflow with multiple offices."""
        # Create admin user
        admin = await test_auth_service.create_user(
            email="admin@dentalvoiceai.com",
            password="adminpassword123",
            role=UserRole.ADMIN
        )
        
        # Login as admin
        login_data = {
            "email": "admin@dentalvoiceai.com",
            "password": "adminpassword123"
        }
        
        response = await test_client.post("/auth/login", json=login_data)
        token_data = response.json()
        access_token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Create multiple office submissions
        offices_data = [
            {
                **sample_office_data,
                "office_name": "Downtown Dental Clinic",
                "phone": "+14155550001",
                "email": "downtown@dental.com"
            },
            {
                **sample_office_data,
                "office_name": "Uptown Dental Practice",
                "phone": "+14155550002",
                "email": "uptown@dental.com"
            },
            {
                **sample_office_data,
                "office_name": "Suburban Dental Center",
                "phone": "+14155550003",
                "email": "suburban@dental.com"
            }
        ]
        
        submission_ids = []
        
        for office_data in offices_data:
            form_data = office_data.copy()
            files = {"faq_file": ("faq.txt", sample_faq_content, "text/plain")}
            
            response = await test_client.post("/offices/onboarding/submit", data=form_data, files=files)
            assert response.status_code == 200
            submission_data = response.json()
            submission_ids.append(submission_data["submission_id"])
        
        # Approve all submissions and create offices
        async for db_session in get_async_db():
            db_service = DatabaseService(db_session)
            
            for i, submission_id in enumerate(submission_ids):
                # Approve submission
                await db_service.update_office_submission_status(
                    submission_id, 
                    OfficeStatus.APPROVED,
                    f"Approved office {i+1}"
                )
                
                # Get submission and create office
                submission = await db_service.get_office_submission(submission_id)
                
                office = await db_service.create_office(
                    tenant_id=f"tenant-{submission_id[:8]}",
                    name=submission.form_data["office_name"],
                    phone=submission.form_data["contact_info"]["phone"],
                    email=submission.form_data["contact_info"]["email"],
                    address=submission.form_data["contact_info"]["address"],
                    business_hours=submission.form_data.get("business_hours", {}),
                    services=submission.form_data.get("services", [])
                )
                
                # Create knowledge base
                await db_service.create_office_knowledge_base(
                    office_id=office.id,
                    faq_items=[
                        {"question": "What are your hours?", "answer": "9 AM to 5 PM"},
                        {"question": "Do you accept insurance?", "answer": "Yes, we accept most plans"}
                    ]
                )
                
                # Create VAPI assistant
                assistant_id = await mock_vapi_service.create_dental_assistant(
                    name=f"{submission.form_data['office_name']} Assistant"
                )
                
                # Create phone number
                phone_number_id = await mock_vapi_service.create_phone_number(
                    assistant_id=assistant_id,
                    area_code="415"
                )
            break
        
        # Verify all offices are created and active
        async for db_session in get_async_db():
            db_service = DatabaseService(db_session)
            offices = await db_service.list_offices()
            
            assert len(offices) == 3
            office_names = [office.name for office in offices]
            assert "Downtown Dental Clinic" in office_names
            assert "Uptown Dental Practice" in office_names
            assert "Suburban Dental Center" in office_names
            
            # Verify all offices are active
            for office in offices:
                assert office.is_active is True
                
                # Verify knowledge base exists
                kb = await db_service.get_office_knowledge_base(office.id)
                assert kb is not None
                assert len(kb.faq_items) == 2
            break
        
        # Verify VAPI assistants and phone numbers
        assert len(mock_vapi_service.assistants) == 3
        assert len(mock_vapi_service.phone_numbers) == 3
        
        # Test calls for each office
        for assistant_id in mock_vapi_service.assistants.keys():
            phone_number_id = None
            for pid, pdata in mock_vapi_service.phone_numbers.items():
                if pdata["assistant_id"] == assistant_id:
                    phone_number_id = pid
                    break
            
            assert phone_number_id is not None
            
            # Create a test call
            call_data = await mock_vapi_service.create_call(
                assistant_id=assistant_id,
                phone_number_id=phone_number_id,
                customer_phone="+1234567890"
            )
            
            assert call_data is not None
            assert call_data["assistant_id"] == assistant_id
            assert call_data["phone_number_id"] == phone_number_id
    
    @pytest.mark.asyncio
    async def test_office_deactivation_workflow(
        self, 
        test_client: AsyncClient, 
        test_auth_service, 
        sample_office_data: dict, 
        sample_faq_content: str,
        mock_vapi_service
    ):
        """Test office deactivation workflow."""
        # Create admin user and login
        admin = await test_auth_service.create_user(
            email="admin@dentalvoiceai.com",
            password="adminpassword123",
            role=UserRole.ADMIN
        )
        
        login_data = {
            "email": "admin@dentalvoiceai.com",
            "password": "adminpassword123"
        }
        
        response = await test_client.post("/auth/login", json=login_data)
        token_data = response.json()
        access_token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Create office submission and approve
        form_data = sample_office_data.copy()
        files = {"faq_file": ("faq.txt", sample_faq_content, "text/plain")}
        
        response = await test_client.post("/offices/onboarding/submit", data=form_data, files=files)
        submission_id = response.json()["submission_id"]
        
        # Approve and create office
        async for db_session in get_async_db():
            db_service = DatabaseService(db_session)
            
            await db_service.update_office_submission_status(
                submission_id, 
                OfficeStatus.APPROVED,
                "Approved for testing"
            )
            
            submission = await db_service.get_office_submission(submission_id)
            office = await db_service.create_office(
                tenant_id=f"tenant-{submission_id[:8]}",
                name=submission.form_data["office_name"],
                phone=submission.form_data["contact_info"]["phone"],
                email=submission.form_data["contact_info"]["email"],
                address=submission.form_data["contact_info"]["address"],
                business_hours=submission.form_data.get("business_hours", {}),
                services=submission.form_data.get("services", [])
            )
            
            # Create VAPI assistant
            assistant_id = await mock_vapi_service.create_dental_assistant(
                name=f"{submission.form_data['office_name']} Assistant"
            )
            
            phone_number_id = await mock_vapi_service.create_phone_number(
                assistant_id=assistant_id,
                area_code="415"
            )
            break
        
        # Verify office is active
        async for db_session in get_async_db():
            db_service = DatabaseService(db_session)
            office = await db_service.get_office_by_tenant_id(f"tenant-{submission_id[:8]}")
            assert office.is_active is True
            break
        
        # Deactivate office
        async for db_session in get_async_db():
            db_service = DatabaseService(db_session)
            office = await db_service.get_office_by_tenant_id(f"tenant-{submission_id[:8]}")
            await db_service.deactivate_office(office.id)
            break
        
        # Verify office is deactivated
        async for db_session in get_async_db():
            db_service = DatabaseService(db_session)
            office = await db_service.get_office_by_tenant_id(f"tenant-{submission_id[:8]}")
            assert office.is_active is False
            break
        
        # Reactivate office
        async for db_session in get_async_db():
            db_service = DatabaseService(db_session)
            office = await db_service.get_office_by_tenant_id(f"tenant-{submission_id[:8]}")
            await db_service.activate_office(office.id)
            break
        
        # Verify office is reactivated
        async for db_session in get_async_db():
            db_service = DatabaseService(db_session)
            office = await db_service.get_office_by_tenant_id(f"tenant-{submission_id[:8]}")
            assert office.is_active is True
            break
    
    @pytest.mark.asyncio
    async def test_error_recovery_workflow(
        self, 
        test_client: AsyncClient, 
        test_auth_service, 
        sample_office_data: dict, 
        sample_faq_content: str
    ):
        """Test error recovery and resilience."""
        # Create admin user and login
        admin = await test_auth_service.create_user(
            email="admin@dentalvoiceai.com",
            password="adminpassword123",
            role=UserRole.ADMIN
        )
        
        login_data = {
            "email": "admin@dentalvoiceai.com",
            "password": "adminpassword123"
        }
        
        response = await test_client.post("/auth/login", json=login_data)
        token_data = response.json()
        access_token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Test invalid submission data
        invalid_form_data = {
            "office_name": "",  # Empty name
            "phone": "invalid-phone",
            "email": "invalid-email",
            "address": "",
            "services": ""
        }
        files = {"faq_file": ("faq.txt", sample_faq_content, "text/plain")}
        
        response = await test_client.post("/offices/onboarding/submit", data=invalid_form_data, files=files)
        assert response.status_code == 422  # Validation error
        
        # Test with valid data
        form_data = sample_office_data.copy()
        response = await test_client.post("/offices/onboarding/submit", data=form_data, files=files)
        assert response.status_code == 200
        submission_id = response.json()["submission_id"]
        
        # Test retrieving non-existent submission
        response = await test_client.get("/offices/onboarding/submission/nonexistent-id")
        assert response.status_code == 404
        
        # Test with invalid authentication
        invalid_headers = {"Authorization": "Bearer invalid-token"}
        response = await test_client.get("/auth/me", headers=invalid_headers)
        assert response.status_code == 401
        
        # Test with expired token (simulated)
        # In a real scenario, this would test token expiration
        # For testing, we'll just verify the error handling works
        
        # Test concurrent operations
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
            submit_office("Concurrent Office 3")
        ]
        
        responses = await asyncio.gather(*tasks)
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200
            assert "submission_id" in response.json()
        
        # Verify all submissions are unique
        submission_ids = [r.json()["submission_id"] for r in responses]
        assert len(set(submission_ids)) == len(submission_ids)
    
    @pytest.mark.asyncio
    async def test_data_consistency_workflow(
        self, 
        test_client: AsyncClient, 
        test_auth_service, 
        sample_office_data: dict, 
        sample_faq_content: str
    ):
        """Test data consistency across operations."""
        # Create admin user and login
        admin = await test_auth_service.create_user(
            email="admin@dentalvoiceai.com",
            password="adminpassword123",
            role=UserRole.ADMIN
        )
        
        login_data = {
            "email": "admin@dentalvoiceai.com",
            "password": "adminpassword123"
        }
        
        response = await test_client.post("/auth/login", json=login_data)
        token_data = response.json()
        access_token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Create office submission
        form_data = sample_office_data.copy()
        files = {"faq_file": ("faq.txt", sample_faq_content, "text/plain")}
        
        response = await test_client.post("/offices/onboarding/submit", data=form_data, files=files)
        submission_id = response.json()["submission_id"]
        
        # Verify submission data consistency
        response = await test_client.get(f"/offices/onboarding/submission/{submission_id}")
        submission_data = response.json()
        
        assert submission_data["office_name"] == sample_office_data["office_name"]
        assert submission_data["status"] == "pending"
        
        # Approve submission
        async for db_session in get_async_db():
            db_service = DatabaseService(db_session)
            await db_service.update_office_submission_status(
                submission_id, 
                OfficeStatus.APPROVED,
                "Approved for testing"
            )
            break
        
        # Verify status update
        response = await test_client.get(f"/offices/onboarding/submission/{submission_id}")
        updated_data = response.json()
        
        assert updated_data["status"] == "approved"
        assert updated_data["admin_notes"] == "Approved for testing"
        
        # Create office and verify data consistency
        async for db_session in get_async_db():
            db_service = DatabaseService(db_session)
            
            submission = await db_service.get_office_submission(submission_id)
            office = await db_service.create_office(
                tenant_id=f"tenant-{submission_id[:8]}",
                name=submission.form_data["office_name"],
                phone=submission.form_data["contact_info"]["phone"],
                email=submission.form_data["contact_info"]["email"],
                address=submission.form_data["contact_info"]["address"],
                business_hours=submission.form_data.get("business_hours", {}),
                services=submission.form_data.get("services", [])
            )
            
            # Verify office data matches submission data
            assert office.name == submission.form_data["office_name"]
            assert office.phone == submission.form_data["contact_info"]["phone"]
            assert office.email == submission.form_data["contact_info"]["email"]
            assert office.address == submission.form_data["contact_info"]["address"]
            
            # Create knowledge base
            await db_service.create_office_knowledge_base(
                office_id=office.id,
                faq_items=[
                    {"question": "What are your hours?", "answer": "9 AM to 5 PM"},
                    {"question": "Do you accept insurance?", "answer": "Yes, we accept most plans"}
                ]
            )
            
            # Verify knowledge base
            kb = await db_service.get_office_knowledge_base(office.id)
            assert kb is not None
            assert len(kb.faq_items) == 2
            assert kb.faq_items[0].question == "What are your hours?"
            assert kb.faq_items[0].answer == "9 AM to 5 PM"
            break
        
        # Test data persistence across operations
        # Update office information
        async for db_session in get_async_db():
            db_service = DatabaseService(db_session)
            office = await db_service.get_office_by_tenant_id(f"tenant-{submission_id[:8]}")
            
            updated_office = await db_service.update_office(
                office.id,
                name="Updated Office Name",
                phone="+1987654321"
            )
            
            assert updated_office.name == "Updated Office Name"
            assert updated_office.phone == "+1987654321"
            assert updated_office.email == office.email  # Should remain unchanged
            break
