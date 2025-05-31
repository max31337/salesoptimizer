import pytest
from infrastructure.services.password_service import PasswordService


class TestPasswordService:
    """Test PasswordService."""
    
    @pytest.fixture
    def password_service(self):
        """Create password service instance."""
        return PasswordService()
    
    def test_hash_password_success(self, password_service: PasswordService):
        """Test successful password hashing."""
        password = "TestPassword123!"
        hashed = password_service.hash_password(password)
        
        assert hashed is not None
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != password  # Should be different from original
        assert hashed.startswith("$2b$")  # bcrypt format
    
    def test_hash_password_empty_raises_error(self, password_service: PasswordService):
        """Test hashing empty password raises error."""
        with pytest.raises(ValueError, match="Password cannot be empty"):
            password_service.hash_password("")
    
    def test_verify_password_success(self, password_service: PasswordService):
        """Test successful password verification."""
        password = "TestPassword123!"
        hashed = password_service.hash_password(password)
        
        assert password_service.verify_password(password, hashed) is True
    
    def test_verify_password_wrong_password(self, password_service: PasswordService):
        """Test password verification with wrong password."""
        password = "TestPassword123!"
        wrong_password = "WrongPassword123!"
        hashed = password_service.hash_password(password)
        
        assert password_service.verify_password(wrong_password, hashed) is False
    
    def test_verify_password_empty_password_returns_false(self, password_service: PasswordService):
        """Test password verification with empty password returns False."""
        hashed = password_service.hash_password("TestPassword123!")
        
        assert password_service.verify_password("", hashed) is False
    
    def test_verify_password_empty_hash_returns_false(self, password_service: PasswordService):
        """Test password verification with empty hash returns False."""
        assert password_service.verify_password("TestPassword123!", "") is False
    
    def test_verify_password_invalid_hash_returns_false(self, password_service: PasswordService):
        """Test password verification with invalid hash returns False."""
        invalid_hash = "not_a_valid_bcrypt_hash"
        
        assert password_service.verify_password("TestPassword123!", invalid_hash) is False
    
    def test_hash_consistency(self, password_service: PasswordService):
        """Test that same password produces different hashes due to salt."""
        password = "TestPassword123!"
        hash1 = password_service.hash_password(password)
        hash2 = password_service.hash_password(password)
        
        # Different hashes due to different salts
        assert hash1 != hash2
        
        # But both should verify correctly
        assert password_service.verify_password(password, hash1) is True
        assert password_service.verify_password(password, hash2) is True