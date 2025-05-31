import pytest
from unittest.mock import AsyncMock

from application.use_cases.auth_use_cases import AuthUseCases
from application.commands.auth_command import LoginCommand
from domain.organization.entities.user import User, UserRole, UserStatus
from domain.organization.value_objects.email import Email
from domain.organization.value_objects.user_id import UserId


class TestAuthUseCases:
    """Test AuthUseCases."""
    
    @pytest.fixture
    def mock_auth_service(self):
        """Mock auth service."""
        return AsyncMock()
    
    @pytest.fixture
    def auth_use_cases(self, mock_auth_service: AsyncMock):
        """Create auth use cases with mocked auth service."""
        return AuthUseCases(mock_auth_service)
    
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
            status=UserStatus.ACTIVE
        )
    
    @pytest.fixture
    def login_command(self):
        """Create login command for testing."""
        return LoginCommand(
            email_or_username="test@example.com",
            password="password123"
        )
    
    @pytest.mark.asyncio
    async def test_login_success(
        self, 
        auth_use_cases: AuthUseCases, 
        mock_auth_service: AsyncMock, 
        login_command: LoginCommand,
        sample_user: User
    ):
        """Test successful login use case."""
        # Setup mocks
        mock_auth_service.authenticate_user.return_value = sample_user
        mock_auth_service.create_tokens.return_value = ("access_token", "refresh_token")
        
        # Execute
        user, access_token, refresh_token = await auth_use_cases.login(login_command)
        
        # Verify
        assert user == sample_user
        assert access_token == "access_token"
        assert refresh_token == "refresh_token"
        
        mock_auth_service.authenticate_user.assert_called_once_with(
            login_command.email_or_username,
            login_command.password
        )
        mock_auth_service.create_tokens.assert_called_once_with(sample_user)
    
    @pytest.mark.asyncio
    async def test_login_propagates_auth_service_exceptions(
        self, 
        auth_use_cases: AuthUseCases, 
        mock_auth_service: AsyncMock, 
        login_command: LoginCommand,
    ):
        """Test login propagates auth service exceptions."""
        from domain.organization.exceptions.auth_exceptions import InvalidCredentialsError
        
        # Setup mock to raise exception
        mock_auth_service.authenticate_user.side_effect = InvalidCredentialsError()
        
        # Execute & Verify
        with pytest.raises(InvalidCredentialsError):
            await auth_use_cases.login(login_command)
        
        mock_auth_service.authenticate_user.assert_called_once_with(
            login_command.email_or_username,
            login_command.password
        )
        # Tokens should not be created if authentication fails
        mock_auth_service.create_tokens.assert_not_called()