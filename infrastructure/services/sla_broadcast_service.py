import asyncio
import logging
from typing import Optional, Dict, Any, List, TypedDict, cast

from infrastructure.websocket.websocket_manager import websocket_manager
from infrastructure.db.database import get_async_session
from infrastructure.dependencies.service_container import get_sla_monitoring_use_case

logger = logging.getLogger(__name__)


class AlertData(TypedDict):
    id: int
    alert_type: str
    title: str
    message: str
    metric_type: str
    current_value: float
    threshold_value: float
    triggered_at: str
    acknowledged: bool
    acknowledged_at: Optional[str]
    acknowledged_by: Optional[str]


class SystemHealthData(TypedDict):
    overall_status: str
    health_percentage: Optional[float]
    uptime_status: str
    uptime_percentage: Optional[float]
    uptime_duration: Optional[str]
    system_start_time: Optional[str]
    total_metrics: int
    healthy_metrics: int
    warning_metrics: int
    critical_metrics: int
    metrics_summary: Dict[str, Any]
    last_updated: Optional[str]


class UpdateData(TypedDict):
    system_health: SystemHealthData
    alerts: List[AlertData]
    connection_count: int


class SLABroadcastService:
    """Service to periodically broadcast SLA monitoring updates via WebSocket."""
    
    def __init__(self, update_interval: int = 30):
        self.update_interval = update_interval  # seconds
        self.is_running = False
        self._task: Optional[asyncio.Task[None]] = None
    
    async def start(self):
        """Start the periodic SLA monitoring broadcast."""
        if self.is_running:
            return
        
        self.is_running = True
        self._task = asyncio.create_task(self._broadcast_loop())
        logger.info(f"SLA broadcast service started with {self.update_interval}s interval")
    
    async def stop(self):
        """Stop the periodic SLA monitoring broadcast."""
        self.is_running = False
        if self._task and not self._task.done():
            try:
                self._task.cancel()
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("SLA broadcast service stopped")
    
    async def _broadcast_loop(self):
        """Main broadcast loop that sends periodic updates."""
        while self.is_running:
            try:
                await self._send_sla_updates()
                await asyncio.sleep(self.update_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in SLA broadcast loop: {e}")
                await asyncio.sleep(5)  # Brief pause before retrying
    
    async def _send_sla_updates(self):
        """Send SLA updates to all connected WebSocket clients."""
        # Check if there are any connections first
        connection_count = websocket_manager.get_connection_count("sla_monitoring")
        if connection_count == 0:
            return
        
        try:
            # Get database session and SLA use case
            async for session in get_async_session():
                sla_use_case = await get_sla_monitoring_use_case(session)
                
                # Get current system health
                system_health = await sla_use_case.get_system_health_summary()
                alerts = await sla_use_case.get_current_alerts()
                
                # Prepare update message
                update_data: UpdateData = {
                    "system_health": {
                        "overall_status": system_health.overall_status,
                        "health_percentage": system_health.health_percentage,
                        "uptime_status": system_health.uptime_status,
                        "uptime_percentage": system_health.uptime_percentage,
                        "uptime_duration": system_health.uptime_duration,
                        "system_start_time": system_health.system_start_time.isoformat() if system_health.system_start_time else None,
                        "total_metrics": system_health.total_metrics,
                        "healthy_metrics": system_health.healthy_metrics,
                        "warning_metrics": system_health.warning_metrics,
                        "critical_metrics": system_health.critical_metrics,
                        "metrics_summary": system_health.metrics_summary,
                        "last_updated": system_health.last_updated.isoformat()
                    },
                    "alerts": [
                        cast(AlertData, {
                            "id": alert.id,
                            "alert_type": alert.alert_type,
                            "title": alert.title,
                            "message": alert.message,
                            "metric_type": alert.metric_type,
                            "current_value": alert.current_value,
                            "threshold_value": alert.threshold_value,
                            "triggered_at": alert.triggered_at.isoformat(),
                            "acknowledged": alert.acknowledged,
                            "acknowledged_at": alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
                            "acknowledged_by": alert.acknowledged_by
                        })
                        for alert in alerts
                    ],
                    "connection_count": connection_count
                }
                
                # Broadcast to all SLA monitoring subscribers
                await websocket_manager.broadcast_sla_update(cast(Dict[str, Any], update_data))
                
                logger.debug(f"Broadcasted SLA update to {connection_count} connections")
                break  # Exit the async generator
                
        except Exception as e:
            logger.error(f"Error sending SLA updates: {e}")
    
    async def broadcast_alert(self, alert_data: AlertData):
        """Broadcast a new alert immediately to all connected clients."""
        try:
            await websocket_manager.broadcast_alert(cast(Dict[str, Any], alert_data))
            logger.info(f"Broadcasted new alert: {alert_data.get('title', 'Unknown')}")
        except Exception as e:
            logger.error(f"Error broadcasting alert: {e}")
    
    async def broadcast_uptime_update(self, uptime_data: Dict[str, Any]):
        """Broadcast uptime update immediately to all connected clients."""
        try:
            await websocket_manager.broadcast_uptime_update(uptime_data)
            logger.debug("Broadcasted uptime update")
        except Exception as e:
            logger.error(f"Error broadcasting uptime update: {e}")


# Global instance
sla_broadcast_service = SLABroadcastService(update_interval=30)
