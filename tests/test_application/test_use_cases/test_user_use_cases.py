import pytest
from unittest.mock import Mock
from uuid import uuid4, UUID

from application.use_cases.user_use_cases import UserUseCases
from application.dtos.user_dto import UserCreateDTO, UserResponseDTO
from domain.entities.user import User, UserRole, UserStatus
from infrastructure.repositories.user_repository_impl import UserRepositoryImpl


class TestUserUseCases:
    """Test user use cases."""
    
    @pytest.fixture
    def mock_user_repository(self) -> Mock:
        """Create a mock user repository."""
        return Mock(spec=UserRepositoryImpl)
    
    @pytest.fixture
    def user_use_cases(self, mock_user_repository: Mock) -> UserUseCases:
        """Create user use cases with mocked dependencies."""
        return UserUseCases(mock_user_repository)
    
    @pytest.fixture
    def sample_user(self) -> User:
        """Create a sample user for testing."""
        return User(
            id=uuid4(),
            email="test@example.com",
            username="testuser",
            first_name="John",
            last_name="Doe",
            phone="+1234567890",
            role=UserRole.SALES_REP,
            status=UserStatus.ACTIVE,
            is_email_verified=True
        )
    
    def test_create_user_success(
        self,
        user_use_cases: UserUseCases,
        mock_user_repository: Mock,
        sample_user: User
    ):
        """Test successful user creation."""
        # Arrange
        user_data = UserCreateDTO(
            email="test@example.com",
            username="testuser",
            first_name="John",
            last_name="Doe",
            phone="+1234567890",
            role=UserRole.SALES_REP
        )
        
        mock_user_repository.exists_by_email.return_value = False
        mock_user_repository.exists_by_username.return_value = False
        mock_user_repository.create.return_value = sample_user
        
        # Act
        result = user_use_cases.create_user(user_data)
        
        # Assert
        mock_user_repository.exists_by_email.assert_called_once_with(user_data.email)
        mock_user_repository.exists_by_username.assert_called_once_with(user_data.username)
        mock_user_repository.create.assert_called_once()
        
        assert isinstance(result, UserResponseDTO)
        assert result.email == "test@example.com"
        assert result.username == "testuser"
        assert result.first_name == "John"
        assert result.last_name == "Doe"
        assert result.phone == "+1234567890"
        assert result.role == UserRole.SALES_REP
        assert result.status == UserStatus.ACTIVE
    
    def test_create_user_email_exists(
        self,
        user_use_cases: UserUseCases,
        mock_user_repository: Mock
    ):
        """Test user creation with existing email."""
        # Arrange
        user_data = UserCreateDTO(
            email="existing@example.com",
            username="testuser",
            first_name="John",
            last_name="Doe",
            phone="+1234567890"
        )
        
        mock_user_repository.exists_by_email.return_value = True
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            user_use_cases.create_user(user_data)
        
        assert str(exc_info.value) == "Email already registered"
        mock_user_repository.exists_by_email.assert_called_once_with(user_data.email)
        mock_user_repository.create.assert_not_called()
    
    def test_create_user_username_exists(
        self,
        user_use_cases: UserUseCases,
        mock_user_repository: Mock
    ):
        """Test user creation with existing username."""
        # Arrange
        user_data = UserCreateDTO(
            email="test@example.com",
            username="existinguser",
            first_name="John",
            last_name="Doe",
            phone="+1234567890"
        )
        
        mock_user_repository.exists_by_email.return_value = False
        mock_user_repository.exists_by_username.return_value = True
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            user_use_cases.create_user(user_data)
        
        assert str(exc_info.value) == "Username already taken"
        mock_user_repository.exists_by_email.assert_called_once_with(user_data.email)
        mock_user_repository.exists_by_username.assert_called_once_with(user_data.username)
        mock_user_repository.create.assert_not_called()
    
    def test_get_user_by_id_success(
        self,
        user_use_cases: UserUseCases,
        mock_user_repository: Mock,
        sample_user: User
    ):
        """Test successful user retrieval by ID."""
        # Arrange
        user_id = str(sample_user.id)
        mock_user_repository.get_by_id.return_value = sample_user
        
        # Act
        result = user_use_cases.get_user_by_id(user_id)
        
        # Assert
        mock_user_repository.get_by_id.assert_called_once_with(UUID(user_id))
        
        assert isinstance(result, UserResponseDTO)
        assert result.id == str(sample_user.id)
        assert result.email == sample_user.email
        assert result.username == sample_user.username
    
    def test_get_user_by_id_not_found(
        self,
        user_use_cases: UserUseCases,
        mock_user_repository: Mock
    ):
        """Test user retrieval by ID when user not found."""
        # Arrange
        user_id = str(uuid4())
        mock_user_repository.get_by_id.return_value = None
        
        # Act
        result = user_use_cases.get_user_by_id(user_id)
        
        # Assert
        mock_user_repository.get_by_id.assert_called_once_with(UUID(user_id))
        assert result is None