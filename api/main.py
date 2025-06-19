from fastapi import FastAPI 
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from infrastructure.db.database import test_connection
from infrastructure.config.settings import settings
from infrastructure.services.startup_service import ensure_platform_initialized
from contextlib import asynccontextmanager

# Import all models via the registry
from infrastructure.db.models import register_models

#Route registration imports
from api.routes import auth, invitations, sla_monitoring, token_revocation, profile, websocket_routes

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"🚀 Starting SalesOptimizer API in {settings.ENVIRONMENT} mode...")
    print(f"🔒 Cookie security: {settings.cookie_secure}")
    print(f"🌐 Frontend URL: {settings.FRONTEND_URL}")
    print(f"🎯 CORS Origins: {settings.CORS_ORIGINS}")
    
    # Register models to ensure proper table creation
    register_models()
    
    # Test database connection
    connection_result = test_connection()
    if connection_result:
        print("✅ Database connection successful")
    else:
        print("❌ Database connection failed")
    
    # Initialize platform (superadmin, system org, platform team)
    try:
        print("\n🔧 Initializing platform components...")
        platform_result = ensure_platform_initialized()
        
        if platform_result.get("success"):
            print("✅ Platform initialization completed")
        else:
            print(f"⚠️  Platform initialization had issues: {platform_result.get('error', 'Unknown error')}")
            # Don't fail startup, just log the issue
    except Exception as e:
        print(f"⚠️  Platform initialization error: {str(e)}")
        # Don't fail startup, just log the error
      # Start SLA WebSocket service for real-time monitoring
    try:
        from infrastructure.services.sla_websocket_service import sla_websocket_service
        await sla_websocket_service.start()
        print("✅ SLA WebSocket service started")
    except Exception as e:
        print(f"⚠️  SLA WebSocket service error: {str(e)}")
    
    yield
    
    # Shutdown
    print("👋 Shutting down SalesOptimizer API...")
    
    # Stop SLA WebSocket service
    try:
        from infrastructure.services.sla_websocket_service import sla_websocket_service
        await sla_websocket_service.stop()
        print("✅ SLA WebSocket service stopped")
    except Exception as e:
        print(f"⚠️  SLA WebSocket service shutdown error: {str(e)}")

app = FastAPI(
    title="SalesOptimizer CRM", 
    version="1.0.0", 
    lifespan=lifespan,
    description="Multi-tenant sales optimization platform with predictive analytics",
    debug=settings.is_development
)

# Environment-aware CORS middleware - MUST come before static files
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # Use settings CORS origins
    allow_credentials=True,  # Essential for cookies
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "Cookie",
        "Set-Cookie"
    ],
    expose_headers=["Set-Cookie"]  # Allow frontend to see Set-Cookie headers
)

# Mount static files for uploads AFTER CORS middleware
uploads_path = Path(__file__).parent.parent / "uploads"
uploads_path.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")

@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Welcome to the SalesOptimizer API"}

# Health check endpoint
@app.get("/health")
async def health_check() -> dict[str, str | bool]:
    return {
        "status": "healthy", 
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0",
        "cookie_secure": settings.cookie_secure
    }


# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(invitations.router, prefix="/api/v1")
app.include_router(token_revocation.router, prefix="/api/v1")
app.include_router(profile.router, prefix="/api/v1")
app.include_router(sla_monitoring.router, prefix="/api/v1")
app.include_router(websocket_routes.router, prefix="/api/v1")