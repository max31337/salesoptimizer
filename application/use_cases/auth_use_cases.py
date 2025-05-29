from typing import Tuple
from domain.organization.entities.user import User
from domain.organization.services.auth_service import AuthService
from application.dtos.auth_dto import RegisterRequest


class AuthUseCases:
    """Authentication use cases."""
    
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service
    
    async def authenticate_user(self, email: str, password: str) -> Tuple[User, str, str]:
        """Authenticate user and return user with tokens."""
        user = await self.auth_service.authenticate_user(email, password)
        access_token, refresh_token = self.auth_service.create_user_tokens(user)
        return user, access_token, refresh_token 
    
    async def complete_registration(self, register_data: RegisterRequest) -> Tuple[User, str, str]:
        """Complete user registration and return user with tokens."""
        user = await self.auth_service.complete_registration(
            invitation_token=register_data.invitation_token,
            password=register_data.password,
            first_name=register_data.first_name,
            last_name=register_data.last_name
        )
        access_token, refresh_token = self.auth_service.create_user_tokens(user)
        return user, access_token, refresh_token
    
    async def refresh_tokens(self, refresh_token: str) -> Tuple[str, str]:
        """Refresh access and refresh tokens."""
        return await self.auth_service.refresh_user_tokens(refresh_token)