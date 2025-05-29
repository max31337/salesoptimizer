import pytest
from fastapi.testclient import TestClient
from fastapi import status
from uuid import uuid4

from domain.organization.entities.user import User, UserRole, UserStatus
from domain.organization.services.auth_service import AuthenticationError


class TestAuthRoutes:
    """Test authentication API routes."""
    
    @pytest.fixture
    def sample_user(self) -> User:
        """Create a sample user for testing."""
        return User(
            id=uuid4(),
            email="test@example.com",
            username="testuser",
            first_name="John",
            last_name="Doe",
            role=UserRole.SALES_REP,
            status=UserStatus.ACTIVE,
            is_email_verified=True
        )
    
    def test_login_success(self, client_with_mocks: TestClient, sample_user: User):
        """Test successful login via API."""
        # Act
        response = client_with_mocks.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "testpassword123"
            }
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["access_token"] == "access_token_123"
        assert data["refresh_token"] == "refresh_token_123"
        assert data["token_type"] == "bearer"
        assert data["user_id"] == "123e4567-e89b-12d3-a456-426614174000"
        assert data["role"] == "sales_rep"
        assert data["email"] == "test@example.com"
        assert data["full_name"] == "John Doe"
    
    def test_login_invalid_credentials(self, client_with_mocks: TestClient):
        """Test login with invalid credentials via API."""
        # Configure the mock to raise an authentication error
        from application.dependencies.service_dependencies import get_application_service
        from api.main import app
        
        mock_service = app.dependency_overrides[get_application_service]()
        mock_service.auth_use_cases.authenticate_user.side_effect = AuthenticationError(
            "Invalid credentials"
        )
        
        # Act
        response = client_with_mocks.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "wrongpassword"
            }
        )
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == "Invalid credentials"
    
    def test_register_success(self, client_with_mocks: TestClient, sample_user: User):
        """Test successful registration via API."""
        register_data = {
            "invitation_token": "valid_token_123",
            "password": "strongpassword123",
            "first_name": "John",
            "last_name": "Doe"
        }
        
        # Act
        response = client_with_mocks.post(
            "/api/v1/auth/register",
            json=register_data
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["message"] == "Registration completed successfully"
        assert data["access_token"] == "access_token_123"
        assert data["refresh_token"] == "refresh_token_123"
        assert data["user_id"] == "123e4567-e89b-12d3-a456-426614174000"
    
    def test_register_invalid_token(self, client_with_mocks: TestClient):
        """Test registration with invalid invitation token via API."""
        # Configure the mock to raise an authentication error
        from application.dependencies.service_dependencies import get_application_service
        from api.main import app
        
        mock_service = app.dependency_overrides[get_application_service]()
        mock_service.auth_use_cases.complete_registration.side_effect = AuthenticationError(
            "Invalid or expired invitation token"
        )
        
        register_data = {
            "invitation_token": "invalid_token",
            "password": "strongpassword123",
            "first_name": "John",
            "last_name": "Doe"
        }
        
        # Act
        response = client_with_mocks.post(
            "/api/v1/auth/register",
            json=register_data
        )
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "Invalid or expired invitation token" in data["detail"]
    
    def test_get_current_user_info(self, client_with_mocks: TestClient):
        """Test getting current user info via API."""
        # Act
        response = client_with_mocks.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer valid_token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["id"] == "123e4567-e89b-12d3-a456-426614174000"
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"
        assert data["role"] == "sales_rep"
        assert data["full_name"] == "Test User"
    
    def test_refresh_token_success(self, client_with_mocks: TestClient):
        """Test successful token refresh via API."""
        # Act
        response = client_with_mocks.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "refresh_token_123"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["access_token"] == "new_access_token_123"
        assert data["refresh_token"] == "new_refresh_token_123"
        assert data["token_type"] == "bearer"
    
    def test_refresh_token_invalid(self, client_with_mocks: TestClient):
        """Test token refresh with invalid token via API."""
        # Configure the mock to raise an authentication error
        from application.dependencies.service_dependencies import get_application_service
        from api.main import app
        
        mock_service = app.dependency_overrides[get_application_service]()
        mock_service.auth_use_cases.refresh_tokens.side_effect = AuthenticationError(
            "Invalid refresh token"
        )
        
        # Act
        response = client_with_mocks.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"] == "Invalid refresh token"
    
    def test_logout(self, client_with_mocks: TestClient):
        """Test logout via API."""
        # Act
        response = client_with_mocks.post("/api/v1/auth/logout")
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Successfully logged out"