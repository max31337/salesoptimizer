"""
Uptime monitoring service startup and integration.
"""
import asyncio
import logging
from typing import Optional, Any, Dict, Union
from fastapi import FastAPI
from contextlib import asynccontextmanager

from infrastructure.services.uptime_scheduler_service import (
    start_uptime_monitoring, 
    stop_uptime_monitoring,
    get_uptime_scheduler
)

logger = logging.getLogger(__name__)


class UptimeServiceStartup:
    """Manages uptime monitoring service lifecycle."""
    
    def __init__(self):
        self._is_started = False
        self._startup_task: Optional[asyncio.Task[Any]] = None
    
    async def start(self):
        """Start the uptime monitoring service."""
        if self._is_started:
            logger.warning("Uptime monitoring service already started")
            return
            
        try:
            logger.info("Starting uptime monitoring service...")
            await start_uptime_monitoring()
            self._is_started = True
            logger.info("Uptime monitoring service started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start uptime monitoring service: {e}", exc_info=True)
            raise
    
    async def stop(self):
        """Stop the uptime monitoring service."""
        if not self._is_started:
            return
            
        try:
            logger.info("Stopping uptime monitoring service...")
            await stop_uptime_monitoring()
            self._is_started = False
            logger.info("Uptime monitoring service stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping uptime monitoring service: {e}", exc_info=True)
    
    @property
    def is_started(self) -> bool:
        """Check if the service is started."""
        return self._is_started


# Global instance
_uptime_startup = UptimeServiceStartup()


async def get_uptime_startup() -> UptimeServiceStartup:
    """Get the global uptime startup instance."""
    return _uptime_startup


@asynccontextmanager
async def uptime_monitoring_lifespan(app: FastAPI):
    """FastAPI lifespan context manager for uptime monitoring."""
    startup = await get_uptime_startup()
    
    # Startup
    try:
        await startup.start()
        yield
    finally:
        # Shutdown
        await startup.stop()


async def force_health_check():
    """Force an immediate health check."""
    try:
        scheduler = await get_uptime_scheduler()
        await scheduler.force_health_check()
        logger.info("Forced health check completed")
    except Exception as e:
        logger.error(f"Failed to force health check: {e}", exc_info=True)


async def get_uptime_status() -> Dict[str, Union[bool, list[str], str]]:
    """Get current uptime status."""
    try:
        scheduler = await get_uptime_scheduler()
        return {
            "is_running": scheduler.is_running,
            "monitoring_enabled": True,
            "services_monitored": ["system", "database", "api", "frontend"]
        }
    except Exception as e:
        logger.error(f"Failed to get uptime status: {e}", exc_info=True)
        return {
            "is_running": False,
            "monitoring_enabled": False,
            "error": str(e)
        }
