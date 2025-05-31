import pytest
from uuid import uuid4
from uuid import UUID
from infrastructure.services.jwt_service import JWTService


class TestJWTService:
    """Test JWTService."""
    
    @pytest.fixture
    def jwt_service(self):
        """Create JWT service instance."""
        return JWTService()

    @pytest.fixture
    def sample_user_data(self) -> dict[str, str | UUID | None]:
        """Sample user data for token creation."""
        return {
            "user_id": uuid4(),         # UUID
            "tenant_id": uuid4(),       # UUID
            "role": "sales_rep",        # str
            "email": "test@example.com" # str
        }

    def test_create_refresh_token_success(self, jwt_service: JWTService, sample_user_data: dict[str, str | UUID | None]):
        """Test successful refresh token creation."""
        token = jwt_service.create_refresh_token(
            sample_user_data["user_id"] if isinstance(sample_user_data["user_id"], UUID) else UUID(str(sample_user_data["user_id"]))
        )

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
        assert token.count('.') == 2  # JWT format
        
        payload = jwt_service.verify_token(token)
        
        assert payload is not None
        assert payload["sub"] == str(sample_user_data["user_id"])
        assert payload["type"] == "refresh"
    
    def test_verify_invalid_token_returns_none(self, jwt_service: JWTService):
        """Test verifying invalid token returns None."""
        invalid_token = "invalid.token.here"
        
        payload = jwt_service.verify_token(invalid_token)
        
        assert payload is None

    def test_verify_malformed_token_returns_none(self, jwt_service: JWTService):
        """Test verifying malformed token returns None."""
        malformed_token = "not_a_jwt_token"
        
        payload = jwt_service.verify_token(malformed_token)

        assert payload is None

    def test_decode_token_without_verification(self, jwt_service: JWTService, sample_user_data: dict[str, str | UUID | None]):
        """Test decoding token without verification."""
        token = jwt_service.create_access_token(
            sample_user_data["user_id"] if isinstance(sample_user_data["user_id"], UUID) else UUID(str(sample_user_data["user_id"])),
            sample_user_data["tenant_id"] if isinstance(sample_user_data["tenant_id"], UUID) or sample_user_data["tenant_id"] is None else UUID(str(sample_user_data["tenant_id"])),
            str(sample_user_data["role"]),
            str(sample_user_data["email"])
        )

        payload = jwt_service.decode_token(token)

        assert payload is not None
        assert payload["sub"] == str(sample_user_data["user_id"])
        assert payload["email"] == sample_user_data["email"]

    def test_access_token_contains_required_fields(self, jwt_service: JWTService, sample_user_data: dict[str, str | UUID | None]):
        """Test access token contains all required fields."""
        tenant_id = sample_user_data["tenant_id"]
        if tenant_id is not None and not isinstance(tenant_id, UUID):
            tenant_id = UUID(str(tenant_id))
        user_id = sample_user_data["user_id"]
        if user_id is None:
            raise ValueError("user_id cannot be None")
        if not isinstance(user_id, UUID):
            user_id = UUID(str(user_id))
        token = jwt_service.create_access_token(
            user_id=user_id,
            tenant_id=tenant_id,
            role=str(sample_user_data["role"]),
            email=str(sample_user_data["email"])
        )
        
        payload = jwt_service.verify_token(token)
        
        assert payload is not None
        required_fields = ["sub", "email", "role", "tenant_id", "type", "exp", "iat"]
        for field in required_fields:
            assert field in payload
    
    def test_refresh_token_contains_required_fields(self, jwt_service: JWTService, sample_user_data: dict[str, str | UUID | None]):
        """Test refresh token contains required fields."""
        user_id = sample_user_data["user_id"]
        if user_id is None:
            raise ValueError("user_id cannot be None")
        if not isinstance(user_id, UUID):
            user_id = UUID(str(user_id))
        token = jwt_service.create_refresh_token(user_id)
        
        payload = jwt_service.verify_token(token)
        
        required_fields = ["sub", "type", "exp", "iat"]
        assert payload is not None
        for field in required_fields:
            assert field in payload
    
    def test_access_token_with_none_tenant_id(self, jwt_service: JWTService, sample_user_data: dict[str, str | UUID | None]):
        """Test access token creation with None tenant_id."""
        user_id = sample_user_data["user_id"]
        if user_id is None:
            raise ValueError("user_id cannot be None")
        if not isinstance(user_id, UUID):
            user_id = UUID(str(user_id))
        token = jwt_service.create_access_token(
            user_id=user_id,
            tenant_id=None,
            role=str(sample_user_data["role"]),
            email=str(sample_user_data["email"])
        )
        
        payload = jwt_service.verify_token(token)
        
        assert payload is not None
        assert payload["tenant_id"] is None