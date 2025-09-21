"""
Consolidated Clinic Models for Healthcare Voice AI

Merges office.py and clinic-related models into a single, comprehensive module.
Includes all clinic management, configuration, and business logic models.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ClinicStatus(str, Enum):
    """Clinic status enumeration."""
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"


class HealthcareIndustry(str, Enum):
    """Healthcare industry types supported by the platform."""
    DENTAL = "dental"
    FAMILY_MEDICINE = "family_medicine"
    INTERNAL_MEDICINE = "internal_medicine"
    DERMATOLOGY = "dermatology"
    CARDIOLOGY = "cardiology"
    ORTHOPEDICS = "orthopedics"
    CHIROPRACTIC = "chiropractic"
    MENTAL_HEALTH = "mental_health"
    THERAPY = "therapy"
    COUNSELING = "counseling"
    VETERINARY = "veterinary"


class ContactInfo(BaseModel):
    """Contact information for a clinic."""
    phone: str = Field(..., description="Primary phone number")
    email: str = Field(..., description="Primary email address")
    address: str = Field(..., description="Clinic address")
    website: Optional[str] = Field(None, description="Clinic website URL")


class BusinessHours(BaseModel):
    """Business hours for each day of the week."""
    monday: Optional[str] = Field(None, description="Monday hours (e.g., '8:00 AM - 6:00 PM')")
    tuesday: Optional[str] = Field(None, description="Tuesday hours")
    wednesday: Optional[str] = Field(None, description="Wednesday hours")
    thursday: Optional[str] = Field(None, description="Thursday hours")
    friday: Optional[str] = Field(None, description="Friday hours")
    saturday: Optional[str] = Field(None, description="Saturday hours")
    sunday: Optional[str] = Field(None, description="Sunday hours")


class Service(BaseModel):
    """Service offered by the clinic."""
    name: str = Field(..., description="Service name")
    description: Optional[str] = Field(None, description="Service description")
    duration_minutes: Optional[int] = Field(None, description="Typical service duration in minutes")
    price: Optional[float] = Field(None, description="Service price")


class ClinicPolicies(BaseModel):
    """Office policies and procedures."""
    cancellation_policy: Optional[str] = Field(None, description="Cancellation policy")
    no_show_policy: Optional[str] = Field(None, description="No-show policy")
    payment_policy: Optional[str] = Field(None, description="Payment policy")
    privacy_policy: Optional[str] = Field(None, description="Privacy policy")


class AssistantConfig(BaseModel):
    """AI Assistant configuration for the clinic."""
    voice_type: Optional[str] = Field(None, description="Preferred voice type")
    language: Optional[str] = Field(default="en-US", description="Assistant language")
    custom_instructions: Optional[str] = Field(None, description="Additional custom instructions")


class ClinicFormData(BaseModel):
    """Data submitted by clinic owner during onboarding."""
    clinic_name: str = Field(..., description="Name of the healthcare practice")
    industry_type: HealthcareIndustry = Field(default=HealthcareIndustry.DENTAL, description="Healthcare industry type")
    contact_info: ContactInfo = Field(..., description="Contact information")
    business_hours: BusinessHours = Field(..., description="Business hours")
    services: List[str] = Field(..., description="List of services offered")
    preferred_voice: Optional[str] = Field(None, description="Preferred voice type")
    
    @validator('services')
    def validate_services(cls, v):
        if not v:
            raise ValueError("At least one service must be specified")
        return v


class ClinicSubmission(BaseModel):
    """Clinic submission for admin review."""
    form_data: ClinicFormData = Field(..., description="Clinic form data")
    faq_file_content: Optional[str] = Field(None, description="FAQ file content")
    faq_filename: Optional[str] = Field(None, description="FAQ filename")


class AdminConfig(BaseModel):
    """Admin configuration for clinic management."""
    notes: Optional[str] = Field(None, description="Admin notes")
    priority: Optional[str] = Field(None, description="Processing priority")
    advanced_settings: Optional[Dict[str, Any]] = Field(None, description="Advanced configuration")


class Clinic(BaseModel):
    """Complete clinic model with all configuration."""
    tenant_id: str = Field(..., description="Unique tenant identifier")
    name: str = Field(..., description="Clinic name")
    industry_type: HealthcareIndustry = Field(default=HealthcareIndustry.DENTAL, description="Healthcare industry type")
    contact_info: ContactInfo = Field(..., description="Contact information")
    business_hours: BusinessHours = Field(..., description="Business hours")
    services: List[Service] = Field(..., description="Services offered")
    policies: ClinicPolicies = Field(default_factory=ClinicPolicies, description="Office policies")
    assistant_config: AssistantConfig = Field(default_factory=AssistantConfig, description="Assistant configuration")
    status: ClinicStatus = Field(default=ClinicStatus.ACTIVE, description="Clinic status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    admin_config: Optional[AdminConfig] = Field(None, description="Admin configuration")


class ClinicResponse(BaseModel):
    """Clinic response model for API endpoints."""
    tenant_id: str
    name: str
    contact_info: ContactInfo
    business_hours: BusinessHours
    services: List[Service]
    status: ClinicStatus
    created_at: datetime
    updated_at: datetime
    assistant_count: Optional[int] = Field(None, description="Number of active assistants")
    phone_number: Optional[str] = Field(None, description="Assigned phone number")


class ClinicUpdate(BaseModel):
    """Model for updating clinic information."""
    name: Optional[str] = Field(None, description="Clinic name")
    contact_info: Optional[ContactInfo] = Field(None, description="Contact information")
    business_hours: Optional[BusinessHours] = Field(None, description="Business hours")
    services: Optional[List[Service]] = Field(None, description="Services offered")
    policies: Optional[ClinicPolicies] = Field(None, description="Office policies")
    assistant_config: Optional[AssistantConfig] = Field(None, description="Assistant configuration")
    status: Optional[ClinicStatus] = Field(None, description="Clinic status")


class ClinicListResponse(BaseModel):
    """Response model for clinic listing endpoints."""
    clinics: List[ClinicResponse]
    total: int
    page: int
    page_size: int
    has_next: bool
    has_previous: bool


class ClinicStats(BaseModel):
    """Clinic statistics and metrics."""
    total_clinics: int
    active_clinics: int
    pending_clinics: int
    suspended_clinics: int
    total_assistants: int
    total_appointments: int
    last_updated: datetime

