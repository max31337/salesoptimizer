from datetime import datetime
from domain.entities.user import User, UserRole, UserStatus

class TestUserEntity:
    
    def test_user_creation_with_defaults(self) -> None:
        """Test creating a user with default values."""
        user = User(
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User"
        )
        
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.role == UserRole.SALES_REP
        assert user.status == UserStatus.ACTIVE
        assert user.is_email_verified is False
        assert user.id is None
        assert user.phone is None
    
    def test_user_creation_with_all_fields(self) -> None:
        """Test creating a user with all fields specified."""
        user = User(
            id=1,
            email="admin@example.com",
            username="admin",
            first_name="Admin",
            last_name="User",
            phone="+1234567890",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            is_email_verified=True
        )
        
        assert user.id == 1
        assert user.email == "admin@example.com"
        assert user.username == "admin"
        assert user.first_name == "Admin"
        assert user.last_name == "User"
        assert user.phone == "+1234567890"
        assert user.role == UserRole.ADMIN
        assert user.status == UserStatus.ACTIVE
        assert user.is_email_verified is True
    
    def test_full_name_method(self) -> None:
        """Test the full_name method."""
        user = User(
            first_name="John",
            last_name="Doe"
        )
        assert user.full_name() == "John Doe"
        
        # Test with empty names
        user_empty = User(first_name="", last_name="")
        assert user_empty.full_name() == ""
        
        # Test with only first name
        user_first_only = User(first_name="John", last_name="")
        assert user_first_only.full_name() == "John"
    
    def test_is_active_method(self) -> None:
        """Test the is_active method."""
        active_user = User(status=UserStatus.ACTIVE)
        assert active_user.is_active() is True
        
        inactive_user = User(status=UserStatus.INACTIVE)
        assert inactive_user.is_active() is False
        
        suspended_user = User(status=UserStatus.SUSPENDED)
        assert suspended_user.is_active() is False
    
    def test_can_manage_users_method(self) -> None:
        """Test the can_manage_users method."""
        admin_user = User(role=UserRole.ADMIN)
        assert admin_user.can_manage_users() is True
        
        manager_user = User(role=UserRole.MANAGER)
        assert manager_user.can_manage_users() is True
        
        sales_rep_user = User(role=UserRole.SALES_REP)
        assert sales_rep_user.can_manage_users() is False
        
        viewer_user = User(role=UserRole.VIEWER)
        assert viewer_user.can_manage_users() is False
    
    def test_activate_method(self) -> None:
        """Test the activate method."""
        user = User(status=UserStatus.INACTIVE)
        user.activate()
        
        assert user.status == UserStatus.ACTIVE
        assert user.updated_at is not None
        assert isinstance(user.updated_at, datetime)
    
    def test_deactivate_method(self) -> None:
        """Test the deactivate method."""
        user = User(status=UserStatus.ACTIVE)
        user.deactivate()
        
        assert user.status == UserStatus.INACTIVE
        assert user.updated_at is not None
        assert isinstance(user.updated_at, datetime)
    
    def test_verify_email_method(self) -> None:
        """Test the verify_email method."""
        user = User(is_email_verified=False)
        user.verify_email()
        
        assert user.is_email_verified is True
        assert user.updated_at is not None
        assert isinstance(user.updated_at, datetime)