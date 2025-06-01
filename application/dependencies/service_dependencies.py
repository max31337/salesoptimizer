from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from infrastructure.db.database import get_async_session
from infrastructure.db.repositories.user_repository_impl import UserRepositoryImpl
from infrastructure.services.password_service import PasswordService
from infrastructure.services.jwt_service import JWTService
from infrastructure.services.oauth_service import OAuthService
from infrastructure.config.oauth_config import OAuthConfig
from domain.organization.services.auth_service import AuthService
from application.use_cases.auth_use_cases import AuthUseCases
import os

class ApplicationService:
    """Application service container."""
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._password_service = PasswordService()
        self._jwt_service = JWTService()
        self._oauth_config = OAuthConfig(
            google_client_id=os.environ["GOOGLE_CLIENT_ID"],
            google_client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
            github_client_id=os.environ["GITHUB_CLIENT_ID"],
            github_client_secret=os.environ["GITHUB_CLIENT_SECRET"],
            microsoft_client_id=os.environ["MICROSOFT_CLIENT_ID"],
            microsoft_client_secret=os.environ["MICROSOFT_CLIENT_SECRET"],
            google_oauth_redirect_url=os.environ["GOOGLE_OAUTH_REDIRECT_URL"],
            github_oauth_redirect_url=os.environ["GITHUB_OAUTH_REDIRECT_URL"],
            microsoft_oauth_redirect_url=os.environ["MICROSOFT_OAUTH_REDIRECT_URL"],
            frontend_url=os.getenv("FRONTEND_URL", "http://localhost:3000"),
            backend_url=os.getenv("BACKEND_URL", "http://localhost:8000")
        )
        self._oauth_service = OAuthService(config=self._oauth_config)
        self._user_repository = UserRepositoryImpl(self._session)
        self._auth_service = AuthService(
            self._user_repository,
            self._password_service,
            self._jwt_service
        )
        self._auth_use_cases = AuthUseCases(self._auth_service, self._oauth_service)


    @property
    def auth_use_cases(self) -> AuthUseCases:
        return self._auth_use_cases

    @property
    def config(self) -> OAuthConfig:
        return self._oauth_config

async def get_application_service(
    session: AsyncSession = Depends(get_async_session)  # type: ignore
) -> ApplicationService:
    """Get application service dependency."""
    return ApplicationService(session)