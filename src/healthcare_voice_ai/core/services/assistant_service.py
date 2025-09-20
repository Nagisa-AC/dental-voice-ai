"""
Assistant Service for Healthcare Voice AI

Handles business logic for assistant management, replacing the factory pattern
with a proper service layer approach.
"""

import uuid
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from healthcare_voice_ai.core.models.office import Clinic
from healthcare_voice_ai.core.models.assistant import (
    Assistant, AssistantConfig, AssistantCreateRequest, 
    AssistantType, VoiceConfig, ModelConfig, AssistantStatus
)
from healthcare_voice_ai.core.models.faq import OfficeKnowledgeBase
# DatabaseService removed - using direct database operations
from healthcare_voice_ai.core.services.async_vapi_service import AsyncVAPIService
from healthcare_voice_ai.core.errors import ValidationError, DatabaseError, VAPIServiceError

logger = logging.getLogger(__name__)


class AssistantService:
    """
    Service for assistant management business logic.
    
    Replaces AssistantFactory with proper service layer pattern.
    Handles business logic for assistant creation, configuration, and VAPI integration.
    """
    
    def __init__(self, vapi_service: AsyncVAPIService):
        """Initialize assistant service with dependencies."""
        self.vapi_service = vapi_service
        self.logger = logging.getLogger(__name__)
    
    async def create_assistant_for_office(
        self, 
        office: Clinic, 
        knowledge_base: OfficeKnowledgeBase, 
        request: AssistantCreateRequest
    ) -> Assistant:
        """
        Create an assistant for a specific office with custom knowledge.
        
        Args:
            office: Clinic configuration
            knowledge_base: Office knowledge base with FAQs
            request: Assistant creation request
            
        Returns:
            Assistant object
            
        Raises:
            ValidationError: If request data is invalid
            VAPIServiceError: If VAPI integration fails
            DatabaseError: If database operation fails
        """
        try:
            # Validate request
            self._validate_assistant_request(request, office)
            
            # Generate system prompt with office-specific knowledge
            system_prompt = self._generate_system_prompt(office, knowledge_base, request)
            
            # Create assistant configuration
            assistant_config = AssistantConfig(
                name=request.name,
                type=request.type,
                voice=VoiceConfig(
                    voice_id=request.voice_id or office.assistant_config.voice_id
                ),
                model=ModelConfig(
                    model=request.model or office.assistant_config.model,
                    system_prompt=system_prompt
                ),
                first_message=request.first_message or self._generate_first_message(office),
                custom_instructions=request.custom_instructions
            )
            
            # Create VAPI assistant
            vapi_assistant_id = await self._create_vapi_assistant(assistant_config, office)
            
            # Create assistant record
            assistant = Assistant(
                id=str(uuid.uuid4()),
                tenant_id=office.tenant_id,
                name=assistant_config.name,
                type=assistant_config.type,
                config=assistant_config,
                vapi_assistant_id=vapi_assistant_id,
                status=AssistantStatus.ACTIVE,
                created_at=datetime.utcnow()
            )
            
            # Save to database
            await self.db.create_assistant(assistant)
            
            self.logger.info(f"Created assistant {assistant.id} for office {office.tenant_id}")
            return assistant
            
        except Exception as e:
            self.logger.error(f"Error creating assistant for office {office.tenant_id}: {e}")
            raise
    
    async def create_default_assistant(
        self, 
        office: Clinic, 
        knowledge_base: OfficeKnowledgeBase
    ) -> Assistant:
        """
        Create a default assistant for an office.
        
        Args:
            office: Clinic configuration
            knowledge_base: Office knowledge base
            
        Returns:
            Assistant object
            
        Raises:
            ValidationError: If office data is invalid
            VAPIServiceError: If VAPI integration fails
            DatabaseError: If database operation fails
        """
        request = AssistantCreateRequest(
            tenant_id=office.tenant_id,
            name=f"{office.name} Assistant",
            type=AssistantType.GENERAL
        )
        
        return await self.create_assistant_for_office(office, knowledge_base, request)
    
    async def update_assistant(self, assistant: Assistant, updates: Dict[str, Any]) -> Assistant:
        """
        Update an existing assistant.
        
        Args:
            assistant: Existing assistant
            updates: Update data
            
        Returns:
            Updated assistant
            
        Raises:
            ValidationError: If update data is invalid
            VAPIServiceError: If VAPI integration fails
            DatabaseError: If database operation fails
        """
        try:
            # Validate updates
            self._validate_assistant_updates(updates)
            
            # Update VAPI assistant if needed
            if any(field in updates for field in ['name', 'first_message', 'custom_instructions']):
                await self._update_vapi_assistant(assistant, updates)
            
            # Update local assistant record
            for field, value in updates.items():
                if hasattr(assistant.config, field):
                    setattr(assistant.config, field, value)
                elif hasattr(assistant, field):
                    setattr(assistant, field, value)
            
            assistant.updated_at = datetime.utcnow()
            
            # Save to database
            await self.db.update_assistant(assistant)
            
            self.logger.info(f"Updated assistant {assistant.id}")
            return assistant
            
        except Exception as e:
            self.logger.error(f"Error updating assistant {assistant.id}: {e}")
            raise
    
    async def deactivate_assistant(self, assistant: Assistant) -> Assistant:
        """
        Deactivate an assistant.
        
        Args:
            assistant: Assistant to deactivate
            
        Returns:
            Deactivated assistant
            
        Raises:
            VAPIServiceError: If VAPI integration fails
            DatabaseError: If database operation fails
        """
        try:
            # Deactivate in VAPI
            await self.vapi_service.deactivate_assistant(assistant.vapi_assistant_id)
            
            # Update local record
            assistant.status = AssistantStatus.INACTIVE
            assistant.updated_at = datetime.utcnow()
            
            # Save to database
            await self.db.update_assistant(assistant)
            
            self.logger.info(f"Deactivated assistant {assistant.id}")
            return assistant
            
        except Exception as e:
            self.logger.error(f"Error deactivating assistant {assistant.id}: {e}")
            raise
    
    def _validate_assistant_request(self, request: AssistantCreateRequest, office: Clinic) -> None:
        """Validate assistant creation request."""
        if not request.name or not request.name.strip():
            raise ValidationError("Assistant name is required")
        
        if not request.tenant_id or request.tenant_id != office.tenant_id:
            raise ValidationError("Invalid tenant ID")
        
        if request.voice_id:
            valid_voices = [
                "cgSgspJ2msm6clMCkdW9", "pNInz6obpgDQGcFmaJgB",
                "EXAVITQu4vr4xnSDxMaL", "VR6AewLTigWG4xSOukaG"
            ]
            if request.voice_id not in valid_voices:
                raise ValidationError("Invalid voice ID")
    
    def _validate_assistant_updates(self, updates: Dict[str, Any]) -> None:
        """Validate assistant update data."""
        allowed_fields = {
            'name', 'first_message', 'custom_instructions', 'status'
        }
        
        for field in updates.keys():
            if field not in allowed_fields:
                raise ValidationError(f"Invalid update field: {field}")
        
        if 'name' in updates and (not updates['name'] or not updates['name'].strip()):
            raise ValidationError("Assistant name cannot be empty")
    
    def _generate_system_prompt(
        self, 
        office: Clinic, 
        knowledge_base: OfficeKnowledgeBase, 
        request: AssistantCreateRequest
    ) -> str:
        """Generate system prompt with office-specific knowledge."""
        
        # Format office information
        office_info = f"""
OFFICE INFORMATION:
- Name: {office.name}
- Phone: {office.contact_info.phone}
- Email: {office.contact_info.email}
- Address: {office.contact_info.address}
- Website: {office.contact_info.website or 'Not provided'}

BUSINESS HOURS:
- Monday: {office.business_hours.monday or 'Closed'}
- Tuesday: {office.business_hours.tuesday or 'Closed'}
- Wednesday: {office.business_hours.wednesday or 'Closed'}
- Thursday: {office.business_hours.thursday or 'Closed'}
- Friday: {office.business_hours.friday or 'Closed'}
- Saturday: {office.business_hours.saturday or 'Closed'}
- Sunday: {office.business_hours.sunday or 'Closed'}

SERVICES OFFERED:
{self._format_services(office.services)}

APPOINTMENT POLICIES:
- Booking Advance: {office.policies.booking_advance_hours} hours minimum
- Cancellation: {office.policies.cancellation_hours} hours notice required
- Late Cancellation Fee: ${office.policies.late_cancellation_fee or 'None'}
- No-Show Fee: ${office.policies.no_show_fee or 'None'}
"""
        
        # Format FAQ knowledge
        faq_knowledge = self._format_faqs(knowledge_base.faqs)
        
        # Custom instructions
        custom_instructions = "\n".join([f"- {instruction}" for instruction in knowledge_base.custom_instructions])
        
        # Combine into system prompt
        system_prompt = f"""
You are {request.name}, the dental office assistant for {office.name}.

{office_info}

FREQUENTLY ASKED QUESTIONS:
{faq_knowledge}

CUSTOM INSTRUCTIONS:
{custom_instructions}

## Important Guidelines:
- ALWAYS use the provided information to answer questions accurately
- Maintain a professional, caring tone throughout all interactions
- If you don't know something, offer to connect the caller with office staff
- Be helpful and efficient in handling appointment requests
- Use the FAQ information to provide consistent answers
- Remember: You're here to make their dental care experience smooth and professional!

## Appointment Management:
When patients call regarding appointments:
- Use the office information above to provide accurate details
- Follow the appointment policies for booking and cancellation
- Be thorough in collecting required information
- Confirm all appointment details before ending the call
"""
        
        return system_prompt
    
    def _generate_first_message(self, office: Clinic) -> str:
        """Generate a personalized first message for the office."""
        return f"Hi there! I'm your dental office assistant for {office.name}. How can I help you today?"
    
    def _format_services(self, services: List[Any]) -> str:
        """Format services list for system prompt."""
        if not services:
            return "- General dental services"
        
        service_list = []
        for service in services:
            if hasattr(service, 'name'):
                service_list.append(f"- {service.name}")
            else:
                service_list.append(f"- {service}")
        
        return "\n".join(service_list)
    
    def _format_faqs(self, faqs: List[Any]) -> str:
        """Format FAQs for system prompt."""
        if not faqs:
            return "No specific FAQs provided. Use general dental knowledge."
        
        faq_text = []
        for faq in faqs:
            if hasattr(faq, 'question') and hasattr(faq, 'answer'):
                faq_text.append(f"Q: {faq.question}")
                faq_text.append(f"A: {faq.answer}")
                faq_text.append("")  # Empty line for readability
        
        return "\n".join(faq_text)
    
    async def _create_vapi_assistant(self, config: AssistantConfig, office: Clinic) -> str:
        """Create VAPI assistant with the given configuration."""
        try:
            # Prepare VAPI assistant data
            assistant_data = {
                "name": config.name,
                "model": {
                    "provider": config.model.provider,
                    "model": config.model.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": config.model.system_prompt
                        }
                    ]
                },
                "voice": {
                    "provider": config.voice.provider,
                    "voiceId": config.voice.voice_id
                },
                "first_message": config.first_message
            }
            
            # Create assistant via VAPI
            vapi_assistant = await self.vapi_service.create_assistant(assistant_data)
            
            self.logger.info(f"Created VAPI assistant: {vapi_assistant.id}")
            return vapi_assistant.id
            
        except Exception as e:
            self.logger.error(f"Error creating VAPI assistant: {e}")
            raise VAPIServiceError(f"Failed to create VAPI assistant: {str(e)}")
    
    async def _update_vapi_assistant(self, assistant: Assistant, updates: Dict[str, Any]) -> None:
        """Update VAPI assistant with new configuration."""
        try:
            update_data = {}
            
            if 'name' in updates:
                update_data['name'] = updates['name']
            
            if 'first_message' in updates:
                update_data['first_message'] = updates['first_message']
            
            if 'custom_instructions' in updates:
                # Update system prompt with new instructions
                # This would require regenerating the system prompt
                pass
            
            if update_data:
                await self.vapi_service.update_assistant(assistant.vapi_assistant_id, update_data)
                self.logger.info(f"Updated VAPI assistant: {assistant.vapi_assistant_id}")
            
        except Exception as e:
            self.logger.error(f"Error updating VAPI assistant: {e}")
            raise VAPIServiceError(f"Failed to update VAPI assistant: {str(e)}")
