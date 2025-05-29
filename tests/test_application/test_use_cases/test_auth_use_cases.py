import pytest
from unittest.mock import Mock
from uuid import uuid4

from application.use_cases.auth_use_cases import AuthUseCases
from application.dtos.auth_dto import RegisterRequest
from domain.entities.user import User, UserRole, UserStatus
from domain.services.auth_service import AuthService, AuthenticationError


class TestAuthUseCases:
    """Test authentication use cases."""
    
    @pytest.fixture
    def mock_auth_service(self) -> Mock:
        """Create a mock auth service."""
        return Mock(spec=AuthService)
    
    @pytest.fixture
    def auth_use_cases(self, mock_auth_service: Mock) -> AuthUseCases:
        """Create auth use cases with mocked dependencies."""
        return AuthUseCases(mock_auth_service)
    
    @pytest.fixture
    def sample_user(self) -> User:
        """Create a sample user for testing."""
        return User(
            id=uuid4(),
            email="test@example.com",
            username="testuser",
            first_name="John",
            last_name="Doe",
            password_hash="hashed_password",
            role=UserRole.SALES_REP,
            status=UserStatus.ACTIVE,
            is_email_verified=True
        )
    
    def test_authenticate_user_success(
        self,
        auth_use_cases: AuthUseCases,
        mock_auth_service: Mock,
        sample_user: User
    ):
        """Test successful user authentication."""
        # Arrange
        email = "test@example.com"
        password = "testpassword123"
        access_token = "access_token_123"
        refresh_token = "refresh_token_123"
        
        mock_auth_service.authenticate_user.return_value = sample_user
        mock_auth_service.create_user_tokens.return_value = (access_token, refresh_token)
        
        # Act
        user, returned_access_token, returned_refresh_token = auth_use_cases.authenticate_user(
            email, password
        )
        
        # Assert
        mock_auth_service.authenticate_user.assert_called_once_with(email, password)
        mock_auth_service.create_user_tokens.assert_called_once_with(sample_user)
        
        assert user == sample_user
        assert returned_access_token == access_token
        assert returned_refresh_token == refresh_token
    
    def test_authenticate_user_failure(
        self,
        auth_use_cases: AuthUseCases,
        mock_auth_service: Mock
    ):
        """Test failed user authentication."""
        # Arrange
        email = "test@example.com"
        password = "wrongpassword"
        
        mock_auth_service.authenticate_user.side_effect = AuthenticationError("Invalid credentials")
        
        # Act & Assert
        with pytest.raises(AuthenticationError) as exc_info:
            auth_use_cases.authenticate_user(email, password)
        
        assert str(exc_info.value) == "Invalid credentials"
        mock_auth_service.authenticate_user.assert_called_once_with(email, password)
        mock_auth_service.create_user_tokens.assert_not_called()
    
    def test_complete_registration_success(
        self,
        auth_use_cases: AuthUseCases,
        mock_auth_service: Mock,
        sample_user: User
    ):
        """Test successful user registration completion."""
        # Arrange
        register_data = RegisterRequest(
            invitation_token="valid_token_123",
            password="strongpassword123",
            first_name="John",
            last_name="Doe"
        )
        access_token = "access_token_123"
        refresh_token = "refresh_token_123"
        
        mock_auth_service.complete_registration.return_value = sample_user
        mock_auth_service.create_user_tokens.return_value = (access_token, refresh_token)
        
        # Act
        user, returned_access_token, returned_refresh_token = auth_use_cases.complete_registration(
            register_data
        )
        
        # Assert
        mock_auth_service.complete_registration.assert_called_once_with(
            invitation_token=register_data.invitation_token,
            password=register_data.password,
            first_name=register_data.first_name,
            last_name=register_data.last_name
        )
        mock_auth_service.create_user_tokens.assert_called_once_with(sample_user)
        
        assert user == sample_user
        assert returned_access_token == access_token
        assert returned_refresh_token == refresh_token
    
    def test_complete_registration_invalid_token(
        self,
        auth_use_cases: AuthUseCases,
        mock_auth_service: Mock
    ):
        """Test registration completion with invalid invitation token."""
        # Arrange
        register_data = RegisterRequest(
            invitation_token="invalid_token",
            password="strongpassword123",
            first_name="John",
            last_name="Doe"
        )
        
        mock_auth_service.complete_registration.side_effect = AuthenticationError(
            "Invalid invitation token"
        )
        
        # Act & Assert
        with pytest.raises(AuthenticationError) as exc_info:
            auth_use_cases.complete_registration(register_data)
        
        assert str(exc_info.value) == "Invalid invitation token"
        mock_auth_service.complete_registration.assert_called_once()
        mock_auth_service.create_user_tokens.assert_not_called()
    
    def test_refresh_tokens_success(
        self,
        auth_use_cases: AuthUseCases,
        mock_auth_service: Mock
    ):
        """Test successful token refresh."""
        # Arrange
        refresh_token = "refresh_token_123"
        new_access_token = "new_access_token_123"
        new_refresh_token = "new_refresh_token_123"
        
        mock_auth_service.refresh_user_tokens.return_value = (new_access_token, new_refresh_token)
        
        # Act
        returned_access_token, returned_refresh_token = auth_use_cases.refresh_tokens(refresh_token)
        
        # Assert
        mock_auth_service.refresh_user_tokens.assert_called_once_with(refresh_token)
        assert returned_access_token == new_access_token
        assert returned_refresh_token == new_refresh_token
    
    def test_refresh_tokens_invalid_token(
        self,
        auth_use_cases: AuthUseCases,
        mock_auth_service: Mock
    ):
        """Test token refresh with invalid refresh token."""
        # Arrange
        refresh_token = "invalid_refresh_token"
        
        mock_auth_service.refresh_user_tokens.side_effect = AuthenticationError(
            "Invalid refresh token"
        )
        
        # Act & Assert
        with pytest.raises(AuthenticationError) as exc_info:
            auth_use_cases.refresh_tokens(refresh_token)
        
        assert str(exc_info.value) == "Invalid refresh token"
        mock_auth_service.refresh_user_tokens.assert_called_once_with(refresh_token)