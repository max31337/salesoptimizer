from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from infrastructure.db.base import get_db, test_connection
from contextlib import asynccontextmanager
from api.routes import users, auth, tenants

# Import all models via the registry
from infrastructure.db.models import register_models

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Testing database connection...")
    
    # Register all models
    models = register_models()
    print(f"Registered models: {[model.__name__ for model in models]}")
    
    if test_connection():
        print("✅ Database connection successful!")
        print("✅ Using Alembic for database migrations!")
    else:
        print("❌ Database connection failed!")
    yield

app = FastAPI(
    title="SalesOptimizer CRM", 
    version="1.0.0", 
    lifespan=lifespan,
    description="Multi-tenant sales optimization platform with predictive analytics"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",    # Frontend
        "http://localhost:8000",    # Swagger UI (same origin)
        "http://127.0.0.1:8000",    # Alternative localhost
        "http://127.0.0.1:3000",    # Alternative frontend
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Add OPTIONS
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(tenants.router, prefix="/api/v1")  
app.include_router(users.router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Hello from Sales Optimizer CRM", "version": "1.0.0"}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    return {"status": "healthy", "database": "connected"}
