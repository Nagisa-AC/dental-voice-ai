"""
Clinic management API endpoints for multi-tenant healthcare practice management.

Combines onboarding and admin functionality into a single, simplified module.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, Request
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from db.models.database_models import Clinic, ClinicStatus
from db.models.pydantic_schemas import ClinicCreate, ClinicUpdate, ClinicResponse
from db.models.assistant import AssistantResponse
from db.models.faq import FAQResponse
# Factory functions removed - using direct service instantiation
from services.office_service import ClinicService
from services.assistant_service import AssistantService
from integrations.vapi.async_vapi_service import AsyncVAPIService
from core.config import settings
from core.auth import require_admin, AuthUser
from core.validation import (
    sanitize_input, validate_office_name, validate_phone_number, validate_email
)
from services.security_service import security_service
from services.file_upload_service import validate_file_upload
from utils.secure_faq_parser import parse_faq_file_securely

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory storage (will be replaced with database in production)
office_submissions: Dict[str, Any] = {}
offices: Dict[str, Any] = {}
knowledge_bases: Dict[str, Any] = {}


# ============================================================================
# ONBOARDING ENDPOINTS
# ============================================================================

@router.get("/industries", response_model=List[Dict[str, Any]])
async def get_healthcare_industries(request: Request):
    """Get list of available healthcare industries for onboarding."""
    try:
        # Return basic healthcare industries for now
        industries = [
            {"type": "dental", "name": "Dental Practice", "description": "General dental services"},
            {"type": "medical", "name": "Medical Practice", "description": "General medical services"},
            {"type": "specialty", "name": "Specialty Practice", "description": "Specialized medical services"}
        ]
        return industries
    except Exception as e:
        logger.error(f"Error getting healthcare industries: {e}")
        raise HTTPException(status_code=500, detail="Failed to get healthcare industries")

@router.get("/industries/{industry_type}/config", response_model=Dict[str, Any])
async def get_industry_config_endpoint(industry_type: str, request: Request):
    """Get configuration for a specific healthcare industry."""
    try:
        from core.configs.industries import HealthcareIndustry
        industry_enum = HealthcareIndustry(industry_type)
        config = get_industry_config(industry_enum)
        return config
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid industry type: {industry_type}")
    except Exception as e:
        logger.error(f"Error getting industry config for {industry_type}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get industry configuration")

@router.post("/submit", response_model=Dict[str, str])
async def submit_office_onboarding(
    request: Request,
    office_name: str = Form(...),
    industry_type: str = Form(default="dental"),
    phone: str = Form(...),
    email: str = Form(...),
    address: str = Form(...),
    website: str = Form(None),
    monday_hours: str = Form(None),
    tuesday_hours: str = Form(None),
    wednesday_hours: str = Form(None),
    thursday_hours: str = Form(None),
    friday_hours: str = Form(None),
    saturday_hours: str = Form(None),
    sunday_hours: str = Form(None),
    services: str = Form(...),  # Comma-separated list
    faq_file: Optional[UploadFile] = File(None),
    office_service: ClinicService = Depends(lambda: ClinicService())
) -> Dict[str, str]:
    """
    Submit office onboarding information.
    
    This endpoint allows dental offices to submit their information for review
    and approval by administrators.
    """
    try:
        # CSRF validation is handled by middleware, but we can add additional checks here if needed
        # The middleware will validate the CSRF token before this function is called
        
        # Validate and sanitize input
        office_name = validate_office_name(office_name)
        phone = validate_phone_number(phone)
        email = validate_email(email)
        address = sanitize_input(address)
        website = sanitize_input(website) if website else None
        
        # Validate business hours
        business_hours = {
            "monday": sanitize_input(monday_hours) if monday_hours else None,
            "tuesday": sanitize_input(tuesday_hours) if tuesday_hours else None,
            "wednesday": sanitize_input(wednesday_hours) if wednesday_hours else None,
            "thursday": sanitize_input(thursday_hours) if thursday_hours else None,
            "friday": sanitize_input(friday_hours) if friday_hours else None,
            "saturday": sanitize_input(saturday_hours) if saturday_hours else None,
            "sunday": sanitize_input(sunday_hours) if sunday_hours else None,
        }
        
        # Parse services
        services_list = [s.strip() for s in services.split(",") if s.strip()]
        
        # Validate file upload if provided
        faq_data = None
        if faq_file:
            # Comprehensive file validation using secure file upload service
            validation_result = validate_file_upload(faq_file, None)  # No user ID for public submission
            
            if not validation_result["valid"]:
                raise HTTPException(
                    status_code=400, 
                    detail=f"File validation failed: {', '.join(validation_result['errors'])}"
                )
            
            # Parse FAQ file securely
            try:
                file_content = faq_file.file.read().decode('utf-8', errors='ignore')
                faq_file.file.seek(0)  # Reset to beginning
                faq_data = parse_faq_file_securely(file_content, faq_file.filename)
            except Exception as e:
                logger.error(f"Failed to parse FAQ file: {e}")
                raise HTTPException(status_code=400, detail="Failed to parse FAQ file")
        
        # Create office form data
        form_data = ClinicFormData(
            office_name=office_name,
            phone=phone,
            email=email,
            address=address,
            website=website,
            business_hours=business_hours,
            services=services_list,
            faq_data=faq_data
        )
        
        # Validate the complete form
        if not validation.validate_office_form(form_data):
            raise HTTPException(status_code=400, detail="Invalid office data")
        
        # Create submission
        submission_id = str(uuid.uuid4())
        submission = ClinicSubmission(
            id=submission_id,
            office_name=office_name,
            phone=phone,
            email=email,
            address=address,
            website=website,
            business_hours=business_hours,
            services=services_list,
            faq_data=faq_data,
            status=ClinicStatus.PENDING,
            submitted_at=datetime.utcnow()
        )
        
        # Store submission (in production, save to database)
        office_submissions[submission_id] = submission.dict()
        
        logger.info(f"Office submission created: {submission_id}")
        
        return {
            "submission_id": submission_id,
            "status": "submitted",
            "message": "Office information submitted successfully. Awaiting admin approval."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit office onboarding: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit office information")


@router.get("/submissions/{submission_id}/status")
async def get_submission_status(submission_id: str) -> Dict[str, Any]:
    """Get the status of an office submission."""
    try:
        if submission_id not in office_submissions:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        submission = office_submissions[submission_id]
        return {
            "submission_id": submission_id,
            "status": submission["status"],
            "submitted_at": submission["submitted_at"],
            "office_name": submission["office_name"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get submission status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get submission status")


# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@router.post("/submissions/{submission_id}/approve")
async def approve_office_submission(
    submission_id: str,
    tenant_id: str,
    calendar_integration: Dict[str, Any],
    phone_number_config: Dict[str, Any],
    admin_notes: Optional[str] = None,
    current_user: AuthUser = Depends(require_admin),
    office_service: ClinicService = Depends(lambda: ClinicService()),
    assistant_service: AssistantService = Depends(lambda: AssistantService(AsyncVAPIService()))
):
    """
    Approve an office submission and create the office.
    """
    try:
        # Get submission from database
        submission = await office_service.get_office_submission(submission_id)
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        if submission.status != ClinicStatus.PENDING:
            raise HTTPException(status_code=400, detail="Submission is not pending approval")
        
        # Create admin configuration
        admin_config = AdminConfig(
            tenant_id=tenant_id,
            calendar_integration=calendar_integration,
            phone_number_config=phone_number_config,
            admin_notes=admin_notes,
            approved_by=current_user.user_id,
            approved_at=datetime.utcnow()
        )
        
        # Create office
        office = await office_service.create_office_from_submission(submission, admin_config)
        
        # Create VAPI assistant
        vapi_service = AsyncVAPIService()
        assistant = await assistant_service.create_assistant_for_office(office, vapi_service)
        
        logger.info(f"Office approved and created: {office.id}")
        
        return {
            "office_id": office.id,
            "assistant_id": assistant.id,
            "status": "approved",
            "message": "Office approved and assistant created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to approve office submission: {e}")
        raise HTTPException(status_code=500, detail="Failed to approve office submission")


@router.get("/submissions", response_model=List[Dict[str, Any]])
async def list_office_submissions(
    status: Optional[ClinicStatus] = None,
    current_user: AuthUser = Depends(require_admin),
    office_service: ClinicService = Depends(lambda: ClinicService())
):
    """List all office submissions with optional status filter."""
    try:
        submissions = await office_service.list_office_submissions(status=status)
        return [submission.dict() for submission in submissions]
        
    except Exception as e:
        logger.error(f"Failed to list office submissions: {e}")
        raise HTTPException(status_code=500, detail="Failed to list submissions")


@router.get("/", response_model=List[ClinicResponse])
async def list_offices(
    current_user: AuthUser = Depends(require_admin),
    office_service: ClinicService = Depends(lambda: ClinicService())
):
    """List all offices."""
    try:
        offices = await office_service.list_offices()
        return [ClinicResponse.from_orm(office) for office in offices]
        
    except Exception as e:
        logger.error(f"Failed to list offices: {e}")
        raise HTTPException(status_code=500, detail="Failed to list offices")


@router.get("/{office_id}", response_model=ClinicResponse)
async def get_office(
    office_id: str,
    current_user: AuthUser = Depends(require_admin),
    office_service: ClinicService = Depends(lambda: ClinicService())
):
    """Get office details."""
    try:
        office = await office_service.get_office(office_id)
        if not office:
            raise HTTPException(status_code=404, detail="Office not found")
        
        return ClinicResponse.from_orm(office)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get office: {e}")
        raise HTTPException(status_code=500, detail="Failed to get office")


@router.put("/{office_id}")
async def update_office(
    office_id: str,
    updates: Dict[str, Any],
    current_user: AuthUser = Depends(require_admin),
    office_service: ClinicService = Depends(lambda: ClinicService())
):
    """Update office information."""
    try:
        office = await office_service.get_office(office_id)
        if not office:
            raise HTTPException(status_code=404, detail="Office not found")
        
        # Update office fields
        for key, value in updates.items():
            if hasattr(office, key):
                setattr(office, key, value)
        
        updated_office = await office_service.update_office(office)
        
        return {
            "office_id": office_id,
            "status": "updated",
            "message": "Office updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update office: {e}")
        raise HTTPException(status_code=500, detail="Failed to update office")


@router.delete("/{office_id}")
async def deactivate_office(
    office_id: str,
    current_user: AuthUser = Depends(require_admin),
    office_service: ClinicService = Depends(lambda: ClinicService())
):
    """Deactivate an office."""
    try:
        office = await office_service.get_office(office_id)
        if not office:
            raise HTTPException(status_code=404, detail="Office not found")
        
        # Deactivate office
        office.status = ClinicStatus.INACTIVE
        office.updated_at = datetime.utcnow()
        
        deactivated_office = await office_service.update_office(office)
        
        return {
            "office_id": office_id,
            "status": "deactivated",
            "message": "Office deactivated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to deactivate office: {e}")
        raise HTTPException(status_code=500, detail="Failed to deactivate office")
