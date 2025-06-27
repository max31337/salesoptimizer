from typing import Tuple, Optional

from domain.organization.entities.user import User
from domain.organization.services.auth_service import AuthService
from domain.organization.services.activity_log_service import ActivityLogService
from domain.organization.services.tenant_service import TenantService
from infrastructure.services.oauth_service import OAuthService
from application.commands.auth_command import LoginCommand, SignupCommand
from application.commands.oauth_command import OAuthLoginCommand, OAuthAuthorizationCommand
from application.dtos.auth_dto import ChangePasswordRequest
from domain.organization.value_objects.email import Email
from domain.organization.value_objects.tenant_name import TenantName
from domain.organization.entities.tenant import Tenant
from domain.organization.value_objects.user_role import UserRole
from domain.organization.value_objects.user_status import UserStatus


class AuthUseCases:
    """Authentication use cases."""
    
    def __init__(
        self, 
        auth_service: AuthService,
        oauth_service: OAuthService,
        activity_log_service: Optional[ActivityLogService] = None
    ) -> None:
        self._auth_service = auth_service
        self._oauth_service = oauth_service
        self._activity_log_service = activity_log_service
    
    async def login(self, command: LoginCommand) -> Tuple[User, str, str]:
        """Login user and return user with tokens."""
        user = await self._auth_service.authenticate_user(
            command.email_or_username,
            command.password
        )
        
        access_token, refresh_token = await self._auth_service.create_tokens(user)
        
        return user, access_token, refresh_token
    
    async def login_with_device_info(
        self, 
        command: LoginCommand, 
        user_agent: str, 
        ip_address: str
    ) -> Tuple[User, str, str]:
        """Login user with device information and return user with tokens."""
        user = await self._auth_service.authenticate_user(
            command.email_or_username,
            command.password
        )
        
        # Log the login activity
        if self._activity_log_service and user.id:
            try:
                await self._activity_log_service.record_user_login(
                    user_id=user.id,
                    tenant_id=user.tenant_id,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
            except Exception as e:
                # Don't fail login if activity logging fails
                print(f"Failed to log login activity: {e}")
        
        access_token, refresh_token = await self._auth_service.create_tokens_with_device_info(
            user, user_agent, ip_address
        )
        
        return user, access_token, refresh_token
    
    async def oauth_login(self, command: OAuthLoginCommand) -> Tuple[User, str, str, bool]:
        """OAuth login and return user with tokens."""
        # Exchange code for token
        token = await self._oauth_service.exchange_code_for_token(
            command.provider,
            command.code,
            command.redirect_uri
        )
        
        # Get user info from provider
        user_info = await self._oauth_service.get_user_info(
            command.provider,
            token
        )
        
        # Authenticate or create user (without invitation)
        user, is_new_user = await self._auth_service.authenticate_oauth_user(
            command.provider,
            user_info
        )
        
        # Create tokens - Add await here too
        access_token, refresh_token = await self._auth_service.create_tokens(user)
        
        return user, access_token, refresh_token, is_new_user
    
    def get_oauth_authorization_url(self, command: OAuthAuthorizationCommand) -> str:
        """Get OAuth authorization URL."""
        return self._oauth_service.get_authorization_url(
            command.provider,
            command.redirect_uri
        )
    
    async def refresh_token(self, refresh_token: str) -> Tuple[User, str, str]:
        """Refresh access token and rotate refresh token."""
        return await self._auth_service.refresh_token(refresh_token)
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return await self._auth_service.get_user_by_email(email)
    
    async def change_password(self, user_id: str, request: ChangePasswordRequest) -> User:
        """Change user password after verifying current password."""
        return await self._auth_service.change_password(
            user_id,
            request.current_password,
            request.new_password
        )