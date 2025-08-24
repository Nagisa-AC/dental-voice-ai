"""
Pydantic Schemas for Dental Voice AI Production System

Basic schemas for health checks and system status.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime


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


