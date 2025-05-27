from sqlalchemy.orm import Session
from infrastructure.repositories.user_repository_impl import UserRepositoryImpl
from domain.entities.user import User, UserRole, UserStatus

class TestUserRepository:
    
    def test_create_user(self, db_session: Session, sample_user: User) -> None:
        """Test creating a user in the repository."""
        repo = UserRepositoryImpl(db_session)
        created_user = repo.create(sample_user)
        
        assert created_user.id is not None
        assert created_user.email == sample_user.email
        assert created_user.username == sample_user.username
        assert created_user.first_name == sample_user.first_name
        assert created_user.last_name == sample_user.last_name
        assert created_user.role == sample_user.role
        assert created_user.status == sample_user.status
        assert created_user.created_at is not None
    
    def test_get_by_id_existing_user(self, db_session: Session, sample_user: User) -> None:
        """Test getting a user by ID when user exists."""
        repo = UserRepositoryImpl(db_session)
        created_user = repo.create(sample_user)
        assert created_user.id is not None
        
        retrieved_user = repo.get_by_id(created_user.id)
        
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == created_user.email
        assert retrieved_user.username == created_user.username
    
    def test_get_by_id_non_existing_user(self, db_session: Session) -> None:
        """Test getting a user by ID when user doesn't exist."""
        repo = UserRepositoryImpl(db_session)
        
        retrieved_user = repo.get_by_id(999)
        
        assert retrieved_user is None
    
    def test_get_by_email_existing_user(self, db_session: Session, sample_user: User) -> None:
        """Test getting a user by email when user exists."""
        repo = UserRepositoryImpl(db_session)
        created_user = repo.create(sample_user)
        
        retrieved_user = repo.get_by_email(created_user.email)
        
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == created_user.email
    
    def test_get_by_email_non_existing_user(self, db_session: Session) -> None:
        """Test getting a user by email when user doesn't exist."""
        repo = UserRepositoryImpl(db_session)
        
        retrieved_user = repo.get_by_email("nonexistent@example.com")
        
        assert retrieved_user is None
    
    def test_get_by_username_existing_user(self, db_session: Session, sample_user: User) -> None:
        """Test getting a user by username when user exists."""
        repo = UserRepositoryImpl(db_session)
        created_user = repo.create(sample_user)
        
        retrieved_user = repo.get_by_username(created_user.username)
        
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.username == created_user.username
    
    def test_get_by_username_non_existing_user(self, db_session: Session) -> None:
        """Test getting a user by username when user doesn't exist."""
        repo = UserRepositoryImpl(db_session)
        
        retrieved_user = repo.get_by_username("nonexistent")
        
        assert retrieved_user is None
    
    def test_get_all_users(self, db_session: Session) -> None:
        """Test getting all users with pagination."""
        repo = UserRepositoryImpl(db_session)
        
        # Create multiple users
        users = [
            User(email=f"user{i}@example.com", username=f"user{i}", 
                 first_name=f"User{i}", last_name="Test")
            for i in range(5)
        ]
        
        for user in users:
            repo.create(user)
        
        # Test getting all users
        all_users = repo.get_all()
        assert len(all_users) == 5
        
        # Test pagination
        paginated_users = repo.get_all(skip=2, limit=2)
        assert len(paginated_users) == 2
    
    def test_update_user_role_and_status(self, db_session: Session, sample_user: User) -> None:
        """Test updating a user's role and status."""
        repo = UserRepositoryImpl(db_session)
        created_user = repo.create(sample_user)
        
        # Update user data including status
        created_user.first_name = "Updated"
        created_user.last_name = "Name"
        created_user.role = UserRole.ADMIN
        created_user.status = UserStatus.INACTIVE  # Now we're using UserStatus!
        
        updated_user = repo.update(created_user)
        
        assert updated_user.first_name == "Updated"
        assert updated_user.last_name == "Name"
        assert updated_user.role == UserRole.ADMIN
        assert updated_user.status == UserStatus.INACTIVE
        assert updated_user.id == created_user.id
    
    def test_create_user_with_different_statuses(self, db_session: Session) -> None:
        """Test creating users with different status values."""
        repo = UserRepositoryImpl(db_session)
        
        # Test creating active user
        active_user = User(
            email="active@example.com",
            username="activeuser",
            first_name="Active",
            last_name="User",
            status=UserStatus.ACTIVE
        )
        created_active = repo.create(active_user)
        assert created_active.status == UserStatus.ACTIVE
        
        # Test creating inactive user
        inactive_user = User(
            email="inactive@example.com",
            username="inactiveuser",
            first_name="Inactive",
            last_name="User",
            status=UserStatus.INACTIVE
        )
        created_inactive = repo.create(inactive_user)
        assert created_inactive.status == UserStatus.INACTIVE
        
        # Test creating suspended user
        suspended_user = User(
            email="suspended@example.com",
            username="suspendeduser",
            first_name="Suspended",
            last_name="User",
            status=UserStatus.SUSPENDED
        )
        created_suspended = repo.create(suspended_user)
        assert created_suspended.status == UserStatus.SUSPENDED
    
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
        
        result = repo.delete(999)
        
        assert result is False
    
    def test_exists_by_email(self, db_session: Session, sample_user: User) -> None:
        """Test checking if user exists by email."""
        repo = UserRepositoryImpl(db_session)
        
        # Should not exist initially
        assert repo.exists_by_email(sample_user.email) is False
        
        # Create user
        repo.create(sample_user)
        
        # Should exist now
        assert repo.exists_by_email(sample_user.email) is True
        assert repo.exists_by_email("nonexistent@example.com") is False
    
    def test_exists_by_username(self, db_session: Session, sample_user: User) -> None:
        """Test checking if user exists by username."""
        repo = UserRepositoryImpl(db_session)
        
        # Should not exist initially
        assert repo.exists_by_username(sample_user.username) is False
        
        # Create user
        repo.create(sample_user)
        
        # Should exist now
        assert repo.exists_by_username(sample_user.username) is True
        assert repo.exists_by_username("nonexistent") is False