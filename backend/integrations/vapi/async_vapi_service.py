
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
Async VAPI Service for Healthcare Voice AI

Handles assistant creation, management, and configuration using async HTTP requests
instead of the synchronous VAPI SDK.
"""

import logging
import httpx
from typing import Dict, Any, Optional
from core.config import settings
# Data service removed - using direct database operations

# Create a VAPI-specific error handler decorator
def vapi_error_handler(func):
    """Decorator for VAPI service error handling."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"VAPI service error in {func.__name__}: {e}")
            raise
    return wrapper

# Simple circuit breaker decorator (can be enhanced later)
def circuit_breaker_protection(func):
    """Simple circuit breaker decorator for VAPI service calls."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Circuit breaker triggered for {func.__name__}: {e}")
            raise
    return wrapper

# Simple rate limiting decorator (can be enhanced later)
def rate_limit_protection(func):
    """Simple rate limiting decorator for VAPI service calls."""
    def wrapper(*args, **kwargs):
        # For now, just pass through - can be enhanced with actual rate limiting
        return func(*args, **kwargs)
    return wrapper

logger = logging.getLogger(__name__)


class AsyncVAPIService:
    """
    Async service for managing VAPI assistants and calls using httpx.
    
    Provides non-blocking HTTP requests for better performance and scalability.
    """
    
    def __init__(self):
        """Initialize async VAPI service with HTTP client."""
        self.api_key = settings.VAPI_API_KEY
        if not self.api_key:
            raise ValueError("VAPI_API_KEY environment variable is required")
        
        self.base_url = "https://api.vapi.ai"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        self.http_client: Optional[httpx.AsyncClient] = None
        # Data service removed - using direct database operations when needed
        logger.info("✅ AsyncVAPIService initialized")

    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client with proper configuration."""
        if not self.http_client:
            self.http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                limits=httpx.Limits(max_keepalive_connections=20, max_connections=100),
                headers=self.headers
            )
        return self.http_client

    @vapi_error_handler
    @circuit_breaker_protection
    @rate_limit_protection
    async def create_dental_assistant(self, name: str = "Dental Assistant") -> str:
        """
        Create a dental assistant using async HTTP requests with structured data integration.

        Args:
            name: Name for the assistant

        Returns:
            Assistant ID
        """
        try:
            # Get structured knowledge base data
            knowledge_base = self.data_service.get_dental_knowledge_base()
            formatted_kb = self.data_service.format_for_vapi("knowledge_base", knowledge_base)

            assistant_data = {
                "name": name,
                "model": {
                    "provider": "openai",
                    "model": "gpt-4o",
                    "messages": [
                        {
                            "role": "system",
                            "content": self._get_dental_system_prompt(formatted_kb)
                        }
                    ],
                },
                "voice": {
                    "provider": "11labs",
                    "voiceId": "cgSgspJ2msm6clMCkdW9"
                },
                "firstMessage": "Hi there! I'm Sam, your dental office assistant. How can I help you today?"
            }

            client = await self._get_http_client()
            response = await client.post(
                f"{self.base_url}/assistant",
                json=assistant_data
            )
            response.raise_for_status()

            assistant_response = response.json()
            assistant_id = assistant_response["id"]
            logger.info(f"✅ Created dental assistant with structured data: {assistant_id}")
            return assistant_id

        except httpx.HTTPError as e:
            logger.error(f"❌ HTTP error creating dental assistant: {e}")
            raise NetworkError(f"Failed to create dental assistant: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Failed to create dental assistant: {e}")
            raise VAPIServiceError(f"Failed to create dental assistant: {str(e)}")

    @vapi_error_handler
    @circuit_breaker_protection
    @rate_limit_protection
    async def create_phone_number(self, assistant_id: str, area_code: str = "415") -> str:
        """
        Create a phone number for an assistant.

        Args:
            assistant_id: ID of the assistant
            area_code: Desired area code for the phone number

        Returns:
            Phone number ID
        """
        try:
            phone_data = {
                "provider": "vapi",
                "assistantId": assistant_id,
                "numberDesiredAreaCode": area_code,
            }

            client = await self._get_http_client()
            response = await client.post(
                f"{self.base_url}/phone-number",
                json=phone_data
            )
            response.raise_for_status()

            phone_response = response.json()
            phone_number_id = phone_response["id"]
            logger.info(f"✅ Created phone number: {phone_number_id}")
            return phone_number_id

        except httpx.HTTPError as e:
            logger.error(f"❌ HTTP error creating phone number: {e}")
            raise NetworkError(f"Failed to create phone number: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Failed to create phone number: {e}")
            raise VAPIServiceError(f"Failed to create phone number: {str(e)}")

    @vapi_error_handler
    @circuit_breaker_protection
    @rate_limit_protection
    async def get_assistant(self, assistant_id: str) -> Dict[str, Any]:
        """
        Get assistant details.

        Args:
            assistant_id: ID of the assistant

        Returns:
            Assistant data
        """
        try:
            client = await self._get_http_client()
            response = await client.get(f"{self.base_url}/assistant/{assistant_id}")
            response.raise_for_status()

            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"❌ HTTP error getting assistant: {e}")
            raise NetworkError(f"Failed to get assistant: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Failed to get assistant: {e}")
            raise VAPIServiceError(f"Failed to get assistant: {str(e)}")

    @vapi_error_handler
    @circuit_breaker_protection
    @rate_limit_protection
    async def update_assistant(self, assistant_id: str, **updates) -> Dict[str, Any]:
        """
        Update assistant configuration.

        Args:
            assistant_id: ID of the assistant
            **updates: Fields to update

        Returns:
            Updated assistant data
        """
        try:
            client = await self._get_http_client()
            response = await client.patch(
                f"{self.base_url}/assistant/{assistant_id}",
                json=updates
            )
            response.raise_for_status()

            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"❌ HTTP error updating assistant: {e}")
            raise NetworkError(f"Failed to update assistant: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Failed to update assistant: {e}")
            raise VAPIServiceError(f"Failed to update assistant: {str(e)}")

    @vapi_error_handler
    @circuit_breaker_protection
    @rate_limit_protection
    async def delete_assistant(self, assistant_id: str) -> bool:
        """
        Delete an assistant.

        Args:
            assistant_id: ID of the assistant

        Returns:
            True if successful
        """
        try:
            client = await self._get_http_client()
            response = await client.delete(f"{self.base_url}/assistant/{assistant_id}")
            response.raise_for_status()

            logger.info(f"✅ Deleted assistant: {assistant_id}")
            return True

        except httpx.HTTPError as e:
            logger.error(f"❌ HTTP error deleting assistant: {e}")
            raise NetworkError(f"Failed to delete assistant: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Failed to delete assistant: {e}")
            raise VAPIServiceError(f"Failed to delete assistant: {str(e)}")

    @vapi_error_handler
    @circuit_breaker_protection
    @rate_limit_protection
    async def list_assistants(self) -> Dict[str, Any]:
        """
        List all assistants.

        Returns:
            List of assistants
        """
        try:
            client = await self._get_http_client()
            response = await client.get(f"{self.base_url}/assistant")
            response.raise_for_status()

            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"❌ HTTP error listing assistants: {e}")
            raise NetworkError(f"Failed to list assistants: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Failed to list assistants: {e}")
            raise VAPIServiceError(f"Failed to list assistants: {str(e)}")

    @vapi_error_handler
    @circuit_breaker_protection
    @rate_limit_protection
    async def create_call(
        self, 
        assistant_id: str, 
        phone_number_id: str, 
        customer_phone: str
    ) -> Dict[str, Any]:
        """
        Create a new call.

        Args:
            assistant_id: ID of the assistant to use
            phone_number_id: ID of the phone number to use
            customer_phone: Phone number to call (E.164 format)

        Returns:
            Call data
        """
        try:
            call_data = {
                "assistantId": assistant_id,
                "phoneNumberId": phone_number_id,
                "customer": {
                    "number": customer_phone
                }
            }

            client = await self._get_http_client()
            response = await client.post(
                f"{self.base_url}/call",
                json=call_data
            )
            response.raise_for_status()

            call_response = response.json()
            logger.info(f"✅ Created call: {call_response.get('id', 'unknown')}")
            return call_response

        except httpx.HTTPError as e:
            logger.error(f"❌ HTTP error creating call: {e}")
            raise NetworkError(f"Failed to create call: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Failed to create call: {e}")
            raise VAPIServiceError(f"Failed to create call: {str(e)}")

    @vapi_error_handler
    @circuit_breaker_protection
    @rate_limit_protection
    async def get_call(self, call_id: str) -> Dict[str, Any]:
        """
        Get call details.

        Args:
            call_id: ID of the call

        Returns:
            Call data
        """
        try:
            client = await self._get_http_client()
            response = await client.get(f"{self.base_url}/call/{call_id}")
            response.raise_for_status()

            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"❌ HTTP error getting call: {e}")
            raise NetworkError(f"Failed to get call: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Failed to get call: {e}")
            raise VAPIServiceError(f"Failed to get call: {str(e)}")

    @vapi_error_handler
    @circuit_breaker_protection
    @rate_limit_protection
    async def list_calls(self) -> Dict[str, Any]:
        """
        List all calls.

        Returns:
            List of calls
        """
        try:
            client = await self._get_http_client()
            response = await client.get(f"{self.base_url}/call")
            response.raise_for_status()

            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"❌ HTTP error listing calls: {e}")
            raise NetworkError(f"Failed to list calls: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Failed to list calls: {e}")
            raise VAPIServiceError(f"Failed to list calls: {str(e)}")

    @vapi_error_handler
    @circuit_breaker_protection
    @rate_limit_protection
    async def get_phone_number(self, phone_number_id: str) -> Dict[str, Any]:
        """
        Get phone number details.

        Args:
            phone_number_id: ID of the phone number

        Returns:
            Phone number data
        """
        try:
            client = await self._get_http_client()
            response = await client.get(f"{self.base_url}/phone-number/{phone_number_id}")
            response.raise_for_status()

            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"❌ HTTP error getting phone number: {e}")
            raise NetworkError(f"Failed to get phone number: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Failed to get phone number: {e}")
            raise VAPIServiceError(f"Failed to get phone number: {str(e)}")

    @vapi_error_handler
    @circuit_breaker_protection
    @rate_limit_protection
    async def list_phone_numbers(self) -> Dict[str, Any]:
        """
        List all phone numbers.

        Returns:
            List of phone numbers
        """
        try:
            client = await self._get_http_client()
            response = await client.get(f"{self.base_url}/phone-number")
            response.raise_for_status()

            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"❌ HTTP error listing phone numbers: {e}")
            raise NetworkError(f"Failed to list phone numbers: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Failed to list phone numbers: {e}")
            raise VAPIServiceError(f"Failed to list phone numbers: {str(e)}")

    @vapi_error_handler
    @circuit_breaker_protection
    @rate_limit_protection
    async def delete_phone_number(self, phone_number_id: str) -> bool:
        """
        Delete a phone number.

        Args:
            phone_number_id: ID of the phone number

        Returns:
            True if successful
        """
        try:
            client = await self._get_http_client()
            response = await client.delete(f"{self.base_url}/phone-number/{phone_number_id}")
            response.raise_for_status()

            logger.info(f"✅ Deleted phone number: {phone_number_id}")
            return True

        except httpx.HTTPError as e:
            logger.error(f"❌ HTTP error deleting phone number: {e}")
            raise NetworkError(f"Failed to delete phone number: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Failed to delete phone number: {e}")
            raise VAPIServiceError(f"Failed to delete phone number: {str(e)}")

    def _get_dental_system_prompt(self, knowledge_base: Dict[str, Any]) -> str:
        """
        Generate dental system prompt with knowledge base integration.

        Args:
            knowledge_base: Structured knowledge base data

        Returns:
            Formatted system prompt
        """
        prompt_parts = [
            "You are Sam, a professional dental office assistant powered by AI.",
            "Your role is to help patients with inquiries, appointment scheduling, and general dental practice information.",
            "",
            "## Practice Information:",
            f"Practice Name: {knowledge_base.get('practice_info', {}).get('name', 'Dental Practice')}",
            f"Address: {knowledge_base.get('practice_info', {}).get('address', 'Not specified')}",
            f"Phone: {knowledge_base.get('practice_info', {}).get('phone', 'Not specified')}",
            f"Email: {knowledge_base.get('practice_info', {}).get('email', 'Not specified')}",
            "",
            "## Available Services:",
        ]
        
        services = knowledge_base.get('services', [])
        for service in services:
            prompt_parts.append(f"- {service}")
        
        prompt_parts.extend([
            "",
            "## Frequently Asked Questions:",
        ])
        
        faqs = knowledge_base.get('faqs', [])
        for i, faq in enumerate(faqs[:10], 1):  # Limit to 10 FAQs
            prompt_parts.append(f"Q{i}: {faq.get('question', '')}")
            prompt_parts.append(f"A{i}: {faq.get('answer', '')}")
            prompt_parts.append("")
        
        prompt_parts.extend([
            "## Instructions:",
            "- Always be polite, professional, and helpful",
            "- If you don't know something, offer to connect the patient with a human staff member",
            "- For appointment scheduling, collect the patient's preferred date and time",
            "- Confirm all appointment details before finalizing",
            "- If a patient needs urgent care, direct them to call the office immediately",
            "- Keep responses concise but informative",
            "- Use the patient's name when possible to personalize the interaction"
        ])
        
        return "\n".join(prompt_parts)

    def _get_structured_data(self) -> Dict[str, Any]:
        """
        Get structured data for VAPI integration.

        Returns:
            Structured data dictionary
        """
        return self.data_service.get_dental_knowledge_base()

    async def close(self) -> None:
        """Close HTTP client connections."""
        if self.http_client:
            await self.http_client.aclose()
            self.http_client = None


# Global async VAPI service instance
_async_vapi_service: Optional[AsyncVAPIService] = None


def get_async_vapi_service() -> AsyncVAPIService:
    """Get global async VAPI service instance."""
    global _async_vapi_service
    if _async_vapi_service is None:
        _async_vapi_service = AsyncVAPIService()
    return _async_vapi_service
