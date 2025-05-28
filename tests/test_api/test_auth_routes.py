import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import uuid4, UUID
from typing import Dict, Any

from domain.entities.user import User, UserRole, UserStatus
from infrastructure.repositories.user_repository_impl import UserRepositoryImpl
from infrastructure.services.password_service import PasswordService
from infrastructure.services.jwt_service import JWTService


class TestAuthRoutes:
    
    @pytest.fixture
    def password_service(self) -> PasswordService:
        return PasswordService()
    
    @pytest.fixture
    def jwt_service(self) -> JWTService:
        return JWTService()
    
    @pytest.fixture
    def active_user(self, db_session: Session, password_service: PasswordService) -> User:
        """Create an active user for testing."""
        repo: UserRepositoryImpl = UserRepositoryImpl(db_session)
        
        user: User = User(
            email="testuser@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            phone="+1234567890",
            password_hash=password_service.hash_password("testpassword123"),
            role=UserRole.SALES_REP,
            status=UserStatus.ACTIVE,
            is_email_verified=True
        )
        
        return repo.create(user)
    
    def test_login_success(self, client: TestClient, active_user: User) -> None:
        """Test successful login."""
        form_data: Dict[str, str] = {
            "username": active_user.email,
            "password": "testpassword123"
        }
        
        response = client.post("/api/v1/auth/login", data=form_data)
        
        assert response.status_code == status.HTTP_200_OK
        data: Dict[str, Any] = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["email"] == active_user.email
        assert data["user_id"] == str(active_user.id)
    
    def test_login_invalid_credentials(self, client: TestClient, active_user: User) -> None:
        """Test login with invalid credentials."""
        form_data: Dict[str, str] = {
            "username": active_user.email,
            "password": "wrongpassword"
        }
        
        response = client.post("/api/v1/auth/login", data=form_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        error_detail: str = response.json()["detail"]
        assert "Invalid credentials" in error_detail or "Invalid email or password" in error_detail
    
    def test_login_nonexistent_user(self, client: TestClient) -> None:
        """Test login with nonexistent user."""
        form_data: Dict[str, str] = {
            "username": "nonexistent@example.com",
            "password": "password123"
        }
        
        response = client.post("/api/v1/auth/login", data=form_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_register_success(self, client: TestClient, jwt_service: JWTService) -> None:
        """Test successful registration with valid invitation token."""
        tenant_id: UUID = uuid4()
        invitation_token: str = jwt_service.create_invitation_token(
            email="invited@example.com",
            tenant_id=tenant_id,
            role="sales_rep"
        )
        
        register_data: Dict[str, str] = {
            "invitation_token": invitation_token,
            "first_name": "Invited",
            "last_name": "User",
            "password": "newpassword123"
        }
        
        response = client.post("/api/v1/auth/register", json=register_data)
        
        assert response.status_code == status.HTTP_200_OK
        data: Dict[str, Any] = response.json()
        assert data["message"] == "Registration completed successfully"
        assert "access_token" in data
        assert "user_id" in data
    
    def test_refresh_token_success(
        self, 
        client: TestClient, 
        active_user: User, 
        jwt_service: JWTService
    ) -> None:
        """Test successful token refresh."""
        assert active_user.id is not None, "active_user.id must not be None"
        refresh_token: str = jwt_service.create_refresh_token(active_user.id)
        
        response = client.post(
            "/api/v1/auth/refresh", 
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data: Dict[str, Any] = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_get_current_user_info(
        self, 
        client: TestClient, 
        active_user: User, 
        jwt_service: JWTService
    ) -> None:
        """Test getting current user info."""
        assert active_user.id is not None, "active_user.id must not be None"
        access_token: str = jwt_service.create_access_token(
            user_id=active_user.id,
            tenant_id=active_user.tenant_id,
            role=active_user.role.value,
            email=active_user.email
        )
        
        headers: Dict[str, str] = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data: Dict[str, Any] = response.json()
        assert data["email"] == active_user.email
        assert data["role"] == active_user.role.value