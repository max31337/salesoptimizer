import pytest
from httpx import AsyncClient
from fastapi import status
from uuid import uuid4
from unittest.mock import AsyncMock, patch, MagicMock

from api.main import app
from domain.organization.entities.user import User, UserRole, UserStatus
from domain.organization.value_objects.email import Email
from domain.organization.value_objects.user_id import UserId


@pytest.mark.integration
class TestAuthenticationFlowWithDbMock:
    """Integration tests with complete database mocking."""
    
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
    
    @pytest.fixture
    def mock_async_session(self):
        """Mock async session."""
        session = AsyncMock()
        session.execute = AsyncMock()
        session.commit = AsyncMock()
        session.close = AsyncMock()
        return session
    
    @pytest.mark.asyncio
    async def test_successful_login_with_db_mock(self, sample_user: User, mock_async_session: AsyncMock):
        """Test successful login with complete database mocking."""
        
        # Mock the entire database infrastructure
        with patch.multiple(
            'infrastructure.db.database',
            get_async_session=AsyncMock(return_value=mock_async_session),
            get_async_db=AsyncMock(return_value=mock_async_session),
            test_connection=MagicMock(return_value=True)
        ), patch('application.dependencies.service_dependencies.get_application_service') as mock_get_app_service:
            
            # Create mock application service
            mock_app_service = AsyncMock()
            mock_auth_use_cases = AsyncMock()
            
            # Setup the login method to return our test data
            mock_auth_use_cases.login.return_value = (
                sample_user,
                "test_access_token", 
                "test_refresh_token"
            )
            
            # Wire up the mocks
            mock_app_service.auth_use_cases = mock_auth_use_cases
            mock_get_app_service.return_value = mock_app_service
            
            # Make the actual HTTP request
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
                assert sample_user.id is not None, "sample_user.id is None"
                assert data["user_id"] == str(sample_user.id.value)
                assert data["email"] == str(sample_user.email)
                assert data["role"] == sample_user.role.value
                assert data["full_name"] == sample_user.full_name