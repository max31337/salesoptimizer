from typing import Tuple, Optional

from domain.organization.entities.user import User
from domain.organization.value_objects.email import Email
from domain.organization.value_objects.password import Password
from domain.organization.repositories.user_repository import UserRepository
from domain.organization.exceptions.auth_exceptions import (
    AuthenticationError,
    InvalidCredentialsError,
    UserNotFoundError,
    InactiveUserError
)
from infrastructure.services.password_service import PasswordService
from infrastructure.services.jwt_service import JWTService


class AuthService:
    """Domain service for authentication operations."""
    
    def __init__(
        self,
        user_repository: UserRepository,
        password_service: PasswordService,
        jwt_service: JWTService
    ) -> None:
        self._user_repository = user_repository
        self._password_service = password_service
        self._jwt_service = jwt_service
    
    async def authenticate_user(self, email_or_username: str, password: str) -> User:
        """Authenticate a user with email/username and password."""
        if not email_or_username or not password:
            raise AuthenticationError("Email/username and password are required")
        
        # Validate password format
        try:
            Password(password)
        except ValueError as e:
            raise InvalidCredentialsError() from e
        
        # Try to find user by email first, then by username
        user: Optional[User] = None
        
        # Check if it's an email format
        try:
            email = Email(email_or_username)
            user = await self._user_repository.get_by_email(email)
        except ValueError:
            # Not an email, try username
            user = await self._user_repository.get_by_username(email_or_username)
        
        if not user:
            raise UserNotFoundError()
        
        # Check if user is active
        if not user.is_active():
            raise InactiveUserError()
        
        # Verify password
        if not user.has_password() or not user.password_hash or not self._password_service.verify_password(
            password, user.password_hash
        ):
            raise InvalidCredentialsError()
        
        # Update last login
        user.record_login()
        await self._user_repository.update(user)
        
        return user
    
    def create_tokens(self, user: User) -> Tuple[str, str]:
        """Create access and refresh tokens for user."""
        if not user.id:
            raise AuthenticationError("User ID is required to create tokens")
        
        access_token = self._jwt_service.create_access_token(
            user_id=user.id.value,
            tenant_id=user.tenant_id,
            role=user.role.value,
            email=str(user.email)
        )
        
        refresh_token = self._jwt_service.create_refresh_token(user.id.value)
        
        return access_token, refresh_token