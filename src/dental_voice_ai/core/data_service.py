"""
Data Service for Dental Voice AI

Handles retrieval and structuring of data from database for VAPI integration.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from functools import lru_cache
from dental_voice_ai.core.config import settings

logger = logging.getLogger(__name__)


class DataService:
    """Service for retrieving and structuring data for VAPI."""
    
    def __init__(self):
        """Initialize data service."""
        self.logger = logging.getLogger(__name__)
        logger.info("✅ Data service initialized")
    
    @lru_cache(maxsize=1)
    def get_dental_knowledge_base(self) -> Dict[str, Any]:
        """
        Get structured dental knowledge base data.
        
        Returns:
            Structured dental practice information
        """
        return {
            "practice_info": {
                "name": "Bright Smile Dental Care",
                "address": "123 Dental Street, San Francisco, CA 94102",
                "phone": "+1 (415) 555-0123",
                "email": "info@brightsmiledental.com",
                "website": "https://brightsmiledental.com"
            },
            "office_hours": {
                "monday": {"open": "8:00 AM", "close": "6:00 PM"},
                "tuesday": {"open": "8:00 AM", "close": "6:00 PM"},
                "wednesday": {"open": "8:00 AM", "close": "6:00 PM"},
                "thursday": {"open": "8:00 AM", "close": "6:00 PM"},
                "friday": {"open": "8:00 AM", "close": "5:00 PM"},
                "saturday": {"open": "9:00 AM", "close": "3:00 PM"},
                "sunday": {"open": "Closed", "close": "Closed"}
            },
            "services": {
                "general_dentistry": [
                    "Dental Cleanings",
                    "Cavity Fillings",
                    "Root Canals",
                    "Tooth Extractions",
                    "Dental Exams"
                ],
                "cosmetic_dentistry": [
                    "Teeth Whitening",
                    "Dental Veneers",
                    "Dental Bonding",
                    "Smile Makeovers"
                ],
                "specialty_services": [
                    "Orthodontics",
                    "Periodontics",
                    "Endodontics",
                    "Oral Surgery"
                ]
            },
            "insurance": {
                "accepted_plans": [
                    "Delta Dental",
                    "Blue Cross Blue Shield",
                    "Aetna",
                    "Cigna",
                    "MetLife",
                    "UnitedHealthcare"
                ],
                "payment_options": [
                    "Insurance",
                    "Cash",
                    "Credit Card",
                    "Payment Plans"
                ]
            },
            "pricing": {
                "consultation": "$150",
                "cleaning": "$120",
                "filling": "$200-400",
                "root_canal": "$800-1200",
                "extraction": "$200-400",
                "whitening": "$300-500"
            },
            "emergency_info": {
                "emergency_phone": "+1 (415) 555-0124",
                "after_hours": "Available 24/7 for emergencies",
                "emergency_services": [
                    "Severe Tooth Pain",
                    "Broken Teeth",
                    "Lost Fillings",
                    "Dental Trauma"
                ]
            },
            "appointment_policies": {
                "booking_advance": "24 hours minimum",
                "cancellation_policy": "24 hours notice required",
                "late_cancellation_fee": "$50",
                "no_show_fee": "$75",
                "new_patient_forms": "Available online"
            }
        }
    
    def get_appointment_availability(self, date: str, service_type: str = None) -> Dict[str, Any]:
        """
        Get appointment availability for a specific date.
        
        Args:
            date: Date in YYYY-MM-DD format
            service_type: Type of service (optional)
            
        Returns:
            Available appointment slots
        """
        # This would integrate with your friend's calendar system
        # For now, returning structured mock data
        return {
            "date": date,
            "available_slots": [
                {"time": "9:00 AM", "duration": "60", "service": "General"},
                {"time": "10:30 AM", "duration": "30", "service": "Cleaning"},
                {"time": "2:00 PM", "duration": "90", "service": "Consultation"},
                {"time": "4:00 PM", "duration": "60", "service": "General"}
            ],
            "total_available": 4,
            "next_available_date": self._get_next_available_date(date)
        }
    
    def get_patient_info(self, patient_id: str) -> Dict[str, Any]:
        """
        Get patient information from database.
        
        Args:
            patient_id: Patient identifier
            
        Returns:
            Patient information
        """
        # This would query your database
        return {
            "patient_id": patient_id,
            "name": "John Doe",
            "phone": "+1 (555) 123-4567",
            "email": "john.doe@email.com",
            "date_of_birth": "1985-03-15",
            "insurance": {
                "provider": "Delta Dental",
                "member_id": "DD123456789",
                "group_number": "12345"
            },
            "medical_history": {
                "allergies": ["Latex"],
                "medications": ["None"],
                "conditions": ["None"]
            },
            "dental_history": {
                "last_visit": "2024-01-15",
                "next_appointment": "2024-04-15",
                "treatment_plan": "Regular cleaning and checkup"
            }
        }
    
    def get_appointment_details(self, appointment_id: str) -> Dict[str, Any]:
        """
        Get appointment details from database.
        
        Args:
            appointment_id: Appointment identifier
            
        Returns:
            Appointment details
        """
        # This would query your database
        return {
            "appointment_id": appointment_id,
            "patient_id": "PAT123",
            "patient_name": "John Doe",
            "date": "2024-04-15",
            "time": "10:00 AM",
            "duration": "60",
            "service": "Dental Cleaning",
            "provider": "Dr. Smith",
            "status": "Confirmed",
            "notes": "Regular cleaning appointment",
            "created_at": "2024-03-15T10:30:00Z",
            "updated_at": "2024-03-15T10:30:00Z"
        }
    
    def search_appointments(self, patient_name: str = None, phone: str = None, date: str = None) -> List[Dict[str, Any]]:
        """
        Search appointments by various criteria.
        
        Args:
            patient_name: Patient name to search
            phone: Phone number to search
            date: Date to search
            
        Returns:
            List of matching appointments
        """
        # This would query your database
        return [
            {
                "appointment_id": "APT001",
                "patient_name": "John Doe",
                "phone": "+1 (555) 123-4567",
                "date": "2024-04-15",
                "time": "10:00 AM",
                "service": "Dental Cleaning",
                "status": "Confirmed"
            },
            {
                "appointment_id": "APT002",
                "patient_name": "Jane Smith",
                "phone": "+1 (555) 987-6543",
                "date": "2024-04-16",
                "time": "2:00 PM",
                "service": "Consultation",
                "status": "Confirmed"
            }
        ]
    
    def get_service_information(self, service_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            Service information
        """
        services = {
            "dental_cleaning": {
                "name": "Dental Cleaning",
                "duration": "60 minutes",
                "price": "$120",
                "description": "Professional teeth cleaning and examination",
                "preparation": "No special preparation required",
                "aftercare": "Continue regular brushing and flossing"
            },
            "consultation": {
                "name": "Dental Consultation",
                "duration": "30 minutes",
                "price": "$150",
                "description": "Comprehensive dental examination and treatment planning",
                "preparation": "Bring any relevant medical records",
                "aftercare": "Follow recommended treatment plan"
            },
            "filling": {
                "name": "Dental Filling",
                "duration": "45-90 minutes",
                "price": "$200-400",
                "description": "Restore damaged teeth with composite or amalgam fillings",
                "preparation": "Avoid eating 2 hours before",
                "aftercare": "Avoid hard foods for 24 hours"
            }
        }
        
        return services.get(service_name.lower().replace(" ", "_"), {
            "name": service_name,
            "duration": "Varies",
            "price": "Contact office",
            "description": "Please contact our office for specific information",
            "preparation": "Contact office",
            "aftercare": "Contact office"
        })
    
    def _get_next_available_date(self, current_date: str) -> str:
        """Get the next available date for appointments."""
        current = datetime.strptime(current_date, "%Y-%m-%d")
        next_date = current + timedelta(days=1)
        return next_date.strftime("%Y-%m-%d")
    
    def format_for_vapi(self, data_type: str, data: Any) -> str:
        """
        Format data for VAPI consumption.
        
        Args:
            data_type: Type of data (knowledge_base, availability, patient, etc.)
            data: Data to format
            
        Returns:
            Formatted string for VAPI
        """
        if data_type == "knowledge_base":
            return self._format_knowledge_base(data)
        elif data_type == "availability":
            return self._format_availability(data)
        elif data_type == "patient":
            return self._format_patient_info(data)
        elif data_type == "appointment":
            return self._format_appointment_details(data)
        else:
            return str(data)
    
    def _format_knowledge_base(self, data: Dict[str, Any]) -> str:
        """Format knowledge base data for VAPI."""
        kb = data
        return f"""
DENTAL_KNOWLEDGE_BASE:

Practice Information:
- Name: {kb['practice_info']['name']}
- Address: {kb['practice_info']['address']}
- Phone: {kb['practice_info']['phone']}
- Email: {kb['practice_info']['email']}

Office Hours:
- Monday-Friday: {kb['office_hours']['monday']['open']} - {kb['office_hours']['monday']['close']}
- Saturday: {kb['office_hours']['saturday']['open']} - {kb['office_hours']['saturday']['close']}
- Sunday: {kb['office_hours']['sunday']['open']}

Services Offered:
- General Dentistry: {', '.join(kb['services']['general_dentistry'])}
- Cosmetic Dentistry: {', '.join(kb['services']['cosmetic_dentistry'])}
- Specialty Services: {', '.join(kb['services']['specialty_services'])}

Insurance Accepted:
- {', '.join(kb['insurance']['accepted_plans'])}

Pricing (approximate):
- Consultation: {kb['pricing']['consultation']}
- Cleaning: {kb['pricing']['cleaning']}
- Filling: {kb['pricing']['filling']}

Emergency Information:
- Emergency Phone: {kb['emergency_info']['emergency_phone']}
- After Hours: {kb['emergency_info']['after_hours']}

Appointment Policies:
- Booking Advance: {kb['appointment_policies']['booking_advance']}
- Cancellation Policy: {kb['appointment_policies']['cancellation_policy']}
- Late Cancellation Fee: {kb['appointment_policies']['late_cancellation_fee']}
"""
    
    def _format_availability(self, data: Dict[str, Any]) -> str:
        """Format availability data for VAPI."""
        slots = data['available_slots']
        slot_list = "\n".join([f"- {slot['time']} ({slot['duration']} min, {slot['service']})" for slot in slots])
        
        return f"""
Available Appointments for {data['date']}:
{slot_list}

Total Available Slots: {data['total_available']}
Next Available Date: {data['next_available_date']}
"""
    
    def _format_patient_info(self, data: Dict[str, Any]) -> str:
        """Format patient information for VAPI."""
        return f"""
Patient Information:
- Name: {data['name']}
- Phone: {data['phone']}
- Email: {data['email']}
- Insurance: {data['insurance']['provider']} (Member ID: {data['insurance']['member_id']})
- Last Visit: {data['dental_history']['last_visit']}
- Next Appointment: {data['dental_history']['next_appointment']}
- Treatment Plan: {data['dental_history']['treatment_plan']}
"""
    
    def _format_appointment_details(self, data: Dict[str, Any]) -> str:
        """Format appointment details for VAPI."""
        return f"""
Appointment Details:
- ID: {data['appointment_id']}
- Patient: {data['patient_name']}
- Date: {data['date']}
- Time: {data['time']}
- Duration: {data['duration']} minutes
- Service: {data['service']}
- Provider: {data['provider']}
- Status: {data['status']}
- Notes: {data['notes']}
"""


# Global data service instance
data_service: Optional[DataService] = None


def get_data_service() -> DataService:
    """Get the global data service instance."""
    global data_service
    if data_service is None:
        data_service = DataService()
    return data_service
