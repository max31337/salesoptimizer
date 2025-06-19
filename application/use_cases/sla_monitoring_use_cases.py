from typing import List

from domain.monitoring.services.sla_monitoring_service import SLAMonitoringService
from domain.monitoring.entities.sla_monitoring import SLAMetric
from application.dtos.monitoring_dto import (
    SLAReportResponse, SLAMetricResponse, SLASystemHealthResponse, SLAAlertResponse
)
from domain.monitoring.entities.sla_monitoring import SLAStatus


class SLAMonitoringUseCase:
    """Use case for SLA monitoring operations."""
    
    def __init__(self, sla_monitoring_service: SLAMonitoringService):
        self.sla_monitoring_service = sla_monitoring_service
    
    async def get_system_health_report(self) -> SLAReportResponse:
        """Get comprehensive system health report."""
        report = await self.sla_monitoring_service.generate_system_health_report()
        
        # Convert metrics to DTOs
        metric_dtos: List[SLAMetricResponse] = []
        for metric in report.metrics:
            metric_dto = SLAMetricResponse(
                id=str(metric.id),
                metric_type=metric.metric_type.value,
                value=metric.value,
                status=metric.status.value,
                threshold_warning=metric.threshold.warning_threshold,
                threshold_critical=metric.threshold.critical_threshold,
                unit=metric.threshold.unit,
                measured_at=metric.measured_at,
                additional_data=metric.additional_data
            )
            metric_dtos.append(metric_dto)
        
        # Count metrics by status
        critical_count = len([m for m in report.metrics if m.status == SLAStatus.CRITICAL])
        warning_count = len([m for m in report.metrics if m.status == SLAStatus.WARNING])
        healthy_count = len([m for m in report.metrics if m.status == SLAStatus.HEALTHY])
        
        return SLAReportResponse(
            id=str(report.id),
            report_type=report.report_type,
            overall_status=report.overall_status.value,
            generated_at=report.generated_at,
            summary=report.summary,
            recommendations=report.recommendations,
            metrics=metric_dtos,
            additional_data=report.additional_data,
            critical_metrics_count=critical_count,
            warning_metrics_count=warning_count,
            healthy_metrics_count=healthy_count,
            total_metrics_count=len(report.metrics)
        )
    
    async def get_system_health_summary(self) -> SLASystemHealthResponse:
        """Get quick system health summary."""
        report = await self.sla_monitoring_service.generate_system_health_report()
        
        # Count metrics by status
        total_metrics = len(report.metrics)
        healthy_count = len([m for m in report.metrics if m.status == SLAStatus.HEALTHY])
        warning_count = len([m for m in report.metrics if m.status == SLAStatus.WARNING])
        critical_count = len([m for m in report.metrics if m.status == SLAStatus.CRITICAL])        
        health_percentage = (healthy_count / total_metrics * 100) if total_metrics > 0 else 0
        
        # Extract key metrics
        cpu_usage = None
        memory_usage = None
        disk_usage = None
        database_response_time = None
        active_users_24h = None
        database_connections = None
        uptime_percentage = None
        uptime_duration = None
        system_start_time = None
        
        for metric in report.metrics:
            if metric.metric_type.value == "cpu_usage":
                cpu_usage = metric.value
            elif metric.metric_type.value == "memory_usage":
                memory_usage = metric.value
            elif metric.metric_type.value == "disk_usage":
                disk_usage = metric.value
            elif metric.metric_type.value == "response_time":
                database_response_time = metric.value
            elif metric.metric_type.value == "active_users":
                active_users_24h = int(metric.value)
            elif metric.metric_type.value == "database_connections":
                database_connections = int(metric.value)
            elif metric.metric_type.value == "uptime":
                uptime_percentage = metric.value
                if metric.additional_data:
                    uptime_duration = metric.additional_data.get("uptime_duration")
                    system_start_time_str = metric.additional_data.get("system_start_time")
                    if system_start_time_str:
                        from datetime import datetime
                        system_start_time = datetime.fromisoformat(system_start_time_str.replace('Z', '+00:00'))
        
        # Determine uptime status
        uptime_status = "operational"
        if uptime_percentage is not None:
            if uptime_percentage < 90:
                uptime_status = "critical"
            elif uptime_percentage < 95:
                uptime_status = "degraded"
            else:
                uptime_status = "operational"
        
        return SLASystemHealthResponse(
            overall_status=report.overall_status.value,
            health_percentage=health_percentage,
            uptime_status=uptime_status,
            last_updated=report.generated_at,
            total_metrics=total_metrics,
            healthy_metrics=healthy_count,            
            warning_metrics=warning_count,
            critical_metrics=critical_count,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            disk_usage=disk_usage,            
            database_response_time=database_response_time,
            active_users_24h=active_users_24h,
            uptime_percentage=uptime_percentage,
            uptime_duration=uptime_duration,
            system_start_time=system_start_time,
            metrics_summary={
                "cpu_usage": cpu_usage or 0.0,
                "memory_usage": memory_usage or 0.0,
                "disk_usage": disk_usage or 0.0,
                "database_response_time": database_response_time or 0.0,
                "active_users": active_users_24h or 0,
                "database_connections": database_connections or 0
            }
        )
    
    async def get_current_alerts(self) -> List[SLAAlertResponse]:
        """Get current active alerts from the database."""
        alert_data = await self.sla_monitoring_service.get_active_alerts()
        alerts: List[SLAAlertResponse] = []
        
        for alert_dict in alert_data:
            alert = SLAAlertResponse(
                id=alert_dict['id'],
                alert_type=alert_dict['alert_type'],
                title=alert_dict['title'],
                message=alert_dict['message'],
                metric_type=alert_dict['metric_type'],
                current_value=alert_dict['current_value'],
                threshold_value=alert_dict['threshold_value'],
                triggered_at=alert_dict['triggered_at'],
                acknowledged=alert_dict['acknowledged'],
                acknowledged_at=alert_dict['acknowledged_at'],
                acknowledged_by=alert_dict['acknowledged_by']
            )
            alerts.append(alert)
        
        return alerts
    
    async def get_metrics_by_type(self, metric_types: List[str]) -> List[SLAMetricResponse]:
        # Collect specific metrics based on requested types
        all_metrics: List[SLAMetric] = []
        
        if "system" in metric_types:
            system_metrics = await self.sla_monitoring_service.collect_system_metrics()
            all_metrics.extend(system_metrics)
        
        if "database" in metric_types:
            database_metrics = await self.sla_monitoring_service.collect_database_metrics()
            all_metrics.extend(database_metrics)
        
        if "application" in metric_types:
            app_metrics = await self.sla_monitoring_service.collect_application_metrics()
            all_metrics.extend(app_metrics)
        
        # Convert to DTOs
        metric_dtos: List[SLAMetricResponse] = []
        for metric in all_metrics:
            metric_dto = SLAMetricResponse(
                id=str(metric.id),
                metric_type=metric.metric_type.value,
                value=metric.value,
                status=metric.status.value,
                threshold_warning=metric.threshold.warning_threshold,
                threshold_critical=metric.threshold.critical_threshold,
                unit=metric.threshold.unit,
                measured_at=metric.measured_at,
                additional_data=metric.additional_data
            )
            metric_dtos.append(metric_dto)
        
        return metric_dtos
    
    async def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """Acknowledge an SLA alert.
        
        Args:
            alert_id: The ID of the alert to acknowledge
            user_id: The ID of the user acknowledging the alert
            
        Returns:
            bool: True if alert was successfully acknowledged
        """
        return await self.sla_monitoring_service.acknowledge_alert(alert_id, user_id)
