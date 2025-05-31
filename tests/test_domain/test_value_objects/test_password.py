import pytest
from domain.organization.value_objects.password import Password


class TestPassword:
    """Test Password value object."""
    
    def test_valid_password_creation(self):
        """Test creating valid password."""
        password = Password("ValidPassword123!")
        assert str(password) == "ValidPassword123!"
        assert password.value == "ValidPassword123!"
    
    def test_minimum_length_password(self):
        """Test password with minimum length."""
        password = Password("12345678")  # 8 characters
        assert len(password.value) == 8
    
    def test_empty_password_raises_error(self):
        """Test empty password raises ValueError."""
        with pytest.raises(ValueError, match="Password cannot be empty"):
            Password("")
    
    def test_short_password_raises_error(self):
        """Test password shorter than 8 characters raises error."""
        short_passwords = ["1", "12", "123", "1234", "12345", "123456", "1234567"]
        
        for short_password in short_passwords:
            with pytest.raises(ValueError, match="Password must be at least 8 characters long"):
                Password(short_password)
    
    def test_password_equality(self):
        """Test password equality."""
        password1 = Password("SamePassword123!")
        password2 = Password("SamePassword123!")
        assert password1 == password2
    
    def test_password_immutability(self):
        """Test password is immutable."""
        password = Password("TestPassword123!")
        with pytest.raises(AttributeError):
            password.value = "NewPassword123!"