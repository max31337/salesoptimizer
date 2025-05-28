import pytest
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from typing import Generator

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.db.base import Base, get_db
# Import ALL models to register them with SQLAlchemy
from api.main import app
from domain.entities.user import User, UserRole, UserStatus
from domain.entities.tenant import Tenant, SubscriptionTier

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create a fresh database for each test."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after each test
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with database dependency override."""
    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            pass
    
    # Override the database dependency
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clear dependency overrides after test
    app.dependency_overrides.clear()

@pytest.fixture
def sample_user() -> User:
    """Create a sample user entity for testing."""
    return User(
        email="test@example.com",
        username="testuser",
        first_name="Test",
        last_name="User",
        phone="+1234567890",
        role=UserRole.SALES_REP,
        status=UserStatus.ACTIVE,
        is_email_verified=False
    )

@pytest.fixture
def sample_user_data() -> dict[str, str]:
    """Create sample user data for API requests."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
        "phone": "+1234567890",
        "role": "sales_rep"
    }

@pytest.fixture
def sample_tenant() -> Tenant:
    """Create a sample tenant entity for testing."""
    return Tenant(
        name="Test Company",
        slug="test-company",
        subscription_tier=SubscriptionTier.BASIC
    )

@pytest.fixture
def sample_tenant_data() -> dict[str, str]:
    """Create sample tenant data for API requests."""
    return {
        "name": "Test Company",
        "slug": "test-company",
        "subscription_tier": "basic"
    }