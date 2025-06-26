import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from infrastructure.db.database import get_async_session
from infrastructure.services.uptime_monitoring_service import UptimeMonitoringService

logger = logging.getLogger(__name__)


class UptimeSchedulerService:
    """Background service that continuously monitors system uptime."""
    
    def __init__(self):
        self._monitoring_task: Optional[asyncio.Task[None]] = None
        self._is_running = False
        self._monitoring_interval = 30  # Check every 30 seconds
        self._uptime_service: Optional[UptimeMonitoringService] = None
        
    async def start_monitoring(self):
        """Start the background uptime monitoring task."""
        if self._is_running:
            logger.warning("Uptime monitoring is already running")
            return
            
        logger.info("Starting uptime monitoring scheduler")
        self._is_running = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        
    async def stop_monitoring(self):
        """Stop the background uptime monitoring task."""
        if not self._is_running:
            return
            
        logger.info("Stopping uptime monitoring scheduler")
        self._is_running = False
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                logger.info("Uptime monitoring task cancelled")
            self._monitoring_task = None
            
    async def _monitoring_loop(self):
        """Main monitoring loop that runs continuously."""
        while self._is_running:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self._monitoring_interval)
            except asyncio.CancelledError:
                logger.info("Monitoring loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                # Continue monitoring even if there's an error
                await asyncio.sleep(self._monitoring_interval)
                
    async def _perform_health_checks(self):
        """Perform health checks on all monitored services."""
        try:
            # Get a fresh database session for each check
            async for session in get_async_session():
                uptime_service = UptimeMonitoringService(session)
                
                # Initialize monitoring if this is the first run
                if self._uptime_service is None:
                    await uptime_service.initialize_monitoring()
                    self._uptime_service = uptime_service
                    
                # Perform the actual health checks
                await uptime_service.perform_health_checks()
                
                # Commit the session
                await session.commit()
                break  # Exit the async generator after first iteration
                
        except Exception as e:
            logger.error(f"Failed to perform health checks: {e}", exc_info=True)
              
    async def get_uptime_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get uptime summary from the monitoring service."""
        try:
            async for session in get_async_session():
                uptime_service = UptimeMonitoringService(session)
                summary = await uptime_service.get_uptime_summary(hours)
                return summary
        except Exception as e:
            logger.error(f"Failed to get uptime summary: {e}", exc_info=True)
            
        # Fallback return value
        return {
            'overall_status': 'unknown',
            'uptime_percentage': 0.0,
            'uptime_duration': '0 minutes',
            'total_downtime_seconds': 0.0,
            'downtime_incidents': 0,
            'period_hours': hours,
            'services': {},
            'metrics_by_service': {},
            'last_updated': datetime.now(timezone.utc)
        }
            
    async def force_health_check(self):
        """Force an immediate health check outside the normal schedule."""
        await self._perform_health_checks()
        
    @property
    def is_running(self) -> bool:
        """Check if the monitoring service is currently running."""
        return self._is_running


# Global instance
_uptime_scheduler = UptimeSchedulerService()


async def get_uptime_scheduler() -> UptimeSchedulerService:
    """Get the global uptime scheduler instance."""
    return _uptime_scheduler


async def start_uptime_monitoring():
    """Start the global uptime monitoring service."""
    scheduler = await get_uptime_scheduler()
    await scheduler.start_monitoring()


async def stop_uptime_monitoring():
    """Stop the global uptime monitoring service."""
    scheduler = await get_uptime_scheduler()
    await scheduler.stop_monitoring()
