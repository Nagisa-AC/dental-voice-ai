
class DatabaseError(Exception):
    """Database-related error."""
    pass


class ValidationError(Exception):
    """Validation-related error."""
    pass


class AuthenticationError(Exception):
    """Authentication-related error."""
    pass


class EncryptionError(Exception):
    """Encryption-related error."""
    pass


class AuthorizationError(Exception):
    """Authorization-related error."""
    pass



"""
Clinic Service for Healthcare Voice AI

Handles business logic for clinic management, replacing the factory pattern
with a proper service layer approach.
"""

import uuid
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from db.models.database_models import Clinic, ClinicStatus
from db.models.pydantic_schemas import ClinicCreate, ClinicUpdate, ClinicResponse
from db.models.faq import ClinicKnowledgeBase, FAQ
# Repositories removed - using direct database operations
from core.database import DatabaseOperations
from utils.faq_parser import parse_faq_file
from core.config import settings

logger = logging.getLogger(__name__)


class ClinicService:
    """
    Service for clinic management business logic.
    
    Replaces OfficeFactory with proper service layer pattern.
    Handles business logic for clinic creation, validation, and management.
    """
    
    def __init__(self, db_operations: DatabaseOperations):
        """Initialize clinic service with database operations."""
        self.db_operations = db_operations
        self.logger = logging.getLogger(__name__)
    
    async def get_clinic_submission(self, submission_id: str) -> Optional[ClinicCreate]:
        """
        Get a clinic submission by ID.
        
        Args:
            submission_id: Submission ID
            
        Returns:
            ClinicCreate object or None if not found
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            db_submission = await self.db_operations.get_office_submission(submission_id)
            if not db_submission:
                return None
            
            # Convert database model to Pydantic model
            return self._convert_db_submission_to_pydantic(db_submission)
        except Exception as e:
            self.logger.error(f"Failed to get office submission {submission_id}: {e}")
            raise DatabaseError(f"Failed to get office submission: {e}")

    async def create_office_submission(
        self, 
        form_data: ClinicCreate, 
        faq_content: str, 
        faq_filename: str
    ) -> ClinicCreate:
        """
        Create an office submission for admin review.
        
        Args:
            form_data: Office form data from owner
            faq_content: FAQ text content
            faq_filename: Original FAQ filename
            
        Returns:
            ClinicCreate object
            
        Raises:
            ValidationError: If form data is invalid
            DatabaseError: If database operation fails
        """
        try:
            # Add industry-specific defaults if not provided
            enhanced_form_data = self._enhance_form_data_with_defaults(form_data)
            
            # Validate form data
            validation_result = self.validate_office_data(enhanced_form_data)
            if not validation_result["valid"]:
                raise ValidationError(f"Invalid office data: {', '.join(validation_result['errors'])}")
            
            # Create submission data for database
            industry_type = enhanced_form_data.industry_type.value if hasattr(enhanced_form_data.industry_type, 'value') else str(enhanced_form_data.industry_type)
            submission_data = {
                'office_name': enhanced_form_data.office_name,
                'industry_type': industry_type,
                'phone': enhanced_form_data.contact_info.phone,
                'email': enhanced_form_data.contact_info.email,
                'address': enhanced_form_data.contact_info.address,
                'website': enhanced_form_data.contact_info.website,
                'business_hours': enhanced_form_data.business_hours.dict(),
                'services': enhanced_form_data.services,
                'faq_content': faq_content,
                'faq_filename': faq_filename,
                'status': 'pending'
            }
            
            # Create submission in database
            db_submission = await self.db_operations.create_office_submission(**submission_data)
            
            # Convert to Pydantic model
            submission = self._convert_db_submission_to_pydantic(db_submission)
            
            self.logger.info(f"Created office submission: {submission.id}")
            return submission
            
        except Exception as e:
            self.logger.error(f"Error creating office submission: {e}")
            raise
    
    async def approve_office_submission(
        self, 
        submission: ClinicCreate, 
        admin_config: Dict[str, Any]
    ) -> Clinic:
        """
        Create an active office from a reviewed submission.
        
        Args:
            submission: Reviewed office submission
            admin_config: Admin configuration
            
        Returns:
            Clinic object
            
        Raises:
            ValidationError: If submission data is invalid
            DatabaseError: If database operation fails
        """
        try:
            # Parse FAQ content
            faqs = parse_faq_file(submission.faq_content)
            
            # Convert form services to Service objects
            services = [
                Service(
                    name=service_name,
                    category="General Dentistry",  # Default category
                    description=f"{service_name} services"
                )
                for service_name in submission.form_data.services
            ]
            
            # Create office
            office = Clinic(
                tenant_id=admin_config.tenant_id,
                name=submission.form_data.office_name,
                contact_info=submission.form_data.contact_info,
                business_hours=submission.form_data.business_hours,
                services=services,
                policies=ClinicPolicies(),  # Default policies
                assistant_config=AssistantConfig(
                    voice_id=self._get_voice_id(submission.form_data.preferred_voice)
                ),
                status=ClinicStatus.ACTIVE,
                admin_config=admin_config,
                created_at=datetime.utcnow()
            )
            
            # Save to database
            await self.office_repo.create(office)
            
            # Update submission status
            await self.submission_repo.update_submission_status(
                submission.id, 
                ClinicStatus.ACTIVE
            )
            
            self.logger.info(f"Created office: {office.tenant_id}")
            return office
            
        except Exception as e:
            self.logger.error(f"Error creating office from submission: {e}")
            raise
    
    async def create_knowledge_base(
        self, 
        tenant_id: str, 
        faq_content: str, 
        office_info: Dict[str, Any]
    ) -> ClinicKnowledgeBase:
        """
        Create knowledge base from FAQ content and office info.
        
        Args:
            tenant_id: Office tenant ID
            faq_content: FAQ text content
            office_info: Additional office information
            
        Returns:
            ClinicKnowledgeBase object
            
        Raises:
            ValidationError: If data is invalid
            DatabaseError: If database operation fails
        """
        try:
            # Parse FAQ content
            faqs = parse_faq_file(faq_content)
            
            # Create knowledge base
            knowledge_base = ClinicKnowledgeBase(
                tenant_id=tenant_id,
                faqs=faqs,
                custom_instructions=self._generate_custom_instructions(office_info),
                office_info=office_info,
                created_at=datetime.utcnow()
            )
            
            # Save to database
            await self.knowledge_base_repo.create(knowledge_base)
            
            self.logger.info(f"Created knowledge base for tenant: {tenant_id} with {len(faqs)} FAQs")
            return knowledge_base
            
        except Exception as e:
            self.logger.error(f"Error creating knowledge base: {e}")
            raise
    
    async def update_office(self, office: Clinic, updates: Dict[str, Any]) -> Clinic:
        """
        Update an existing office.
        
        Args:
            office: Existing office
            updates: Update data
            
        Returns:
            Updated office
            
        Raises:
            ValidationError: If update data is invalid
            DatabaseError: If database operation fails
        """
        try:
            # Validate updates
            self._validate_office_updates(updates)
            
            # Update fields
            for field, value in updates.items():
                if hasattr(office, field):
                    setattr(office, field, value)
            
            # Update timestamp
            office.updated_at = datetime.utcnow()
            
            # Save to database
            await self.office_repo.update(office)
            
            self.logger.info(f"Updated office: {office.tenant_id}")
            return office
            
        except Exception as e:
            self.logger.error(f"Error updating office: {e}")
            raise
    
    async def deactivate_office(self, office: Clinic) -> Clinic:
        """
        Deactivate an office.
        
        Args:
            office: Office to deactivate
            
        Returns:
            Deactivated office
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            office.status = ClinicStatus.INACTIVE
            office.updated_at = datetime.utcnow()
            
            # Save to database
            await self.office_repo.update(office)
            
            self.logger.info(f"Deactivated office: {office.tenant_id}")
            return office
            
        except Exception as e:
            self.logger.error(f"Error deactivating office: {e}")
            raise
    
    def validate_office_data(self, form_data: ClinicCreate) -> Dict[str, Any]:
        """
        Validate office form data.
        
        Args:
            form_data: Office form data
            
        Returns:
            Validation result with errors if any
        """
        errors = []
        
        # Validate required fields
        if not form_data.office_name.strip():
            errors.append("Office name is required")
        
        if not form_data.contact_info.phone.strip():
            errors.append("Phone number is required")
        
        if not form_data.contact_info.email.strip():
            errors.append("Email address is required")
        
        if not form_data.contact_info.address.strip():
            errors.append("Office address is required")
        
        if not form_data.services:
            errors.append("At least one service must be specified")
        
        # Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, form_data.contact_info.email):
            errors.append("Invalid email format")
        
        # Validate phone format
        phone_pattern = r'^\+?[\d\s\-\(\)]+$'
        if not re.match(phone_pattern, form_data.contact_info.phone):
            errors.append("Invalid phone number format")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _get_voice_id(self, preferred_voice: Optional[str]) -> str:
        """Get voice ID based on preference."""
        voice_mapping = {
            "professional_female": "cgSgspJ2msm6clMCkdW9",
            "professional_male": "pNInz6obpgDQGcFmaJgB",
            "friendly_female": "EXAVITQu4vr4xnSDxMaL",
            "friendly_male": "VR6AewLTigWG4xSOukaG"
        }
        
        return voice_mapping.get(preferred_voice, "cgSgspJ2msm6clMCkdW9")
    
    def _generate_custom_instructions(self, office_info: Dict[str, Any]) -> List[str]:
        """Generate custom instructions for the assistant."""
        instructions = [
            "Always maintain a professional and caring tone",
            "Use the provided FAQ information to answer questions accurately",
            "If you don't know something, offer to connect the caller with office staff",
            "Be helpful and efficient in handling appointment requests"
        ]
        
        # Add office-specific instructions
        if office_info.get("emergency_phone"):
            instructions.append(f"For emergencies, direct callers to {office_info['emergency_phone']}")
        
        if office_info.get("new_patient_special"):
            instructions.append("Mention our new patient special when appropriate")
        
        return instructions
    
    def _validate_office_updates(self, updates: Dict[str, Any]) -> None:
        """Validate office update data."""
        allowed_fields = {
            'name', 'contact_info', 'business_hours', 'services', 
            'policies', 'assistant_config', 'status'
        }
        
        for field in updates.keys():
            if field not in allowed_fields:
                raise ValidationError(f"Invalid update field: {field}")
        
        # Additional validation for specific fields
        if 'contact_info' in updates:
            contact_info = updates['contact_info']
            if hasattr(contact_info, 'email'):
                import re
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, contact_info.email):
                    raise ValidationError("Invalid email format")
    
    # ============================================================================
    # CONVERSION METHODS
    # ============================================================================
    
    def _convert_db_submission_to_pydantic(self, db_submission) -> ClinicCreate:
        """Convert database submission model to Pydantic model."""
        from db.models.office import ContactInfo, BusinessHours
        
        # Convert contact info
        contact_info = ContactInfo(
            phone=db_submission.phone,
            email=db_submission.email,
            address=db_submission.address,
            website=db_submission.website
        )
        
        # Convert business hours
        business_hours = BusinessHours(**db_submission.business_hours) if db_submission.business_hours else BusinessHours()
        
        # Create form data
        form_data = ClinicCreate(
            office_name=db_submission.office_name,
            contact_info=contact_info,
            business_hours=business_hours,
            services=db_submission.services,
            preferred_voice=None  # Not stored in database
        )
        
        # Create submission
        return ClinicCreate(
            id=db_submission.id,
            form_data=form_data,
            faq_content=db_submission.faq_content,
            faq_filename=db_submission.faq_filename,
            status=ClinicStatus(db_submission.status),
            submitted_at=db_submission.created_at,
            admin_notes=db_submission.admin_notes
        )
    
    def _convert_pydantic_submission_to_db(self, submission: ClinicCreate) -> Dict[str, Any]:
        """Convert Pydantic submission model to database model data."""
        return {
            'office_name': submission.form_data.office_name,
            'phone': submission.form_data.contact_info.phone,
            'email': submission.form_data.contact_info.email,
            'address': submission.form_data.contact_info.address,
            'website': submission.form_data.contact_info.website,
            'business_hours': submission.form_data.business_hours.dict(),
            'services': submission.form_data.services,
            'faq_content': submission.faq_content,
            'faq_filename': submission.faq_filename,
            'status': submission.status.value,
            'admin_notes': submission.admin_notes
        }
    
    def _enhance_form_data_with_defaults(self, form_data: ClinicCreate) -> ClinicCreate:
        """Add industry-specific defaults to form data if not provided."""
        try:
            # Get industry type
            industry_type = form_data.industry_type
            if hasattr(industry_type, 'value'):
                industry_enum = HealthcareIndustry(industry_type.value)
            else:
                industry_enum = HealthcareIndustry(industry_type)
            
            # Get industry config
            config = get_industry_config(industry_enum)
            
            # Add default services if none provided
            if not form_data.services:
                form_data.services = get_default_services(industry_enum)
            
            # Add default business hours if none provided
            if not form_data.business_hours or not any(form_data.business_hours.dict().values()):
                from db.models.office import BusinessHours
                default_hours = get_default_hours(industry_enum)
                form_data.business_hours = BusinessHours(**default_hours)
            
            return form_data
            
        except Exception as e:
            self.logger.warning(f"Failed to enhance form data with defaults: {e}")
            return form_data
