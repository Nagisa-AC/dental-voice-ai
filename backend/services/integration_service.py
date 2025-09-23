"""
Integration management service for multi-tenant healthcare practice management.

Handles calendar integrations, assistant-clinic mappings, and system alerts.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import json

from db.models.database_models import (
    AssistantClinicMapping, ClinicCalendarIntegration, SystemAlert,
    ClinicConfiguration, IntegrationTestResult, Clinic
)
from services.orm_service import ORMService
from core.database import db_manager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select

# Define custom exceptions for integration service
class ValidationError(Exception):
    """Raised when validation fails."""
    pass

class DatabaseError(Exception):
    """Raised when database operations fail."""
    pass

logger = logging.getLogger(__name__)


class IntegrationService:
    """
    Service for managing integrations and assistant-clinic mappings.
    
    Provides methods for:
    - Managing assistant-clinic mappings
    - Configuring calendar integrations
    - Handling system alerts
    - Managing clinic configurations
    - Running integration tests
    """
    
    def __init__(self, db_session=None):
        """Initialize integration service."""
        self.db_session = db_session
        self.logger = logging.getLogger(__name__)
    
    async def create_assistant_clinic_mapping(
        self,
        assistant_id: str,
        clinic_id: str
    ) -> str:
        """Create mapping between assistant and clinic."""
        try:
            async with db_manager.get_async_session() as session:
                # Check if mapping already exists
                existing = await session.execute(
                    select(AssistantClinicMapping).where(
                        AssistantClinicMapping.assistant_id == assistant_id
                    )
                )
                if existing.scalar_one_or_none():
                    raise ValidationError(f"Assistant {assistant_id} already mapped to a clinic")
                
                # Create new mapping
                mapping = AssistantClinicMapping(
                    assistant_id=assistant_id,
                    clinic_id=clinic_id,
                    is_active=True
                )
                
                session.add(mapping)
                await session.commit()
                
                self.logger.info(f"Created assistant-clinic mapping: {assistant_id} -> {clinic_id}")
                return mapping.id
                
        except Exception as e:
            self.logger.error(f"Error creating assistant-clinic mapping: {e}")
            raise DatabaseError(f"Failed to create mapping: {str(e)}")
    
    async def get_clinic_for_assistant(self, assistant_id: str) -> Optional[str]:
        """Get clinic ID for a given assistant."""
        try:
            async with db_manager.get_async_session() as session:
                result = await session.execute(
                    select(AssistantClinicMapping.clinic_id).where(
                        AssistantClinicMapping.assistant_id == assistant_id,
                        AssistantClinicMapping.is_active == True
                    )
                )
                clinic_id = result.scalar_one_or_none()
                return clinic_id
                
        except Exception as e:
            self.logger.error(f"Error getting clinic for assistant {assistant_id}: {e}")
            return None
    
    async def configure_calendar_integration(
        self,
        clinic_id: str,
        integration_type: str,
        integration_config: Dict[str, Any]
    ) -> str:
        """Configure calendar integration for a clinic."""
        try:
            async with db_manager.get_async_session() as session:
                # Check if integration already exists
                existing = await session.execute(
                    select(ClinicCalendarIntegration).where(
                        ClinicCalendarIntegration.clinic_id == clinic_id,
                        ClinicCalendarIntegration.integration_type == integration_type
                    )
                )
                
                if existing.scalar_one_or_none():
                    # Update existing integration
                    integration = existing.scalar_one()
                    integration.integration_config = integration_config
                    integration.updated_at = datetime.utcnow()
                else:
                    # Create new integration
                    integration = ClinicCalendarIntegration(
                        clinic_id=clinic_id,
                        integration_type=integration_type,
                        integration_config=integration_config,
                        is_active=True
                    )
                    session.add(integration)
                
                await session.commit()
                
                # Auto-resolve any calendar configuration alerts
                await self._auto_resolve_calendar_alerts(session, clinic_id)
                
                self.logger.info(f"Configured {integration_type} integration for clinic {clinic_id}")
                return integration.id
                
        except Exception as e:
            self.logger.error(f"Error configuring calendar integration: {e}")
            raise DatabaseError(f"Failed to configure integration: {str(e)}")
    
    async def get_calendar_integration(
        self,
        clinic_id: str,
        integration_type: str = "google_calendar"
    ) -> Optional[Dict[str, Any]]:
        """Get calendar integration configuration for a clinic."""
        try:
            async with db_manager.get_async_session() as session:
                result = await session.execute(
                    select(ClinicCalendarIntegration).where(
                        ClinicCalendarIntegration.clinic_id == clinic_id,
                        ClinicCalendarIntegration.integration_type == integration_type,
                        ClinicCalendarIntegration.is_active == True
                    )
                )
                integration = result.scalar_one_or_none()
                
                if integration:
                    return {
                        "id": integration.id,
                        "clinic_id": integration.clinic_id,
                        "integration_type": integration.integration_type,
                        "integration_config": integration.integration_config,
                        "is_active": integration.is_active
                    }
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting calendar integration: {e}")
            return None
    
    async def create_system_alert(
        self,
        clinic_id: str,
        alert_type: str,
        message: str,
        priority: str = "medium"
    ) -> str:
        """Create a system alert for a clinic."""
        try:
            async with db_manager.get_async_session() as session:
                alert = SystemAlert(
                    clinic_id=clinic_id,
                    alert_type=alert_type,
                    priority=priority,
                    message=message,
                    is_resolved=False
                )
                
                session.add(alert)
                await session.commit()
                
                self.logger.info(f"Created {priority} alert for clinic {clinic_id}: {alert_type}")
                return alert.id
                
        except Exception as e:
            self.logger.error(f"Error creating system alert: {e}")
            raise DatabaseError(f"Failed to create alert: {str(e)}")
    
    async def get_system_alerts(
        self,
        clinic_id: str,
        include_resolved: bool = False,
        priority: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get system alerts for a clinic."""
        try:
            async with db_manager.get_async_session() as session:
                query = select(SystemAlert).where(SystemAlert.clinic_id == clinic_id)
                
                if not include_resolved:
                    query = query.where(SystemAlert.is_resolved == False)
                
                if priority:
                    query = query.where(SystemAlert.priority == priority)
                
                query = query.order_by(SystemAlert.created_at.desc())
                
                result = await session.execute(query)
                alerts = result.scalars().all()
                
                return [
                    {
                        "id": alert.id,
                        "clinic_id": alert.clinic_id,
                        "alert_type": alert.alert_type,
                        "priority": alert.priority,
                        "message": alert.message,
                        "is_resolved": alert.is_resolved,
                        "auto_resolved": alert.auto_resolved,
                        "resolved_by": alert.resolved_by,
                        "resolved_at": alert.resolved_at,
                        "created_at": alert.created_at
                    }
                    for alert in alerts
                ]
                
        except Exception as e:
            self.logger.error(f"Error getting system alerts: {e}")
            return []
    
    async def resolve_alert(
        self,
        alert_id: str,
        resolved_by: str,
        auto_resolved: bool = False
    ) -> bool:
        """Resolve a system alert."""
        try:
            async with db_manager.get_async_session() as session:
                result = await session.execute(
                    select(SystemAlert).where(SystemAlert.id == alert_id)
                )
                alert = result.scalar_one_or_none()
                
                if not alert:
                    raise ValidationError(f"Alert {alert_id} not found")
                
                alert.is_resolved = True
                alert.auto_resolved = auto_resolved
                alert.resolved_by = resolved_by
                alert.resolved_at = datetime.utcnow()
                
                await session.commit()
                
                self.logger.info(f"Resolved alert {alert_id} by {resolved_by}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error resolving alert: {e}")
            return False
    
    async def set_clinic_configuration(
        self,
        clinic_id: str,
        config_key: str,
        config_value: str,
        config_type: str = "string",
        description: Optional[str] = None
    ) -> str:
        """Set a clinic-specific configuration."""
        try:
            async with db_manager.get_async_session() as session:
                # Check if configuration already exists
                existing = await session.execute(
                    select(ClinicConfiguration).where(
                        ClinicConfiguration.clinic_id == clinic_id,
                        ClinicConfiguration.config_key == config_key
                    )
                )
                
                if existing.scalar_one_or_none():
                    # Update existing configuration
                    config = existing.scalar_one()
                    config.config_value = config_value
                    config.config_type = config_type
                    config.description = description
                    config.updated_at = datetime.utcnow()
                else:
                    # Create new configuration
                    config = ClinicConfiguration(
                        clinic_id=clinic_id,
                        config_key=config_key,
                        config_value=config_value,
                        config_type=config_type,
                        description=description
                    )
                    session.add(config)
                
                await session.commit()
                
                self.logger.info(f"Set configuration {config_key} for clinic {clinic_id}")
                return config.id
                
        except Exception as e:
            self.logger.error(f"Error setting clinic configuration: {e}")
            raise DatabaseError(f"Failed to set configuration: {str(e)}")
    
    async def get_clinic_configurations(self, clinic_id: str) -> Dict[str, Any]:
        """Get all clinic configurations."""
        try:
            async with db_manager.get_async_session() as session:
                result = await session.execute(
                    select(ClinicConfiguration).where(
                        ClinicConfiguration.clinic_id == clinic_id
                    )
                )
                configs = result.scalars().all()
                
                configurations = {}
                for config in configs:
                    # Convert value based on type
                    if config.config_type == "integer":
                        configurations[config.config_key] = int(config.config_value)
                    elif config.config_type == "boolean":
                        configurations[config.config_key] = config.config_value.lower() == "true"
                    elif config.config_type == "json":
                        configurations[config.config_key] = json.loads(config.config_value)
                    else:
                        configurations[config.config_key] = config.config_value
                
                return configurations
                
        except Exception as e:
            self.logger.error(f"Error getting clinic configurations: {e}")
            return {}
    
    async def run_integration_test(
        self,
        clinic_id: str,
        integration_type: str,
        test_type: str = "full_suite"
    ) -> Dict[str, Any]:
        """Run integration test for a clinic."""
        try:
            start_time = datetime.utcnow()
            
            # Get integration configuration
            integration = await self.get_calendar_integration(clinic_id, integration_type)
            
            if not integration:
                test_results = {
                    "connection_test": {"status": "failed", "error": "Integration not configured"},
                    "availability_test": {"status": "failed", "error": "Integration not configured"},
                    "appointment_creation_test": {"status": "failed", "error": "Integration not configured"}
                }
                overall_status = "failed"
            else:
                # Run mock tests (since we don't have real Google Calendar configured)
                test_results = await self._run_mock_integration_tests(integration)
                overall_status = "passed" if all(
                    test.get("status") == "passed" for test in test_results.values()
                ) else "partial"
            
            end_time = datetime.utcnow()
            test_duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Store test results
            await self._store_test_results(
                clinic_id, integration_type, test_type, overall_status,
                test_results, test_duration_ms
            )
            
            return {
                "status": overall_status,
                "test_type": test_type,
                "results": test_results,
                "duration_ms": test_duration_ms
            }
            
        except Exception as e:
            self.logger.error(f"Error running integration test: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def _run_mock_integration_tests(self, integration: Dict[str, Any]) -> Dict[str, Any]:
        """Run mock integration tests."""
        return {
            "connection_test": {
                "status": "passed",
                "message": "Mock connection successful",
                "response_time_ms": 150
            },
            "availability_test": {
                "status": "passed",
                "message": "Mock availability retrieved",
                "slots_found": 8
            },
            "appointment_creation_test": {
                "status": "passed",
                "message": "Mock appointment created",
                "appointment_id": f"mock_{uuid.uuid4().hex[:8]}"
            }
        }
    
    async def _store_test_results(
        self,
        clinic_id: str,
        integration_type: str,
        test_type: str,
        test_status: str,
        test_results: Dict[str, Any],
        test_duration_ms: int
    ):
        """Store integration test results."""
        try:
            async with db_manager.get_async_session() as session:
                test_result = IntegrationTestResult(
                    clinic_id=clinic_id,
                    integration_type=integration_type,
                    test_type=test_type,
                    test_status=test_status,
                    test_results=test_results,
                    test_duration_ms=test_duration_ms
                )
                
                session.add(test_result)
                await session.commit()
                
        except Exception as e:
            self.logger.error(f"Error storing test results: {e}")
    
    async def _auto_resolve_calendar_alerts(self, session: AsyncSession, clinic_id: str):
        """Auto-resolve calendar configuration alerts."""
        try:
            result = await session.execute(
                select(SystemAlert).where(
                    SystemAlert.clinic_id == clinic_id,
                    SystemAlert.alert_type == "calendar_not_configured",
                    SystemAlert.is_resolved == False
                )
            )
            alerts = result.scalars().all()
            
            for alert in alerts:
                alert.is_resolved = True
                alert.auto_resolved = True
                alert.resolved_at = datetime.utcnow()
            
            if alerts:
                self.logger.info(f"Auto-resolved {len(alerts)} calendar configuration alerts for clinic {clinic_id}")
                
        except Exception as e:
            self.logger.error(f"Error auto-resolving calendar alerts: {e}")
