from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
from infrastructure.db.database import test_connection
from infrastructure.config.settings import settings
from contextlib import asynccontextmanager

# Import all models via the registry
from infrastructure.db.models import register_models

#Route registration imports hehe
from api.routes import auth, invitations

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting SalesOptimizer...")
    print(f"🌍 Environment: {settings.ENVIRONMENT}")
    print(f"🔗 Frontend URL: {settings.FRONTEND_URL}")
    print(f"🔗 Backend URL: {settings.BACKEND_URL}")
    
    # Register all models
    register_models()
    
    # Test database connection
    if not test_connection():
        print("❌ Failed to connect to database!")
        raise Exception("Database connection failed")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down SalesOptimizer...")

app = FastAPI(
    title="SalesOptimizer CRM", 
    version="1.0.0", 
    lifespan=lifespan,
    description="Multi-tenant sales optimization platform with predictive analytics",
    debug=settings.is_development
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0"
    }

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(invitations.router, prefix="/api/v1")
