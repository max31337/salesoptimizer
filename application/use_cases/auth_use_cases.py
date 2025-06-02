from typing import Tuple

from domain.organization.entities.user import User
from domain.organization.services.auth_service import AuthService
from infrastructure.services.oauth_service import OAuthService
from application.commands.auth_command import LoginCommand
from application.commands.oauth_command import OAuthLoginCommand, OAuthAuthorizationCommand


class AuthUseCases:
    """Authentication use cases."""
    
    def __init__(
        self, 
        auth_service: AuthService,
        oauth_service: OAuthService
    ) -> None:
        self._auth_service = auth_service
        self._oauth_service = oauth_service
    
    async def login(self, command: LoginCommand) -> Tuple[User, str, str]:
        """Login user and return user with tokens."""
        user = await self._auth_service.authenticate_user(
            command.email_or_username,
            command.password
        )
        
        access_token, refresh_token = self._auth_service.create_tokens(user)
        
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
        
        # Create tokens
        access_token, refresh_token = self._auth_service.create_tokens(user)
        
        return user, access_token, refresh_token, is_new_user
    
    def get_oauth_authorization_url(self, command: OAuthAuthorizationCommand) -> str:
        """Get OAuth authorization URL."""
        return self._oauth_service.get_authorization_url(
            command.provider,
            command.redirect_uri
        )