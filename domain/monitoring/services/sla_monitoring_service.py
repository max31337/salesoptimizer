import psutil
import time
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, func, select

from domain.monitoring.entities.sla_monitoring import (
    SLAMetric, SLAThreshold, SLAReport, SLAStatus, MetricType
)
from infrastructure.db.models.refresh_token_model import RefreshTokenModel
from infrastructure.db.repositories.sla_repository_impl import SLARepositoryImpl
from infrastructure.services.uptime_monitoring_service import UptimeMonitoringService

logger = logging.getLogger(__name__)


class SLAMonitoringService:
    """Service for SLA monitoring and metrics collection."""
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = SLARepositoryImpl(session)
        self.uptime_service = UptimeMonitoringService(session)
        self._default_thresholds = self._get_default_thresholds()
        self._system_start_time = self._get_system_start_time()
    
    def _get_default_thresholds(self) -> Dict[MetricType, SLAThreshold]:
        """Get default SLA thresholds for different metrics."""
        return {
            MetricType.UPTIME: SLAThreshold(
                metric_type=MetricType.UPTIME,
                warning_threshold=95.0,  # 95% uptime warning
                critical_threshold=90.0,  # 90% uptime critical
                unit="%"
            ),
            MetricType.RESPONSE_TIME: SLAThreshold(
                metric_type=MetricType.RESPONSE_TIME,
                warning_threshold=500.0,  # 500ms warning
                critical_threshold=1000.0,  # 1s critical
                unit="ms"
            ),
            MetricType.ERROR_RATE: SLAThreshold(
                metric_type=MetricType.ERROR_RATE,
                warning_threshold=5.0,  # 5% error rate warning
                critical_threshold=10.0,  # 10% error rate critical
                unit="%"
            ),
            MetricType.MEMORY_USAGE: SLAThreshold(
                metric_type=MetricType.MEMORY_USAGE,
                warning_threshold=80.0,  # 80% memory warning
                critical_threshold=90.0,  # 90% memory critical
                unit="%"
            ),
            MetricType.CPU_USAGE: SLAThreshold(
                metric_type=MetricType.CPU_USAGE,
                warning_threshold=80.0,  # 80% CPU warning
                critical_threshold=90.0,  # 90% CPU critical
                unit="%"
            ),
            MetricType.DISK_USAGE: SLAThreshold(
                metric_type=MetricType.DISK_USAGE,
                warning_threshold=80.0,  # 80% disk warning
                critical_threshold=90.0,  # 90% disk critical
                unit="%"
            ),
        }
    def _get_system_start_time(self) -> datetime:
        """Get system boot time."""
        try:
            boot_timestamp = psutil.boot_time()
            return datetime.fromtimestamp(boot_timestamp, tz=timezone.utc)
        except Exception:
            # Fallback to current time if unable to get boot time
            return datetime.now(timezone.utc)
    
    def _calculate_uptime_percentage(self, start_time: datetime, current_time: datetime) -> float:
        """Calculate real system uptime percentage over the last 24 hours using uptime monitoring."""
        # This method is now deprecated in favor of the uptime monitoring service
        # Return default value for backward compatibility
        return 000.0  # Fallback value
    
    def _format_uptime_duration(self, start_time: datetime, current_time: datetime) -> str:
        """Format uptime duration as human-readable string."""
        uptime_duration = current_time - start_time
        
        days = uptime_duration.days
        hours, remainder = divmod(uptime_duration.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        if days > 0:
            return f"{days} day{'s' if days != 1 else ''}, {hours} hour{'s' if hours != 1 else ''}"
        elif hours > 0:
            return f"{hours} hour{'s' if hours != 1 else ''}, {minutes} minute{'s' if minutes != 1 else ''}"
        else:
            return f"{minutes} minute{'s' if minutes != 1 else ''}"
    
    async def collect_system_metrics(self) -> List[SLAMetric]:
        """Collect current system performance metrics."""
        metrics: List[SLAMetric] = []
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_metric = SLAMetric.create(
            metric_type=MetricType.MEMORY_USAGE,
            value=memory.percent,
            threshold=self._default_thresholds[MetricType.MEMORY_USAGE],
            additional_data={
                "total": memory.total,
                "available": memory.available,
                "used": memory.used
            }
        )
        metrics.append(memory_metric)
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_metric = SLAMetric.create(
            metric_type=MetricType.CPU_USAGE,
            value=cpu_percent,
            threshold=self._default_thresholds[MetricType.CPU_USAGE],
            additional_data={
                "cpu_count": psutil.cpu_count(),
                "load_avg": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
            }
        )
        metrics.append(cpu_metric)
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_metric = SLAMetric.create(
            metric_type=MetricType.DISK_USAGE,
            value=(disk.used / disk.total) * 100,
            threshold=self._default_thresholds[MetricType.DISK_USAGE],
            additional_data={
                "total": disk.total,
                "used": disk.used,
                "free": disk.free
            }
        )
        metrics.append(disk_metric)
        
        # Uptime - Use real uptime monitoring service
        current_time = datetime.now(timezone.utc)
        
        try:
            # Get real uptime metrics from the uptime monitoring service
            uptime_summary = await self.uptime_service.get_uptime_summary(24)
            uptime_percentage = uptime_summary.get('uptime_percentage', 100.0)
            uptime_duration = uptime_summary.get('uptime_duration', 'Unknown')
            
            # Additional data includes detailed service states and incidents
            additional_uptime_data: Dict[str, Any] = {
                "system_start_time": self._system_start_time.isoformat(),
                "current_time": current_time.isoformat(),
                "uptime_percentage": uptime_percentage,
                "uptime_duration": uptime_duration,
                "overall_status": uptime_summary.get('overall_status', 'unknown'),
                "total_downtime_seconds": uptime_summary.get('total_downtime_seconds', 0.0),
                "downtime_incidents": uptime_summary.get('downtime_incidents', 0),
                "period_hours": 24,
                "services": uptime_summary.get('services', {}),
                "last_updated": uptime_summary.get('last_updated', current_time).isoformat() if uptime_summary.get('last_updated') else current_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get real uptime metrics, using fallback: {e}")
            # Fallback to old calculation method if uptime service fails
            uptime_percentage = self._calculate_uptime_percentage(self._system_start_time, current_time)
            additional_uptime_data: Dict[str, Any] = {
                "system_start_time": self._system_start_time.isoformat(),
                "current_time": current_time.isoformat(),
                "uptime_percentage": uptime_percentage,
                "uptime_duration": self._format_uptime_duration(self._system_start_time, current_time),
                "fallback_mode": True,
                "error": str(e)
            }
        
        uptime_metric = SLAMetric.create(
            metric_type=MetricType.UPTIME,
            value=uptime_percentage,
            threshold=self._default_thresholds[MetricType.UPTIME],
            additional_data=additional_uptime_data
        )
        metrics.append(uptime_metric)
        
        return metrics
      
    async def collect_database_metrics(self) -> List[SLAMetric]:
        """Collect database performance metrics."""
        metrics: List[SLAMetric] = []
        
        try:            # Database connection test and response time
            start_time = time.time()
            result = await self.session.execute(text("SELECT 1"))
            result.fetchone()
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            response_metric = SLAMetric.create(
                metric_type=MetricType.RESPONSE_TIME,
                value=response_time,
                threshold=self._default_thresholds[MetricType.RESPONSE_TIME],
                additional_data={
                    "query": "SELECT 1",
                    "connection_successful": True
                }
            )
            metrics.append(response_metric)
            
            # Database connections (if supported)
            try:
                connections_result = await self.session.execute(
                    text("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'")
                )
                active_connections = connections_result.scalar()
                
                # Create dynamic threshold for database connections
                db_connections_threshold = SLAThreshold(
                    metric_type=MetricType.DATABASE_CONNECTIONS,
                    warning_threshold=80.0,  # 80 connections warning
                    critical_threshold=100.0,  # 100 connections critical
                    unit="count"
                )
                
                connections_metric = SLAMetric.create(
                    metric_type=MetricType.DATABASE_CONNECTIONS,
                    value=float(active_connections or 0),
                    threshold=db_connections_threshold,
                    additional_data={
                        "active_connections": active_connections
                    }
                )
                metrics.append(connections_metric)
                
            except Exception:
                # If not PostgreSQL or query fails, skip this metric
                pass
                
        except Exception as e:
            # Database connection failed
            response_metric = SLAMetric.create(
                metric_type=MetricType.RESPONSE_TIME,
                value=10000.0,  # 10 seconds - very high response time
                threshold=self._default_thresholds[MetricType.RESPONSE_TIME],
                additional_data={
                    "connection_successful": False,
                    "error": str(e)
                }
            )
            metrics.append(response_metric)
        
        return metrics
      
    async def collect_application_metrics(self) -> List[SLAMetric]:
        """Collect application-specific metrics."""
        metrics: List[SLAMetric] = []
        
        current_time = datetime.now(timezone.utc)
        
        # Active users - Multiple approaches for comprehensive SLA monitoring
        
        # 1. Users with valid authentication sessions (current approach)
        stmt_valid_tokens = select(func.count(func.distinct(RefreshTokenModel.user_id))).where(
            RefreshTokenModel.is_revoked == False,
            RefreshTokenModel.expires_at > current_time
        )
        result_valid_tokens = await self.session.execute(stmt_valid_tokens)
        users_with_valid_tokens = result_valid_tokens.scalar() or 0
        
        # 2. Users who have been active in the last 24 hours (better for SLA)
        try:
            from infrastructure.db.models.login_activity_model import LoginActivityModel
            twenty_four_hours_ago = current_time - timedelta(hours=24)
            
            stmt_recent_activity = select(func.count(func.distinct(LoginActivityModel.user_id))).where(
                LoginActivityModel.login_at >= twenty_four_hours_ago
            )
            result_recent_activity = await self.session.execute(stmt_recent_activity)
            users_active_24h = result_recent_activity.scalar() or 0
        except Exception:
            # Fallback if login activity tracking is not available
            users_active_24h = users_with_valid_tokens
        
        # 3. Real-time active users (WebSocket connections)
        try:
            from infrastructure.websocket.websocket_manager import websocket_manager
            users_online_now = len(websocket_manager.connections)
        except Exception:
            users_online_now = 0
        
        # Use the most comprehensive metric for SLA monitoring
        # Priority: Recent activity > Valid tokens > Online now
        primary_active_users = max(users_active_24h, users_with_valid_tokens)
        
        # Create dynamic threshold for active users
        active_users_threshold = SLAThreshold(
            metric_type=MetricType.ACTIVE_USERS,
            warning_threshold=1000.0,  # Warning if less than 1000 active users
            critical_threshold=500.0,   # Critical if less than 500 active users
            unit="count"
        )
        
        active_users_metric = SLAMetric.create(
            metric_type=MetricType.ACTIVE_USERS,
            value=float(primary_active_users),
            threshold=active_users_threshold,
            additional_data={
                "period": "24_hours",
                "measurement_time": current_time.isoformat(),
                "description": "Users active in the last 24 hours",
                "breakdown": {
                    "users_with_valid_tokens": users_with_valid_tokens,
                    "users_active_24h": users_active_24h,
                    "users_online_now": users_online_now,
                    "primary_metric": "users_active_24h" if users_active_24h > 0 else "users_with_valid_tokens"
                }
            }
        )
        metrics.append(active_users_metric)
        
        return metrics
    
    async def generate_system_health_report(self) -> SLAReport:
        """Generate comprehensive system health report."""
        all_metrics: List[SLAMetric] = []
        
        # Collect all metrics
        system_metrics = await self.collect_system_metrics()
        database_metrics = await self.collect_database_metrics()
        application_metrics = await self.collect_application_metrics()
        
        all_metrics.extend(system_metrics)
        all_metrics.extend(database_metrics)
        all_metrics.extend(application_metrics)
        
        # Persist metrics to database
        await self.repository.save_metrics_batch(all_metrics)
        
        # Create alerts for critical and warning metrics
        await self._create_alerts_for_metrics(all_metrics)
        
        # Generate summary
        summary = self._generate_summary(all_metrics)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(all_metrics)
        
        report = SLAReport.create(
            report_type="system_health",
            metrics=all_metrics,
            summary=summary,
            recommendations=recommendations,
            additional_data={
                "total_metrics": len(all_metrics),
                "report_version": "1.0"
            }
        )
        
        # Persist report to database
        await self.repository.save_report(report)
        
        return report
    
    async def _create_alerts_for_metrics(self, metrics: List[SLAMetric]) -> None:
        """Create alerts for metrics that exceed thresholds."""
        for metric in metrics:
            if metric.status in [SLAStatus.WARNING, SLAStatus.CRITICAL]:
                alert_data: Dict[str, Any] = {
                    'alert_type': metric.status.value,
                    'title': f"{metric.status.value.upper()}: {metric.metric_type.value.replace('_', ' ').title()}",
                    'message': f"{metric.metric_type.value.replace('_', ' ').title()} is at {metric.value}{metric.threshold.unit}, exceeding {metric.status.value} threshold of {metric.threshold.warning_threshold if metric.status == SLAStatus.WARNING else metric.threshold.critical_threshold}{metric.threshold.unit}",
                    'metric_type': metric.metric_type.value,
                    'current_value': metric.value,
                    'threshold_value': metric.threshold.warning_threshold if metric.status == SLAStatus.WARNING else metric.threshold.critical_threshold,
                    'triggered_at': metric.measured_at,
                    'additional_data': {
                        'metric_id': str(metric.id),
                        'metric_additional_data': metric.additional_data if metric.additional_data else {}
                    }
                }
                await self.repository.save_alert(alert_data)
    
    async def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active alerts."""
        alert_models = await self.repository.get_active_alerts()
        
        alerts: List[Dict[str, Any]] = []
        for alert in alert_models:
            alerts.append({
                'id': str(alert.id),
                'alert_type': alert.alert_type,
                'title': alert.title,
                'message': alert.message,
                'metric_type': alert.metric_type,
                'current_value': alert.current_value,
                'threshold_value': alert.threshold_value,
                'triggered_at': alert.triggered_at,
                'acknowledged': alert.acknowledged,
                'acknowledged_at': alert.acknowledged_at,
                'acknowledged_by': str(alert.acknowledged_by) if alert.acknowledged_by else None
            })
        
        return alerts
    
    async def acknowledge_alert(self, alert_id: str, acknowledged_by_user_id: str) -> bool:
        """Acknowledge an alert."""
        from uuid import UUID
        try:
            alert_uuid = UUID(alert_id)
            user_uuid = UUID(acknowledged_by_user_id)
            return await self.repository.acknowledge_alert(alert_uuid, user_uuid)
        except (ValueError, TypeError):
            return False

    def _generate_summary(self, metrics: List[SLAMetric]) -> str:
        """Generate human-readable summary of metrics."""
        if not metrics:
            return "No metrics available for analysis."
        
        healthy_count = sum(1 for m in metrics if m.status == SLAStatus.HEALTHY)
        warning_count = sum(1 for m in metrics if m.status == SLAStatus.WARNING)
        critical_count = sum(1 for m in metrics if m.status == SLAStatus.CRITICAL)
        
        total_count = len(metrics)
        health_percentage = (healthy_count / total_count) * 100
        
        if critical_count > 0:
            return f"System health is CRITICAL. {critical_count} critical issue(s) detected out of {total_count} metrics monitored. Immediate attention required."
        elif warning_count > 0:
            return f"System health shows WARNING signs. {warning_count} metric(s) need attention out of {total_count} monitored. Overall health: {health_percentage:.1f}%"
        else:
            return f"System health is GOOD. All {total_count} monitored metrics are within normal ranges. Overall health: {health_percentage:.1f}%"
    
    def _generate_recommendations(self, metrics: List[SLAMetric]) -> List[str]:
        """Generate actionable recommendations based on metrics."""
        recommendations: List[str] = []
        
        for metric in metrics:
            if metric.status == SLAStatus.CRITICAL:
                recommendations.extend(self._get_critical_recommendations(metric))
            elif metric.status == SLAStatus.WARNING:
                recommendations.extend(self._get_warning_recommendations(metric))
        
        # Remove duplicates and limit to top 10
        unique_recommendations = list(dict.fromkeys(recommendations))
        return unique_recommendations[:10]
    
    def _get_critical_recommendations(self, metric: SLAMetric) -> List[str]:
        """Get recommendations for critical metrics."""
        recommendations: List[str] = []
        
        if metric.metric_type == MetricType.MEMORY_USAGE:
            recommendations.append("CRITICAL: Memory usage is extremely high. Restart services and investigate memory leaks.")
            recommendations.append("Consider increasing server memory or optimizing application memory usage.")
        
        elif metric.metric_type == MetricType.CPU_USAGE:
            recommendations.append("CRITICAL: CPU usage is extremely high. Identify and terminate resource-intensive processes.")
            recommendations.append("Consider scaling horizontally or upgrading server capacity.")
        
        elif metric.metric_type == MetricType.DISK_USAGE:
            recommendations.append("CRITICAL: Disk space is almost full. Clean up unnecessary files immediately.")
            recommendations.append("Implement log rotation and archive old data.")
        
        elif metric.metric_type == MetricType.RESPONSE_TIME:
            recommendations.append("CRITICAL: Database response time is very slow. Check database performance and connections.")
            recommendations.append("Consider database optimization or scaling.")
        
        elif metric.metric_type == MetricType.DATABASE_CONNECTIONS:
            recommendations.append("CRITICAL: Too many database connections. Review connection pooling settings.")
            recommendations.append("Investigate potential connection leaks in the application.")
        
        return recommendations
    
    def _get_warning_recommendations(self, metric: SLAMetric) -> List[str]:
        """Get recommendations for warning metrics."""
        recommendations: List[str] = []
        
        if metric.metric_type == MetricType.MEMORY_USAGE:
            recommendations.append("Monitor memory usage trends and plan for capacity increase.")
            
        elif metric.metric_type == MetricType.CPU_USAGE:
            recommendations.append("Monitor CPU usage patterns and consider optimization.")
            
        elif metric.metric_type == MetricType.DISK_USAGE:
            recommendations.append("Plan disk cleanup and consider storage expansion.")
            
        elif metric.metric_type == MetricType.RESPONSE_TIME:
            recommendations.append("Monitor database performance and consider optimization.")
            
        elif metric.metric_type == MetricType.ACTIVE_USERS:
            recommendations.append("Monitor user activity trends and engagement metrics.")
        
        return recommendations
    
    async def initialize_uptime_monitoring(self):
        """Initialize the uptime monitoring system."""
        try:
            await self.uptime_service.initialize_monitoring()
            logger.info("Uptime monitoring initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize uptime monitoring: {e}")
    
    async def perform_health_checks(self):
        """Perform health checks using the uptime monitoring service."""
        try:
            await self.uptime_service.perform_health_checks()
        except Exception as e:
            logger.error(f"Failed to perform health checks: {e}")
    
    async def get_uptime_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive uptime summary."""
        try:
            return await self.uptime_service.get_uptime_summary(hours)
        except Exception as e:
            logger.error(f"Failed to get uptime summary: {e}")
            # Return fallback data
            current_time = datetime.now(timezone.utc)
            return {
                'overall_status': 'unknown',
                'uptime_percentage': 100.0,
                'uptime_duration': 'Unknown',
                'total_downtime_seconds': 0.0,
                'downtime_incidents': 0,
                'period_hours': hours,
                'services': {},
                'metrics_by_service': {},
                'last_updated': current_time
            }
    
    async def get_recent_incidents(self, hours: int = 24, limit: int = 10) -> Sequence[Dict[str, Any]]:
        """Get recent uptime incidents."""
        try:
            incidents = await self.uptime_service.get_recent_incidents(hours, limit)
            return [dict(incident) for incident in incidents]
        except Exception as e:
            logger.error(f"Failed to get recent incidents: {e}")
            return []

