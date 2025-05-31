import pytest
from domain.organization.value_objects.email import Email


class TestEmail:
    """Test Email value object."""
    
    def test_valid_email_creation(self):
        """Test creating valid email."""
        email = Email("test@example.com")
        assert str(email) == "test@example.com"
        assert email.value == "test@example.com"
    
    def test_email_with_plus_sign(self):
        """Test email with plus sign."""
        email = Email("test+tag@example.com")
        assert str(email) == "test+tag@example.com"
    
    def test_email_with_subdomain(self):
        """Test email with subdomain."""
        email = Email("user@mail.example.com")
        assert str(email) == "user@mail.example.com"
    
    def test_empty_email_raises_error(self):
        """Test empty email raises ValueError."""
        with pytest.raises(ValueError, match="Email cannot be empty"):
            Email("")
    
    def test_invalid_email_format_raises_error(self):
        """Test invalid email format raises ValueError."""
        invalid_emails = [
            "invalid",
            "invalid@",
            "@example.com",
            "invalid@.com",
            "invalid.example.com",
            "invalid@example",
            "invalid@@example.com"
        ]
        
        for invalid_email in invalid_emails:
            with pytest.raises(ValueError, match="Invalid email format"):
                Email(invalid_email)
    
    def test_email_equality(self):
        """Test email equality."""
        email1 = Email("test@example.com")
        email2 = Email("test@example.com")
        assert email1 == email2
    
    def test_email_immutability(self):
        """Test email is immutable."""
        email = Email("test@example.com")
        with pytest.raises(AttributeError):
            email.value = "new@example.com"