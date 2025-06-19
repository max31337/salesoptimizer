import asyncio
import logging
from typing import Dict, Any, Optional

from infrastructure.websocket.websocket_manager import websocket_manager
from infrastructure.db.database import get_async_session
from infrastructure.dependencies.service_container import get_sla_monitoring_use_case

logger = logging.getLogger(__name__)


class SLAWebSocketService:
    """Service for handling real-time SLA monitoring updates via WebSocket."""
    
    def __init__(self, update_interval: int = 30):
        self.update_interval = update_interval  # seconds
        self.is_running = False
        self._task: Optional[asyncio.Task[None]] = None
        self._last_data: Optional[Dict[str, Any]] = None
    
    async def start(self):
        """Start the background service for periodic SLA updates."""
        if self.is_running:
            logger.warning("SLA WebSocket service is already running")
            return
        
        self.is_running = True
        self._task = asyncio.create_task(self._periodic_update_loop())
        logger.info(f"SLA WebSocket service started with {self.update_interval}s interval")
    
    async def stop(self):
        """Stop the background service."""
        self.is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("SLA WebSocket service stopped")
    
    async def _periodic_update_loop(self):
        """Main loop for periodic SLA updates."""
        while self.is_running:
            try:
                await self._send_sla_update()
                await asyncio.sleep(self.update_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in SLA update loop: {e}")
                await asyncio.sleep(5)  # Short delay before retrying
    
    async def _send_sla_update(self):
        """Collect and send SLA data to all connected clients."""
        try:
            # Check if there are any connected clients
            connection_count = websocket_manager.get_connection_count("sla_monitoring")
            if connection_count == 0:
                return  # No clients connected, skip update
            
            # Get SLA data using the use case
            async for session in get_async_session():
                sla_use_case = await get_sla_monitoring_use_case(session)
                
                system_health = await sla_use_case.get_system_health_summary()
                alerts = await sla_use_case.get_current_alerts()
                
                # Prepare the data
                sla_data: Dict[str, Any] = {
                    "system_health": {
                        "overall_status": system_health.overall_status,
                        "health_percentage": system_health.health_percentage,
                        "uptime_status": system_health.uptime_status,
                        "uptime_percentage": system_health.uptime_percentage,
                        "uptime_duration": system_health.uptime_duration,
                        "system_start_time": system_health.system_start_time.isoformat() if system_health.system_start_time else None,
                        "last_updated": system_health.last_updated.isoformat(),
                        "total_metrics": system_health.total_metrics,
                        "healthy_metrics": system_health.healthy_metrics,
                        "warning_metrics": system_health.warning_metrics,
                        "critical_metrics": system_health.critical_metrics,
                        "metrics_summary": system_health.metrics_summary
                    },
                    "alerts": [
                        {
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
                        }
                        for alert in alerts
                    ],
                    "connection_info": {
                        "active_connections": connection_count,
                        "update_interval": self.update_interval
                    }
                }
                
                # Only send update if data has changed (to reduce unnecessary traffic)
                if self._has_data_changed(sla_data):
                    await websocket_manager.broadcast_sla_update(sla_data)
                    self._last_data = sla_data
                    logger.debug(f"SLA update sent to {connection_count} clients")
                
                break  # Exit the async generator
                
        except Exception as e:
            logger.error(f"Error collecting SLA data: {e}")
    
    def _has_data_changed(self, new_data: Dict[str, Any]) -> bool:
        """Check if the SLA data has changed since the last update."""
        if self._last_data is None:
            return True
        
        # Compare key metrics that change frequently
        last_health = self._last_data.get("system_health", {})
        new_health = new_data.get("system_health", {})
        
        # Check if important metrics have changed
        key_metrics = [
            "overall_status", "health_percentage", "uptime_percentage",
            "healthy_metrics", "warning_metrics", "critical_metrics"
        ]
        
        for metric in key_metrics:
            if last_health.get(metric) != new_health.get(metric):
                return True
        
        # Check if alerts have changed
        last_alerts = self._last_data.get("alerts", [])
        new_alerts = new_data.get("alerts", [])
        
        if len(last_alerts) != len(new_alerts):
            return True
        
        # Check if any alert status has changed
        for last_alert, new_alert in zip(last_alerts, new_alerts):
            if (last_alert.get("acknowledged") != new_alert.get("acknowledged") or
                last_alert.get("id") != new_alert.get("id")):
                return True
        
        return False
    
    async def send_immediate_update(self):
        """Send an immediate SLA update (useful after manual actions)."""
        await self._send_sla_update()
    
    async def send_uptime_alert(self, uptime_data: Dict[str, Any]):
        """Send a specific uptime alert to all connected clients."""
        await websocket_manager.broadcast_uptime_update(uptime_data)
    
    async def send_new_alert(self, alert_data: Dict[str, Any]):
        """Send a new alert notification to all connected clients."""
        await websocket_manager.broadcast_alert(alert_data)


# Global SLA WebSocket service instance
sla_websocket_service = SLAWebSocketService(update_interval=30)  # Update every 30 seconds
