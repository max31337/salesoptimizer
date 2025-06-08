#!/usr/bin/env python3
"""
Startup Service - Handles platform initialization on FastAPI startup.
This service ensures the platform is properly initialized with system organization,
superadmin, and platform management team.
"""
import sys
from pathlib import Path
from typing import Dict, Any, Callable, TypeVar, Awaitable
import asyncio
from functools import wraps

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.create_super_admin import initialize_platform

T = TypeVar('T')

def async_to_sync(func: Callable[..., Awaitable[T]]) -> Callable[..., T]:
    """Decorator to run async functions in sync context."""
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        if loop.is_running():
            # If we're already in an async context, create a new thread
            import concurrent.futures
            
            async def run_async():
                return await func(*args, **kwargs)
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, run_async())
                return future.result()
        else:
            return loop.run_until_complete(func(*args, **kwargs))
    
    return wrapper


class StartupService:
    """Service for handling platform startup initialization."""
    
    @staticmethod
    def initialize_platform_on_startup() -> Dict[str, Any]:
        """Initialize platform components on startup - runs synchronously."""
        try:
            print("🔧 Performing startup platform initialization...")
            
            # Call the initialization function
            result = initialize_platform()
            
            if result.get("success"):
                print("✅ Platform startup initialization completed successfully")
                
                # Log what was done
                superadmin = result["superadmin"]
                system_org = result["system_organization"]
                platform_team = result["platform_team"]
                
                if superadmin["created"]:
                    print(f"   📧 Created superadmin: {superadmin['email']}")
                else:
                    print(f"   ✅ Verified superadmin: {superadmin['email']}")
                
                if system_org["created"]:
                    print(f"   🏢 Created system organization: {system_org['name']}")
                else:
                    print(f"   ✅ Verified system organization: {system_org['name']}")
                
                if platform_team["created"]:
                    print(f"   👥 Created platform team: {platform_team['name']}")
                else:
                    print(f"   ✅ Verified platform team: {platform_team['name']}")
                
                other_admins = result.get("other_superadmins_processed", 0)
                if other_admins > 0:
                    print(f"   🔄 Processed {other_admins} additional superadmin(s)")
                
                return result
            else:
                error_msg = result.get("error", "Unknown error")
                print(f"❌ Platform startup initialization failed: {error_msg}")
                return result
                
        except Exception as e:
            error_msg = f"Exception during platform initialization: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
    
    @staticmethod
    @async_to_sync
    async def async_initialize_platform() -> Dict[str, Any]:
        """Async wrapper for platform initialization."""
        return StartupService.initialize_platform_on_startup()


# Convenience function for direct import
def ensure_platform_initialized() -> Dict[str, Any]:
    """Ensure platform is initialized - can be called from anywhere."""
    return StartupService.initialize_platform_on_startup()
