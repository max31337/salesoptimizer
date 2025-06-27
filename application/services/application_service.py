from infrastructure.config.oauth_config import OAuthConfig
from domain.organization.services.auth_service import AuthService
from domain.organization.services.invitation_service import InvitationService
from domain.organization.services.tenant_service import TenantService
from application.use_cases.auth_use_cases import AuthUseCases
from application.use_cases.invitation_use_cases import InvitationUseCases
from application.use_cases.organization_registration_use_cases import OrganizationRegistrationUseCases
from application.use_cases.token_revocation_use_cases import TokenRevocationUseCases

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
        organization_registration_use_cases: OrganizationRegistrationUseCases,
        token_revocation_use_cases: TokenRevocationUseCases,
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
        self._organization_registration_use_cases = organization_registration_use_cases
        self.token_revocation_use_cases = token_revocation_use_cases
        
        # Configuration
        self._oauth_config = oauth_config

    @property
    def auth_use_cases(self) -> AuthUseCases:
        return self._auth_use_cases
    
    @property
    def invitation_use_cases(self) -> InvitationUseCases:
        return self._invitation_use_cases

    @property
    def organization_registration_use_cases(self) -> OrganizationRegistrationUseCases:
        return self._organization_registration_use_cases

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