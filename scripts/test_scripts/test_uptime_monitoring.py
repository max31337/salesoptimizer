"""
Test script to verify uptime monitoring functionality
"""
import asyncio
import logging
from datetime import datetime, timezone
from infrastructure.db.database import get_async_session
from infrastructure.services.uptime_monitoring_service import UptimeMonitoringService
from infrastructure.services.uptime_scheduler_service import get_uptime_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_uptime_monitoring():
    """Test the uptime monitoring system"""
    print("🧪 Testing Uptime Monitoring System")
    print("=" * 50)
    
    try:
        # Test 1: Basic service creation and initialization
        print("\n1. Testing service initialization...")
        async for session in get_async_session():
            uptime_service = UptimeMonitoringService(session)
            await uptime_service.initialize_monitoring()
            await session.commit()
            print("✅ Service initialized successfully")
            break
        
        # Test 2: Test health checks
        print("\n2. Testing health checks...")
        async for session in get_async_session():
            uptime_service = UptimeMonitoringService(session)
            await uptime_service.perform_health_checks()
            await session.commit()
            print("✅ Health checks completed")
            break
        
        # Test 3: Test uptime calculation
        print("\n3. Testing uptime metrics calculation...")
        async for session in get_async_session():
            uptime_service = UptimeMonitoringService(session)
            summary = await uptime_service.get_uptime_summary(24)
            
            print(f"Overall Status: {summary.get('overall_status', 'unknown')}")
            print(f"Uptime Percentage: {summary.get('uptime_percentage', 0):.2f}%")
            print(f"Uptime Duration: {summary.get('uptime_duration', 'unknown')}")
            print(f"Downtime Incidents: {summary.get('downtime_incidents', 0)}")
            print(f"Services: {list(summary.get('services', {}).keys())}")
            
            print("✅ Uptime metrics calculated successfully")
            break
        
        # Test 4: Test recent incidents
        print("\n4. Testing recent incidents...")
        async for session in get_async_session():
            uptime_service = UptimeMonitoringService(session)
            incidents = await uptime_service.get_recent_incidents(24, 5)
            print(f"Recent incidents found: {len(incidents)}")
            
            for i, incident in enumerate(incidents[:3], 1):
                print(f"  {i}. Service: {incident['service_name']}, "
                      f"Started: {incident['started_at']}, "
                      f"Resolved: {incident['resolved']}")
            
            print("✅ Recent incidents retrieved successfully")
            break
        
        # Test 5: Test scheduler service
        print("\n5. Testing scheduler service...")
        scheduler = await get_uptime_scheduler()
        
        print(f"Scheduler running: {scheduler.is_running}")
        # Remove access to protected attribute
        print("Monitoring interval: [configured]")
        
        # Get summary through scheduler
        scheduler_summary = await scheduler.get_uptime_summary(24)
        print(f"Scheduler uptime percentage: {scheduler_summary.get('uptime_percentage', 0):.2f}%")
        print("✅ Scheduler service tested successfully")
        
        print("\n🎉 All tests completed successfully!")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        logger.error(f"Test error: {e}", exc_info=True)
        return False


async def simulate_downtime():
    """Simulate a downtime event for testing"""
    print("\n🔧 Simulating downtime for testing...")
    
    try:
        async for session in get_async_session():
            uptime_service = UptimeMonitoringService(session)
            
            # Record a manual downtime
            start_time = datetime.now(timezone.utc)
            await uptime_service.record_manual_downtime(
                service_name='database',
                start_time=start_time,
                reason='Test downtime simulation',
                severity='minor'
            )
            
            # Wait a moment and then record recovery
            await asyncio.sleep(2)
            
            # Recovery will be detected automatically by the next health check
            await uptime_service.perform_health_checks()
            
            await session.commit()
            print("✅ Downtime simulation completed")
            break
            
        # Check the results
        async for session in get_async_session():
            uptime_service = UptimeMonitoringService(session)
            summary = await uptime_service.get_uptime_summary(1)  # Last 1 hour
            print(f"Post-simulation uptime: {summary.get('uptime_percentage', 100):.2f}%")
            print(f"Downtime incidents: {summary.get('downtime_incidents', 0)}")
            break
            
    except Exception as e:
        print(f"❌ Downtime simulation failed: {e}")
        logger.error(f"Simulation error: {e}", exc_info=True)


if __name__ == "__main__":
    async def main():
        success = await test_uptime_monitoring()
        
        if success:
            print("\nRunning downtime simulation...")
            await simulate_downtime()
        
        print("\n🏁 Testing complete!")
    
    asyncio.run(main())
