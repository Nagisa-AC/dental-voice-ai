"""
Assistant models for multi-tenant assistant management.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class AssistantStatus(str, Enum):
    """Assistant status enumeration."""
    CREATING = "creating"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


class AssistantType(str, Enum):
    """Assistant type enumeration."""
    GENERAL = "general"
    APPOINTMENT = "appointment"
    EMERGENCY = "emergency"
    CUSTOM = "custom"


class VoiceConfig(BaseModel):
    """Voice configuration for assistant."""
    provider: str = Field(default="11labs", description="Voice provider")
    voice_id: str = Field(default="cgSgspJ2msm6clMCkdW9", description="Voice ID")
    speed: Optional[float] = Field(None, description="Speech speed (0.5-2.0)")
    stability: Optional[float] = Field(None, description="Voice stability (0.0-1.0)")


class ModelConfig(BaseModel):
    """AI model configuration for assistant."""
    provider: str = Field(default="openai", description="Model provider")
    model: str = Field(default="gpt-4o", description="Model name")
    temperature: float = Field(default=0.7, description="Model temperature")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens")
    system_prompt: Optional[str] = Field(None, description="Custom system prompt")


class AssistantConfig(BaseModel):
    """Complete assistant configuration."""
    name: str = Field(..., description="Assistant name")
    type: AssistantType = Field(default=AssistantType.GENERAL, description="Assistant type")
    voice: VoiceConfig = Field(default_factory=VoiceConfig, description="Voice configuration")
    model: ModelConfig = Field(default_factory=ModelConfig, description="Model configuration")
    first_message: str = Field(default="Hi there! I'm your dental office assistant. How can I help you today?", description="First message")
    custom_instructions: Optional[str] = Field(None, description="Custom instructions")
    knowledge_base_id: Optional[str] = Field(None, description="Associated knowledge base ID")


class Assistant(BaseModel):
    """Complete assistant model."""
    id: str = Field(..., description="Unique assistant ID")
    tenant_id: str = Field(..., description="Office tenant ID")
    name: str = Field(..., description="Assistant name")
    type: AssistantType = Field(..., description="Assistant type")
    config: AssistantConfig = Field(..., description="Assistant configuration")
    vapi_assistant_id: Optional[str] = Field(None, description="VAPI assistant ID")
    phone_number_id: Optional[str] = Field(None, description="Associated phone number ID")
    status: AssistantStatus = Field(default=AssistantStatus.CREATING, description="Assistant status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    last_used: Optional[datetime] = Field(None, description="Last usage timestamp")
    call_count: int = Field(default=0, description="Total number of calls handled")
    error_message: Optional[str] = Field(None, description="Error message if status is error")


class AssistantCreateRequest(BaseModel):
    """Request to create a new assistant."""
    tenant_id: str = Field(..., description="Office tenant ID")
    name: str = Field(..., description="Assistant name")
    type: AssistantType = Field(default=AssistantType.GENERAL, description="Assistant type")
    voice_id: Optional[str] = Field(None, description="Voice ID override")
    model: Optional[str] = Field(None, description="Model override")
    first_message: Optional[str] = Field(None, description="Custom first message")
    custom_instructions: Optional[str] = Field(None, description="Custom instructions")


class AssistantUpdateRequest(BaseModel):
    """Request to update an assistant."""
    name: Optional[str] = Field(None, description="New assistant name")
    voice_id: Optional[str] = Field(None, description="New voice ID")
    model: Optional[str] = Field(None, description="New model")
    first_message: Optional[str] = Field(None, description="New first message")
    custom_instructions: Optional[str] = Field(None, description="New custom instructions")
    status: Optional[AssistantStatus] = Field(None, description="New status")


class AssistantResponse(BaseModel):
    """Assistant response model for API endpoints."""
    id: str
    tenant_id: str
    name: str
    type: AssistantType
    status: AssistantStatus
    vapi_assistant_id: Optional[str]
    phone_number_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    call_count: int
    last_used: Optional[datetime]


class PhoneNumberConfig(BaseModel):
    """Phone number configuration."""
    area_code: str = Field(default="415", description="Desired area code")
    country_code: str = Field(default="US", description="Country code")
    provider: str = Field(default="vapi", description="Phone provider")
    custom_greeting: Optional[str] = Field(None, description="Custom greeting message")


class PhoneNumber(BaseModel):
    """Phone number model."""
    id: str = Field(..., description="Unique phone number ID")
    tenant_id: str = Field(..., description="Office tenant ID")
    assistant_id: str = Field(..., description="Associated assistant ID")
    number: str = Field(..., description="Phone number")
    area_code: str = Field(..., description="Area code")
    provider: str = Field(..., description="Phone provider")
    status: str = Field(..., description="Phone number status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    activated_at: Optional[datetime] = Field(None, description="Activation timestamp")


class CallRecord(BaseModel):
    """Call record model."""
    id: str = Field(..., description="Unique call ID")
    tenant_id: str = Field(..., description="Office tenant ID")
    assistant_id: str = Field(..., description="Assistant ID")
    phone_number_id: str = Field(..., description="Phone number ID")
    customer_phone: str = Field(..., description="Customer phone number")
    status: str = Field(..., description="Call status")
    duration_seconds: Optional[int] = Field(None, description="Call duration in seconds")
    started_at: datetime = Field(default_factory=datetime.utcnow, description="Call start time")
    ended_at: Optional[datetime] = Field(None, description="Call end time")
    transcript: Optional[str] = Field(None, description="Call transcript")
    summary: Optional[str] = Field(None, description="Call summary")
    outcome: Optional[str] = Field(None, description="Call outcome (appointment booked, etc.)")
