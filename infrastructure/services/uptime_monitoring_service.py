import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, TypedDict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, and_ 
import logging

from infrastructure.db.models.uptime_event_model import UptimeEventModel

logger = logging.getLogger(__name__)


class IncidentDict(TypedDict):
    id: str
    service_name: str
    started_at: datetime
    ended_at: Optional[datetime]
    duration_seconds: Optional[float]
    reason: Optional[str]
    severity: str
    resolved: bool
    auto_detected: bool


class UptimeMonitoringService:
    """Service for tracking and monitoring system uptime."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self._health_check_interval = 30  # seconds
        self._downtime_threshold = 60  # seconds before considering system down
        self._monitored_services = ['system', 'database', 'api', 'frontend']
        self._last_health_check: Dict[str, datetime] = {}
        self._service_states: Dict[str, bool] = {}  # True = up, False = down
        self._downtime_start: Dict[str, Optional[datetime]] = {}
        
    async def initialize_monitoring(self):
        """Initialize the uptime monitoring system."""
        current_time = datetime.now(timezone.utc)
        
        # Record system start event
        await self._record_event(
            service_name='system',
            event_type='start',
            timestamp=current_time,
            reason='System initialization',
            auto_detected=True
        )
        
        # Initialize all services as up
        for service in self._monitored_services:
            self._service_states[service] = True
            self._last_health_check[service] = current_time
            self._downtime_start[service] = None
            
        logger.info("Uptime monitoring initialized for services: %s", self._monitored_services)
    
    async def record_health_check(self, service_name: str, is_healthy: bool, metadata: Optional[Dict[str, Any]] = None):
        """Record a health check result for a service."""
        current_time = datetime.now(timezone.utc)
        previous_state = self._service_states.get(service_name, True)
        
        # Update service state
        self._service_states[service_name] = is_healthy
        self._last_health_check[service_name] = current_time
        
        # Handle state transitions
        if previous_state and not is_healthy:
            # Service went down
            self._downtime_start[service_name] = current_time
            await self._record_event(
                service_name=service_name,
                event_type='downtime_start',
                timestamp=current_time,
                reason='Health check failed',
                severity='major' if service_name in ['system', 'database'] else 'minor',
                auto_detected=True,
                meta_data=metadata
            )
            logger.warning(f"Service {service_name} went down at {current_time}")
            
        elif not previous_state and is_healthy:
            # Service came back up
            downtime_start = self._downtime_start.get(service_name)
            if downtime_start:
                downtime_duration = (current_time - downtime_start).total_seconds()
                await self._record_event(
                    service_name=service_name,
                    event_type='downtime_end',
                    timestamp=current_time,
                    duration_seconds=downtime_duration,
                    reason='Service recovered',
                    severity='minor',
                    auto_detected=True,
                    meta_data=metadata
                )
                self._downtime_start[service_name] = None
                logger.info(f"Service {service_name} recovered after {downtime_duration:.1f} seconds")
    
    async def perform_health_checks(self):
        """Perform health checks on all monitored services."""
        try:
            # Check database connectivity
            db_healthy = await self._check_database_health()
            await self.record_health_check('database', db_healthy)
            
            # Check API health (basic check)
            api_healthy = await self._check_api_health()
            await self.record_health_check('api', api_healthy)
            
            # System health is implied if we can execute this code
            await self.record_health_check('system', True)
            
        except Exception as e:
            logger.error(f"Error during health checks: {e}")
            # If we can't perform health checks, consider all services potentially down
            for service in self._monitored_services:
                if service != 'system':  # System is obviously up if we're running this code
                    await self.record_health_check(service, False, {'error': str(e)})
    
    async def _check_database_health(self) -> bool:
        """Check if database is healthy."""
        try:
            start_time = time.time()
            result = await self.session.execute(text("SELECT 1"))
            result.fetchone()
            response_time = time.time() - start_time
            
            # Consider unhealthy if response time > 5 seconds
            return response_time < 5.0
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    async def _check_api_health(self) -> bool:
        """Check if API is healthy."""
        try:
            # This is a simple check - in production you might want to make HTTP requests
            # For now, we'll assume API is healthy if database is healthy
            return await self._check_database_health()
        except Exception:
            return False
    
    async def _record_event(
        self,
        service_name: str,
        event_type: str,
        timestamp: datetime,
        duration_seconds: Optional[float] = None,
        reason: Optional[str] = None,
        severity: str = 'minor',
        auto_detected: bool = True,
        meta_data: Optional[Dict[str, Any]] = None
    ):
        """Record an uptime event in the database."""
        try:
            event = UptimeEventModel(
                event_type=event_type,
                service_name=service_name,
                timestamp=timestamp,
                duration_seconds=duration_seconds,
                reason=reason,
                severity=severity,
                auto_detected=auto_detected,
                meta_data=meta_data
            )
            
            self.session.add(event)
            await self.session.commit()
            
        except Exception as e:
            logger.error(f"Failed to record uptime event: {e}")
            await self.session.rollback()
    
    async def calculate_uptime_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """Calculate uptime metrics for the specified period."""
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=hours)
        
        metrics: Dict[str, Any] = {}
        
        for service in self._monitored_services:
            uptime_data = await self._calculate_service_uptime(service, start_time, end_time)
            metrics[service] = uptime_data
        
        # Calculate overall system uptime (worst case of all services)
        if metrics:
            overall_uptime = min(m['uptime_percentage'] for m in metrics.values()) 
            total_incidents = sum(m['downtime_incidents'] for m in metrics.values()) 
            total_downtime = sum(m['total_downtime_seconds'] for m in metrics.values())
            
            metrics['overall'] = {
                'uptime_percentage': overall_uptime,
                'total_downtime_seconds': total_downtime,
                'downtime_incidents': total_incidents,
                'period_hours': hours
            }
        
        return metrics
    
    async def _calculate_service_uptime(
        self, 
        service_name: str, 
        start_time: datetime, 
        end_time: datetime
    ) -> Dict[str, Any]:
        """Calculate uptime metrics for a specific service."""
        try:
            # Get all downtime events in the period
            stmt = select(UptimeEventModel).where(
                and_(
                    UptimeEventModel.service_name == service_name,
                    UptimeEventModel.timestamp >= start_time,
                    UptimeEventModel.timestamp <= end_time,
                    UptimeEventModel.event_type.in_(['downtime_start', 'downtime_end'])
                )
            ).order_by(UptimeEventModel.timestamp)
            
            result = await self.session.execute(stmt)
            events = result.scalars().all()
            
            # Calculate total downtime
            total_downtime_seconds = 0.0
            downtime_incidents = 0
            current_downtime_start = None
            
            # Check if service was already down at the start of the period
            pre_period_stmt = select(UptimeEventModel).where(
                and_(
                    UptimeEventModel.service_name == service_name,
                    UptimeEventModel.timestamp < start_time,
                    UptimeEventModel.event_type.in_(['downtime_start', 'downtime_end'])
                )
            ).order_by(UptimeEventModel.timestamp.desc()).limit(1)
            
            pre_result = await self.session.execute(pre_period_stmt)
            last_event = pre_result.scalar_one_or_none()
            
            if last_event and last_event.event_type == 'downtime_start':
                # Service was down at start of period
                current_downtime_start = start_time
                downtime_incidents += 1
            
            # Process events in chronological order
            for event in events:
                if event.event_type == 'downtime_start':
                    current_downtime_start = event.timestamp
                    downtime_incidents += 1
                elif event.event_type == 'downtime_end' and current_downtime_start:
                    downtime_duration = (event.timestamp - current_downtime_start).total_seconds()
                    total_downtime_seconds += downtime_duration
                    current_downtime_start = None
            
            # If service is still down at end of period
            if current_downtime_start:
                downtime_duration = (end_time - current_downtime_start).total_seconds()
                total_downtime_seconds += downtime_duration
            
            # Calculate uptime percentage
            total_period_seconds = (end_time - start_time).total_seconds()
            uptime_seconds = total_period_seconds - total_downtime_seconds
            uptime_percentage = (uptime_seconds / total_period_seconds) * 100 if total_period_seconds > 0 else 100.0
            
            # Ensure percentage is between 0 and 100
            uptime_percentage = max(0.0, min(100.0, uptime_percentage))
            
            return {
                'uptime_percentage': uptime_percentage,
                'total_downtime_seconds': total_downtime_seconds,
                'downtime_incidents': downtime_incidents,
                'uptime_seconds': uptime_seconds,
                'total_period_seconds': total_period_seconds
            }
            
        except Exception as e:
            logger.error(f"Error calculating uptime for {service_name}: {e}")
            return {
                'uptime_percentage': 0.0,
                'total_downtime_seconds': 0.0,
                'downtime_incidents': 0,
                'uptime_seconds': 0.0,
                'total_period_seconds': 0.0
            }
    
    async def get_current_service_states(self) -> Dict[str, Dict[str, Any]]:
        """Get current state of all monitored services."""
        current_time = datetime.now(timezone.utc)
        states: Dict[str, Dict[str, Any]] = {}
        
        for service in self._monitored_services:
            last_check = self._last_health_check.get(service)
            is_up = self._service_states.get(service, True)
            downtime_start = self._downtime_start.get(service)
            
            # Check if service is stale (no health check in a while)
            is_stale = False
            if last_check:
                time_since_check = (current_time - last_check).total_seconds()
                is_stale = time_since_check > self._downtime_threshold * 2
            
            current_downtime = 0.0
            if downtime_start and not is_up:
                current_downtime = (current_time - downtime_start).total_seconds()
            
            states[service] = {
                'is_up': is_up and not is_stale,
                'last_check': last_check,
                'is_stale': is_stale,
                'current_downtime_seconds': current_downtime,
                'status': 'operational' if (is_up and not is_stale) else 'down'
            }
        
        return states
    
    async def get_uptime_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get a comprehensive uptime summary."""
        metrics = await self.calculate_uptime_metrics(hours)
        states = await self.get_current_service_states()
        
        # Determine overall status
        overall_status = 'operational'
        all_services_up = all(state['is_up'] for state in states.values())
        
        if not all_services_up:
            critical_services_down = any(
                not states.get(service, {}).get('is_up', True) 
                for service in ['system', 'database']
            )
            overall_status = 'critical' if critical_services_down else 'degraded'
        
        overall_metrics = metrics.get('overall', {})
        uptime_percentage = overall_metrics.get('uptime_percentage', 100.0)
        
        # Format uptime duration
        current_time = datetime.now(timezone.utc)
        uptime_duration = self._format_uptime_duration(uptime_percentage, hours)
        
        return {
            'overall_status': overall_status,
            'uptime_percentage': uptime_percentage,
            'uptime_duration': uptime_duration,
            'total_downtime_seconds': overall_metrics.get('total_downtime_seconds', 0.0),
            'downtime_incidents': overall_metrics.get('downtime_incidents', 0),
            'period_hours': hours,
            'services': states,
            'metrics_by_service': metrics,
            'last_updated': current_time
        }
    
    def _format_uptime_duration(self, uptime_percentage: float, period_hours: int) -> str:
        """Format uptime as a human-readable duration."""
        if uptime_percentage >= 99.9:
            return f">{period_hours - 1}h {int((period_hours % 1) * 60)}m"
        
        downtime_hours = period_hours * (100 - uptime_percentage) / 100
        
        if downtime_hours < 1:
            downtime_minutes = int(downtime_hours * 60)
            uptime_hours = period_hours
            uptime_minutes = int((period_hours * 60) - downtime_minutes)
            return f"{uptime_hours}h {uptime_minutes}m"
        else:
            uptime_hours = int(period_hours - downtime_hours)
            uptime_minutes = int((period_hours - downtime_hours - uptime_hours) * 60)
            return f"{uptime_hours}h {uptime_minutes}m"
    
    async def record_manual_downtime(
        self,
        service_name: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        reason: str = "Manual maintenance",
        severity: str = 'minor'
    ):
        """Record a manual downtime event (e.g., planned maintenance)."""
        await self._record_event(
            service_name=service_name,
            event_type='downtime_start',
            timestamp=start_time,
            reason=reason,
            severity=severity,
            auto_detected=False
        )
        
        if end_time:
            duration = (end_time - start_time).total_seconds()
            await self._record_event(
                service_name=service_name,
                event_type='downtime_end',
                timestamp=end_time,
                duration_seconds=duration,
                reason=f"{reason} - ended",
                severity=severity,
                auto_detected=False
            )
    
    async def get_recent_incidents(self, hours: int = 24, limit: int = 10) -> List[IncidentDict]:
        """Get recent downtime incidents."""
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=hours)
        
        stmt = select(UptimeEventModel).where(
            and_(
                UptimeEventModel.timestamp >= start_time,
                UptimeEventModel.event_type == 'downtime_start'
            )
        ).order_by(UptimeEventModel.timestamp.desc()).limit(limit)
        
        result = await self.session.execute(stmt)
        events = result.scalars().all()
        
        incidents: List[IncidentDict] = []
        for event in events:
            # Try to find corresponding end event
            end_stmt = select(UptimeEventModel).where(
                and_(
                    UptimeEventModel.service_name == event.service_name,
                    UptimeEventModel.event_type == 'downtime_end',
                    UptimeEventModel.timestamp > event.timestamp
                )
            ).order_by(UptimeEventModel.timestamp).limit(1)
            
            end_result = await self.session.execute(end_stmt)
            end_event = end_result.scalar_one_or_none()
            
            duration = None
            resolved = end_event is not None
            if end_event:
                duration = (end_event.timestamp - event.timestamp).total_seconds()
            
            incidents.append({
                'id': str(event.id),
                'service_name': event.service_name,
                'started_at': event.timestamp,
                'ended_at': end_event.timestamp if end_event else None,
                'duration_seconds': duration,
                'reason': event.reason,
                'severity': event.severity,
                'resolved': resolved,
                'auto_detected': event.auto_detected
            })
        
        return incidents
