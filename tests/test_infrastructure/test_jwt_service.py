import pytest
import os
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from unittest.mock import patch
import time

from infrastructure.services.jwt_service import JWTService


class TestJWTService:
    
    @pytest.fixture
    def jwt_service(self) -> JWTService:
        """Create a JWT service with test configuration."""
        with patch.dict(os.environ, {
            'JWT_SECRET_KEY': 'test-secret-key-at-least-32-characters-long-for-testing-purposes',
            'JWT_ALGORITHM': 'HS256',
            'JWT_EXPIRE_MINUTES': '30',
            'REFRESH_TOKEN_EXPIRE_DAYS': '7'
        }):
            return JWTService()
    
    def test_jwt_service_initialization(self, jwt_service: JWTService) -> None:
        """Test JWT service initialization with valid config."""
        assert jwt_service.secret_key == 'test-secret-key-at-least-32-characters-long-for-testing-purposes'
        assert jwt_service.algorithm == 'HS256'
        assert jwt_service.access_token_expire_minutes == 30
        assert jwt_service.refresh_token_expire_days == 7
    
    def test_jwt_service_initialization_short_secret(self) -> None:
        """Test JWT service initialization with short secret key."""
        with patch.dict(os.environ, {'JWT_SECRET_KEY': 'short'}):
            with pytest.raises(ValueError, match="JWT_SECRET_KEY must be at least 32 characters long"):
                JWTService()
    
    def test_jwt_service_initialization_no_secret(self) -> None:
        """Test JWT service initialization with no secret key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="JWT_SECRET_KEY must be set"):
                JWTService()
    
    def test_create_access_token(self, jwt_service: JWTService) -> None:
        """Test creating an access token."""
        user_id = uuid4()
        tenant_id = uuid4()
        role = "sales_rep"
        email = "test@example.com"
        
        token = jwt_service.create_access_token(user_id, tenant_id, role, email)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Verify token can be decoded
        payload = jwt_service.verify_token(token)
        assert payload is not None
        assert payload["sub"] == str(user_id)
        assert payload["tenant_id"] == str(tenant_id)
        assert payload["role"] == role
        assert payload["email"] == email
        assert payload["type"] == "access"
    
    def test_create_access_token_no_tenant(self, jwt_service: JWTService) -> None:
        """Test creating access token for super admin (no tenant)."""
        user_id = uuid4()
        role = "super_admin"
        email = "admin@example.com"
        
        token = jwt_service.create_access_token(user_id, None, role, email)
        
        payload = jwt_service.verify_token(token)
        assert payload is not None
        assert payload["tenant_id"] is None
        assert payload["role"] == role
    
    def test_create_refresh_token(self, jwt_service: JWTService) -> None:
        """Test creating a refresh token."""
        user_id = uuid4()
        
        token = jwt_service.create_refresh_token(user_id)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Verify token can be decoded
        payload = jwt_service.verify_token(token)
        assert payload is not None
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "refresh"
        assert "tenant_id" not in payload
        assert "role" not in payload
    
    def test_create_invitation_token(self, jwt_service: JWTService) -> None:
        """Test creating an invitation token."""
        email = "invited@example.com"
        tenant_id = uuid4()
        role = "sales_rep"
        
        token = jwt_service.create_invitation_token(email, tenant_id, role)
        
        payload = jwt_service.verify_token(token)
        assert payload is not None
        assert payload["email"] == email
        assert payload["tenant_id"] == str(tenant_id)
        assert payload["role"] == role
        assert payload["type"] == "invitation"
    
    def test_verify_token_valid(self, jwt_service: JWTService) -> None:
        """Test verifying a valid token."""
        user_id = uuid4()
        tenant_id = uuid4()
        token = jwt_service.create_access_token(user_id, tenant_id, "sales_rep", "test@example.com")
        
        payload = jwt_service.verify_token(token)
        
        assert payload is not None
        assert payload["sub"] == str(user_id)
    
    def test_verify_token_invalid(self, jwt_service: JWTService) -> None:
        """Test verifying an invalid token."""
        invalid_token = "invalid.token.here"
        
        payload = jwt_service.verify_token(invalid_token)
        
        assert payload is None
    
    def test_verify_token_with_bearer_prefix(self, jwt_service: JWTService) -> None:
        """Test verifying token with Bearer prefix."""
        user_id = uuid4()
        token = jwt_service.create_access_token(user_id, None, "sales_rep", "test@example.com")
        bearer_token = f"Bearer {token}"
        
        payload = jwt_service.verify_token(bearer_token)
        
        assert payload is not None
        assert payload["sub"] == str(user_id)
    
    def test_verify_token_empty_string(self, jwt_service: JWTService) -> None:
        """Test verifying empty token."""
        payload = jwt_service.verify_token("")
        assert payload is None
    
    def test_decode_token_without_verification(self, jwt_service: JWTService) -> None:
        """Test decoding token without verification."""
        user_id = uuid4()
        token = jwt_service.create_access_token(user_id, None, "sales_rep", "test@example.com")
        
        payload = jwt_service.decode_token_without_verification(token)
        
        assert payload is not None
        assert payload["sub"] == str(user_id)
    
    def test_get_token_expiry(self, jwt_service: JWTService) -> None:
        """Test getting token expiry time."""
        user_id = uuid4()
        token = jwt_service.create_access_token(user_id, None, "sales_rep", "test@example.com")
        
        expiry = jwt_service.get_token_expiry(token)
        
        assert expiry is not None
        assert isinstance(expiry, datetime)
        assert expiry > datetime.now(timezone.utc)
    
    def test_is_token_expired(self, jwt_service: JWTService) -> None:
        """Test checking if token is expired."""
        # Valid token
        user_id = uuid4()
        token = jwt_service.create_access_token(user_id, None, "sales_rep", "test@example.com")
        
        assert jwt_service.is_token_expired(token) is False
        
        # Invalid token
        assert jwt_service.is_token_expired("invalid.token") is True
    
    def test_extract_user_id_from_token(self, jwt_service: JWTService) -> None:
        """Test extracting user ID from token."""
        user_id = uuid4()
        token = jwt_service.create_access_token(user_id, None, "sales_rep", "test@example.com")
        
        extracted_id = jwt_service.extract_user_id_from_token(token)
        
        assert extracted_id == str(user_id)
    
    def test_create_invitation_token_custom_expiry(self, jwt_service: JWTService) -> None:
        """Test creating invitation token with custom expiry."""
        email = "test@example.com"
        tenant_id = uuid4()
        role = "sales_rep"
        custom_hours = 72
        
        # Use a time without microseconds to avoid precision issues
        base_time = datetime.now(timezone.utc).replace(microsecond=0)
        
        with patch('infrastructure.services.jwt_service.datetime') as mock_datetime:
            mock_datetime.now.return_value = base_time
            mock_datetime.fromtimestamp = datetime.fromtimestamp
            
            token = jwt_service.create_invitation_token(email, tenant_id, role)
        
        payload = jwt_service.verify_token(token)
        assert payload is not None
        
        # Check expiry is approximately correct (allow 2 second tolerance)
        expiry = jwt_service.get_token_expiry(token)
        assert expiry is not None
        
        expected_expiry = base_time + timedelta(hours=custom_hours)
        time_diff = abs((expiry - expected_expiry).total_seconds())
        assert time_diff <= 2  # Within 2 seconds tolerance
    
    def test_verify_token_expired(self) -> None:
        """Test verifying an expired token."""
        # Create JWT service with very short expiry
        with patch.dict(os.environ, {
            'JWT_SECRET_KEY': 'test-secret-key-at-least-32-characters-long-for-testing-purposes',
            'JWT_EXPIRE_MINUTES': '0'  # Immediate expiry
        }):
            jwt_service = JWTService()
            user_id = uuid4()
            
            # Create token that expires immediately
            token = jwt_service.create_access_token(user_id, None, "sales_rep", "test@example.com")
            
            # Small delay to ensure expiry
            time.sleep(0.1)
            
            payload = jwt_service.verify_token(token)
            assert payload is None
    
    def test_create_invitation_token_default_expiry(self, jwt_service: JWTService) -> None:
        """Test creating invitation token with default expiry."""
        email = "test@example.com"
        tenant_id = uuid4()
        role = "sales_rep"
        
        # Use a time without microseconds to avoid precision issues
        base_time = datetime.now(timezone.utc).replace(microsecond=0)
        
        with patch('infrastructure.services.jwt_service.datetime') as mock_datetime:
            mock_datetime.now.return_value = base_time
            mock_datetime.fromtimestamp = datetime.fromtimestamp
            
            token = jwt_service.create_invitation_token(email, tenant_id, role)
        
        payload = jwt_service.verify_token(token)
        assert payload is not None
        
        expiry = jwt_service.get_token_expiry(token)
        assert expiry is not None
        
        # Should expire in 48 hours (default) - allow 2 second tolerance
        expected_expiry = base_time + timedelta(hours=48)
        time_diff = abs((expiry - expected_expiry).total_seconds())
        assert time_diff <= 2  # Within 2 seconds tolerance
    
    def test_decode_token_without_verification_invalid(self, jwt_service: JWTService) -> None:
        """Test decoding invalid token without verification."""
        payload = jwt_service.decode_token_without_verification("invalid.token")
        assert payload is None
    
    def test_get_token_expiry_invalid_token(self, jwt_service: JWTService) -> None:
        """Test getting expiry of invalid token."""
        expiry = jwt_service.get_token_expiry("invalid.token")
        assert expiry is None
    
    def test_extract_user_id_from_invalid_token(self, jwt_service: JWTService) -> None:
        """Test extracting user ID from invalid token."""
        user_id = jwt_service.extract_user_id_from_token("invalid.token")
        assert user_id is None
    
    def test_verify_token_malformed(self, jwt_service: JWTService) -> None:
        """Test verifying malformed token."""
        malformed_tokens = [
            "not.a.jwt",
            "Bearer",
            "Bearer ",
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.invalid",
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0In0.invalid"
        ]
        
        for token in malformed_tokens:
            payload = jwt_service.verify_token(token)
            assert payload is None, f"Token {token} should be invalid"
    
    def test_create_invitation_token_expiry_precision(self, jwt_service: JWTService) -> None:
        """Test that invitation token expiry works correctly despite timestamp precision."""
        email = "test@example.com"
        tenant_id = uuid4()
        role = "sales_rep"
        custom_hours = 24
        
        # Create token
        token = jwt_service.create_invitation_token(email, tenant_id, role, custom_hours)
        
        # Verify the token is valid
        payload = jwt_service.verify_token(token)
        assert payload is not None
        assert payload["email"] == email
        assert payload["type"] == "invitation"
        
        # Check that expiry is reasonable (within expected range)
        expiry = jwt_service.get_token_expiry(token)
        assert expiry is not None
        
        now = datetime.now(timezone.utc)
        min_expiry = now + timedelta(hours=custom_hours - 1)  # 1 hour tolerance
        max_expiry = now + timedelta(hours=custom_hours + 1)  # 1 hour tolerance
        
        assert min_expiry <= expiry <= max_expiry
    
    def test_token_roundtrip_consistency(self, jwt_service: JWTService) -> None:
        """Test that tokens can be created and verified consistently."""
        from typing import Any, Dict, List
        test_cases: List[Dict[str, Any]] = [
            {
                "email": "user1@example.com",
                "tenant_id": uuid4(),
                "role": "sales_rep",
                "expires_hours": 12
            },
            {
                "email": "user2@example.com", 
                "tenant_id": uuid4(),
                "role": "manager",
                "expires_hours": 48
            },
            {
                "email": "user3@example.com",
                "tenant_id": uuid4(), 
                "role": "admin",
                "expires_hours": 168  # 1 week
            }
        ]
        
        for case in test_cases:
            token = jwt_service.create_invitation_token(
                case["email"], 
                case["tenant_id"], 
                case["role"]
            )
            
            # Verify token
            payload = jwt_service.verify_token(token)
            assert payload is not None
            assert payload["email"] == case["email"]
            assert payload["tenant_id"] == str(case["tenant_id"])
            assert payload["role"] == case["role"]
            assert payload["type"] == "invitation"
            
            # Check that token is not expired
            assert not jwt_service.is_token_expired(token)