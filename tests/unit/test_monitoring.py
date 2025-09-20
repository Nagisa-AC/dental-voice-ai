"""
Unit tests for monitoring system.

Tests the monitoring, alerting, and observability infrastructure
to ensure proper metrics collection and alerting.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from healthcare_voice_ai.core.monitoring import (
    MonitoringService, StructuredLogEntry, Alert, Metric,
    LogLevel, AlertSeverity, MetricType, HealthStatus
)


class TestStructuredLogEntry:
    """Test structured log entry functionality."""
    
    def test_structured_log_entry_creation(self):
        """Test creating a structured log entry."""
        entry = StructuredLogEntry(
            timestamp=datetime.utcnow(),
            level=LogLevel.INFO,
            message="Test message",
            service="test_service",
            component="test_component",
            tenant_id="test_tenant",
            user_id="test_user",
            request_id="test_request",
            duration_ms=100.5,
            metadata={"key": "value"}
        )
        
        assert entry.level == LogLevel.INFO
        assert entry.message == "Test message"
        assert entry.service == "test_service"
        assert entry.component == "test_component"
        assert entry.tenant_id == "test_tenant"
        assert entry.user_id == "test_user"
        assert entry.request_id == "test_request"
        assert entry.duration_ms == 100.5
        assert entry.metadata == {"key": "value"}
    
    def test_structured_log_entry_to_dict(self):
        """Test converting log entry to dictionary."""
        entry = StructuredLogEntry(
            timestamp=datetime.utcnow(),
            level=LogLevel.ERROR,
            message="Error message",
            service="test_service",
            component="test_component"
        )
        
        entry_dict = entry.to_dict()
        
        assert isinstance(entry_dict, dict)
        assert entry_dict["level"] == "ERROR"
        assert entry_dict["message"] == "Error message"
        assert entry_dict["service"] == "test_service"
        assert entry_dict["component"] == "test_component"
        assert "timestamp" in entry_dict


class TestAlert:
    """Test alert functionality."""
    
    def test_alert_creation(self):
        """Test creating an alert."""
        alert = Alert(
            id="test_alert_1",
            title="Test Alert",
            message="This is a test alert",
            severity=AlertSeverity.HIGH,
            service="test_service",
            component="test_component",
            tenant_id="test_tenant",
            metadata={"error_code": "E001"}
        )
        
        assert alert.id == "test_alert_1"
        assert alert.title == "Test Alert"
        assert alert.message == "This is a test alert"
        assert alert.severity == AlertSeverity.HIGH
        assert alert.service == "test_service"
        assert alert.component == "test_component"
        assert alert.tenant_id == "test_tenant"
        assert alert.metadata == {"error_code": "E001"}
        assert alert.is_active is True
        assert alert.acknowledged is False
    
    def test_alert_acknowledge(self):
        """Test acknowledging an alert."""
        alert = Alert(
            id="test_alert_1",
            title="Test Alert",
            message="This is a test alert",
            severity=AlertSeverity.MEDIUM,
            service="test_service",
            component="test_component"
        )
        
        assert alert.acknowledged is False
        
        alert.acknowledge("test_user")
        
        assert alert.acknowledged is True
        assert alert.acknowledged_by == "test_user"
        assert alert.acknowledged_at is not None
    
    def test_alert_resolve(self):
        """Test resolving an alert."""
        alert = Alert(
            id="test_alert_1",
            title="Test Alert",
            message="This is a test alert",
            severity=AlertSeverity.LOW,
            service="test_service",
            component="test_component"
        )
        
        assert alert.is_active is True
        
        alert.resolve("test_user")
        
        assert alert.is_active is False
        assert alert.resolved_by == "test_user"
        assert alert.resolved_at is not None


class TestMetric:
    """Test metric functionality."""
    
    def test_counter_metric_creation(self):
        """Test creating a counter metric."""
        metric = Metric(
            name="test_counter",
            type=MetricType.COUNTER,
            value=1,
            service="test_service",
            component="test_component",
            tenant_id="test_tenant",
            tags={"endpoint": "/test"}
        )
        
        assert metric.name == "test_counter"
        assert metric.type == MetricType.COUNTER
        assert metric.value == 1
        assert metric.service == "test_service"
        assert metric.component == "test_component"
        assert metric.tenant_id == "test_tenant"
        assert metric.tags == {"endpoint": "/test"}
    
    def test_gauge_metric_creation(self):
        """Test creating a gauge metric."""
        metric = Metric(
            name="test_gauge",
            type=MetricType.GAUGE,
            value=42.5,
            service="test_service",
            component="test_component"
        )
        
        assert metric.name == "test_gauge"
        assert metric.type == MetricType.GAUGE
        assert metric.value == 42.5
    
    def test_histogram_metric_creation(self):
        """Test creating a histogram metric."""
        metric = Metric(
            name="test_histogram",
            type=MetricType.HISTOGRAM,
            value=150.0,
            service="test_service",
            component="test_component",
            tags={"operation": "database_query"}
        )
        
        assert metric.name == "test_histogram"
        assert metric.type == MetricType.HISTOGRAM
        assert metric.value == 150.0
        assert metric.tags == {"operation": "database_query"}


class TestMonitoringService:
    """Test monitoring service functionality."""
    
    @pytest.fixture
    def monitoring_service(self):
        """Create a monitoring service instance."""
        return MonitoringService()
    
    def test_monitoring_service_initialization(self, monitoring_service):
        """Test monitoring service initialization."""
        assert monitoring_service is not None
        assert monitoring_service.alerts == []
        assert monitoring_service.metrics == []
        assert monitoring_service.logs == []
    
    def test_log_structured_entry(self, monitoring_service):
        """Test logging a structured entry."""
        entry = StructuredLogEntry(
            timestamp=datetime.utcnow(),
            level=LogLevel.INFO,
            message="Test log entry",
            service="test_service",
            component="test_component"
        )
        
        monitoring_service.log_structured_entry(entry)
        
        assert len(monitoring_service.logs) == 1
        assert monitoring_service.logs[0] == entry
    
    def test_create_alert(self, monitoring_service):
        """Test creating an alert."""
        alert = monitoring_service.create_alert(
            title="Test Alert",
            message="This is a test alert",
            severity=AlertSeverity.HIGH,
            service="test_service",
            component="test_component"
        )
        
        assert alert is not None
        assert alert.title == "Test Alert"
        assert alert.severity == AlertSeverity.HIGH
        assert len(monitoring_service.alerts) == 1
        assert monitoring_service.alerts[0] == alert
    
    def test_record_metric(self, monitoring_service):
        """Test recording a metric."""
        metric = monitoring_service.record_metric(
            name="test_metric",
            type=MetricType.COUNTER,
            value=1,
            service="test_service",
            component="test_component"
        )
        
        assert metric is not None
        assert metric.name == "test_metric"
        assert metric.type == MetricType.COUNTER
        assert metric.value == 1
        assert len(monitoring_service.metrics) == 1
        assert monitoring_service.metrics[0] == metric
    
    def test_get_active_alerts(self, monitoring_service):
        """Test getting active alerts."""
        # Create some alerts
        alert1 = monitoring_service.create_alert(
            title="Active Alert 1",
            message="This is active",
            severity=AlertSeverity.HIGH,
            service="test_service",
            component="test_component"
        )
        
        alert2 = monitoring_service.create_alert(
            title="Active Alert 2",
            message="This is also active",
            severity=AlertSeverity.MEDIUM,
            service="test_service",
            component="test_component"
        )
        
        # Resolve one alert
        alert2.resolve("test_user")
        
        active_alerts = monitoring_service.get_active_alerts()
        
        assert len(active_alerts) == 1
        assert active_alerts[0] == alert1
    
    def test_get_alerts_by_severity(self, monitoring_service):
        """Test getting alerts by severity."""
        # Create alerts with different severities
        monitoring_service.create_alert(
            title="High Alert",
            message="High severity alert",
            severity=AlertSeverity.HIGH,
            service="test_service",
            component="test_component"
        )
        
        monitoring_service.create_alert(
            title="Medium Alert",
            message="Medium severity alert",
            severity=AlertSeverity.MEDIUM,
            service="test_service",
            component="test_component"
        )
        
        monitoring_service.create_alert(
            title="Low Alert",
            message="Low severity alert",
            severity=AlertSeverity.LOW,
            service="test_service",
            component="test_component"
        )
        
        high_alerts = monitoring_service.get_alerts_by_severity(AlertSeverity.HIGH)
        medium_alerts = monitoring_service.get_alerts_by_severity(AlertSeverity.MEDIUM)
        low_alerts = monitoring_service.get_alerts_by_severity(AlertSeverity.LOW)
        
        assert len(high_alerts) == 1
        assert len(medium_alerts) == 1
        assert len(low_alerts) == 1
        
        assert high_alerts[0].title == "High Alert"
        assert medium_alerts[0].title == "Medium Alert"
        assert low_alerts[0].title == "Low Alert"
    
    def test_get_metrics_by_name(self, monitoring_service):
        """Test getting metrics by name."""
        # Record some metrics
        monitoring_service.record_metric(
            name="test_counter",
            type=MetricType.COUNTER,
            value=1,
            service="test_service",
            component="test_component"
        )
        
        monitoring_service.record_metric(
            name="test_counter",
            type=MetricType.COUNTER,
            value=2,
            service="test_service",
            component="test_component"
        )
        
        monitoring_service.record_metric(
            name="test_gauge",
            type=MetricType.GAUGE,
            value=42.5,
            service="test_service",
            component="test_component"
        )
        
        counter_metrics = monitoring_service.get_metrics_by_name("test_counter")
        gauge_metrics = monitoring_service.get_metrics_by_name("test_gauge")
        
        assert len(counter_metrics) == 2
        assert len(gauge_metrics) == 1
        
        assert counter_metrics[0].value == 1
        assert counter_metrics[1].value == 2
        assert gauge_metrics[0].value == 42.5
    
    def test_get_health_status(self, monitoring_service):
        """Test getting health status."""
        # Create some alerts to test health status
        monitoring_service.create_alert(
            title="Critical Alert",
            message="Critical issue",
            severity=AlertSeverity.CRITICAL,
            service="test_service",
            component="test_component"
        )
        
        monitoring_service.create_alert(
            title="High Alert",
            message="High severity issue",
            severity=AlertSeverity.HIGH,
            service="test_service",
            component="test_component"
        )
        
        health_status = monitoring_service.get_health_status()
        
        assert health_status.status == HealthStatus.UNHEALTHY
        assert health_status.critical_alerts == 1
        assert health_status.high_alerts == 1
        assert health_status.total_alerts == 2
    
    def test_cleanup_old_data(self, monitoring_service):
        """Test cleaning up old data."""
        # Create some old data
        old_time = datetime.utcnow() - timedelta(days=8)
        
        old_alert = Alert(
            id="old_alert",
            title="Old Alert",
            message="This is old",
            severity=AlertSeverity.LOW,
            service="test_service",
            component="test_component",
            created_at=old_time
        )
        monitoring_service.alerts.append(old_alert)
        
        old_metric = Metric(
            name="old_metric",
            type=MetricType.COUNTER,
            value=1,
            service="test_service",
            component="test_component",
            timestamp=old_time
        )
        monitoring_service.metrics.append(old_metric)
        
        old_log = StructuredLogEntry(
            timestamp=old_time,
            level=LogLevel.INFO,
            message="Old log",
            service="test_service",
            component="test_component"
        )
        monitoring_service.logs.append(old_log)
        
        # Create some recent data
        recent_alert = monitoring_service.create_alert(
            title="Recent Alert",
            message="This is recent",
            severity=AlertSeverity.LOW,
            service="test_service",
            component="test_component"
        )
        
        # Cleanup old data (older than 7 days)
        monitoring_service.cleanup_old_data(days=7)
        
        # Check that old data is removed but recent data remains
        assert len(monitoring_service.alerts) == 1
        assert monitoring_service.alerts[0] == recent_alert
        assert len(monitoring_service.metrics) == 0
        assert len(monitoring_service.logs) == 0


class TestMonitoringServiceIntegration:
    """Integration tests for monitoring service."""
    
    @pytest.fixture
    def monitoring_service(self):
        """Create a monitoring service instance."""
        return MonitoringService()
    
    def test_full_monitoring_workflow(self, monitoring_service):
        """Test a complete monitoring workflow."""
        # Log some entries
        entry1 = StructuredLogEntry(
            timestamp=datetime.utcnow(),
            level=LogLevel.INFO,
            message="User login",
            service="auth_service",
            component="login_handler",
            tenant_id="tenant_1",
            user_id="user_1"
        )
        monitoring_service.log_structured_entry(entry1)
        
        # Record some metrics
        monitoring_service.record_metric(
            name="login_attempts",
            type=MetricType.COUNTER,
            value=1,
            service="auth_service",
            component="login_handler",
            tenant_id="tenant_1"
        )
        
        monitoring_service.record_metric(
            name="response_time",
            type=MetricType.HISTOGRAM,
            value=150.0,
            service="auth_service",
            component="login_handler",
            tenant_id="tenant_1"
        )
        
        # Create an alert
        alert = monitoring_service.create_alert(
            title="High Login Failure Rate",
            message="Login failure rate is above threshold",
            severity=AlertSeverity.HIGH,
            service="auth_service",
            component="login_handler",
            tenant_id="tenant_1"
        )
        
        # Verify data
        assert len(monitoring_service.logs) == 1
        assert len(monitoring_service.metrics) == 2
        assert len(monitoring_service.alerts) == 1
        
        # Test filtering
        auth_logs = monitoring_service.get_logs_by_service("auth_service")
        assert len(auth_logs) == 1
        
        auth_metrics = monitoring_service.get_metrics_by_service("auth_service")
        assert len(auth_metrics) == 2
        
        tenant_alerts = monitoring_service.get_alerts_by_tenant("tenant_1")
        assert len(tenant_alerts) == 1
        
        # Test health status
        health = monitoring_service.get_health_status()
        assert health.status == HealthStatus.UNHEALTHY
        assert health.high_alerts == 1
    
    def test_alert_workflow(self, monitoring_service):
        """Test alert workflow from creation to resolution."""
        # Create alert
        alert = monitoring_service.create_alert(
            title="Database Connection Issue",
            message="Cannot connect to database",
            severity=AlertSeverity.CRITICAL,
            service="database_service",
            component="connection_pool"
        )
        
        assert alert.is_active is True
        assert alert.acknowledged is False
        
        # Acknowledge alert
        alert.acknowledge("admin_user")
        assert alert.acknowledged is True
        assert alert.acknowledged_by == "admin_user"
        
        # Resolve alert
        alert.resolve("admin_user")
        assert alert.is_active is False
        assert alert.resolved_by == "admin_user"
        
        # Check that alert is no longer active
        active_alerts = monitoring_service.get_active_alerts()
        assert len(active_alerts) == 0
        
        # Check health status
        health = monitoring_service.get_health_status()
        assert health.status == HealthStatus.HEALTHY
        assert health.critical_alerts == 0
