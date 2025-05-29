from datetime import datetime, timezone
from uuid import UUID, uuid4

from domain.organization.entities.user import User, UserRole, UserStatus


class TestUserEntity:
    
    def test_user_creation_with_defaults(self) -> None:
        """Test creating a user with default values."""
        user = User(
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        
        assert user.email == "test@example.com"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.role == UserRole.SALES_REP
        assert user.status == UserStatus.PENDING
        assert user.tenant_id is None
        assert user.username is None
        assert user.phone is None
        assert user.password_hash is None
        assert user.is_email_verified is False
        assert user.last_login is None
        assert user.invitation_token is None
        assert user.invitation_expires_at is None
        assert isinstance(user.id, UUID)
        assert user.created_at is not None
        assert user.updated_at is None
    
    def test_user_creation_with_all_fields(self) -> None:
        """Test creating a user with all fields specified."""
        user_id = uuid4()
        tenant_id = uuid4()
        created_at = datetime.now(timezone.utc)
        
        user = User(
            id=user_id,
            tenant_id=tenant_id,
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            phone="+1234567890",
            password_hash="hashed_password",
            role=UserRole.ORG_ADMIN,
            status=UserStatus.ACTIVE,
            is_email_verified=True,
            created_at=created_at
        )
        
        assert user.id == user_id
        assert user.tenant_id == tenant_id
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.phone == "+1234567890"
        assert user.password_hash == "hashed_password"
        assert user.role == UserRole.ORG_ADMIN
        assert user.status == UserStatus.ACTIVE
        assert user.is_email_verified is True
        assert user.created_at == created_at
    
    def test_full_name_method(self) -> None:
        """Test the full_name method."""
        user = User(
            email="test@example.com",
            first_name="John",
            last_name="Doe"
        )
        assert user.full_name == "John Doe"
        
        # Test with extra spaces (should be cleaned up)
        user_with_spaces = User(
            email="test@example.com",
            first_name="  John  ",
            last_name="  Doe  "
        )
        assert user_with_spaces.full_name == "John Doe"
        
        # Test with empty last name
        user_no_last = User(
            email="test@example.com",
            first_name="John",
            last_name=""
        )
        assert user_no_last.full_name == "John"
        
        # Test with empty first name
        user_no_first = User(
            email="test@example.com",
            first_name="",
            last_name="Doe"
        )
        assert user_no_first.full_name == "Doe"
        
        # Test with both names having spaces
        user_spaces = User(
            email="test@example.com",
            first_name=" Mary Jane ",
            last_name=" Watson Smith "
        )
        assert user_spaces.full_name == "Mary Jane Watson Smith"
    
    def test_is_active_method(self) -> None:
        """Test the is_active method."""
        active_user = User(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            status=UserStatus.ACTIVE
        )
        assert active_user.is_active() is True
        
        inactive_user = User(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            status=UserStatus.INACTIVE
        )
        assert inactive_user.is_active() is False
        
        suspended_user = User(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            status=UserStatus.SUSPENDED
        )
        assert suspended_user.is_active() is False
        
        pending_user = User(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            status=UserStatus.PENDING
        )
        assert pending_user.is_active() is False
    
    def test_is_super_admin_method(self) -> None:
        """Test the is_super_admin method."""
        super_admin = User(
            email="admin@example.com",
            first_name="Super",
            last_name="Admin",
            role=UserRole.SUPER_ADMIN
        )
        assert super_admin.is_super_admin() is True
        
        org_admin = User(
            email="admin@example.com",
            first_name="Org",
            last_name="Admin",
            role=UserRole.ORG_ADMIN
        )
        assert org_admin.is_super_admin() is False
        
        manager = User(
            email="manager@example.com",
            first_name="Manager",
            last_name="User",
            role=UserRole.MANAGER
        )
        assert manager.is_super_admin() is False
        
        sales_rep = User(
            email="sales@example.com",
            first_name="Sales",
            last_name="Rep",
            role=UserRole.SALES_REP
        )
        assert sales_rep.is_super_admin() is False
    
    def test_can_manage_users_method(self) -> None:
        """Test the can_manage_users method."""
        super_admin = User(
            email="admin@example.com",
            first_name="Super",
            last_name="Admin",
            role=UserRole.SUPER_ADMIN
        )
        assert super_admin.can_manage_users() is True
        
        org_admin = User(
            email="admin@example.com",
            first_name="Org",
            last_name="Admin",
            role=UserRole.ORG_ADMIN
        )
        assert org_admin.can_manage_users() is True
        
        manager = User(
            email="manager@example.com",
            first_name="Manager",
            last_name="User",
            role=UserRole.MANAGER
        )
        assert manager.can_manage_users() is True
        
        sales_rep = User(
            email="sales@example.com",
            first_name="Sales",
            last_name="Rep",
            role=UserRole.SALES_REP
        )
        assert sales_rep.can_manage_users() is False
    
    def test_can_access_tenant_method(self) -> None:
        """Test the can_access_tenant method."""
        tenant_id = uuid4()
        other_tenant_id = uuid4()
        
        # Super admin can access any tenant
        super_admin = User(
            email="admin@example.com",
            first_name="Super",
            last_name="Admin",
            role=UserRole.SUPER_ADMIN,
            tenant_id=None
        )
        assert super_admin.can_access_tenant(tenant_id) is True
        assert super_admin.can_access_tenant(other_tenant_id) is True
        
        # Regular user can only access their own tenant
        user = User(
            email="user@example.com",
            first_name="Regular",
            last_name="User",
            role=UserRole.SALES_REP,
            tenant_id=tenant_id
        )
        assert user.can_access_tenant(tenant_id) is True
        assert user.can_access_tenant(other_tenant_id) is False
    
    def test_activate_method(self) -> None:
        """Test the activate method."""
        user = User(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            status=UserStatus.INACTIVE
        )
        initial_updated_at = user.updated_at
        
        user.activate()
        
        assert user.status == UserStatus.ACTIVE
        assert user.updated_at is not None
        assert user.updated_at != initial_updated_at
        assert isinstance(user.updated_at, datetime)
    
    def test_deactivate_method(self) -> None:
        """Test the deactivate method."""
        user = User(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            status=UserStatus.ACTIVE
        )
        initial_updated_at = user.updated_at
        
        user.deactivate()
        
        assert user.status == UserStatus.INACTIVE
        assert user.updated_at is not None
        assert user.updated_at != initial_updated_at
        assert isinstance(user.updated_at, datetime)
    
    def test_verify_email_method(self) -> None:
        """Test the verify_email method."""
        user = User(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            is_email_verified=False
        )
        initial_updated_at = user.updated_at
        
        user.verify_email()
        
        assert user.is_email_verified is True
        assert user.updated_at is not None
        assert user.updated_at != initial_updated_at
        assert isinstance(user.updated_at, datetime)
    
    def test_set_password_method(self) -> None:
        """Test the set_password method."""
        user = User(
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        initial_updated_at = user.updated_at
        
        user.set_password("hashed_password_123")
        
        assert user.password_hash == "hashed_password_123"
        assert user.updated_at is not None
        assert user.updated_at != initial_updated_at
        assert isinstance(user.updated_at, datetime)
    
    def test_record_login_method(self) -> None:
        """Test the record_login method."""
        user = User(
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        initial_updated_at = user.updated_at
        assert user.last_login is None
        
        user.record_login()
        
        assert user.last_login is not None
        assert isinstance(user.last_login, datetime)
        assert user.updated_at is not None
        assert user.updated_at != initial_updated_at
        assert isinstance(user.updated_at, datetime)
    
    def test_user_roles_enum(self) -> None:
        """Test UserRole enum values."""
        assert UserRole.SUPER_ADMIN.value == "super_admin"
        assert UserRole.ORG_ADMIN.value == "org_admin"
        assert UserRole.MANAGER.value == "manager"
        assert UserRole.SALES_REP.value == "sales_rep"
    
    def test_user_status_enum(self) -> None:
        """Test UserStatus enum values."""
        assert UserStatus.ACTIVE.value == "active"
        assert UserStatus.INACTIVE.value == "inactive"
        assert UserStatus.SUSPENDED.value == "suspended"
        assert UserStatus.PENDING.value == "pending"
    
    def test_user_id_auto_generation(self) -> None:
        """Test that user ID is automatically generated."""
        user1 = User(
            email="user1@example.com",
            first_name="User",
            last_name="One"
        )
        user2 = User(
            email="user2@example.com",
            first_name="User",
            last_name="Two"
        )
        
        assert isinstance(user1.id, UUID)
        assert isinstance(user2.id, UUID)
        assert user1.id != user2.id  # Should be unique
    
    def test_user_created_at_auto_generation(self) -> None:
        """Test that created_at is automatically set."""
        user = User(
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        
        assert user.created_at is not None
        assert isinstance(user.created_at, datetime)
        assert user.created_at.tzinfo == timezone.utc
    
    def test_full_name_edge_cases(self) -> None:
        """Test full_name method with edge cases."""
        # Test with None values (shouldn't happen but let's be safe)
        user_none_first = User(
            email="test@example.com",
            first_name="",
            last_name="Doe"
        )
        assert user_none_first.full_name == "Doe"
        
        # Test with only spaces
        user_spaces_only = User(
            email="test@example.com",
            first_name="   ",
            last_name="   "
        )
        assert user_spaces_only.full_name == ""
        
        # Test with special characters
        user_special = User(
            email="test@example.com",
            first_name="José María",
            last_name="García-López"
        )
        assert user_special.full_name == "José María García-López"