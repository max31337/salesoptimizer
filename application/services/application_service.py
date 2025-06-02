from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from infrastructure.db.database import get_async_session
from infrastructure.db.repositories.user_repository_impl import UserRepositoryImpl
from infrastructure.db.repositories.invitation_repository_impl import InvitationRepositoryImpl
from infrastructure.db.repositories.tenant_repository_impl import TenantRepositoryImpl
from infrastructure.services.password_service import PasswordService
from infrastructure.services.jwt_service import JWTService
from infrastructure.services.oauth_service import OAuthService
from infrastructure.config.oauth_config import OAuthConfig
from domain.organization.services.auth_service import AuthService
from domain.organization.services.invitation_service import InvitationService
from domain.organization.services.tenant_service import TenantService
from application.use_cases.auth_use_cases import AuthUseCases
from application.use_cases.invitation_use_cases import InvitationUseCases

class ApplicationService:
    """Application service container - Pure application layer."""
    
    def __init__(
        self,
        # Domain services
        auth_service: AuthService,
        invitation_service: InvitationService,
        tenant_service: TenantService,
        # Use cases
        auth_use_cases: AuthUseCases,
        invitation_use_cases: InvitationUseCases,
        # Configuration
        oauth_config: OAuthConfig
    ):
        # Domain services
        self._auth_service = auth_service
        self._invitation_service = invitation_service
        self._tenant_service = tenant_service
        
        # Use cases
        self._auth_use_cases = auth_use_cases
        self._invitation_use_cases = invitation_use_cases
        
        # Configuration
        self._oauth_config = oauth_config

    @property
    def auth_use_cases(self) -> AuthUseCases:
        return self._auth_use_cases
    
    @property
    def invitation_use_cases(self) -> InvitationUseCases:
        return self._invitation_use_cases

    @property
    def config(self) -> OAuthConfig:
        return self._oauth_config
    
    @property
    def auth_service(self) -> AuthService:
        return self._auth_service
    
    @property
    def invitation_service(self) -> InvitationService:
        return self._invitation_service
    
    @property
    def tenant_service(self) -> TenantService:
        return self._tenant_service

async def get_application_service(
    session: AsyncSession = Depends(get_async_session)  # type: ignore
) -> ApplicationService:
    """Get application service with all dependencies."""
    async with get_async_session() as session:
        # Configuration
        oauth_config = OAuthConfig()
        
        # Repositories
        user_repository = UserRepositoryImpl(session)
        invitation_repository = InvitationRepositoryImpl(session)
        tenant_repository = TenantRepositoryImpl(session)
        
        # Services
        password_service = PasswordService()
        jwt_service = JWTService()
        oauth_service = OAuthService(oauth_config)
        
        # Domain services
        auth_service = AuthService(
            user_repository=user_repository,
            password_service=password_service,
            jwt_service=jwt_service
        )
        invitation_service = InvitationService(invitation_repository, tenant_repository)
        tenant_service = TenantService(tenant_repository)
        
        # Use cases
        auth_use_cases = AuthUseCases(auth_service, oauth_service)
        invitation_use_cases = InvitationUseCases(invitation_service, auth_service)
        
        return ApplicationService(
            auth_service=auth_service,
            invitation_service=invitation_service,
            tenant_service=tenant_service,
            auth_use_cases=auth_use_cases,
            invitation_use_cases=invitation_use_cases,
            oauth_config=oauth_config
        )