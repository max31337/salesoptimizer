from typing import Optional, Tuple, Dict, Any
from uuid import UUID

from domain.entities.user import User, UserRole, UserStatus
from domain.repositories.user_repository import UserRepository
from infrastructure.services.password_service import PasswordService
from infrastructure.services.jwt_service import JWTService

class AuthenticationError(Exception):
    """Custom exception for authentication errors."""
    pass

class AuthService:
    """Service for handling authentication operations."""
    
    def __init__(
        self, 
        user_repository: UserRepository, 
        password_service: PasswordService, 
        jwt_service: JWTService
    ) -> None:
        self.user_repository: UserRepository = user_repository
        self.password_service: PasswordService = password_service
        self.jwt_service: JWTService = jwt_service
    
    def authenticate_user(self, email_or_username: str, password: str) -> User:
        """Authenticate a user with email/username and password."""
        if not email_or_username or not password:
            raise AuthenticationError("Email/username and password are required")
        
        # Try to find user by email first, then by username
        user: Optional[User] = self.user_repository.get_by_email(email_or_username)
        if not user:
            user = self.user_repository.get_by_username(email_or_username)
        
        if not user:
            raise AuthenticationError("Invalid credentials")
        
        # Check if user is active
        if user.status != UserStatus.ACTIVE:
            raise AuthenticationError("Account is not active")
        
        # Verify password
        if not user.password_hash or not self.password_service.verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid credentials")
        
        # Update last login
        user.record_login()
        self.user_repository.update(user)
        
        return user
    
    def complete_registration(
        self, 
        invitation_token: str, 
        password: str, 
        first_name: str, 
        last_name: str
    ) -> User:
        """Complete user registration using invitation token."""
        if not invitation_token or not password or not first_name or not last_name:
            raise AuthenticationError("All fields are required")
        
        # Verify invitation token
        token_payload: Optional[Dict[str, Any]] = self.jwt_service.verify_token(invitation_token)
        if not token_payload or token_payload.get("type") != "invitation":
            raise AuthenticationError("Invalid or expired invitation token")
        
        email: str = token_payload.get("email", "")
        tenant_id_str: Optional[str] = token_payload.get("tenant_id")
        role_str: str = token_payload.get("role", "sales_rep")
        
        if not email:
            raise AuthenticationError("Invalid invitation token - missing email")
        
        # Check if user already exists
        if self.user_repository.exists_by_email(email):
            raise AuthenticationError("User already exists with this email")
        
        # Parse tenant_id
        tenant_id: Optional[UUID] = None
        if tenant_id_str:
            try:
                tenant_id = UUID(tenant_id_str)
            except ValueError:
                raise AuthenticationError("Invalid tenant ID in invitation token")
        
        # Parse role
        try:
            role: UserRole = UserRole(role_str)
        except ValueError:
            role = UserRole.SALES_REP
        
        # Hash password
        password_hash: str = self.password_service.hash_password(password)
        
        # Create user
        user: User = User(
            email=email,
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            password_hash=password_hash,
            role=role,
            status=UserStatus.ACTIVE,
            tenant_id=tenant_id,
            is_email_verified=True  # Email is verified through invitation
        )
        
        created_user: User = self.user_repository.create(user)
        return created_user
    
    def create_user_tokens(self, user: User) -> Tuple[str, str]:
        """Create access and refresh tokens for user."""
        if not user.id:
            raise AuthenticationError("User ID is required to create tokens")
        
        access_token: str = self.jwt_service.create_access_token(
            user_id=user.id,
            tenant_id=user.tenant_id,
            role=user.role.value,
            email=user.email
        )
        
        refresh_token: str = self.jwt_service.create_refresh_token(user.id)
        
        return access_token, refresh_token
    
    def refresh_user_tokens(self, refresh_token: str) -> Tuple[str, str]:
        """Refresh user tokens using refresh token."""
        if not refresh_token:
            raise AuthenticationError("Refresh token is required")
        
        # Verify refresh token
        token_payload: Optional[Dict[str, Any]] = self.jwt_service.verify_token(refresh_token)
        if not token_payload or token_payload.get("type") != "refresh":
            raise AuthenticationError("Invalid refresh token")
        
        user_id_str: Optional[str] = token_payload.get("sub")
        if not user_id_str:
            raise AuthenticationError("Invalid refresh token - missing user ID")
        
        try:
            user_id: UUID = UUID(user_id_str)
        except ValueError:
            raise AuthenticationError("Invalid user ID in refresh token")
        
        # Get user
        user: Optional[User] = self.user_repository.get_by_id(user_id)
        if not user or user.status != UserStatus.ACTIVE:
            raise AuthenticationError("User not found or inactive")
        
        # Create new tokens
        return self.create_user_tokens(user)
    
    def verify_invitation_token(self, invitation_token: str) -> Dict[str, Any]:
        """Verify invitation token and return payload."""
        if not invitation_token:
            raise AuthenticationError("Invitation token is required")
        
        token_payload: Optional[Dict[str, Any]] = self.jwt_service.verify_token(invitation_token)
        if not token_payload or token_payload.get("type") != "invitation":
            raise AuthenticationError("Invalid or expired invitation token")
        
        return token_payload