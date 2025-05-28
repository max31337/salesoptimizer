import pytest
import string
from infrastructure.services.password_service import PasswordService


class TestPasswordService:
    
    @pytest.fixture
    def password_service(self) -> PasswordService:
        """Create a password service instance."""
        return PasswordService()
    
    def test_hash_password(self, password_service: PasswordService) -> None:
        """Test password hashing."""
        password = "test_password_123"
        
        hashed = password_service.hash_password(password)
        
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != password
        assert hashed.startswith("$2b$")  # bcrypt format
    
    def test_hash_password_different_results(self, password_service: PasswordService) -> None:
        """Test that hashing the same password twice gives different results."""
        password = "test_password_123"
        
        hash1 = password_service.hash_password(password)
        hash2 = password_service.hash_password(password)
        
        assert hash1 != hash2
    
    def test_verify_password_correct(self, password_service: PasswordService) -> None:
        """Test verifying correct password."""
        password = "test_password_123"
        hashed = password_service.hash_password(password)
        
        result = password_service.verify_password(password, hashed)
        
        assert result is True
    
    def test_verify_password_incorrect(self, password_service: PasswordService) -> None:
        """Test verifying incorrect password."""
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = password_service.hash_password(password)
        
        result = password_service.verify_password(wrong_password, hashed)
        
        assert result is False
    
    def test_verify_password_empty(self, password_service: PasswordService) -> None:
        """Test verifying empty password."""
        password = "test_password_123"
        hashed = password_service.hash_password(password)
        
        result = password_service.verify_password("", hashed)
        
        assert result is False
    
    def test_generate_temp_password_default_length(self, password_service: PasswordService) -> None:
        """Test generating temporary password with default length."""
        temp_password = password_service.generate_temp_password()
        
        assert isinstance(temp_password, str)
        assert len(temp_password) == 12
    
    def test_generate_temp_password_custom_length(self, password_service: PasswordService) -> None:
        """Test generating temporary password with custom length."""
        length = 16
        temp_password = password_service.generate_temp_password(length)
        
        assert len(temp_password) == length
    
    def test_generate_temp_password_contains_valid_chars(self, password_service: PasswordService) -> None:
        """Test that generated password contains only valid characters."""
        temp_password = password_service.generate_temp_password()
        
        valid_chars = string.ascii_letters + string.digits + "!@#$%^&*"
        assert all(char in valid_chars for char in temp_password)
    
    def test_generate_temp_password_uniqueness(self, password_service: PasswordService) -> None:
        """Test that generated passwords are unique."""
        passwords = [password_service.generate_temp_password() for _ in range(10)]
        
        assert len(set(passwords)) == len(passwords)  # All unique
    
    def test_generate_temp_password_complexity(self, password_service: PasswordService) -> None:
        """Test that generated password has good complexity."""
        temp_password = password_service.generate_temp_password(20)
        
        # Should contain at least some variety
        has_upper = any(c.isupper() for c in temp_password)
        has_lower = any(c.islower() for c in temp_password)
        has_digit = any(c.isdigit() for c in temp_password)
        
        # At least 2 of the 3 types should be present
        assert sum([has_upper, has_lower, has_digit]) >= 2