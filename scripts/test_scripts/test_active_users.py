import asyncio
import sys
sys.path.append('.')
from infrastructure.db.database import get_async_session
from application.use_cases.sla_monitoring_use_cases import SLAMonitoringUseCase
from domain.monitoring.services.sla_monitoring_service import SLAMonitoringService

async def test_system_health():
    async for session in get_async_session():
        sla_service = SLAMonitoringService(session)
        use_case = SLAMonitoringUseCase(sla_service)
        
        # Test the system health summary
        health = await use_case.get_system_health_summary()
        print(f'Active Users (24h): {health.active_users_24h}')
        print(f'Metrics Summary Active Users: {health.metrics_summary.get("active_users", "N/A")}')
        break

if __name__ == "__main__":
    asyncio.run(test_system_health())
