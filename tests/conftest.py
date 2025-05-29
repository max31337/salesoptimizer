import pytest
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator, Dict
from fastapi.testclient import TestClient
from unittest.mock import Mock
from unittest.mock import patch

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import domain entities for fixtures
from domain.entities.user import User, UserRole
from domain.entities.tenant import Tenant, SubscriptionTier
from infrastructure.services.password_service import PasswordService

# Import ALL database models to ensure they're registered with SQLAlchemy
from infrastructure.db.base import Base, get_db


def _import_models() -> list[type]:
    """Import all models to register them with SQLAlchemy metadata."""
    from infrastructure.db.models.user_model import UserModel
    from infrastructure.db.models.tenant_model import TenantModel
    
    return [UserModel, TenantModel]


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    db = None
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        if db is not None:
            db.close()


@pytest.fixture(scope="session")
def setup_test_db():
    """Setup test database schema."""
    # Import all models to ensure they're registered
    _import_models()
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(setup_test_db: None) -> Generator[Session, None, None]:
    """Create a fresh database for each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def sample_user(db_session: Session, password_service: PasswordService) -> User:
    """Create a sample user entity in the database for testing."""
    import uuid
    user = User(
        email="test@example.com",
        username="testuser",
        first_name="Test",
        last_name="User",
        phone="+1234567890",
        role=UserRole.SALES_REP,
        password_hash=password_service.hash_password("testpassword123"),
        tenant_id=uuid.uuid4()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_user_with_tenant(db_session: Session, password_service: PasswordService) -> tuple[User, Tenant]:
    """Create a sample user with tenant for testing."""
    # Create tenant first
    tenant = Tenant(
        name="Test Company",
        slug="test-company",
        subscription_tier=SubscriptionTier.BASIC
    )
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    
    # Create user with tenant
    user = User(
        email="test@example.com",
        username="testuser",
        first_name="Test",
        last_name="User",
        phone="+1234567890",
        role=UserRole.SALES_REP,
        password_hash=password_service.hash_password("testpassword123"),
        tenant_id=tenant.id
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    return user, tenant


@pytest.fixture(scope="function") 
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with database dependency override."""
    try:
        from api.main import app
        
        # Only override the database dependency - don't import application service here
        app.dependency_overrides[get_db] = lambda: db_session
        
        with TestClient(app) as test_client:
            yield test_client
        
        # Clean up
        app.dependency_overrides.clear()
    except ImportError:
        pytest.skip("FastAPI not available for this test")


@pytest.fixture(scope="function")
def client_with_mocks(mock_application_service_api: Mock) -> Generator[TestClient, None, None]:
    """Create a test client with all dependencies mocked for API tests."""
    try:
        from api.main import app
        from unittest.mock import Mock
        import uuid
        
        # Create a proper mock user for authentication with real values
        mock_user = Mock()
        mock_user.id = uuid.UUID("123e4567-e89b-12d3-a456-426614174000")
        mock_user.email = "test@example.com"
        mock_user.username = "testuser"
        mock_user.first_name = "Test"
        mock_user.last_name = "User"
        mock_user.role.value = "sales_rep"
        mock_user.full_name = "Test User"
        mock_user.tenant_id = uuid.UUID("456e7890-e89b-12d3-a456-426614174001")
        mock_user.status.value = "active"
        mock_user.is_email_verified = True
        
        # Override dependencies using FastAPI's dependency system
        app.dependency_overrides[get_db] = lambda: Mock()  # Mock DB session
        
        # Import the dependency functions from their proper modules
        from application.dependencies.service_dependencies import get_application_service
        app.dependency_overrides[get_application_service] = lambda: mock_application_service_api
        
        from api.dependencies.auth import get_current_user
        app.dependency_overrides[get_current_user] = lambda: mock_user

        with TestClient(app) as test_client:
            yield test_client

        # Clean up
        app.dependency_overrides.clear()
    except ImportError:
        pytest.skip("FastAPI not available for this test")


@pytest.fixture
def mock_application_service_api():
    """Create a mock application service with all use cases (for API tests)."""
    from unittest.mock import Mock
    import uuid
    
    mock_service = Mock()
    mock_service.auth_use_cases = Mock()
    mock_service.user_use_cases = Mock()
    mock_service.tenant_use_cases = Mock()
    
    # Create a proper mock user with real UUID values
    mock_user = Mock()
    mock_user.id = uuid.UUID("123e4567-e89b-12d3-a456-426614174000")
    mock_user.email = "test@example.com"
    mock_user.tenant_id = uuid.UUID("456e7890-e89b-12d3-a456-426614174001")
    mock_user.role.value = "sales_rep"
    mock_user.full_name = "John Doe"
    
    # Configure auth use cases to return successful responses
    mock_service.auth_use_cases.authenticate_user.return_value = (
        mock_user,
        "access_token_123",
        "refresh_token_123"
    )
    
    # Create another mock user for registration
    mock_registration_user = Mock()
    mock_registration_user.id = uuid.UUID("123e4567-e89b-12d3-a456-426614174000")
    mock_registration_user.tenant_id = uuid.UUID("456e7890-e89b-12d3-a456-426614174001")
    
    mock_service.auth_use_cases.complete_registration.return_value = (
        mock_registration_user,
        "access_token_123", 
        "refresh_token_123"
    )
    
    mock_service.auth_use_cases.refresh_tokens.return_value = (
        "new_access_token_123",
        "new_refresh_token_123"
    )
    
    # Configure user use cases
    def mock_update_user(user_id: str, update_data: Dict[str, str]) -> Mock:
        from unittest.mock import Mock
        if user_id == "123e4567-e89b-12d3-a456-426614174000":
            raise ValueError("User not found")
        return Mock(
            id=user_id,
            email=update_data.get("email", "updated@example.com"),
            username=update_data.get("username", "updateduser")
        )
    
    mock_service.user_use_cases.update_user.side_effect = mock_update_user
    
    return mock_service


# Application Layer Test Fixtures (for mocking)
@pytest.fixture
def mock_db_session():
    """Create a mock database session for application layer tests."""
    from unittest.mock import Mock
    return Mock(spec=Session)

@pytest.fixture
def mock_application_service():
    """Create a mock application service with all use cases."""
    from unittest.mock import Mock
    
    mock_service = Mock()
    mock_service.auth_use_cases = Mock()
    mock_service.user_use_cases = Mock()
    mock_service.tenant_use_cases = Mock()
    
    # Configure auth use cases to return successful responses
    mock_service.auth_use_cases.authenticate_user.return_value = (
        Mock(
            id="123e4567-e89b-12d3-a456-426614174000", 
            email="test@example.com",
            role=Mock(value="sales_rep"),
            full_name="John Doe"
        ),
        "access_token_123",
        "refresh_token_123"
    )
    
    mock_service.auth_use_cases.complete_registration.return_value = (
        Mock(id="123e4567-e89b-12d3-a456-426614174000"),
        "access_token_123", 
        "refresh_token_123"
    )
    
    mock_service.auth_use_cases.refresh_tokens.return_value = (
        "new_access_token_123",
        "new_refresh_token_123"
    )
    
    # Configure get_current_user_info to return user info
    mock_service.auth_use_cases.get_current_user_info.return_value = Mock(
        id="123e4567-e89b-12d3-a456-426614174000",
        email="test@example.com",
        username="testuser",
        role=Mock(value="sales_rep"),
        full_name="Test User"
    )
    
    # Configure user use cases
    def mock_update_user(user_id: str, update_data: Dict[str, str]) -> Mock:
        from unittest.mock import Mock
        if user_id == "123e4567-e89b-12d3-a456-426614174000":
            raise ValueError("User not found")
        return Mock(
            id=user_id,
            email=update_data.get("email", "updated@example.com"),
            username=update_data.get("username", "updateduser")
        )
    
    mock_service.user_use_cases.update_user.side_effect = mock_update_user
    
    return mock_service


@pytest.fixture
def mock_get_current_user():
    """Mock the get_current_user dependency."""
    from unittest.mock import Mock
    import uuid
    
    mock_user = Mock()
    mock_user.id = uuid.UUID("123e4567-e89b-12d3-a456-426614174000")
    mock_user.email = "test@example.com"
    mock_user.username = "testuser"
    mock_user.first_name = "Test"
    mock_user.last_name = "User"
    mock_user.role.value = "sales_rep"
    mock_user.full_name = "Test User"
    mock_user.tenant_id = uuid.UUID("456e7890-e89b-12d3-a456-426614174001")
    mock_user.status.value = "active"
    mock_user.is_email_verified = True
    
    return mock_user


@pytest.fixture
def client_with_mocked_auth(client: TestClient, mock_get_current_user: Mock) -> Generator[TestClient, None, None]:
    """Create a test client with mocked authentication."""
    from unittest.mock import patch
    from api.main import app
    
    with patch('api.dependencies.auth.get_current_user', return_value=mock_get_current_user):
        app.dependency_overrides.clear()  # Clear any existing overrides
        yield client
    
    app.dependency_overrides.clear()


@pytest.fixture
def client_with_mocked_service(client: TestClient, mock_application_service: Mock) -> Generator[TestClient, None, None]:
    """Create a test client with mocked application service."""
    
    # Mock the application service dependency
    with patch('api.dependencies.service_dependencies.get_application_service', return_value=mock_application_service):
        yield client

@pytest.fixture
def application_service(mock_db_session: Session):
    """Create application service with mocked database for testing."""
    from application.services.application_service import ApplicationService
    return ApplicationService(mock_db_session)


@pytest.fixture
def mock_user_repository():
    """Create a mock user repository."""
    from unittest.mock import Mock
    from infrastructure.repositories.user_repository_impl import UserRepositoryImpl
    return Mock(spec=UserRepositoryImpl)


@pytest.fixture
def mock_tenant_repository():
    """Create a mock tenant repository."""
    from unittest.mock import Mock
    from infrastructure.repositories.tenant_repository_impl import TenantRepositoryImpl
    return Mock(spec=TenantRepositoryImpl)


@pytest.fixture
def mock_auth_service():
    """Create a mock auth service."""
    from unittest.mock import Mock
    from domain.services.auth_service import AuthService
    return Mock(spec=AuthService)


@pytest.fixture
def authenticated_client(client: TestClient, sample_user: User):
    """Create a test client with authentication mocked."""
    from unittest.mock import patch
    
    with patch('api.dependencies.auth.get_current_user', return_value=sample_user):
        yield client


@pytest.fixture
def valid_auth_tokens():
    """Create valid test tokens."""
    return {
        "access_token": "test_access_token_123",
        "refresh_token": "test_refresh_token_123",
        "token_type": "bearer"
    }


# Common Test Data Fixtures
@pytest.fixture
def password_service() -> PasswordService:
    """Create password service for testing."""
    return PasswordService()


@pytest.fixture
def sample_user_data() -> Dict[str, str]:
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
def sample_tenant_data() -> Dict[str, str]:
    """Create sample tenant data for API requests."""
    return {
        "name": "Test Company",
        "slug": "test-company",
        "subscription_tier": "basic"
    }