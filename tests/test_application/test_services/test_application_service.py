

from application.services.application_service import ApplicationService
from application.use_cases.user_use_cases import UserUseCases
from application.use_cases.tenant_use_cases import TenantUseCases
from application.use_cases.auth_use_cases import AuthUseCases


class TestApplicationService:
    """Test application service factory."""
    
    def test_user_use_cases_creation(self, application_service: ApplicationService):
        """Test user use cases are created correctly."""
        use_cases = application_service.user_use_cases
        
        assert isinstance(use_cases, UserUseCases)
        assert use_cases.user_repository is not None
    
    def test_tenant_use_cases_creation(self, application_service: ApplicationService):
        """Test tenant use cases are created correctly."""
        use_cases = application_service.tenant_use_cases
        
        assert isinstance(use_cases, TenantUseCases)
        assert use_cases.tenant_repository is not None
    
    def test_auth_use_cases_creation(self, application_service: ApplicationService):
        """Test auth use cases are created correctly."""
        use_cases = application_service.auth_use_cases
        
        assert isinstance(use_cases, AuthUseCases)
        assert use_cases.auth_service is not None
    
    def test_auth_service_creation(self, application_service: ApplicationService):
        """Test auth service is created correctly."""
        auth_service = application_service.auth_service
        
        assert auth_service is not None
        # Verify singleton behavior
        assert application_service.auth_service is auth_service
    
    def test_singleton_behavior(self, application_service: ApplicationService):
        """Test that services are created as singletons within the same instance."""
        # Get services multiple times
        user_use_cases_1 = application_service.user_use_cases
        user_use_cases_2 = application_service.user_use_cases
        
        tenant_use_cases_1 = application_service.tenant_use_cases
        tenant_use_cases_2 = application_service.tenant_use_cases
        
        auth_use_cases_1 = application_service.auth_use_cases
        auth_use_cases_2 = application_service.auth_use_cases
        
        # Verify same instances are returned
        assert user_use_cases_1 is user_use_cases_2
        assert tenant_use_cases_1 is tenant_use_cases_2
        assert auth_use_cases_1 is auth_use_cases_2