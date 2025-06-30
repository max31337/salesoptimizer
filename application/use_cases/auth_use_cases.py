from typing import Tuple, Optional

from domain.organization.entities.user import User
from domain.organization.services.auth_service import AuthService
from domain.organization.services.login_activity_service import LoginActivityService
from infrastructure.services.oauth_service import OAuthService
from application.commands.auth_command import LoginCommand
from application.commands.oauth_command import OAuthLoginCommand, OAuthAuthorizationCommand
from application.dtos.auth_dto import ChangePasswordRequest
from domain.organization.value_objects.user_id import UserId


class AuthUseCases:
    """Authentication use cases."""
    
    def __init__(
        self,
        auth_service: AuthService,
        oauth_service: OAuthService,
        login_activity_service: LoginActivityService
    ) -> None:
        self._auth_service = auth_service
        self._oauth_service = oauth_service
        self._login_activity_service = login_activity_service
    
    async def login(self, command: LoginCommand) -> Tuple[User, str, str]:
        """Login user and return user with tokens. Tracks device info if provided."""
        user = await self._auth_service.authenticate_user(
            command.email_or_username,
            command.password
        )
        # Record login activity
        if user.id:
            login_activity = await self._login_activity_service.record_login(
                user_id=user.id,
                ip_address=command.ip_address,
                user_agent=command.user_agent
            )
            user.login_activities.append(login_activity)
        access_token, refresh_token = await self._auth_service.create_tokens_with_device_info(
            user, command.user_agent, command.ip_address
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

    async def logout(self, user_id: UserId) -> None:
        """Logout user and record logout activity."""
        await self._login_activity_service.record_logout(user_id)
