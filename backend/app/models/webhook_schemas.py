"""
Pydantic Schemas for Dental Voice AI Production System

Type-safe data models for webhook processing, VAPI integration,
and call analytics with comprehensive validation.
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum


class IntentType(str, Enum):
    """Enumeration of dental practice intent types."""
    APPOINTMENT_BOOKING = "appointment_booking"
    APPOINTMENT_CANCEL = "appointment_cancel" 
    APPOINTMENT_RESCHEDULE = "appointment_reschedule"
    HOURS_INQUIRY = "hours_inquiry"
    INSURANCE_INQUIRY = "insurance_inquiry"
    SERVICES_INQUIRY = "services_inquiry"
    LOCATION_INQUIRY = "location_inquiry"
    EMERGENCY = "emergency"
    PAYMENT_INQUIRY = "payment_inquiry"
    FAQ_SPECIFIC = "faq_specific"
    GENERAL_INFO = "general_info"
    UNKNOWN = "unknown"


# Intent Recognition Schemas
class IntentAnalysisRequest(BaseModel):
    """Request schema for intent analysis."""
    transcript: str = Field(..., description="Text to analyze", min_length=1)
    tenant_id: Optional[str] = Field(None, description="Practice ID for context")

    @validator('transcript')
    def validate_transcript(cls, v):
        if not v or not v.strip():
            raise ValueError('Transcript cannot be empty')
        return v.strip()


class IntentAnalysisResult(BaseModel):
    """Result schema for intent analysis."""
    intent: IntentType
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")
    matched_keywords: List[str] = Field(default_factory=list)
    extracted_entities: Dict[str, Any] = Field(default_factory=dict)
    tenant_specific: bool = Field(default=False)
    faq_matched: Optional[str] = Field(None, description="Matched FAQ question")


class ResponseData(BaseModel):
    """Schema for AI-generated response data."""
    text: str = Field(..., min_length=1, description="Response text")
    should_speak: bool = Field(default=True)
    end_call: bool = Field(default=False)
    priority: Optional[str] = Field(None, pattern="^(normal|urgent|emergency)$")
    escalate: Optional[bool] = None


class PracticeInfo(BaseModel):
    """Schema for dental practice information."""
    identified: bool
    name: Optional[str] = None
    practice_id: Optional[str] = None
    error: Optional[str] = None


class IntentAnalysisResponse(BaseModel):
    """Complete intent analysis response schema."""
    status: str = Field(..., pattern="^(analyzed|error)$")
    request_id: Optional[str] = None
    transcript_length: Optional[int] = Field(None, ge=0)
    intent_analysis: IntentAnalysisResult
    response: ResponseData
    practice_info: PracticeInfo


# VAPI Webhook Schemas
class VAPIFunctionCall(BaseModel):
    """Schema for VAPI function call data."""
    name: str
    arguments: str = Field(..., description="JSON string of function arguments")


class VAPIToolCall(BaseModel):
    """Schema for VAPI tool call."""
    id: str
    type: str = Field(default="function")
    function: VAPIFunctionCall


class VAPICallData(BaseModel):
    """Schema for VAPI call metadata."""
    id: Optional[str] = None
    phoneNumber: Optional[str] = None
    phoneNumberId: Optional[str] = None
    assistantId: Optional[str] = None
    durationSeconds: Optional[int] = Field(None, ge=0)
    cost: Optional[float] = Field(None, ge=0)
    endedReason: Optional[str] = None
    startedAt: Optional[str] = None
    endedAt: Optional[str] = None
    type: Optional[str] = None


class VAPICustomerData(BaseModel):
    """Schema for VAPI customer information."""
    number: Optional[str] = None


class VAPIMessageData(BaseModel):
    """Schema for VAPI webhook message data."""
    type: Optional[str] = None
    call: Optional[VAPICallData] = None
    customer: Optional[VAPICustomerData] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None
    analysis: Optional[Dict[str, Any]] = None
    recordingUrl: Optional[str] = None
    artifacts: Optional[List[Any]] = None
    error: Optional[str] = None
    warnings: Optional[List[str]] = None


class VAPIWebhookPayload(BaseModel):
    """Schema for complete VAPI webhook payload."""
    # Standard webhook fields
    message: Optional[Union[VAPIMessageData, str]] = None
    event: Optional[str] = None
    call_id: Optional[str] = None
    transcript: Optional[str] = None
    phoneNumber: Optional[str] = None
    assistantId: Optional[str] = None
    
    # Function call fields
    id: Optional[str] = None
    type: Optional[str] = None
    function: Optional[VAPIFunctionCall] = None
    
    # Direct function parameters
    query: Optional[str] = None
    phone_number: Optional[str] = None
    caller_number: Optional[str] = None
    
    class Config:
        extra = "allow"  # Allow additional fields from VAPI


# Response Schemas
class VAPIFunctionResponse(BaseModel):
    """Schema for VAPI function call responses."""
    results: List[Dict[str, str]] = Field(..., min_items=1)

    @validator('results')
    def validate_results(cls, v):
        for result in v:
            if 'toolCallId' not in result or 'result' not in result:
                raise ValueError('Each result must have toolCallId and result fields')
        return v


class WebhookResponse(BaseModel):
    """Schema for standard webhook responses."""
    status: str = Field(..., pattern="^(logged|error|processed)$")
    call_id: str
    event_type: str
    processed: bool
    timestamp: Optional[str] = Field(default_factory=lambda: datetime.utcnow().isoformat())
    extracted_data: Optional[Dict[str, Any]] = None
    intent_analysis: Optional[IntentAnalysisResult] = None
    practice_info: Optional[PracticeInfo] = None


# Health Check Schemas
class ComponentStatus(BaseModel):
    """Schema for individual component status."""
    status: str = Field(..., pattern="^(available|unavailable|error|degraded)$")
    response_time_ms: Optional[float] = Field(None, ge=0)
    message: Optional[str] = None
    endpoint: Optional[str] = None


class HealthCheckResponse(BaseModel):
    """Schema for health check responses."""
    status: str = Field(..., pattern="^(healthy|degraded|unhealthy)$")
    service: str
    version: str
    environment: str
    timestamp: str
    health_check_id: int
    components: Dict[str, ComponentStatus]
    warnings: Optional[List[str]] = None