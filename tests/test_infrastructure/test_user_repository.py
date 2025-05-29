import pytest
from sqlalchemy.orm import Session
from uuid import uuid4

from infrastructure.repositories.user_repository_impl import UserRepositoryImpl
from domain.organization.entities.user import User, UserRole, UserStatus


class TestUserRepository:
    
    @pytest.fixture
    def sample_user(self) -> User:
        """Create a sample user for testing."""
        return User(
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            role=UserRole.SALES_REP,
            status=UserStatus.ACTIVE
        )
    
    def test_create_user(self, db_session: Session, sample_user: User) -> None:
        """Test creating a user in the repository."""
        repo = UserRepositoryImpl(db_session)
        
        created_user = repo.create(sample_user)
        
        assert created_user.id is not None
        assert created_user.email == sample_user.email
        assert created_user.username == sample_user.username
        assert created_user.first_name == sample_user.first_name
        assert created_user.created_at is not None
    
    def test_create_user_duplicate_email(self, db_session: Session, sample_user: User) -> None:
        """Test creating a user with duplicate email raises error."""
        repo = UserRepositoryImpl(db_session)
        repo.create(sample_user)
        
        duplicate_user = User(
            email=sample_user.email,  # Same email
            username="differentuser",
            first_name="Different",
            last_name="User"
        )
        
        with pytest.raises(ValueError, match="User with this email or username already exists"):
            repo.create(duplicate_user)
    
    def test_create_user_duplicate_username(self, db_session: Session, sample_user: User) -> None:
        """Test creating a user with duplicate username raises error."""
        repo = UserRepositoryImpl(db_session)
        repo.create(sample_user)
        
        duplicate_user = User(
            email="different@example.com",
            username=sample_user.username,  # Same username
            first_name="Different",
            last_name="User"
        )
        
        with pytest.raises(ValueError, match="User with this email or username already exists"):
            repo.create(duplicate_user)
    
    def test_get_by_id_existing_user(self, db_session: Session, sample_user: User) -> None:
        """Test getting a user by ID when user exists."""
        repo = UserRepositoryImpl(db_session)
        created_user = repo.create(sample_user)
        
        assert created_user.id is not None
        retrieved_user = repo.get_by_id(created_user.id)
        
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == created_user.email
    
    def test_get_by_id_non_existing_user(self, db_session: Session) -> None:
        """Test getting a user by ID when user doesn't exist."""
        repo = UserRepositoryImpl(db_session)
        
        retrieved_user = repo.get_by_id(uuid4())
        
        assert retrieved_user is None
    
    def test_get_by_email_existing_user(self, db_session: Session, sample_user: User) -> None:
        """Test getting a user by email when user exists."""
        repo = UserRepositoryImpl(db_session)
        created_user = repo.create(sample_user)
        
        retrieved_user = repo.get_by_email(created_user.email)
        
        assert retrieved_user is not None
        assert retrieved_user.email == created_user.email
        assert retrieved_user.username == created_user.username
    
    def test_get_by_email_non_existing_user(self, db_session: Session) -> None:
        """Test getting a user by email when user doesn't exist."""
        repo = UserRepositoryImpl(db_session)
        
        retrieved_user = repo.get_by_email("nonexistent@example.com")
        
        assert retrieved_user is None
    
    def test_get_by_username_existing_user(self, db_session: Session, sample_user: User) -> None:
        """Test getting a user by username when user exists."""
        repo = UserRepositoryImpl(db_session)
        created_user = repo.create(sample_user)
        
        assert created_user.username is not None
        retrieved_user = repo.get_by_username(created_user.username)
        
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.username == created_user.username
    
    def test_get_by_username_non_existing_user(self, db_session: Session) -> None:
        """Test getting a user by username when user doesn't exist."""
        repo = UserRepositoryImpl(db_session)
        
        retrieved_user = repo.get_by_username("nonexistent")
        
        assert retrieved_user is None
    
    def test_get_by_tenant(self, db_session: Session) -> None:
        """Test getting users by tenant ID."""
        repo = UserRepositoryImpl(db_session)
        tenant_id = uuid4()
        other_tenant_id = uuid4()
        
        # Create users for specific tenant
        for i in range(3):
            user = User(
                email=f"user{i}@example.com",
                username=f"user{i}",
                first_name=f"User{i}",
                last_name="Test",
                tenant_id=tenant_id
            )
            repo.create(user)
        
        # Create user for different tenant
        other_user = User(
            email="other@example.com",
            username="other",
            first_name="Other",
            last_name="User",
            tenant_id=other_tenant_id
        )
        repo.create(other_user)
        
        # Get users by tenant
        tenant_users = repo.get_by_tenant(tenant_id)
        
        assert len(tenant_users) == 3
        assert all(user.tenant_id == tenant_id for user in tenant_users)
    
    def test_get_by_tenant_with_pagination(self, db_session: Session) -> None:
        """Test getting users by tenant with pagination."""
        repo = UserRepositoryImpl(db_session)
        tenant_id = uuid4()
        
        # Create 5 users
        for i in range(5):
            user = User(
                email=f"user{i}@example.com",
                username=f"user{i}",
                first_name=f"User{i}",
                last_name="Test",
                tenant_id=tenant_id
            )
            repo.create(user)
        
        # Test pagination
        page1 = repo.get_by_tenant(tenant_id, skip=0, limit=2)
        page2 = repo.get_by_tenant(tenant_id, skip=2, limit=2)
        page3 = repo.get_by_tenant(tenant_id, skip=4, limit=2)
        
        assert len(page1) == 2
        assert len(page2) == 2
        assert len(page3) == 1
        
        # Ensure no overlapping users
        all_user_ids = [u.id for u in page1 + page2 + page3]
        assert len(all_user_ids) == len(set(all_user_ids))
    
    def test_get_by_invitation_token(self, db_session: Session) -> None:
        """Test getting user by invitation token."""
        repo = UserRepositoryImpl(db_session)
        invitation_token = "invitation_token_123"
        
        user = User(
            email="invited@example.com",
            username="invited",
            first_name="Invited",
            last_name="User",
            invitation_token=invitation_token
        )
        created_user = repo.create(user)
        
        retrieved_user = repo.get_by_invitation_token(invitation_token)
        
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.invitation_token == invitation_token
    
    def test_get_by_invitation_token_non_existing(self, db_session: Session) -> None:
        """Test getting user by non-existing invitation token."""
        repo = UserRepositoryImpl(db_session)
        
        retrieved_user = repo.get_by_invitation_token("nonexistent_token")
        
        assert retrieved_user is None
    
    def test_get_all_users(self, db_session: Session) -> None:
        """Test getting all users."""
        repo = UserRepositoryImpl(db_session)
        
        # Create multiple users
        from typing import List
        users: List[User] = []
        for i in range(3):
            user = User(
                email=f"user{i}@example.com",
                username=f"user{i}",
                first_name=f"User{i}",
                last_name="Test"
            )
            users.append(repo.create(user))
        
        all_users = repo.get_all()
        
        assert len(all_users) == 3
        created_emails = {u.email for u in users}
        retrieved_emails = {u.email for u in all_users}
        assert created_emails == retrieved_emails
    
    def test_get_all_users_with_pagination(self, db_session: Session) -> None:
        """Test getting all users with pagination."""
        repo = UserRepositoryImpl(db_session)
        
        # Create 5 users
        for i in range(5):
            user = User(
                email=f"user{i}@example.com",
                username=f"user{i}",
                first_name=f"User{i}",
                last_name="Test"
            )
            repo.create(user)
        
        # Test pagination
        page1 = repo.get_all(skip=0, limit=2)
        page2 = repo.get_all(skip=2, limit=2)
        page3 = repo.get_all(skip=4, limit=2)
        
        assert len(page1) == 2
        assert len(page2) == 2
        assert len(page3) == 1
    
    def test_update_user(self, db_session: Session, sample_user: User) -> None:
        """Test updating a user."""
        repo = UserRepositoryImpl(db_session)
        created_user = repo.create(sample_user)
        
        # Update user data
        created_user.first_name = "Updated"
        created_user.last_name = "Name"
        created_user.role = UserRole.MANAGER
        
        updated_user = repo.update(created_user)
        
        assert updated_user.first_name == "Updated"
        assert updated_user.last_name == "Name"
        assert updated_user.role == UserRole.MANAGER
        assert updated_user.id == created_user.id
    
    def test_update_user_not_found(self, db_session: Session) -> None:
        """Test updating a user that doesn't exist."""
        repo = UserRepositoryImpl(db_session)
        
        user = User(
            id=uuid4(),
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        
        with pytest.raises(ValueError, match="User not found"):
            repo.update(user)
    
    def test_delete_user_existing(self, db_session: Session, sample_user: User) -> None:
        """Test deleting an existing user."""
        repo = UserRepositoryImpl(db_session)
        created_user = repo.create(sample_user)
        
        assert created_user.id is not None
        result = repo.delete(created_user.id)
        
        assert result is True
        assert repo.get_by_id(created_user.id) is None
    
    def test_delete_user_non_existing(self, db_session: Session) -> None:
        """Test deleting a non-existing user."""
        repo = UserRepositoryImpl(db_session)
        
        result = repo.delete(uuid4())
        
        assert result is False
    
    def test_exists_by_email(self, db_session: Session, sample_user: User) -> None:
        """Test checking if user exists by email."""
        repo = UserRepositoryImpl(db_session)
        
        assert repo.exists_by_email(sample_user.email) is False
        
        repo.create(sample_user)
        
        assert repo.exists_by_email(sample_user.email) is True
        assert repo.exists_by_email("nonexistent@example.com") is False
    
    def test_exists_by_username(self, db_session: Session, sample_user: User) -> None:
        """Test checking if user exists by username."""
        repo = UserRepositoryImpl(db_session)
        
        assert repo.exists_by_username(sample_user.username or "") is False
        
        repo.create(sample_user)
        
        assert repo.exists_by_username(sample_user.username or "") is True
        assert repo.exists_by_username("nonexistent") is False
    
    def test_count_by_tenant_and_role(self, db_session: Session) -> None:
        """Test counting users by tenant and role."""
        repo = UserRepositoryImpl(db_session)
        tenant_id = uuid4()
        
        # Create users with different roles
        admin_user = User(
            email="admin@example.com",
            username="admin",
            first_name="Admin",
            last_name="User",
            tenant_id=tenant_id,
            role=UserRole.ORG_ADMIN
        )
        repo.create(admin_user)
        
        for i in range(3):
            sales_user = User(
                email=f"sales{i}@example.com",
                username=f"sales{i}",
                first_name=f"Sales{i}",
                last_name="User",
                tenant_id=tenant_id,
                role=UserRole.SALES_REP
            )
            repo.create(sales_user)
        
        # Test counts
        admin_count = repo.count_by_tenant_and_role(tenant_id, UserRole.ORG_ADMIN)
        sales_count = repo.count_by_tenant_and_role(tenant_id, UserRole.SALES_REP)
        manager_count = repo.count_by_tenant_and_role(tenant_id, UserRole.MANAGER)
        
        assert admin_count == 1
        assert sales_count == 3
        assert manager_count == 0
    
    def test_user_with_all_statuses(self, db_session: Session) -> None:
        """Test creating and retrieving users with all status values."""
        repo = UserRepositoryImpl(db_session)
        
        from typing import List
        statuses = [UserStatus.ACTIVE, UserStatus.INACTIVE, UserStatus.SUSPENDED, UserStatus.PENDING]
        created_users: List[User] = []
        
        for i, status in enumerate(statuses):
            user = User(
                email=f"user{i}@example.com",
                username=f"user{i}",
                first_name=f"User{i}",
                last_name="Test",
                status=status
            )
            created_users.append(repo.create(user))
        
        # Verify all users were created with correct statuses
        for created_user, expected_status in zip(created_users, statuses):
            assert created_user.id is not None
            retrieved_user = repo.get_by_id(created_user.id)
            assert retrieved_user is not None
            assert retrieved_user.status == expected_status