from typing import Tuple, Optional, Dict, Any, TYPE_CHECKING
from uuid import uuid4, UUID

from domain.organization.entities.user import User
from domain.organization.value_objects.email import Email
from domain.organization.value_objects.user_id import UserId
from domain.organization.value_objects.password import Password
from domain.organization.value_objects.user_role import UserRole
from domain.organization.value_objects.user_status import UserStatus
from domain.organization.repositories.user_repository import UserRepository
from domain.organization.exceptions.auth_exceptions import (
    AuthenticationError,
    InvalidCredentialsError,
    UserNotFoundError,
    InactiveUserError
)
from infrastructure.services.password_service import PasswordService
from infrastructure.services.jwt_service import JWTService

if TYPE_CHECKING:
    from domain.organization.entities.invitation import Invitation
    from domain.organization.value_objects.tenant_id import TenantId


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
        
        # Verify password - Fix: Check password_hash directly instead of has_password()
        if not user.password_hash or not self._password_service.verify_password(
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
    
    async def authenticate_oauth_user_with_invitation(
        self, 
        provider: str, 
        user_info: Dict[str, Any],
        invitation: Optional['Invitation'] = None,
        tenant_id: Optional['TenantId'] = None
    ) -> Tuple[User, bool]:
        """Authenticate or create user via OAuth with invitation and tenant."""
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
            # Create new user with tenant
            is_new_user = True
            user = self._create_oauth_user_with_tenant(provider, user_info, email, tenant_id)
            
            # If invitation exists, use the invited role
            if invitation:
                user.role = invitation.role
            
            user = await self._user_repository.save(user)
        else:
            # Check if user is active
            if not user.is_active():
                raise InactiveUserError()
            
            # Update tenant if provided and user doesn't have one
            if tenant_id and not user.tenant_id:
                user.tenant_id = tenant_id.value
                user = await self._user_repository.update(user)
            
            # Update last login
            user.record_login()
            user = await self._user_repository.update(user)
        
        return user, is_new_user

    async def refresh_token(self, refresh_token: str) -> Tuple[User, str, str]:
        """Refresh access token and rotate refresh token."""
        # Verify refresh token 
        payload = await self._jwt_service.verify_token(refresh_token)
        if not payload:
            raise AuthenticationError("Invalid refresh token")
        
        # Validate token type
        if not self._jwt_service.validate_token_type(refresh_token, "refresh"):
            raise AuthenticationError("Invalid token type")
        
        # Extract user ID from token
        user_id_str = self._jwt_service.extract_user_id_from_token(refresh_token)
        if not user_id_str:
            raise AuthenticationError("Invalid refresh token - no user ID")
        
        # Get user from database
        user = await self.get_user_by_id(user_id_str)
        if not user or not user.is_active():
            raise AuthenticationError("User not found or inactive")
        
        # Generate new tokens using token rotation
        access_token, new_refresh_token = await self.create_tokens(user)
        
        return user, access_token, new_refresh_token

    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token."""
        return await self._jwt_service.verify_token(token)

    async def revoke_token(self, token: str) -> bool:
        """Revoke a specific token."""
        # For now, return True as token revocation logic needs to be implemented
        # This would typically involve adding the token to a blacklist
        return True

    async def revoke_all_user_tokens(self, user_id: str) -> bool:
        """Revoke all tokens for a user (logout from all devices)."""
        # For now, return True as token revocation logic needs to be implemented
        # This would typically involve blacklisting all tokens for the user
        return True

    async def logout_from_current_device(self, access_token: str, refresh_token: str) -> bool:
        """Logout from current device by revoking both tokens."""
        # For now, return True as token revocation logic needs to be implemented
        return True

    async def logout_from_all_devices(self, user_id: str) -> bool:
        """Logout from all devices by revoking all refresh tokens."""
        # For now, return True as token revocation logic needs to be implemented
        return True

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
            password_hash='',  # Empty string for OAuth users (not None)
            role=UserRole.sales_rep(),
            status=UserStatus.active(),
            _oauth_provider=provider,
            _oauth_provider_id=str(user_info.get('id', ''))
        )

    def _create_oauth_user_with_tenant(
        self, 
        provider: str, 
        user_info: Dict[str, Any], 
        email: Email,
        tenant_id: Optional['TenantId'] = None
    ) -> User:
        """Create new user from OAuth with tenant."""
        # Create user using existing method
        user = self._create_oauth_user(provider, user_info, email)
        
        # Override role to user instead of sales_rep
        user.role = UserRole.sales_rep()
        
        # Set tenant if provided
        if tenant_id:
            user.tenant_id = tenant_id.value
        
        return user

    def _extract_full_name(self, provider: str, user_info: Dict[str, Any]) -> str:
        """Extract full name from OAuth user info based on provider."""
        if provider == "google":
            first_name = user_info.get('given_name', '')
            last_name = user_info.get('family_name', '')
            full_name = user_info.get('name', f"{first_name} {last_name}".strip())
        elif provider == "github":
            full_name = user_info.get('name', '')
            if not full_name:
                full_name = user_info.get('login', '')
        elif provider == "microsoft":
            first_name = user_info.get('given_name', '')
            last_name = user_info.get('family_name', '')
            full_name = user_info.get('name', f"{first_name} {last_name}".strip())
        else:
            full_name = user_info.get('name', '')
        
        return full_name or 'Unknown User'
    
    async def create_tokens(self, user: User) -> Tuple[str, str]:
        """Create access and refresh tokens for user."""
        if not user.id:
            raise AuthenticationError("User ID is required to create tokens")
        
        access_token = self._jwt_service.create_access_token(
            user_id=str(user.id.value),
            tenant_id=str(user.tenant_id) if user.tenant_id else None,
            role=user.role.value,
            email=str(user.email)
        )
        
        # Use the async method for refresh token creation
        refresh_token = await self._jwt_service.create_refresh_token_with_storage(
            user_id=str(user.id.value),
            device_info=None,  # You can extract this from request headers
            ip_address=None,   # You can extract this from request
            user_agent=None    # You can extract this from request headers
        )
        
        return access_token, refresh_token
    
    async def create_tokens_with_device_info(
        self, 
        user: User, 
        user_agent: str, 
        ip_address: str
    ) -> Tuple[str, str]:
        """Create access and refresh tokens for user with device information."""
        if not user.id:
            raise AuthenticationError("User ID is required to create tokens")
        
        access_token = self._jwt_service.create_access_token(
            user_id=str(user.id.value),
            tenant_id=str(user.tenant_id) if user.tenant_id else None,
            role=user.role.value,
            email=str(user.email)
        )
        
        # Use the async method for refresh token creation with device info
        refresh_token = await self._jwt_service.create_refresh_token_with_storage(
            user_id=str(user.id.value),
            device_info=f"Login from {user_agent[:100]}",  # Truncate user agent
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return access_token, refresh_token

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        try:
            email_obj = Email(email)
            return await self._user_repository.get_by_email(email_obj)
        except ValueError:
            return None

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        try:
            user_id_obj = UserId(UUID(user_id))
            return await self._user_repository.get_by_id(user_id_obj)
        except (ValueError, TypeError):
            return None

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return await self._user_repository.get_by_username(username)