from typing import Tuple, Optional, Dict, Any, TYPE_CHECKING
from uuid import uuid4, UUID
import logging

from domain.organization.entities.user import User
from domain.organization.value_objects.email import Email
from domain.organization.value_objects.user_id import UserId
from domain.organization.value_objects.password import Password
from domain.organization.value_objects.user_role import UserRole
from domain.organization.value_objects.user_status import UserStatus
from domain.organization.repositories.user_repository import UserRepository
from domain.organization.repositories.oauth_provider_repository import OAuthProviderRepository
from domain.organization.repositories.email_verification_repository import EmailVerificationRepository
from domain.organization.entities.oauth_provider import OAuthProvider
from domain.organization.exceptions.auth_exceptions import (
    AuthenticationError,
    InvalidCredentialsError,
    UserNotFoundError,
    InactiveUserError
)
from infrastructure.services.password_service import PasswordService
from infrastructure.services.jwt_service import JWTService
from infrastructure.utils.device_parser import generate_device_info_string

if TYPE_CHECKING:
    from domain.organization.entities.invitation import Invitation
    from domain.organization.value_objects.tenant_id import TenantId


class AuthService:
    """Domain service for authentication operations."""
    
    def __init__(
        self,
        user_repository: UserRepository,
        oauth_provider_repository: OAuthProviderRepository,
        email_verification_repository: EmailVerificationRepository,
        password_service: PasswordService,
        jwt_service: JWTService
    ) -> None:
        self._user_repository = user_repository
        self._oauth_provider_repository = oauth_provider_repository
        self._email_verification_repository = email_verification_repository
        self._password_service = password_service
        self._jwt_service = jwt_service
        self._logger = logging.getLogger(__name__)

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
        
        # Log login activity instead of last_login
        from domain.organization.entities.login_activity import LoginActivity
        if user.id is None:
            raise AuthenticationError("User ID is missing for login activity")
        login_activity = LoginActivity(
            id=None,
            user_id=user.id,
            ip_address=None,  # You may want to pass these from the command/request
            user_agent=None
        )
        if hasattr(user, 'login_activities'):
            user.login_activities.append(login_activity)
        else:
            user.login_activities = [login_activity]
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
        
        # Try to find existing user by OAuth provider details first
        oauth_provider_id = str(user_info.get('id', ''))
        oauth_provider_entity = await self._oauth_provider_repository.get_by_provider_user_id(provider, oauth_provider_id)

        if oauth_provider_entity:
            user = await self._user_repository.get_by_id(oauth_provider_entity.user_id)
            is_new_user = False
        else:
            user = await self._user_repository.get_by_email(email)
            is_new_user = False

        if not user:
            # Create new user
            is_new_user = True
            user = self._create_oauth_user(provider, user_info, email)
            user = await self._user_repository.save(user)
            # Create and save the oauth provider link
            if user.id:
                oauth_provider_entity = OAuthProvider(
                    id=uuid4(),
                    user_id=user.id,
                    provider=provider,
                    provider_user_id=oauth_provider_id
                )
                await self._oauth_provider_repository.add(oauth_provider_entity)
        else:
            # Check if user is active
            if not user.is_active():
                raise InactiveUserError()

            # Link the OAuth provider if it's not already linked
            if not oauth_provider_entity:
                if user.id:
                    oauth_provider_entity = OAuthProvider(
                        id=uuid4(),
                        user_id=user.id,
                        provider=provider,
                        provider_user_id=oauth_provider_id
                    )
                    await self._oauth_provider_repository.add(oauth_provider_entity)

            # Log login activity instead of last_login
            from domain.organization.entities.login_activity import LoginActivity
            if user.id is None:
                raise AuthenticationError("User ID is missing for login activity")
            login_activity = LoginActivity(
                id=None,
                user_id=user.id,
                ip_address=None,  # You may want to pass these from the command/request
                user_agent=None
            )
            if hasattr(user, 'login_activities'):
                user.login_activities.append(login_activity)
            else:
                user.login_activities = [login_activity]
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
            
            # Log login activity instead of last_login
            from domain.organization.entities.login_activity import LoginActivity
            if user.id is None:
                raise AuthenticationError("User ID is missing for login activity")
            login_activity = LoginActivity(
                id=None,
                user_id=user.id,
                ip_address=None,  # You may want to pass these from the command/request
                user_agent=None
            )
            if hasattr(user, 'login_activities'):
                user.login_activities.append(login_activity)
            else:
                user.login_activities = [login_activity]
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
        try:
            # Verify and extract payload
            payload = self._jwt_service.verify_token_sync(token)
            if not payload:
                return False
            
            token_type = payload.get("type")
            jti = payload.get("jti")
            
            if not jti:
                return False
            
            if token_type == "access":
                # Add access token to blacklist
                if self._jwt_service.token_blacklist_service:
                    from datetime import datetime, timezone
                    await self._jwt_service.token_blacklist_service.revoke_token(
                        jti,
                        datetime.now(timezone.utc)
                    )
                    return True
            elif token_type == "refresh":
                # Revoke refresh token in database
                if self._jwt_service.refresh_token_repository:
                        return await self._jwt_service.refresh_token_repository.revoke_refresh_token_by_jti(
                            jti
                        )
                
                return False
                    
        except Exception as e:
            self._logger.error(f"Failed to revoke token: {e}")
        return False
    
    async def get_user_active_sessions(
        self, 
        user_id: str, 
        page: int = 1, 
        page_size: int = 10
    ) -> Dict[str, Any]:
        """Get active sessions for a user with pagination."""
        try:
            from uuid import UUID
            user_uuid = UUID(user_id)
            if self._jwt_service.refresh_token_repository:
                result = await self._jwt_service.refresh_token_repository.get_user_active_sessions(
                    user_uuid, page, page_size
                )
                return result
            
            return {
                "sessions": [],
                "total_count": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0
            }
            
        except Exception as e:
            self._logger.error(f"Failed to get active sessions: {e}")
            return {
                "sessions": [],
                "total_count": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0
            }

    async def get_user_revoked_sessions(
        self, 
        user_id: str, 
        page: int = 1, 
        page_size: int = 10
    ) -> Dict[str, Any]:
        """Get revoked sessions for a user with pagination."""
        try:
            from uuid import UUID
            user_uuid = UUID(user_id)
            if self._jwt_service.refresh_token_repository:
                result = await self._jwt_service.refresh_token_repository.get_user_revoked_sessions(
                    user_uuid, page, page_size
                )
                return result
            
            return {
                "sessions": [],
                "total_count": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0
            }
            
        except Exception as e:
            self._logger.error(f"Failed to get revoked sessions: {e}")
            return {
                "sessions": [],
                "total_count": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0
            }

    async def logout_from_current_device(
        self, 
        access_token: str, 
        refresh_token: str
    ) -> bool:
        """Logout from current device by revoking the specific tokens."""
        try:
            # Extract JTI from access token
            access_payload = self._jwt_service.verify_token_sync(access_token)
            if access_payload and access_payload.get("jti"):
                access_jti = access_payload["jti"]
                # Add access token to blacklist
                if self._jwt_service.token_blacklist_service:
                    from datetime import datetime, timezone
                    await self._jwt_service.token_blacklist_service.revoke_token(
                        access_jti,
                        datetime.now(timezone.utc)
                    )
            
            # Extract JTI from refresh token and revoke it
            refresh_payload = self._jwt_service.verify_token_sync(refresh_token)
            if refresh_payload and refresh_payload.get("jti"):
                refresh_jti = refresh_payload["jti"]
                # Revoke refresh token in database
                if self._jwt_service.refresh_token_repository:
                    await self._jwt_service.refresh_token_repository.revoke_refresh_token_by_jti(
                        refresh_jti
                    )
            
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to logout from current device: {e}")
            return False

    async def logout_from_all_devices(self, user_id: str) -> bool:
        """Logout from all devices by revoking all user tokens."""
        try:
            user_uuid = UUID(user_id)
            
            # Revoke all refresh tokens for the user
            if self._jwt_service.refresh_token_repository:
                count = await self._jwt_service.refresh_token_repository.revoke_all_user_refresh_tokens(
                    user_uuid
                )
                return count > 0
            
            return False
                
        except Exception as e:
            self._logger.error(f"Failed to logout from all devices: {e}")
            return False
    async def revoke_session_by_id(self, session_id: str, user_id: str) -> bool:
        """Revoke a specific session by session ID."""
        try:
            if not self._jwt_service.refresh_token_repository:
                self._logger.error("Refresh token repository not available")
                return False
                
            # Revoke the refresh token by its database ID (session_id is the database ID)
            success = await self._jwt_service.refresh_token_repository.revoke_refresh_token_by_id(
                session_id
            )
            
            if success:
                self._logger.info(f"Successfully revoked session {session_id} for user {user_id}")
            else:
                self._logger.warning(f"Session {session_id} not found or already revoked for user {user_id}")
            
            return success
        except Exception as e:
            self._logger.error(f"Failed to revoke session {session_id} for user {user_id}: {e}")
            return False

    def _create_oauth_user(
        self, 
        provider: str, 
        user_info: Dict[str, Any], 
        email: Email
    ) -> User:
        """Create a new user from OAuth information."""        # Extract name information
        if provider == "google":
            first_name = user_info.get('given_name', '')
            last_name = user_info.get('family_name', '')
        elif provider == "github":
            name = user_info.get('name', '')
            username = user_info.get('login', '')
            first_name = name.split()[0] if name else username
            last_name = ' '.join(name.split()[1:]) if len(name.split()) > 1 else ''
        elif provider == "microsoft":
            first_name = user_info.get('given_name', '')
            last_name = user_info.get('family_name', '')
        else:
            first_name = email.value.split('@')[0]
            last_name = ''
        
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
            is_email_verified=True # OAuth users have verified emails
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
        
        # Generate user-friendly device info
        # Generate user-friendly device info
        device_info = self._generate_device_info_string(user_agent)
        # Use the async method for refresh token creation with device info
        refresh_token = await self._jwt_service.create_refresh_token_with_storage(
            user_id=str(user.id.value),
            device_info=device_info,
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

    def _generate_device_info_string(self, user_agent: str) -> str:
        """Generate a user-friendly device info string from user agent."""
        return generate_device_info_string(user_agent)
    
    async def get_user_active_sessions_grouped(
        self, 
        user_id: str, 
        group_by: str,
        page: int = 1, 
        page_size: int = 10
    ) -> Dict[str, Any]:
        """Get active sessions for a user grouped by device or IP."""
        try:
            from uuid import UUID
            user_uuid = UUID(user_id)
            if self._jwt_service.refresh_token_repository:
                if group_by == "device":
                    result = await self._jwt_service.refresh_token_repository.get_user_active_sessions_grouped_by_device(
                        user_uuid, page, page_size
                    )
                elif group_by == "ip":
                    result = await self._jwt_service.refresh_token_repository.get_user_active_sessions_grouped_by_ip(
                        user_uuid, page, page_size
                    )
                else:
                    # Fall back to regular method
                    result = await self._jwt_service.refresh_token_repository.get_user_active_sessions(
                        user_uuid, page, page_size
                    )
                return result
            
            return {
                "grouped_sessions": {},
                "total_sessions": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0
            }
            
        except Exception as e:
            self._logger.error(f"Failed to get grouped active sessions: {e}")
            return {
                "grouped_sessions": {},
                "total_sessions": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0
            }

    async def get_user_revoked_sessions_grouped(
        self, 
        user_id: str, 
        group_by: str,
        page: int = 1, 
        page_size: int = 10
    ) -> Dict[str, Any]:
        """Get revoked sessions for a user grouped by device or IP."""
        try:
            from uuid import UUID
            user_uuid = UUID(user_id)
            if self._jwt_service.refresh_token_repository:
                if group_by == "device":
                    result = await self._jwt_service.refresh_token_repository.get_user_revoked_sessions_grouped_by_device(
                        user_uuid, page, page_size
                    )
                elif group_by == "ip":
                    result = await self._jwt_service.refresh_token_repository.get_user_revoked_sessions_grouped_by_ip(
                        user_uuid, page, page_size
                    )
                else:                    # Fall back to regular method
                    result = await self._jwt_service.refresh_token_repository.get_user_revoked_sessions(
                        user_uuid, page, page_size
                    )
                return result
            
            return {
                "grouped_sessions": {},
                "total_sessions": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0
            }
            
        except Exception as e:
            self._logger.error(f"Failed to get grouped revoked sessions: {e}")
            return {
                "grouped_sessions": {},
                "total_sessions": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0
            }
    
    async def change_password(self, user_id: str, current_password: str, new_password: str) -> User:
        """Change user password after verifying current password."""
        # Get user by ID
        user = await self.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        
        # Check if user is active
        if not user.is_active():
            raise InactiveUserError()
          # Verify current password if user has one (not OAuth users)
        if user.password_hash:
            if not self._password_service.verify_password(current_password, user.password_hash):
                raise InvalidCredentialsError()
          # Validate new password format and calculate strength
        try:
            password_obj = Password(new_password)
            password_strength = password_obj.strength.value
        except ValueError as e:
            raise ValueError(f"Invalid new password: {str(e)}")
        
        # Hash new password
        new_password_hash = self._password_service.hash_password(new_password)
        
        # Update user password and strength
        user.password_hash = new_password_hash
        user.password_strength = password_strength
        
        # Save user
        updated_user = await self._user_repository.update(user)
        
        self._logger.info(f"Password changed successfully for user {user_id}")
        
        return updated_user
