from typing import Tuple, Optional, Dict, Any
from uuid import uuid4

from domain.organization.entities.user import User, UserRole, UserStatus
from domain.organization.value_objects.email import Email
from domain.organization.value_objects.user_id import UserId
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
    
    async def authenticate_oauth_user(
        self, 
        provider: str, 
        user_info: Dict[str, Any]
    ) -> Tuple[User, bool]:
        """Authenticate or create user via OAuth."""
        email_str = user_info.get('email')
        if not email_str:
            raise AuthenticationError("Email is required for OAuth authentication")
        
        try:
            email = Email(email_str)
        except ValueError as e:
            raise AuthenticationError(f"Invalid email format: {email_str}") from e
        
        # Try to find existing user
        user = await self._user_repository.get_by_email(email)
        is_new_user = False
        
        if not user:
            # Create new user
            is_new_user = True
            user = self._create_oauth_user(provider, user_info, email)
            user = await self._user_repository.save(user)
        else:
            # Check if user is active
            if not user.is_active():
                raise InactiveUserError()
            
            # Update last login
            user.record_login()
            user = await self._user_repository.update(user)
        
        return user, is_new_user
    
    def _create_oauth_user(
        self, 
        provider: str, 
        user_info: Dict[str, Any], 
        email: Email
    ) -> User:
        """Create a new user from OAuth information."""
        # Extract name information
        if provider == "google":
            first_name = user_info.get('given_name', '')
            last_name = user_info.get('family_name', '')
            full_name = user_info.get('name', f"{first_name} {last_name}".strip())
        elif provider == "github":
            full_name = user_info.get('name', '')
            username = user_info.get('login', '')
            first_name = full_name.split()[0] if full_name else username
            last_name = ' '.join(full_name.split()[1:]) if len(full_name.split()) > 1 else ''
        elif provider == "microsoft":
            first_name = user_info.get('given_name', '')
            last_name = user_info.get('family_name', '')
            full_name = user_info.get('name', f"{first_name} {last_name}".strip())
        else:
            first_name = ''
            last_name = ''
            full_name = email.value.split('@')[0]
        
        # Generate username from email if not provided
        username = email.value.split('@')[0] + f"_{provider}_{str(uuid4())[:8]}"
        
        # Create user with OAuth provider info
        return User(
            id=UserId.generate(),
            email=email,
            username=username,
            first_name=first_name or 'Unknown',
            last_name=last_name or 'User',
            password_hash='',  # No password for OAuth users
            role=UserRole.sales_rep(),
            status=UserStatus.active(),
            _oauth_provider=provider,
            _oauth_provider_id=str(user_info.get('id', ''))
        )

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