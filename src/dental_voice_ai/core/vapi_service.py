"""
VAPI SDK Service for Dental Voice AI

Handles assistant creation, management, and configuration using VAPI Server SDK.
"""

import logging
import requests
from typing import Dict, Any, Optional
from vapi import Vapi
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dental_voice_ai.core.config import settings
from dental_voice_ai.core.data_service import get_data_service
from dental_voice_ai.core.exceptions import VAPIServiceError, NetworkError

logger = logging.getLogger(__name__)


class VAPIService:
    """Service for managing VAPI assistants and calls using VAPI Server SDK."""
    
    def __init__(self):
        """Initialize VAPI SDK client with connection pooling."""
        self.api_key = settings.VAPI_API_KEY
        if not self.api_key:
            raise ValueError("VAPI_API_KEY environment variable is required")
        
        self.client = Vapi(token=self.api_key)
        self.base_url = "https://api.vapi.ai"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Setup session with connection pooling and retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=20)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self.data_service = get_data_service()
        logger.info("✅ VAPI SDK client initialized with connection pooling")
    
    def create_dental_assistant(self, name: str = "Dental Assistant") -> str:
        """
        Create a dental assistant using VAPI SDK with structured data integration.
        
        Args:
            name: Name for the assistant
            
        Returns:
            Assistant ID
        """
        try:
            # Get structured knowledge base data
            knowledge_base = self.data_service.get_dental_knowledge_base()
            formatted_kb = self.data_service.format_for_vapi("knowledge_base", knowledge_base)
            
            assistant = self.client.assistants.create(
                name=name,
                model={
                    "provider": "openai",
                    "model": "gpt-4o",
                    "messages": [
                        {
                            "role": "system", 
                            "content": self._get_dental_system_prompt(formatted_kb)
                        }
                    ],
                },
                voice={
                    "provider": "11labs", 
                    "voiceId": "cgSgspJ2msm6clMCkdW9"
                },
                first_message="Hi there! I'm Sam, your dental office assistant. How can I help you today?"
            )
            
            assistant_id = assistant.id
            logger.info(f"✅ Created dental assistant with structured data: {assistant_id}")
            return assistant_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create dental assistant: {e}")
            raise
    
    def update_assistant_with_data(self, assistant_id: str, data_type: str, **kwargs) -> Dict[str, Any]:
        """
        Update assistant with specific data from database.
        
        Args:
            assistant_id: ID of the assistant to update
            data_type: Type of data to update (availability, patient, appointment, etc.)
            **kwargs: Additional parameters for data retrieval
            
        Returns:
            Updated assistant details
        """
        try:
            # Get structured data based on type
            if data_type == "availability":
                date = kwargs.get("date")
                service_type = kwargs.get("service_type")
                data = self.data_service.get_appointment_availability(date, service_type)
                formatted_data = self.data_service.format_for_vapi("availability", data)
                
            elif data_type == "patient":
                patient_id = kwargs.get("patient_id")
                data = self.data_service.get_patient_info(patient_id)
                formatted_data = self.data_service.format_for_vapi("patient", data)
                
            elif data_type == "appointment":
                appointment_id = kwargs.get("appointment_id")
                data = self.data_service.get_appointment_details(appointment_id)
                formatted_data = self.data_service.format_for_vapi("appointment", data)
                
            elif data_type == "service":
                service_name = kwargs.get("service_name")
                data = self.data_service.get_service_information(service_name)
                formatted_data = f"Service Information:\n{str(data)}"
                
            else:
                raise ValueError(f"Unknown data type: {data_type}")
            
            # Update assistant with new data
            update_message = {
                "role": "system",
                "content": f"Updated information for {data_type}:\n{formatted_data}"
            }
            
            assistant = self.client.assistants.update(
                assistant_id,
                model={
                    "messages": [update_message]
                }
            )
            
            logger.info(f"✅ Updated assistant {assistant_id} with {data_type} data")
            return assistant.dict()
            
        except Exception as e:
            logger.error(f"❌ Failed to update assistant with {data_type} data: {e}")
            raise
    
    def get_structured_data(self, data_type: str, **kwargs) -> str:
        """
        Get structured data formatted for VAPI consumption.
        
        Args:
            data_type: Type of data to retrieve
            **kwargs: Parameters for data retrieval
            
        Returns:
            Formatted data string
        """
        try:
            if data_type == "knowledge_base":
                data = self.data_service.get_dental_knowledge_base()
                return self.data_service.format_for_vapi("knowledge_base", data)
                
            elif data_type == "availability":
                date = kwargs.get("date")
                service_type = kwargs.get("service_type")
                data = self.data_service.get_appointment_availability(date, service_type)
                return self.data_service.format_for_vapi("availability", data)
                
            elif data_type == "patient":
                patient_id = kwargs.get("patient_id")
                data = self.data_service.get_patient_info(patient_id)
                return self.data_service.format_for_vapi("patient", data)
                
            elif data_type == "appointment":
                appointment_id = kwargs.get("appointment_id")
                data = self.data_service.get_appointment_details(appointment_id)
                return self.data_service.format_for_vapi("appointment", data)
                
            elif data_type == "service":
                service_name = kwargs.get("service_name")
                data = self.data_service.get_service_information(service_name)
                return f"Service Information:\n{str(data)}"
                
            else:
                raise ValueError(f"Unknown data type: {data_type}")
                
        except Exception as e:
            logger.error(f"❌ Failed to get structured data for {data_type}: {e}")
            raise
    
    def create_phone_number(self, assistant_id: str, area_code: str = "415") -> str:
        """
        Create a phone number for an assistant.
        
        Args:
            assistant_id: ID of the assistant
            area_code: Desired area code for the phone number
            
        Returns:
            Phone number ID
        """
        try:
            response = self.session.post(
                f"{self.base_url}/phone-number",
                headers=self.headers,
                json={
                    "provider": "vapi",
                    "assistantId": assistant_id,
                    "numberDesiredAreaCode": area_code,
                },
                timeout=settings.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            phone_number_data = response.json()
            phone_number_id = phone_number_data["id"]
            logger.info(f"✅ Created phone number: {phone_number_id}")
            return phone_number_id
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error creating phone number: {e}")
            raise NetworkError(f"Failed to create phone number: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Failed to create phone number: {e}")
            raise VAPIServiceError(f"Failed to create phone number: {str(e)}")
    
    def create_call(self, assistant_id: str, phone_number_id: str, customer_phone: str = None) -> str:
        """
        Create a call using an existing assistant and phone number.
        
        Args:
            assistant_id: ID of the assistant to use
            phone_number_id: ID of the phone number to use
            customer_phone: Phone number to call (E.164 format, e.g., +1234567890)
            
        Returns:
            Call ID
        """
        try:
            # Prepare call parameters
            call_params = {
                "assistant_id": assistant_id,
                "phone_number_id": phone_number_id
            }
            
            # Add customer information if provided
            if customer_phone:
                call_params["customer"] = {
                    "number": customer_phone
                }
            
            call = self.client.calls.create(**call_params)
            
            call_id = call.id
            logger.info(f"✅ Created call: {call_id}")
            return call_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create call: {e}")
            raise
    
    def get_assistant(self, assistant_id: str) -> Dict[str, Any]:
        """
        Get assistant details.
        
        Args:
            assistant_id: ID of the assistant
            
        Returns:
            Assistant details
        """
        try:
            assistant = self.client.assistants.get(assistant_id)
            return assistant.dict()
        except Exception as e:
            logger.error(f"❌ Failed to get assistant {assistant_id}: {e}")
            raise
    
    def list_assistants(self) -> list:
        """
        List all assistants.
        
        Returns:
            List of assistants
        """
        try:
            assistants = self.client.assistants.list()
            return [assistant.dict() for assistant in assistants]
        except Exception as e:
            logger.error(f"❌ Failed to list assistants: {e}")
            raise
    
    def update_assistant(self, assistant_id: str, **kwargs) -> Dict[str, Any]:
        """
        Update assistant configuration.
        
        Args:
            assistant_id: ID of the assistant
            **kwargs: Fields to update
            
        Returns:
            Updated assistant details
        """
        try:
            assistant = self.client.assistants.update(assistant_id, **kwargs)
            logger.info(f"✅ Updated assistant: {assistant_id}")
            return assistant.dict()
        except Exception as e:
            logger.error(f"❌ Failed to update assistant {assistant_id}: {e}")
            raise
    
    def delete_assistant(self, assistant_id: str) -> bool:
        """
        Delete an assistant.
        
        Args:
            assistant_id: ID of the assistant
            
        Returns:
            True if successful
        """
        try:
            self.client.assistants.delete(assistant_id)
            logger.info(f"✅ Deleted assistant: {assistant_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to delete assistant {assistant_id}: {e}")
            raise
    
    def _get_dental_system_prompt(self, knowledge_base: str = "") -> str:
        """Get the system prompt for dental assistant with structured data."""
        return f"""
You are Sam, the dental office assistant for Bright Smile Dental Care. 

CRITICAL: You have access to the following structured dental knowledge base. Use this information to provide accurate, up-to-date information about our practice.

{knowledge_base}

## Appointment Management
When patients call regarding schedule, reschedule, or canceling appointments:
important: use this tenant id for the post and get methods: 7a57af74-68c3-4de1-a3c2-01b0e844d667

### For Booking Appointments:
1. **Use `get_tenant_appointment_availability` tool** to check available slots
2. **Ask**: "Are you a new patient to Wellness Partners, or have you visited us before?"
3. **Collect required information**:
   - Patient's full name
   - Phone number
   - Preferred appointment date and time
   - Reason for visit (required)
4. **Use `post_tenant_apointment` tool** to store the appointment data
5. **Confirm booking** with appointment ID

### For Canceling Appointments:
1. **Collect patient identification** (name, phone number)
2. **Locate their appointment**
3. **Use `post_tenant_apointment` tool** to update status to "cancelled"
4. **Confirm cancellation** and explain any policies

## Important Guidelines
- ALWAYS use the appropriate tools for appointment management
- Use GET method to check availability, POST method to store/update appointments
- Maintain a professional, caring tone throughout
- Always ensure you're providing the most current information from the knowledge base
- Be thorough in collecting all required information before using the tools
- Use the structured data provided to give accurate information about services, pricing, and policies

Remember: You're here to make their dental care experience smooth, professional, and efficient!
"""


# Global VAPI service instance
vapi_service: Optional[VAPIService] = None


def get_vapi_service() -> VAPIService:
    """Get the global VAPI service instance."""
    global vapi_service
    if vapi_service is None:
        vapi_service = VAPIService()
    return vapi_service
