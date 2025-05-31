import pytest
from unittest.mock import AsyncMock, patch, MagicMock

# Mock everything BEFORE importing the app
with patch.multiple(
    'infrastructure.db.database',
    get_async_database_url=MagicMock(return_value="sqlite+aiosqlite:///:memory:"),
    test_connection=MagicMock(return_value=True),
    create_async_engine=MagicMock(),
    async_sessionmaker=MagicMock(),
):
    from httpx import AsyncClient
    from fastapi import status
    from uuid import uuid4
    
    from api.main import app
    from domain.organization.entities.user import User, UserRole, UserStatus
    from domain.organization.value_objects.email import Email
    from domain.organization.value_objects.user_id import UserId


@pytest.mark.integration
class TestAuthenticationFlowSimple:
    """Simplified integration tests."""
    
    @pytest.fixture
    def sample_user(self):
        """Create sample user."""
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
    
    @pytest.mark.asyncio
    async def test_successful_login_simple(self, sample_user: User):
        """Test successful login with simplified mocking."""
        
        with patch('application.dependencies.service_dependencies.get_application_service') as mock_get_app_service:
            mock_app_service = AsyncMock()
            mock_auth_use_cases = AsyncMock()
            
            mock_auth_use_cases.login.return_value = (
                sample_user,
                "test_access_token", 
                "test_refresh_token"
            )
            
            mock_app_service.auth_use_cases = mock_auth_use_cases
            mock_get_app_service.return_value = mock_app_service
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/auth/login",
                    data={
                        "username": "test@example.com",
                        "password": "TestPassword123!"
                    }
                )
                
                # Verify the response
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                
                # Check response structure
                assert data["access_token"] == "test_access_token"
                assert data["refresh_token"] == "test_refresh_token" 
                assert data["token_type"] == "bearer"
                assert data["user_id"] == (str(sample_user.id.value) if sample_user.id is not None and getattr(sample_user.id, "value", None) is not None else None)
                assert data["email"] == str(sample_user.email)
                assert data["role"] == sample_user.role.value
                assert data["full_name"] == sample_user.full_name
                
                # Verify the use case was called with correct parameters
                mock_auth_use_cases.login.assert_called_once()
                
                # Get the command that was passed to login
                call_args = mock_auth_use_cases.login.call_args[0][0]
                assert call_args.email_or_username == "test@example.com"
                assert call_args.password == "TestPassword123!"

    @pytest.mark.asyncio 
    async def test_invalid_credentials_integration(self):
        """Test invalid credentials handling."""
        
        from domain.organization.exceptions.auth_exceptions import InvalidCredentialsError
        
        with patch('application.dependencies.service_dependencies.get_application_service') as mock_get_app_service:
            mock_app_service = AsyncMock()
            mock_auth_use_cases = AsyncMock()
            
            # Setup mock to raise InvalidCredentialsError
            mock_auth_use_cases.login.side_effect = InvalidCredentialsError()
            
            mock_app_service.auth_use_cases = mock_auth_use_cases
            mock_get_app_service.return_value = mock_app_service
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/auth/login",
                    data={
                        "username": "test@example.com", 
                        "password": "WrongPassword123!"
                    }
                )
                
                assert response.status_code == status.HTTP_401_UNAUTHORIZED
                assert response.json()["detail"] == "Invalid credentials"

    @pytest.mark.asyncio
    async def test_user_not_found_integration(self):
        """Test user not found handling."""
        
        from domain.organization.exceptions.auth_exceptions import UserNotFoundError
        
        with patch('application.dependencies.service_dependencies.get_application_service') as mock_get_app_service:
            mock_app_service = AsyncMock()
            mock_auth_use_cases = AsyncMock()
            
            # Setup mock to raise UserNotFoundError  
            mock_auth_use_cases.login.side_effect = UserNotFoundError()
            
            mock_app_service.auth_use_cases = mock_auth_use_cases
            mock_get_app_service.return_value = mock_app_service
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/auth/login",
                    data={
                        "username": "nonexistent@example.com",
                        "password": "TestPassword123!"
                    }
                )
                
                assert response.status_code == status.HTTP_401_UNAUTHORIZED
                assert response.json()["detail"] == "Invalid credentials"

    @pytest.mark.asyncio
    async def test_inactive_user_integration(self):
        """Test inactive user handling."""
        
        from domain.organization.exceptions.auth_exceptions import InactiveUserError
        
        with patch('application.dependencies.service_dependencies.get_application_service') as mock_get_app_service:
            mock_app_service = AsyncMock()
            mock_auth_use_cases = AsyncMock()
            
            # Setup mock to raise InactiveUserError
            mock_auth_use_cases.login.side_effect = InactiveUserError()
            
            mock_app_service.auth_use_cases = mock_auth_use_cases
            mock_get_app_service.return_value = mock_app_service
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/auth/login",
                    data={
                        "username": "inactive@example.com",
                        "password": "TestPassword123!"
                    }
                )
                
                assert response.status_code == status.HTTP_401_UNAUTHORIZED
                assert response.json()["detail"] == "Account is not active"

    @pytest.mark.asyncio
    async def test_authentication_error_integration(self):
        """Test general authentication error handling."""
        
        from domain.organization.exceptions.auth_exceptions import AuthenticationError
        
        with patch('application.dependencies.service_dependencies.get_application_service') as mock_get_app_service:
            mock_app_service = AsyncMock()
            mock_auth_use_cases = AsyncMock()
            
            # Setup mock to raise AuthenticationError
            mock_auth_use_cases.login.side_effect = AuthenticationError("Custom error message")
            
            mock_app_service.auth_use_cases = mock_auth_use_cases
            mock_get_app_service.return_value = mock_app_service
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/auth/login",
                    data={
                        "username": "test@example.com",
                        "password": "TestPassword123!"
                    }
                )
                
                assert response.status_code == status.HTTP_401_UNAUTHORIZED
                assert response.json()["detail"] == "Custom error message"

    @pytest.mark.asyncio
    async def test_validation_error_integration(self):
        """Test validation error handling."""
        
        with patch('application.dependencies.service_dependencies.get_application_service') as mock_get_app_service:
            mock_app_service = AsyncMock()
            mock_auth_use_cases = AsyncMock()
            
            # Setup mock to raise ValueError
            mock_auth_use_cases.login.side_effect = ValueError("Validation failed")
            
            mock_app_service.auth_use_cases = mock_auth_use_cases
            mock_get_app_service.return_value = mock_app_service
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/auth/login",
                    data={
                        "username": "test@example.com",
                        "password": "TestPassword123!"
                    }
                )
                
                assert response.status_code == status.HTTP_400_BAD_REQUEST
                assert response.json()["detail"] == "Validation failed"

    @pytest.mark.asyncio
    async def test_request_validation_integration(self):
        """Test FastAPI request validation."""
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Test missing username
            response = await client.post(
                "/api/v1/auth/login",
                data={
                    "password": "TestPassword123!"
                }
            )
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            
            # Test missing password
            response = await client.post(
                "/api/v1/auth/login",
                data={
                    "username": "test@example.com"
                }
            )
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            
            # Test empty data
            response = await client.post(
                "/api/v1/auth/login",
                data={}
            )
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_cors_headers_integration(self):
        """Test CORS headers are properly set."""
        
        with patch('application.dependencies.service_dependencies.get_application_service') as mock_get_app_service:
            mock_app_service = AsyncMock()
            mock_auth_use_cases = AsyncMock()
            
            from domain.organization.exceptions.auth_exceptions import InvalidCredentialsError
            mock_auth_use_cases.login.side_effect = InvalidCredentialsError()
            mock_app_service.auth_use_cases = mock_auth_use_cases
            mock_get_app_service.return_value = mock_app_service
            
            async with AsyncClient(app=app, base_url="http://localhost:3000") as client:
                response = await client.post(
                    "/api/v1/auth/login",
                    data={
                        "username": "test@example.com",
                        "password": "password"
                    },
                    headers={
                        "Origin": "http://localhost:3000"
                    }
                )
                
                # Check CORS headers are present
                assert "access-control-allow-origin" in response.headers
                assert response.headers["access-control-allow-origin"] == "http://localhost:3000"