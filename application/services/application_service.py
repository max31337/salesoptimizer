from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.repositories.user_repository_impl import UserRepositoryImpl
from infrastructure.repositories.tenant_repository_impl import TenantRepositoryImpl
from infrastructure.services.password_service import PasswordService
from infrastructure.services.jwt_service import JWTService
from domain.organization.services.auth_service import AuthService
from application.use_cases.user_use_cases import UserUseCases
from application.use_cases.tenant_use_cases import TenantUseCases
from application.use_cases.auth_use_cases import AuthUseCases


class ApplicationService:
    """Factory for creating application use cases with proper dependencies."""
    
    def __init__(self, db: AsyncSession):  # Change to AsyncSession
        self.db = db
        self._user_repository = None
        self._tenant_repository = None
        self._auth_service = None
        self._user_use_cases = None
        self._tenant_use_cases = None
        self._auth_use_cases = None
    
    @property
    def user_repository(self) -> UserRepositoryImpl:
        if self._user_repository is None:
            self._user_repository = UserRepositoryImpl(self.db)
        return self._user_repository
    
    @property
    def tenant_repository(self) -> TenantRepositoryImpl:
        if self._tenant_repository is None:
            self._tenant_repository = TenantRepositoryImpl(self.db)
        return self._tenant_repository
    
    @property
    def auth_service(self) -> AuthService:
        if self._auth_service is None:
            password_service = PasswordService()
            jwt_service = JWTService()
            self._auth_service = AuthService(self.user_repository, password_service, jwt_service)
        return self._auth_service
    
    @property
    def user_use_cases(self) -> UserUseCases:
        if self._user_use_cases is None:
            self._user_use_cases = UserUseCases(self.user_repository)
        return self._user_use_cases
    
    @property
    def tenant_use_cases(self) -> TenantUseCases:
        if self._tenant_use_cases is None:
            self._tenant_use_cases = TenantUseCases(self.tenant_repository)
        return self._tenant_use_cases
    
    @property
    def auth_use_cases(self) -> AuthUseCases:
        if self._auth_use_cases is None:
            self._auth_use_cases = AuthUseCases(self.auth_service)
        return self._auth_use_cases