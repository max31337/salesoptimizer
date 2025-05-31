import pytest
from application.commands.auth_command import LoginCommand


class TestLoginCommand:
    """Test LoginCommand."""
    
    def test_valid_login_command_creation(self):
        """Test creating valid login command."""
        command = LoginCommand(
            email_or_username="test@example.com",
            password="password123"
        )
        
        assert command.email_or_username == "test@example.com"
        assert command.password == "password123"
    
    def test_login_command_with_username(self):
        """Test creating login command with username."""
        command = LoginCommand(
            email_or_username="testuser",
            password="password123"
        )
        
        assert command.email_or_username == "testuser"
        assert command.password == "password123"
    
    def test_empty_email_or_username_raises_error(self):
        """Test empty email or username raises ValueError."""
        with pytest.raises(ValueError, match="Email or username is required"):
            LoginCommand(email_or_username="", password="password123")
    
    def test_whitespace_email_or_username_raises_error(self):
        """Test whitespace-only email or username raises ValueError."""
        with pytest.raises(ValueError, match="Email or username is required"):
            LoginCommand(email_or_username="   ", password="password123")
    
    def test_empty_password_raises_error(self):
        """Test empty password raises ValueError."""
        with pytest.raises(ValueError, match="Password is required"):
            LoginCommand(email_or_username="test@example.com", password="")
    
    def test_whitespace_password_raises_error(self):
        """Test whitespace-only password raises ValueError."""
        with pytest.raises(ValueError, match="Password is required"):
            LoginCommand(email_or_username="test@example.com", password="   ")
    
    def test_command_immutability(self):
        """Test command is immutable."""
        command = LoginCommand(
            email_or_username="test@example.com",
            password="password123"
        )
        
        with pytest.raises(AttributeError):
            command.email_or_username = "new@example.com"
        
        with pytest.raises(AttributeError):
            command.password = "newpassword"