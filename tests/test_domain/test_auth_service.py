import pytest
from unittest.mock import Mock
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from domain.services.auth_service import AuthService, AuthenticationError
from domain.entities.user import User, UserRole, UserStatus
from domain.repositories.user_repository import UserRepository
from infrastructure.services.password_service import PasswordService
from infrastructure.services.jwt_service import JWTService


class TestAuthService:
    
    @pytest.fixture
    def mock_user_repo(self) -> Mock:
        """Create a mock user repository."""
        return Mock(spec=UserRepository)
    
    @pytest.fixture
    def mock_password_service(self) -> Mock:
        """Create a mock password service."""
        return Mock(spec=PasswordService)
    
    @pytest.fixture
    def mock_jwt_service(self) -> Mock:
        """Create a mock JWT service."""
        return Mock(spec=JWTService)
    
    @pytest.fixture
    def auth_service(
        self, 
        mock_user_repo: Mock, 
        mock_password_service: Mock, 
        mock_jwt_service: Mock
    ) -> AuthService:
        """Create an auth service with mocked dependencies."""
        return AuthService(mock_user_repo, mock_password_service, mock_jwt_service)
    
    @pytest.fixture
    def active_user(self) -> User:
        """Create an active user for testing."""
        return User(
            id=uuid4(),
            tenant_id=uuid4(),
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            password_hash="hashed_password_123",
            role=UserRole.SALES_REP,
            status=UserStatus.ACTIVE,
            is_email_verified=True
        )
    
    @pytest.fixture
    def pending_user(self) -> User:
        """Create a pending user for testing."""
        return User(
            id=uuid4(),
            tenant_id=uuid4(),
            email="pending@example.com",
            username="pendinguser",
            first_name="Pending",
            last_name="User",
            password_hash=None,
            role=UserRole.SALES_REP,
            status=UserStatus.PENDING,
            invitation_token="invitation_token_123",
            invitation_expires_at=datetime.now(timezone.utc) + timedelta(hours=24)
        )

    def test_authenticate_user_success(
        self, 
        auth_service: AuthService, 
        mock_user_repo: Mock, 
        mock_password_service: Mock,
        active_user: User
    ) -> None:
        """Test successful user authentication."""
        email = "test@example.com"
        password = "correct_password"
        
        # Setup mocks
        mock_user_repo.get_by_email.return_value = active_user
        mock_password_service.verify_password.return_value = True
        mock_user_repo.update.return_value = active_user
        
        # Execute
        result = auth_service.authenticate_user(email, password)
        
        # Assert
        assert result is not None
        assert result.id == active_user.id
        assert result.email == active_user.email
        
        # Verify method calls
        mock_user_repo.get_by_email.assert_called_once_with(email)
        mock_password_service.verify_password.assert_called_once_with(password, active_user.password_hash)
        mock_user_repo.update.assert_called_once_with(active_user)

    def test_authenticate_user_not_found(
        self, 
        auth_service: AuthService, 
        mock_user_repo: Mock
    ) -> None:
        """Test authentication when user is not found."""
        email = "nonexistent@example.com"
        password = "password"
        
        # Setup mocks
        mock_user_repo.get_by_email.return_value = None
        
        # Execute
        result = auth_service.authenticate_user(email, password)
        
        # Assert
        assert result is None
        mock_user_repo.get_by_email.assert_called_once_with(email)

    def test_authenticate_user_no_password_hash(
        self, 
        auth_service: AuthService, 
        mock_user_repo: Mock,
        pending_user: User
    ) -> None:
        """Test authentication when user has no password hash (pending registration)."""
        email = "pending@example.com"
        password = "password"
        
        # Setup mocks
        mock_user_repo.get_by_email.return_value = pending_user
        
        # Execute & Assert
        with pytest.raises(AuthenticationError, match="User has not completed registration"):
            auth_service.authenticate_user(email, password)
        
        mock_user_repo.get_by_email.assert_called_once_with(email)

    def test_authenticate_user_wrong_password(
        self, 
        auth_service: AuthService, 
        mock_user_repo: Mock, 
        mock_password_service: Mock,
        active_user: User
    ) -> None:
        """Test authentication with wrong password."""
        email = "test@example.com"
        password = "wrong_password"
        
        # Setup mocks
        mock_user_repo.get_by_email.return_value = active_user
        mock_password_service.verify_password.return_value = False
        
        # Execute
        result = auth_service.authenticate_user(email, password)
        
        # Assert
        assert result is None
        mock_user_repo.get_by_email.assert_called_once_with(email)
        mock_password_service.verify_password.assert_called_once_with(password, active_user.password_hash)

    def test_authenticate_user_inactive_status(
        self, 
        auth_service: AuthService, 
        mock_user_repo: Mock, 
        mock_password_service: Mock,
        active_user: User
    ) -> None:
        """Test authentication when user is inactive."""
        email = "test@example.com"
        password = "correct_password"
        
        # Make user inactive
        active_user.status = UserStatus.INACTIVE
        
        # Setup mocks
        mock_user_repo.get_by_email.return_value = active_user
        mock_password_service.verify_password.return_value = True
        
        # Execute & Assert
        with pytest.raises(AuthenticationError, match="User account is inactive"):
            auth_service.authenticate_user(email, password)
        
        mock_user_repo.get_by_email.assert_called_once_with(email)
        mock_password_service.verify_password.assert_called_once_with(password, active_user.password_hash)

    def test_authenticate_user_suspended_status(
        self, 
        auth_service: AuthService, 
        mock_user_repo: Mock, 
        mock_password_service: Mock,
        active_user: User
    ) -> None:
        """Test authentication when user is suspended."""
        email = "test@example.com"
        password = "correct_password"
        
        # Make user suspended
        active_user.status = UserStatus.SUSPENDED
        
        # Setup mocks
        mock_user_repo.get_by_email.return_value = active_user
        mock_password_service.verify_password.return_value = True
        
        # Execute & Assert
        with pytest.raises(AuthenticationError, match="User account is suspended"):
            auth_service.authenticate_user(email, password)

    def test_create_user_tokens_success(
        self, 
        auth_service: AuthService, 
        mock_jwt_service: Mock,
        active_user: User
    ) -> None:
        """Test successful token creation for user."""
        # Setup mocks
        mock_access_token = "access_token_123"
        mock_refresh_token = "refresh_token_123"
        mock_jwt_service.create_access_token.return_value = mock_access_token
        mock_jwt_service.create_refresh_token.return_value = mock_refresh_token
        
        # Execute
        access_token, refresh_token = auth_service.create_user_tokens(active_user)
        
        # Assert
        assert access_token == mock_access_token
        assert refresh_token == mock_refresh_token
        
        # Verify method calls
        mock_jwt_service.create_access_token.assert_called_once_with(
            user_id=active_user.id,
            tenant_id=active_user.tenant_id,
            role=active_user.role.value,
            email=active_user.email
        )
        mock_jwt_service.create_refresh_token.assert_called_once_with(active_user.id)

    def test_verify_invitation_token_valid(
        self, 
        auth_service: AuthService, 
        mock_jwt_service: Mock
    ) -> None:
        """Test verifying valid invitation token."""
        token = "valid_invitation_token"
        expected_payload = {
            "email": "test@example.com",
            "tenant_id": str(uuid4()),
            "role": "sales_rep",
            "type": "invitation"
        }
        
        # Setup mocks
        mock_jwt_service.verify_token.return_value = expected_payload
        
        # Execute
        result = auth_service.verify_invitation_token(token)
        
        # Assert
        assert result == expected_payload
        mock_jwt_service.verify_token.assert_called_once_with(token)

    def test_verify_invitation_token_invalid(
        self, 
        auth_service: AuthService, 
        mock_jwt_service: Mock
    ) -> None:
        """Test verifying invalid invitation token."""
        token = "invalid_token"
        
        # Setup mocks
        mock_jwt_service.verify_token.return_value = None
        
        # Execute
        result = auth_service.verify_invitation_token(token)
        
        # Assert
        assert result is None
        mock_jwt_service.verify_token.assert_called_once_with(token)

    def test_verify_invitation_token_wrong_type(
        self, 
        auth_service: AuthService, 
        mock_jwt_service: Mock
    ) -> None:
        """Test verifying token with wrong type."""
        token = "access_token_not_invitation"
        payload = {
            "email": "test@example.com",
            "type": "access"  # Wrong type
        }
        
        # Setup mocks
        mock_jwt_service.verify_token.return_value = payload
        
        # Execute
        result = auth_service.verify_invitation_token(token)
        
        # Assert
        assert result is None

    def test_complete_registration_success(
        self, 
        auth_service: AuthService, 
        mock_user_repo: Mock, 
        mock_password_service: Mock,
        mock_jwt_service: Mock,
        pending_user: User
    ) -> None:
        """Test successful registration completion."""
        invitation_token = "valid_invitation_token"
        password = "new_password_123"
        first_name = "John"
        last_name = "Doe"
        hashed_password = "hashed_new_password_123"
        
        # Setup mocks
        mock_jwt_service.verify_token.return_value = {
            "email": pending_user.email,
            "tenant_id": str(pending_user.tenant_id),
            "role": "sales_rep",
            "type": "invitation"
        }
        mock_user_repo.get_by_email.return_value = pending_user
        mock_password_service.hash_password.return_value = hashed_password
        mock_user_repo.update.return_value = pending_user
        
        # Execute
        result = auth_service.complete_registration(
            invitation_token, password, first_name, last_name
        )
        
        # Assert
        assert result is not None
        assert result.first_name == first_name
        assert result.last_name == last_name
        assert result.password_hash == hashed_password
        assert result.status == UserStatus.ACTIVE
        assert result.is_email_verified is True
        assert result.invitation_token is None
        assert result.invitation_expires_at is None
        
        # Verify method calls
        mock_jwt_service.verify_token.assert_called_once_with(invitation_token)
        mock_user_repo.get_by_email.assert_called_once_with(pending_user.email)
        mock_password_service.hash_password.assert_called_once_with(password)
        mock_user_repo.update.assert_called_once_with(pending_user)

    def test_complete_registration_invalid_token(
        self, 
        auth_service: AuthService, 
        mock_jwt_service: Mock
    ) -> None:
        """Test registration completion with invalid token."""
        invitation_token = "invalid_token"
        password = "password"
        first_name = "John"
        last_name = "Doe"
        
        # Setup mocks
        mock_jwt_service.verify_token.return_value = None
        
        # Execute & Assert
        with pytest.raises(AuthenticationError, match="Invalid or expired invitation token"):
            auth_service.complete_registration(invitation_token, password, first_name, last_name)

    def test_complete_registration_user_not_found(
        self, 
        auth_service: AuthService, 
        mock_user_repo: Mock, 
        mock_jwt_service: Mock
    ) -> None:
        """Test registration completion when user is not found."""
        invitation_token = "valid_token"
        password = "password"
        first_name = "John"
        last_name = "Doe"
        
        # Setup mocks
        mock_jwt_service.verify_token.return_value = {
            "email": "nonexistent@example.com",
            "type": "invitation"
        }
        mock_user_repo.get_by_email.return_value = None
        
        # Execute & Assert
        with pytest.raises(AuthenticationError, match="User not found"):
            auth_service.complete_registration(invitation_token, password, first_name, last_name)

    def test_complete_registration_already_completed(
        self, 
        auth_service: AuthService, 
        mock_user_repo: Mock, 
        mock_jwt_service: Mock,
        active_user: User
    ) -> None:
        """Test registration completion when user is already active."""
        invitation_token = "valid_token"
        password = "password"
        first_name = "John"
        last_name = "Doe"
        
        # Setup mocks
        mock_jwt_service.verify_token.return_value = {
            "email": active_user.email,
            "type": "invitation"
        }
        mock_user_repo.get_by_email.return_value = active_user  # Already active
        
        # Execute & Assert
        with pytest.raises(AuthenticationError, match="User registration already completed"):
            auth_service.complete_registration(invitation_token, password, first_name, last_name)

    def test_create_user_tokens_with_super_admin(
        self, 
        auth_service: AuthService, 
        mock_jwt_service: Mock
    ) -> None:
        """Test token creation for super admin user (no tenant)."""
        super_admin = User(
            id=uuid4(),
            tenant_id=None,  # Super admin has no tenant
            email="admin@example.com",
            first_name="Super",
            last_name="Admin",
            role=UserRole.SUPER_ADMIN,
            status=UserStatus.ACTIVE
        )
        
        # Setup mocks
        mock_access_token = "admin_access_token"
        mock_refresh_token = "admin_refresh_token"
        mock_jwt_service.create_access_token.return_value = mock_access_token
        mock_jwt_service.create_refresh_token.return_value = mock_refresh_token
        
        # Execute
        access_token, refresh_token = auth_service.create_user_tokens(super_admin)
        
        # Assert
        assert access_token == mock_access_token
        assert refresh_token == mock_refresh_token
        
        # Verify method calls
        mock_jwt_service.create_access_token.assert_called_once_with(
            user_id=super_admin.id,
            tenant_id=None,  # No tenant for super admin
            role=super_admin.role.value,
            email=super_admin.email
        )

    def test_authenticate_user_records_login(
        self, 
        auth_service: AuthService, 
        mock_user_repo: Mock, 
        mock_password_service: Mock,
        active_user: User
    ) -> None:
        """Test that successful authentication records login time."""
        email = "test@example.com"
        password = "correct_password"
        original_last_login = active_user.last_login
        
        # Setup mocks
        mock_user_repo.get_by_email.return_value = active_user
        mock_password_service.verify_password.return_value = True
        mock_user_repo.update.return_value = active_user
        
        # Execute
        result = auth_service.authenticate_user(email, password)
        
        # Assert
        assert result is not None
        assert active_user.last_login != original_last_login
        assert active_user.last_login is not None
        
        # Verify update was called with the user
        mock_user_repo.update.assert_called_once_with(active_user)

    def test_auth_service_initialization(self) -> None:
        """Test that AuthService can be initialized with required dependencies."""
        user_repo = Mock(spec=UserRepository)
        password_service = Mock(spec=PasswordService)
        jwt_service = Mock(spec=JWTService)
        
        auth_service = AuthService(user_repo, password_service, jwt_service)
        
        # Instead of accessing private attributes, check that AuthService was initialized without error
        assert isinstance(auth_service, AuthService)

    def test_verify_invitation_token_empty_payload(
        self, 
        auth_service: AuthService, 
        mock_jwt_service: Mock
    ) -> None:
        """Test verifying invitation token with empty payload."""
        token = "token_with_empty_payload"
        
        # Setup mocks
        mock_jwt_service.verify_token.return_value = {}  # Empty payload
        
        # Execute
        result = auth_service.verify_invitation_token(token)
        
        # Assert
        assert result is None

    def test_complete_registration_updates_user_fields_correctly(
        self, 
        auth_service: AuthService, 
        mock_user_repo: Mock, 
        mock_password_service: Mock,
        mock_jwt_service: Mock,
        pending_user: User
    ) -> None:
        """Test that registration completion updates all required user fields."""
        invitation_token = "valid_invitation_token"
        password = "new_password_123"
        first_name = "UpdatedFirst"
        last_name = "UpdatedLast"
        hashed_password = "hashed_new_password_123"
        
        # Store original values
        original_status = pending_user.status
        original_email_verified = pending_user.is_email_verified
        original_invitation_token = pending_user.invitation_token
        original_invitation_expires = pending_user.invitation_expires_at
        
        # Setup mocks
        mock_jwt_service.verify_token.return_value = {
            "email": pending_user.email,
            "type": "invitation"
        }
        mock_user_repo.get_by_email.return_value = pending_user
        mock_password_service.hash_password.return_value = hashed_password
        mock_user_repo.update.return_value = pending_user
        
        # Execute
        auth_service.complete_registration(invitation_token, password, first_name, last_name)
        
        # Assert all fields were updated correctly
        assert pending_user.first_name == first_name
        assert pending_user.last_name == last_name
        assert pending_user.password_hash == hashed_password
        assert pending_user.status == UserStatus.ACTIVE
        assert pending_user.is_email_verified is True
        assert pending_user.invitation_token is None
        assert pending_user.invitation_expires_at is None
        
        # Verify these were different from original values
        assert pending_user.status != original_status
        assert pending_user.is_email_verified != original_email_verified
        assert pending_user.invitation_token != original_invitation_token
        assert pending_user.invitation_expires_at != original_invitation_expires