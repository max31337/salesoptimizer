import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import status
from uuid import uuid4

from api.main import app
from domain.organization.entities.user import User, UserRole, UserStatus
from domain.organization.value_objects.email import Email
from domain.organization.value_objects.user_id import UserId
from domain.organization.exceptions.auth_exceptions import (
    InvalidCredentialsError,
    UserNotFoundError,
    InactiveUserError,
    AuthenticationError
)


class TestAuthRoutes:
    """Test authentication routes."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def sample_user(self):
        """Create sample user for testing."""
        return User(
            id=UserId.generate(),
            email=Email("test@example.com"),
            username="testuser",
            first_name="Test",
            last_name="User",
            password_hash="hashed_password",
            role=UserRole.SALES_REP,
            status=UserStatus.ACTIVE,
            tenant_id=uuid4()
        )
    
    @patch('application.dependencies.service_dependencies.get_application_service')
    def test_login_success(self, mock_get_app_service: 'MagicMock', client: TestClient, sample_user: User):
        """Test successful login."""
        # Setup mocks
        mock_app_service = AsyncMock()
        mock_auth_use_cases = AsyncMock()
        mock_app_service.auth_use_cases = mock_auth_use_cases
        mock_auth_use_cases.login.return_value = (sample_user, "access_token", "refresh_token")
        mock_get_app_service.return_value = mock_app_service
        
        # Execute
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "password123"
            }
        )
        
        # Verify
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["access_token"] == "access_token"
        assert data["refresh_token"] == "refresh_token"
        assert data["token_type"] == "bearer"
        assert data["user_id"] == (str(sample_user.id.value) if sample_user.id is not None else None)
        assert data["tenant_id"] == str(sample_user.tenant_id)
        assert data["role"] == sample_user.role.value
        assert data["email"] == str(sample_user.email)
        assert data["full_name"] == sample_user.full_name
    
    @patch('application.dependencies.service_dependencies.get_application_service')
    def test_login_invalid_credentials(self, mock_get_app_service: 'MagicMock', client: TestClient):
        """Test login with invalid credentials."""
        # Setup mocks
        mock_app_service = AsyncMock()
        mock_auth_use_cases = AsyncMock()
        mock_app_service.auth_use_cases = mock_auth_use_cases
        mock_auth_use_cases.login.side_effect = InvalidCredentialsError()
        mock_get_app_service.return_value = mock_app_service
        
        # Execute
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "wrongpassword"
            }
        )
        
        # Verify
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Invalid credentials"
    
    @patch('application.dependencies.service_dependencies.get_application_service')
    def test_login_user_not_found(self, mock_get_app_service: 'MagicMock', client: TestClient):
        """Test login with non-existent user."""
        # Setup mocks
        mock_app_service = AsyncMock()
        mock_auth_use_cases = AsyncMock()
        mock_app_service.auth_use_cases = mock_auth_use_cases
        mock_auth_use_cases.login.side_effect = UserNotFoundError()
        mock_get_app_service.return_value = mock_app_service
        
        # Execute
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "password123"
            }
        )
        
        # Verify
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Invalid credentials"
    
    @patch('application.dependencies.service_dependencies.get_application_service')
    def test_login_inactive_user(self, mock_get_app_service: 'MagicMock', client: TestClient):
        """Test login with inactive user."""
        # Setup mocks
        mock_app_service = AsyncMock()
        mock_auth_use_cases = AsyncMock()
        mock_app_service.auth_use_cases = mock_auth_use_cases
        mock_auth_use_cases.login.side_effect = InactiveUserError()
        mock_get_app_service.return_value = mock_app_service
        
        # Execute
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "inactive@example.com",
                "password": "password123"
            }
        )
        
        # Verify
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Account is not active"
    
    @patch('application.dependencies.service_dependencies.get_application_service')
    def test_login_authentication_error(self, mock_get_app_service: 'MagicMock', client: TestClient):
        """Test login with general authentication error."""
        # Setup mocks
        mock_app_service = AsyncMock()
        mock_auth_use_cases = AsyncMock()
        mock_app_service.auth_use_cases = mock_auth_use_cases
        mock_auth_use_cases.login.side_effect = AuthenticationError("Custom auth error")
        mock_get_app_service.return_value = mock_app_service
        
        # Execute
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "password123"
            }
        )
        
        # Verify
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Custom auth error"
    
    @patch('application.dependencies.service_dependencies.get_application_service')
    def test_login_value_error(self, mock_get_app_service: 'MagicMock', client: TestClient):
        """Test login with value error."""
        # Setup mocks
        mock_app_service = AsyncMock()
        mock_auth_use_cases = AsyncMock()
        mock_app_service.auth_use_cases = mock_auth_use_cases
        mock_auth_use_cases.login.side_effect = ValueError("Validation error")
        mock_get_app_service.return_value = mock_app_service
        
        # Execute
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "password123"
            }
        )
        
        # Verify
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Validation error"
    
    def test_login_missing_username(self, client: TestClient):
        """Test login with missing username."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "password": "password123"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_login_missing_password(self, client: TestClient):
        """Test login with missing password."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @patch('application.dependencies.service_dependencies.get_application_service')
    def test_login_user_without_id_raises_error(self, mock_get_app_service: 'MagicMock', client: TestClient):
        """Test login with user that has no ID raises error."""
        user_without_id = User(
            id=None,  # No ID
            email=Email("test@example.com"),
            username="testuser",
            first_name="Test",
            last_name="User",
            password_hash="hashed_password",
            role=UserRole.SALES_REP,
            status=UserStatus.ACTIVE
        )
        
        # Setup mocks
        mock_app_service = AsyncMock()
        mock_auth_use_cases = AsyncMock()
        mock_app_service.auth_use_cases = mock_auth_use_cases
        mock_auth_use_cases.login.return_value = (user_without_id, "access_token", "refresh_token")
        mock_get_app_service.return_value = mock_app_service
        
        # Execute
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "password123"
            }
        )
        
        # Verify
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json()["detail"] == "User ID is missing"