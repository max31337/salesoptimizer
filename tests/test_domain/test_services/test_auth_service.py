import pytest
from unittest.mock import AsyncMock, Mock
from domain.organization.entities.user import User, UserRole, UserStatus
from domain.organization.value_objects.email import Email
from domain.organization.value_objects.user_id import UserId
from domain.organization.services.auth_service import AuthService
from domain.organization.exceptions.auth_exceptions import (
    AuthenticationError,
    InvalidCredentialsError,
    UserNotFoundError,
    InactiveUserError
)


class TestAuthService:
    """Test AuthService domain service."""
    
    @pytest.fixture
    def mock_user_repository(self):
        """Mock user repository."""
        return AsyncMock()
    
    @pytest.fixture
    def mock_password_service(self):
        """Mock password service."""
        return Mock()
    
    @pytest.fixture
    def mock_jwt_service(self):
        """Mock JWT service."""
        return Mock()
    
    @pytest.fixture
    def auth_service(
        self,
        mock_user_repository: AsyncMock,
        mock_password_service: Mock,
        mock_jwt_service: Mock
    ) -> AuthService:
        """Create auth service with mocked dependencies."""
        return AuthService(
            mock_user_repository,
            mock_password_service,
            mock_jwt_service
        )
    
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
    
    @pytest.mark.asyncio
    async def test_authenticate_user_success_with_email(
        self, 
        auth_service: AuthService, 
        mock_user_repository: AsyncMock, 
        mock_password_service: Mock,
        sample_user: User
    ):
        """Test successful authentication with email."""
        # Setup mocks
        mock_user_repository.get_by_email.return_value = sample_user
        mock_user_repository.update.return_value = sample_user
        mock_password_service.verify_password.return_value = True
        
        # Execute
        result = await auth_service.authenticate_user("test@example.com", "password123")
        
        # Verify
        assert result == sample_user
        mock_user_repository.get_by_email.assert_called_once()
        mock_password_service.verify_password.assert_called_once_with("password123", "hashed_password")
        mock_user_repository.update.assert_called_once_with(sample_user)
    
    @pytest.mark.asyncio
    async def test_authenticate_user_success_with_username(
        self, 
        auth_service: AuthService, 
        mock_user_repository: AsyncMock, 
        mock_password_service: Mock,
        sample_user: User
    ):
        """Test successful authentication with username."""
        # Setup mocks
        mock_user_repository.get_by_email.return_value = None
        mock_user_repository.get_by_username.return_value = sample_user
        mock_user_repository.update.return_value = sample_user
        mock_password_service.verify_password.return_value = True
        
        # Execute
        result = await auth_service.authenticate_user("testuser", "password123")
        
        # Verify
        assert result == sample_user
        mock_user_repository.get_by_username.assert_called_once_with("testuser")
        mock_password_service.verify_password.assert_called_once_with("password123", "hashed_password")
    
    @pytest.mark.asyncio
    async def test_authenticate_user_empty_credentials_raises_error(self, auth_service: AuthService):
        """Test authentication with empty credentials raises error."""
        with pytest.raises(AuthenticationError, match="Email/username and password are required"):
            await auth_service.authenticate_user("", "password")
        
        with pytest.raises(AuthenticationError, match="Email/username and password are required"):
            await auth_service.authenticate_user("email@test.com", "")
    
    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_password_format_raises_error(self, auth_service: AuthService):
        """Test authentication with invalid password format raises error."""
        with pytest.raises(InvalidCredentialsError):
            await auth_service.authenticate_user("test@example.com", "short")  # Too short
    
    @pytest.mark.asyncio
    async def test_authenticate_user_not_found_raises_error(
        self, 
        auth_service: AuthService, 
        mock_user_repository: AsyncMock
    ):
        """Test authentication with non-existent user raises error."""
        # Setup mocks
        mock_user_repository.get_by_email.return_value = None
        mock_user_repository.get_by_username.return_value = None
        
        # Execute & Verify
        with pytest.raises(UserNotFoundError):
            await auth_service.authenticate_user("nonexistent@example.com", "password123")
    
    @pytest.mark.asyncio
    async def test_authenticate_user_inactive_raises_error(
        self, 
        auth_service: AuthService, 
        mock_user_repository: AsyncMock,
        sample_user: User
    ):
        """Test authentication with inactive user raises error."""
        # Make user inactive
        sample_user.status = UserStatus.INACTIVE
        
        # Setup mocks
        mock_user_repository.get_by_email.return_value = sample_user
        
        # Execute & Verify
        with pytest.raises(InactiveUserError):
            await auth_service.authenticate_user("test@example.com", "password123")
    
    @pytest.mark.asyncio
    async def test_authenticate_user_no_password_raises_error(
        self, 
        auth_service: AuthService, 
        mock_user_repository: AsyncMock,
        sample_user: User
    ):
        """Test authentication with user having no password raises error."""
        # Remove password hash
        sample_user.password_hash = None
        
        # Setup mocks
        mock_user_repository.get_by_email.return_value = sample_user
        
        # Execute & Verify
        with pytest.raises(InvalidCredentialsError):
            await auth_service.authenticate_user("test@example.com", "password123")
    
    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password_raises_error(
        self, 
        auth_service: AuthService, 
        mock_user_repository: AsyncMock, 
        mock_password_service: Mock,
        sample_user: User
    ):
        """Test authentication with wrong password raises error."""
        # Setup mocks
        mock_user_repository.get_by_email.return_value = sample_user
        mock_password_service.verify_password.return_value = False
        
        # Execute & Verify
        with pytest.raises(InvalidCredentialsError):
            await auth_service.authenticate_user("test@example.com", "wrongpassword")
    
    def test_create_tokens_success(self, auth_service: AuthService, mock_jwt_service: Mock, sample_user: User):
        """Test successful token creation."""
        # Setup mocks
        mock_jwt_service.create_access_token.return_value = "access_token"
        mock_jwt_service.create_refresh_token.return_value = "refresh_token"
        
        # Ensure sample_user.id is not None
        assert sample_user.id is not None, "sample_user.id should not be None for this test"
        
        # Execute
        access_token, refresh_token = auth_service.create_tokens(sample_user)
        
        # Verify
        assert access_token == "access_token"
        assert refresh_token == "refresh_token"
        mock_jwt_service.create_access_token.assert_called_once_with(
            user_id=sample_user.id.value,
            tenant_id=sample_user.tenant_id,
            role=sample_user.role.value,
            email=str(sample_user.email)
        )
        mock_jwt_service.create_refresh_token.assert_called_once_with(sample_user.id.value)

    def test_create_tokens_no_user_id_raises_error(self, auth_service: AuthService, sample_user: User):
        """Test token creation with no user ID raises error."""
        # Remove user ID
        sample_user.id = None
        
        # Execute & Verify
        with pytest.raises(AuthenticationError, match="User ID is required to create tokens"):
            auth_service.create_tokens(sample_user)