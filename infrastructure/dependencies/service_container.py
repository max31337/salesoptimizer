import os
from functools import lru_cache
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
import redis

from infrastructure.config.settings import settings
from infrastructure.db.database import get_async_session
from infrastructure.db.repositories.user_repository_impl import UserRepositoryImpl
from infrastructure.db.repositories.invitation_repository_impl import InvitationRepositoryImpl
from infrastructure.db.repositories.tenant_repository_impl import TenantRepositoryImpl
from infrastructure.db.repositories.refresh_token_repository_impl import RefreshTokenRepositoryImpl
from infrastructure.db.repositories.profile_update_request_repository_impl import ProfileUpdateRequestRepositoryImpl
from infrastructure.email.smtp_email_service import SMTPEmailService
from infrastructure.services.password_service import PasswordService
from infrastructure.services.jwt_service import JWTService
from infrastructure.services.oauth_service import OAuthService
from infrastructure.config.oauth_config import OAuthConfig
from infrastructure.config.redis_config import redis_config

# Domain services
from domain.organization.services.auth_service import AuthService
from domain.organization.services.invitation_service import InvitationService
from domain.organization.services.tenant_service import TenantService
from domain.organization.services.profile_update_service import ProfileUpdateService

# Application layer
from application.services.application_service import ApplicationService
from application.use_cases.auth_use_cases import AuthUseCases
from application.use_cases.invitation_use_cases import InvitationUseCases
from application.use_cases.token_revocation_use_cases import TokenRevocationUseCases
from application.use_cases.profile_update_use_cases import ProfileUpdateUseCase
from domain.shared.services.email_service import EmailService
from domain.shared.services.token_blacklist_service import InMemoryTokenBlacklistService

# use for later 
#from infrastructure.services.redis_token_blacklist_service import RedisTokenBlacklistService


def create_oauth_config() -> OAuthConfig:
    """Create OAuth configuration from environment variables."""
    return OAuthConfig(
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


@lru_cache()
def get_email_service() -> EmailService:
    """Get email service instance."""
    return SMTPEmailService(
        smtp_host=settings.SMTP_HOST,
        smtp_port=settings.SMTP_PORT,
        smtp_username=settings.SMTP_USERNAME,
        smtp_password=settings.SMTP_PASSWORD,
        use_tls=settings.SMTP_USE_TLS,
        use_starttls=settings.SMTP_USE_STARTTLS, 
        default_from_email=settings.DEFAULT_FROM_EMAIL,
        default_from_name=settings.DEFAULT_FROM_NAME,
        base_url=settings.FRONTEND_URL
    )

@lru_cache()
def get_redis_client() -> redis.Redis:
    """Get Redis client."""
    return redis_config.get_redis_client()

async def get_application_service(
    session: AsyncSession = Depends(get_async_session)
) -> ApplicationService:
    """Get application service with all dependencies - Infrastructure layer responsibility."""
    
    # Infrastructure services
    password_service = PasswordService()
    oauth_config = create_oauth_config()
    oauth_service = OAuthService(config=oauth_config)
    
    # Repositories (Infrastructure layer)
    user_repository = UserRepositoryImpl(session)
    tenant_repository = TenantRepositoryImpl(session)
    invitation_repository = InvitationRepositoryImpl(session)
    refresh_token_repository = RefreshTokenRepositoryImpl(session)
    
    # Token blacklist service (use Redis in production)
    token_blacklist_service = InMemoryTokenBlacklistService()  # or RedisTokenBlacklistService()
    
    # JWT service with both blacklist and refresh token repository
    jwt_service = JWTService(
        secret_key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
        access_token_expire_minutes=settings.JWT_EXPIRE_MINUTES,
        refresh_token_expire_days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
        token_blacklist_service=token_blacklist_service,
        refresh_token_repository=refresh_token_repository
    )
    
    # Domain services
    auth_service = AuthService(
        user_repository=user_repository,
        password_service=password_service,
        jwt_service=jwt_service
    )
    
    tenant_service = TenantService(tenant_repository)
    
    email_service = get_email_service()
    
    invitation_service = InvitationService(
        invitation_repository=invitation_repository,
        tenant_repository=tenant_repository,
        email_service=email_service
    )
    
    # Token revocation use cases
    token_revocation_use_cases = TokenRevocationUseCases(
        auth_service,
        token_blacklist_service
    )
    
    # Application use cases
    auth_use_cases = AuthUseCases(auth_service, oauth_service)
    invitation_use_cases = InvitationUseCases(invitation_service, auth_service)
      # Application service (orchestrates everything)
    return ApplicationService(
        auth_service=auth_service,
        invitation_service=invitation_service,
        tenant_service=tenant_service,
        auth_use_cases=auth_use_cases,
        invitation_use_cases=invitation_use_cases,
        oauth_config=oauth_config,
        token_revocation_use_cases=token_revocation_use_cases
    )


async def get_profile_update_use_case(
    session: AsyncSession = Depends(get_async_session)
) -> ProfileUpdateUseCase:
    """Get profile update use case with dependencies."""
    
    # Repositories
    user_repository = UserRepositoryImpl(session)
    profile_update_request_repository = ProfileUpdateRequestRepositoryImpl(session)
    
    # Domain services
    profile_service = ProfileUpdateService()
    
    # Use case
    return ProfileUpdateUseCase(
        user_repository=user_repository,
        profile_service=profile_service,
        profile_update_request_repository=profile_update_request_repository
    )