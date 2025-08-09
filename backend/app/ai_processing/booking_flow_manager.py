"""
Booking Flow Manager for Dental Voice AI

Manages the conversational booking flow to gather customer information
and guide users through the appointment booking process.
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)

class BookingStep(str, Enum):
    """Steps in the booking flow."""
    INITIAL_INTENT = "initial_intent"
    GATHER_NAME = "gather_name"
    GATHER_PHONE = "gather_phone"
    GATHER_SERVICE = "gather_service"
    CONFIRM_DETAILS = "confirm_details"
    CHECK_AVAILABILITY = "check_availability"
    SELECT_SLOT = "select_slot"
    FINAL_CONFIRMATION = "final_confirmation"
    COMPLETED = "completed"

@dataclass
class BookingSession:
    """Represents an active booking session."""
    session_id: str
    call_id: str
    current_step: BookingStep
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    service_type: Optional[str] = None
    urgency: str = "normal"
    preferred_date: Optional[str] = None
    preferred_time: Optional[str] = None
    selected_slot: Optional[Dict[str, Any]] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

class BookingFlowManager:
    """Manages the booking flow conversation."""
    
    def __init__(self):
        self.active_sessions: Dict[str, BookingSession] = {}
    
    def start_booking_session(self, call_id: str) -> str:
        """Start a new booking session."""
        session_id = f"booking_{call_id}_{int(datetime.utcnow().timestamp())}"
        session = BookingSession(
            session_id=session_id,
            call_id=call_id,
            current_step=BookingStep.INITIAL_INTENT
        )
        self.active_sessions[session_id] = session
        logger.info(f"🆕 Started booking session: {session_id}")
        return session_id
    
    def get_next_question(self, session_id: str, user_response: str = None) -> Dict[str, Any]:
        """Get the next question based on current step and user response."""
        session = self.active_sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
        
        # Update session with user response
        if user_response:
            self._update_session_with_response(session, user_response)
        
        # Determine next step and question
        if session.current_step == BookingStep.INITIAL_INTENT:
            session.current_step = BookingStep.GATHER_NAME
            return {
                "question": "Great! I'd be happy to help you schedule an appointment. What's your name?",
                "step": session.current_step.value,
                "session_id": session_id,
                "requires_response": True,
                "step_description": "Gathering customer name"
            }
        
        elif session.current_step == BookingStep.GATHER_NAME:
            if not session.customer_name:
                return {
                    "question": "I didn't catch your name. Could you please tell me your full name?",
                    "step": session.current_step.value,
                    "session_id": session_id,
                    "requires_response": True,
                    "step_description": "Gathering customer name"
                }
            
            session.current_step = BookingStep.GATHER_PHONE
            return {
                "question": f"Thank you, {session.customer_name}. What's the best phone number to reach you?",
                "step": session.current_step.value,
                "session_id": session_id,
                "requires_response": True,
                "step_description": "Gathering phone number"
            }
        
        elif session.current_step == BookingStep.GATHER_PHONE:
            if not session.customer_phone:
                return {
                    "question": "I didn't get your phone number. Could you please repeat it?",
                    "step": session.current_step.value,
                    "session_id": session_id,
                    "requires_response": True,
                    "step_description": "Gathering phone number"
                }
            
            session.current_step = BookingStep.GATHER_SERVICE
            return {
                "question": "What type of appointment do you need? For example: cleaning, checkup, consultation, or something specific?",
                "step": session.current_step.value,
                "session_id": session_id,
                "requires_response": True,
                "step_description": "Gathering service type"
            }
        
        elif session.current_step == BookingStep.GATHER_SERVICE:
            if not session.service_type:
                return {
                    "question": "I didn't catch what service you need. Could you please tell me again?",
                    "step": session.current_step.value,
                    "session_id": session_id,
                    "requires_response": True,
                    "step_description": "Gathering service type"
                }
            
            session.current_step = BookingStep.CONFIRM_DETAILS
            return {
                "question": self._generate_confirmation_question(session),
                "step": session.current_step.value,
                "session_id": session_id,
                "requires_response": True,
                "step_description": "Confirming details",
                "confirmation_data": {
                    "name": session.customer_name,
                    "phone": session.customer_phone,
                    "service": session.service_type
                }
            }
        
        elif session.current_step == BookingStep.CONFIRM_DETAILS:
            # Check if user confirmed or needs changes
            if self._is_confirmation_positive(user_response):
                session.current_step = BookingStep.CHECK_AVAILABILITY
                return {
                    "question": "Perfect! Let me check our available appointment times...",
                    "step": session.current_step.value,
                    "session_id": session_id,
                    "requires_response": False,
                    "step_description": "Checking availability",
                    "next_action": "check_availability"
                }
            else:
                # User wants to change something - go back to appropriate step
                return self._handle_confirmation_changes(session, user_response)
        
        return {"error": "Unknown step"}
    
    def _update_session_with_response(self, session: BookingSession, response: str):
        """Update session with user's response."""
        if session.current_step == BookingStep.GATHER_NAME:
            session.customer_name = response.strip()
        elif session.current_step == BookingStep.GATHER_PHONE:
            # Clean and validate phone number
            session.customer_phone = self._clean_phone_number(response)
        elif session.current_step == BookingStep.GATHER_SERVICE:
            session.service_type = self._normalize_service_type(response)
        
        session.updated_at = datetime.utcnow()
    
    def _clean_phone_number(self, phone: str) -> str:
        """Clean and format phone number."""
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)
        
        # Handle different formats
        if len(digits_only) == 10:
            return f"({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:]}"
        elif len(digits_only) == 11 and digits_only[0] == '1':
            return f"({digits_only[1:4]}) {digits_only[3:6]}-{digits_only[6:]}"
        else:
            return phone.strip()  # Return original if can't format
    
    def _normalize_service_type(self, service: str) -> str:
        """Normalize service type to standard categories."""
        service_lower = service.lower()
        
        service_mapping = {
            "cleaning": ["cleaning", "hygiene", "prophylaxis", "routine cleaning"],
            "checkup": ["checkup", "exam", "consultation", "inspection", "evaluation"],
            "emergency": ["emergency", "urgent", "pain", "broken", "lost"],
            "filling": ["filling", "cavity", "decay", "hole in tooth"],
            "crown": ["crown", "cap", "restoration", "dental crown"],
            "root_canal": ["root canal", "endodontic", "nerve treatment"],
            "extraction": ["extraction", "pull tooth", "remove tooth", "take out"],
            "whitening": ["whitening", "bleaching", "teeth whitening", "brighten"],
            "braces": ["braces", "orthodontic", "straighten teeth", "alignment"],
            "implant": ["implant", "dental implant", "replacement tooth"]
        }
        
        for standard_service, variations in service_mapping.items():
            if any(var in service_lower for var in variations):
                return standard_service
        
        return service.strip()  # Return original if no match
    
    def _generate_confirmation_question(self, session: BookingSession) -> str:
        """Generate confirmation question with gathered details."""
        return (
            f"Let me confirm your details:\n"
            f"• Name: {session.customer_name}\n"
            f"• Phone: {session.customer_phone}\n"
            f"• Service: {session.service_type}\n\n"
            f"Is this correct? Please say 'yes' to confirm or 'no' if you need to change anything."
        )
    
    def _is_confirmation_positive(self, response: str) -> bool:
        """Check if user confirmed positively."""
        positive_words = ["yes", "yeah", "yep", "correct", "right", "that's right", "sounds good"]
        return any(word in response.lower() for word in positive_words)
    
    def _handle_confirmation_changes(self, session: BookingSession, response: str) -> Dict[str, Any]:
        """Handle user wanting to change confirmation details."""
        response_lower = response.lower()
        
        if "name" in response_lower:
            session.current_step = BookingStep.GATHER_NAME
            return {
                "question": "What would you like to change your name to?",
                "step": session.current_step.value,
                "session_id": session.session_id,
                "requires_response": True,
                "step_description": "Updating customer name"
            }
        elif "phone" in response_lower or "number" in response_lower:
            session.current_step = BookingStep.GATHER_PHONE
            return {
                "question": "What's the correct phone number?",
                "step": session.current_step.value,
                "session_id": session.session_id,
                "requires_response": True,
                "step_description": "Updating phone number"
            }
        elif "service" in response_lower or "appointment" in response_lower:
            session.current_step = BookingStep.GATHER_SERVICE
            return {
                "question": "What type of appointment do you need?",
                "step": session.current_step.value,
                "session_id": session.session_id,
                "requires_response": True,
                "step_description": "Updating service type"
            }
        else:
            # Generic response for unclear changes
            return {
                "question": "I'm not sure what you'd like to change. Could you please specify: name, phone, or service?",
                "step": session.current_step.value,
                "session_id": session.session_id,
                "requires_response": True,
                "step_description": "Clarifying changes"
            }
    
    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get summary of current booking session."""
        session = self.active_sessions.get(session_id)
        if not session:
            return None
        
        return {
            "session_id": session.session_id,
            "current_step": session.current_step.value,
            "customer_name": session.customer_name,
            "customer_phone": session.customer_phone,
            "service_type": session.service_type,
            "urgency": session.urgency,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat()
        }
    
    def end_session(self, session_id: str) -> bool:
        """End a booking session."""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            logger.info(f"🔚 Ended booking session: {session_id}")
            return True
        return False
    
    def get_active_sessions_count(self) -> int:
        """Get count of active booking sessions."""
        return len(self.active_sessions)