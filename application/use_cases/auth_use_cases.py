from typing import Tuple

from domain.organization.entities.user import User
from domain.organization.services.auth_service import AuthService
from application.commands.auth_command import LoginCommand


class AuthUseCases:
    """Authentication use cases."""
    
    def __init__(self, auth_service: AuthService) -> None:
        self._auth_service = auth_service
    
    async def login(self, command: LoginCommand) -> Tuple[User, str, str]:
        """Login user and return user with tokens."""
        user = await self._auth_service.authenticate_user(
            command.email_or_username,
            command.password
        )
        
        access_token, refresh_token = self._auth_service.create_tokens(user)
        
        return user, access_token, refresh_token