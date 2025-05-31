"""Test application setup for integration tests."""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Set test environment before any other imports
os.environ["TESTING"] = "true"

# Import routes
from api.routes import auth


def create_test_app() -> FastAPI:
    """Create test FastAPI application without database dependencies."""
    
    app = FastAPI(
        title="SalesOptimizer CRM Test",
        version="1.0.0-test",
        description="Test application for integration tests"
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
            "http://127.0.0.1:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(auth.router, prefix="/api/v1")

    @app.get("/")
    def root():  # noqa: F401
        return {"message": "Hello from Test SalesOptimizer CRM", "version": "1.0.0-test"}

    @app.get("/health")
    def health_check():
        return {"status": "healthy", "database": "mocked"}

    # Silence linter warning for unused endpoint functions
    _ = root, health_check

    return app


# Create the test app instance
test_app = create_test_app()