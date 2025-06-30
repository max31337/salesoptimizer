import pytest
from datetime import datetime, timezone
from domain.organization.entities.user import User, UserRole, UserStatus
from domain.organization.value_objects.email import Email
from domain.organization.value_objects.user_id import UserId


class TestUser:
    """Test User entity."""
    
    def test_valid_user_creation(self):
        """Test creating valid user."""
        user_id = UserId.generate()
        email = Email("test@example.com")
        
        user = User(
            id=user_id,
            email=email,
            username="testuser",
            first_name="John",
            last_name="Doe",
            password_hash="hashed_password",
            role=UserRole.SALES_REP,
            status=UserStatus.ACTIVE
        )
        
        assert user.id == user_id
        assert user.email == email
        assert user.username == "testuser"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.role == UserRole.SALES_REP
        assert user.status == UserStatus.ACTIVE
    
    def test_full_name_property(self):
        """Test full name property."""
        user = User(
            id=None,
            email=Email("test@example.com"),
            username=None,
            first_name="John",
            last_name="Doe",
            password_hash=None,
            role=UserRole.SALES_REP,
            status=UserStatus.PENDING
        )
        
        assert user.full_name == "John Doe"
    
    def test_is_active_method(self):
        """Test is_active method."""
        active_user = User(
            id=None,
            email=Email("active@example.com"),
            username=None,
            first_name="Active",
            last_name="User",
            password_hash=None,
            role=UserRole.SALES_REP,
            status=UserStatus.ACTIVE
        )
        
        inactive_user = User(
            id=None,
            email=Email("inactive@example.com"),
            username=None,
            first_name="Inactive",
            last_name="User",
            password_hash=None,
            role=UserRole.SALES_REP,
            status=UserStatus.INACTIVE
        )
        
        assert active_user.is_active() is True
        assert inactive_user.is_active() is False
    
    def test_has_password_method(self):
        """Test has_password method."""
        user_with_password = User(
            id=None,
            email=Email("test@example.com"),
            username=None,
            first_name="Test",
            last_name="User",
            password_hash="hashed_password",
            role=UserRole.SALES_REP,
            status=UserStatus.ACTIVE
        )
        
        user_without_password = User(
            id=None,
            email=Email("test2@example.com"),
            username=None,
            first_name="Test2",
            last_name="User",
            password_hash=None,
            role=UserRole.SALES_REP,
            status=UserStatus.PENDING
        )
        
        assert user_with_password.has_password() is True
        assert user_without_password.has_password() is False
    
    # Removed test_record_login_method since last_login is deprecated and replaced by login_activity tracking
    
    def test_empty_first_name_raises_error(self):
        """Test empty first name raises ValueError."""
        with pytest.raises(ValueError, match="First name cannot be empty"):
            User(
                id=None,
                email=Email("test@example.com"),
                username=None,
                first_name="",
                last_name="Doe",
                password_hash=None,
                role=UserRole.SALES_REP,
                status=UserStatus.PENDING
            )
    
    def test_empty_last_name_raises_error(self):
        """Test empty last name raises ValueError."""
        with pytest.raises(ValueError, match="Last name cannot be empty"):
            User(
                id=None,
                email=Email("test@example.com"),
                username=None,
                first_name="John",
                last_name="",
                password_hash=None,
                role=UserRole.SALES_REP,
                status=UserStatus.PENDING
            )
    
    def test_whitespace_only_names_raise_error(self):
        """Test whitespace-only names raise ValueError."""
        with pytest.raises(ValueError, match="First name cannot be empty"):
            User(
                id=None,
                email=Email("test@example.com"),
                username=None,
                first_name="   ",
                last_name="Doe",
                password_hash=None,
                role=UserRole.SALES_REP,
                status=UserStatus.PENDING
            )