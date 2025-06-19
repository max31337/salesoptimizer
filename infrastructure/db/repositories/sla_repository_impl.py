from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func
from uuid import UUID

from infrastructure.db.models.sla_metric_model import SLAMetricModel
from infrastructure.db.models.sla_alert_model import SLAAlertModel
from infrastructure.db.models.sla_report_model import SLAReportModel
from infrastructure.db.models.sla_threshold_model import SLAThresholdModel
from domain.monitoring.entities.sla_monitoring import SLAMetric, SLAReport


class SLARepositoryImpl:
    """Repository implementation for SLA monitoring data persistence."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def save_metric(self, metric: SLAMetric) -> None:
        """Save an SLA metric to the database."""
        metric_model = SLAMetricModel(
            id=metric.id,
            metric_type=metric.metric_type.value,
            value=metric.value,
            status=metric.status.value,
            unit=metric.threshold.unit,
            threshold_warning=metric.threshold.warning_threshold,
            threshold_critical=metric.threshold.critical_threshold,
            measured_at=metric.measured_at,
            additional_data=metric.additional_data
        )
        
        self.session.add(metric_model)
        await self.session.commit()
    
    async def save_metrics_batch(self, metrics: List[SLAMetric]) -> None:
        """Save multiple SLA metrics in batch."""
        metric_models: List[SLAMetricModel] = []
        for metric in metrics:
            metric_model = SLAMetricModel(
                id=metric.id,
                metric_type=metric.metric_type.value,
                value=metric.value,
                status=metric.status.value,
                unit=metric.threshold.unit,
                threshold_warning=metric.threshold.warning_threshold,
                threshold_critical=metric.threshold.critical_threshold,
                measured_at=metric.measured_at,
                additional_data=metric.additional_data
            )
            metric_models.append(metric_model)
        
        self.session.add_all(metric_models)
        await self.session.commit()
    
    async def save_alert(self, alert_data: Dict[str, Any]) -> SLAAlertModel:
        """Save an SLA alert to the database."""
        alert_model = SLAAlertModel(
            alert_type=alert_data['alert_type'],
            title=alert_data['title'],
            message=alert_data['message'],
            metric_type=alert_data['metric_type'],
            current_value=alert_data['current_value'],           
            threshold_value=alert_data['threshold_value'],
            triggered_at=alert_data.get('triggered_at', datetime.now(timezone.utc)),
            additional_data=alert_data.get('additional_data', {})
        )
        
        self.session.add(alert_model)
        await self.session.commit()
        await self.session.refresh(alert_model)
        return alert_model
    
    async def save_report(self, report: SLAReport) -> None:
        """Save an SLA report to the database."""
        # Convert metrics to serializable format for snapshot
        metrics_snapshot: List[Dict[str, Any]] = []
        for metric in report.metrics:
            metrics_snapshot.append({
                'id': str(metric.id),
                'metric_type': metric.metric_type.value,
                'value': metric.value,
                'status': metric.status.value,
                'measured_at': metric.measured_at.isoformat(),
                'additional_data': metric.additional_data
            })
        
        report_model = SLAReportModel(
            id=report.id,
            report_type=report.report_type,
            overall_status=report.overall_status.value,
            generated_at=report.generated_at,
            summary=report.summary,
            recommendations=report.recommendations,
            metrics_snapshot=metrics_snapshot,
            critical_metrics_count=len(report.critical_metrics),
            warning_metrics_count=len(report.warning_metrics),
            healthy_metrics_count=len(report.healthy_metrics),
            total_metrics_count=len(report.metrics),
            additional_data=report.additional_data
        )
        
        self.session.add(report_model)
        await self.session.commit()
    
    async def get_active_alerts(self) -> List[SLAAlertModel]:
        """Get all active (unresolved) alerts."""
        stmt = select(SLAAlertModel).where(
            SLAAlertModel.resolved == False
        ).order_by(desc(SLAAlertModel.triggered_at))
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_alert_by_id(self, alert_id: UUID) -> Optional[SLAAlertModel]:
        """Get an alert by ID."""
        stmt = select(SLAAlertModel).where(SLAAlertModel.id == alert_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    async def acknowledge_alert(self, alert_id: UUID, acknowledged_by: UUID) -> bool:
        """Acknowledge an alert."""
        try:
            print(f"DEBUG: Repository - acknowledging alert {alert_id} by user {acknowledged_by}")
            alert = await self.get_alert_by_id(alert_id)
            if not alert:
                print(f"DEBUG: Alert {alert_id} not found")
                return False
            
            if alert.acknowledged:
                print(f"DEBUG: Alert {alert_id} already acknowledged")
                return False
            
            alert.acknowledged = True
            alert.acknowledged_at = datetime.now(timezone.utc)
            alert.acknowledged_by = acknowledged_by
            
            print(f"DEBUG: Committing acknowledgment for alert {alert_id}")
            await self.session.commit()
            print(f"DEBUG: Successfully acknowledged alert {alert_id}")
            return True
        except Exception as e:
            print(f"DEBUG: Error in acknowledge_alert: {e}")
            await self.session.rollback()
            raise
    
    async def resolve_alert(self, alert_id: UUID) -> bool:
        """Mark an alert as resolved."""
        alert = await self.get_alert_by_id(alert_id)
        if not alert or alert.resolved:
            return False
        
        alert.resolved = True
        alert.resolved_at = datetime.now(timezone.utc)
        
        await self.session.commit()
        return True
    
    async def get_metrics_history(self, 
                                metric_type: Optional[str] = None,
                                hours: int = 24,
                                limit: int = 1000) -> List[SLAMetricModel]:
        """Get historical metrics data."""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        stmt = select(SLAMetricModel).where(
            SLAMetricModel.measured_at >= cutoff_time
        )
        
        if metric_type:
            stmt = stmt.where(SLAMetricModel.metric_type == metric_type)
        
        stmt = stmt.order_by(desc(SLAMetricModel.measured_at)).limit(limit)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_thresholds(self) -> List[SLAThresholdModel]:
        """Get all active SLA thresholds."""
        stmt = select(SLAThresholdModel).where(SLAThresholdModel.is_active == True)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_threshold_by_metric_type(self, metric_type: str) -> Optional[SLAThresholdModel]:
        """Get active threshold for a specific metric type."""
        stmt = select(SLAThresholdModel).where(
            and_(
                SLAThresholdModel.metric_type == metric_type,
                SLAThresholdModel.is_active == True
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_reports_history(self, report_type: Optional[str] = None, limit: int = 50) -> List[SLAReportModel]:
        """Get historical reports."""
        stmt = select(SLAReportModel)
        
        if report_type:
            stmt = stmt.where(SLAReportModel.report_type == report_type)
        
        stmt = stmt.order_by(desc(SLAReportModel.generated_at)).limit(limit)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_system_health_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get aggregated system health statistics."""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        # Get metrics count by status
        status_stmt = select(
            SLAMetricModel.status,
            func.count(SLAMetricModel.id).label('count')
        ).where(
            SLAMetricModel.measured_at >= cutoff_time
        ).group_by(SLAMetricModel.status)
        
        status_result = await self.session.execute(status_stmt)
        status_counts = {row.status: row.count for row in status_result}
        
        # Get alert counts
        alert_stmt = select(
            func.count(SLAAlertModel.id).label('total_alerts'),
            func.sum(func.case((SLAAlertModel.acknowledged == False, 1), else_=0)).label('unacknowledged_alerts'),
            func.sum(func.case((SLAAlertModel.resolved == False, 1), else_=0)).label('unresolved_alerts')
        ).where(
            SLAAlertModel.triggered_at >= cutoff_time
        )
        
        alert_result = await self.session.execute(alert_stmt)
        alert_counts = alert_result.one()
        
        return {
            'metrics_by_status': status_counts,
            'total_alerts': alert_counts.total_alerts or 0,
            'unacknowledged_alerts': alert_counts.unacknowledged_alerts or 0,
            'unresolved_alerts': alert_counts.unresolved_alerts or 0,
            'period_hours': hours
        }
