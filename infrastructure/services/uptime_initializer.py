import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from infrastructure.db.database import get_async_session
from infrastructure.services.uptime_scheduler_service import start_uptime_monitoring, stop_uptime_monitoring
from domain.monitoring.services.sla_monitoring_service import SLAMonitoringService

logger = logging.getLogger(__name__)


class UptimeMonitoringInitializer:
    """Service to initialize and manage uptime monitoring during application lifecycle."""
    
    @staticmethod
    async def initialize():
        """Initialize uptime monitoring on application startup."""
        try:
            logger.info("Initializing uptime monitoring system...")
            
            # Initialize the SLA monitoring service with uptime monitoring
            async for session in get_async_session():
                sla_service = SLAMonitoringService(session)
                await sla_service.initialize_uptime_monitoring()
                await session.commit()
                break  # Exit the generator after first iteration
            
            # Start the background uptime monitoring scheduler
            await start_uptime_monitoring()
            
            logger.info("Uptime monitoring system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize uptime monitoring: {e}", exc_info=True)
            # Don't raise exception to prevent app startup failure
    
    @staticmethod
    async def shutdown():
        """Shutdown uptime monitoring on application shutdown."""
        try:
            logger.info("Shutting down uptime monitoring system...")
            await stop_uptime_monitoring()
            logger.info("Uptime monitoring system shutdown completed")
        except Exception as e:
            logger.error(f"Error during uptime monitoring shutdown: {e}", exc_info=True)


@asynccontextmanager
async def uptime_monitoring_lifespan(app: FastAPI):
    """Lifespan context manager for uptime monitoring."""
    # Startup
    await UptimeMonitoringInitializer.initialize()
    
    try:
        yield
    finally:
        # Shutdown
        await UptimeMonitoringInitializer.shutdown()


# For manual initialization if needed
async def initialize_uptime_monitoring():
    """Initialize uptime monitoring manually."""
    await UptimeMonitoringInitializer.initialize()


async def shutdown_uptime_monitoring():
    """Shutdown uptime monitoring manually."""
    await UptimeMonitoringInitializer.shutdown()
