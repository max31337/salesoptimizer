import pytest
from pydantic import ValidationError
from uuid import uuid4

from application.dtos.auth_dto import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    UserInfoResponse
)


class TestAuthDTOs:
    """Test authentication DTOs."""
    
    def test_login_request_valid(self):
        """Test valid login request."""
        request = LoginRequest(
            email="test@example.com",
            password="testpassword123"
        )
        
        assert request.email == "test@example.com"
        assert request.password == "testpassword123"
    
    def test_login_request_invalid_email(self):
        """Test login request with invalid email."""
        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(
                email="invalid-email",
                password="testpassword123"
            )
        
        assert "value is not a valid email address" in str(exc_info.value)
    
    def test_login_request_empty_password(self):
        """Test login request with empty password."""
        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(
                email="test@example.com",
                password=""
            )
        
        assert "Password cannot be empty" in str(exc_info.value)
    
    def test_register_request_valid(self):
        """Test valid register request."""
        request = RegisterRequest(
            invitation_token="valid_token_123",
            password="strongpassword123",
            first_name="John",
            last_name="Doe"
        )
        
        assert request.invitation_token == "valid_token_123"
        assert request.password == "strongpassword123"
        assert request.first_name == "John"
        assert request.last_name == "Doe"
    
    def test_register_request_weak_password(self):
        """Test register request with weak password."""
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(
                invitation_token="valid_token_123",
                password="weak",
                first_name="John",
                last_name="Doe"
            )
        
        assert "Password must be at least 8 characters long" in str(exc_info.value)
    
    def test_register_request_empty_names(self):
        """Test register request with empty names."""
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(
                invitation_token="valid_token_123",
                password="strongpassword123",
                first_name="",
                last_name="Doe"
            )
        
        assert "Name cannot be empty" in str(exc_info.value)
    
    def test_login_response_creation(self):
        """Test login response creation."""
        user_id = uuid4()
        tenant_id = uuid4()
        
        response = LoginResponse(
            access_token="access_token_123",
            refresh_token="refresh_token_123",
            token_type="bearer",
            user_id=user_id,
            tenant_id=tenant_id,
            role="sales_rep",
            email="test@example.com",
            full_name="John Doe"
        )
        
        assert response.access_token == "access_token_123"
        assert response.refresh_token == "refresh_token_123"
        assert response.token_type == "bearer"
        assert response.user_id == user_id
        assert response.tenant_id == tenant_id
        assert response.role == "sales_rep"
        assert response.email == "test@example.com"
        assert response.full_name == "John Doe"
    
    def test_user_info_response_from_attributes(self):
        """Test user info response creation."""
        user_id = uuid4()
        tenant_id = uuid4()
        
        response = UserInfoResponse(
            id=user_id,
            email="test@example.com",
            username="testuser",
            first_name="John",
            last_name="Doe",
            role="sales_rep",
            full_name="John Doe",
            tenant_id=tenant_id,
            status="active",
            is_email_verified=True
        )
        
        assert response.id == user_id
        assert response.email == "test@example.com"
        assert response.username == "testuser"
        assert response.first_name == "John"
        assert response.last_name == "Doe"
        assert response.role == "sales_rep"
        assert response.full_name == "John Doe"
        assert response.tenant_id == tenant_id
        assert response.status == "active"
        assert response.is_email_verified is True