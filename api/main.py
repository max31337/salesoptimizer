from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
from infrastructure.db.database import test_connection
from infrastructure.config.settings import settings
from contextlib import asynccontextmanager

# Import all models via the registry
from infrastructure.db.models import register_models

#Route registration imports
from api.routes import auth, invitations, token_revocation, profile

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
    
    yield
    
    # Shutdown
    print("👋 Shutting down SalesOptimizer API...")

app = FastAPI(
    title="SalesOptimizer CRM", 
    version="1.0.0", 
    lifespan=lifespan,
    description="Multi-tenant sales optimization platform with predictive analytics",
    debug=settings.is_development
)

# Environment-aware CORS middleware
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