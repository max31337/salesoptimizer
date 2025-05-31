import pytest
from uuid import UUID, uuid4
from domain.organization.value_objects.user_id import UserId


class TestUserId:
    """Test UserId value object."""
    
    def test_valid_user_id_creation(self):
        """Test creating valid user ID."""
        uuid_val = uuid4()
        user_id = UserId(uuid_val)
        assert user_id.value == uuid_val
        assert str(user_id) == str(uuid_val)
    
    def test_generate_new_user_id(self):
        """Test generating new user ID."""
        user_id = UserId.generate()
        assert isinstance(user_id.value, UUID)
        assert user_id.value is not None
    
    def test_from_string_valid_uuid(self):
        """Test creating user ID from valid UUID string."""
        uuid_str = str(uuid4())
        user_id = UserId.from_string(uuid_str)
        assert str(user_id) == uuid_str
    
    def test_from_string_invalid_uuid_raises_error(self):
        """Test creating user ID from invalid UUID string raises error."""
        with pytest.raises(ValueError, match="Invalid UUID format"):
            UserId.from_string("invalid-uuid")
    
    def test_non_uuid_value_raises_error(self):
        """Test non-UUID value raises ValueError."""
        with pytest.raises(ValueError, match="User ID must be a valid UUID"):
            UserId("not-a-uuid")  # type: ignore
    
    def test_user_id_equality(self):
        """Test user ID equality."""
        uuid_val = uuid4()
        user_id1 = UserId(uuid_val)
        user_id2 = UserId(uuid_val)
        assert user_id1 == user_id2
    
    def test_user_id_immutability(self):
        """Test user ID is immutable."""
        user_id = UserId(uuid4())
        with pytest.raises(AttributeError):
            user_id.value = uuid4()