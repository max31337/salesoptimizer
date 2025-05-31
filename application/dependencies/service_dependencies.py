from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from infrastructure.db.database import get_async_session
from infrastructure.repositories.user_repository_impl import UserRepositoryImpl
from infrastructure.services.password_service import PasswordService
from infrastructure.services.jwt_service import JWTService
from domain.organization.services.auth_service import AuthService
from application.use_cases.auth_use_cases import AuthUseCases


class ApplicationService:
    """Application service container."""
    
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._user_repository = UserRepositoryImpl(session)
        self._password_service = PasswordService()
        self._jwt_service = JWTService()
        self._auth_service = AuthService(
            self._user_repository,
            self._password_service,
            self._jwt_service
        )
        self._auth_use_cases = AuthUseCases(self._auth_service)
    
    @property
    def auth_use_cases(self) -> AuthUseCases:
        """Get auth use cases."""
        return self._auth_use_cases


async def get_application_service(
    session: AsyncSession = Depends(get_async_session)  # type: ignore
) -> ApplicationService:
    """Get application service dependency."""
    return ApplicationService(session)