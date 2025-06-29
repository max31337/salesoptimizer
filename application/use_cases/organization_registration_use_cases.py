from typing import Tuple, Optional
from datetime import datetime, timezone
from uuid import uuid4

from application.commands.organization_registration_command import OrganizationRegistrationCommand
from domain.organization.entities.user import User
from domain.organization.entities.tenant import Tenant
from domain.organization.services.auth_service import AuthService
from domain.organization.services.tenant_service import TenantService
from domain.organization.services.invitation_service import InvitationService
from domain.organization.repositories.user_repository import UserRepository
from domain.organization.value_objects.email import Email
from domain.organization.value_objects.tenant_name import TenantName
from domain.organization.value_objects.user_role import UserRole
from domain.organization.value_objects.user_status import UserStatus
from domain.organization.value_objects.user_id import UserId
from infrastructure.services.password_service import PasswordService
from infrastructure.db.database import AsyncSessionLocal
from infrastructure.email.template_service import EmailTemplateService
from domain.shared.services.email_service import EmailMessage, EmailService


class OrganizationRegistrationUseCases:
    """Use cases for self-serve organization registration."""
    
    def __init__(
        self,
        auth_service: AuthService,
        tenant_service: TenantService,
        invitation_service: InvitationService,
        user_repository: UserRepository,
        password_service: PasswordService,
        email_service: EmailService,  # <-- Injected from DI container
    ):
        self._auth_service = auth_service
        self._tenant_service = tenant_service
        self._invitation_service = invitation_service
        self._user_repository = user_repository
        self._password_service = password_service
        self._email_service = email_service  # <-- Store for use
    
    async def register_organization(
        self,
        command: OrganizationRegistrationCommand
    ) -> Tuple[User, Tenant]:
        """
        Register a new organization with admin user (self-serve).
        
        Returns:
            Tuple of (admin_user, tenant)
        """
        async with AsyncSessionLocal() as session:
            try:
                # Check if user already exists (by email)
                email = Email(command.email)
                existing_user = await self._user_repository.get_by_email(email)
                if existing_user:
                    raise ValueError("A user with this email already exists.")

                # Check if username already exists
                if command.username:
                    existing_username = await self._user_repository.get_by_username(command.username)
                    if existing_username:
                        raise ValueError("A user with this username already exists.")

                # Generate a new user ID inside the transaction
                new_user_id = UserId.generate()
                password_hash: str = self._password_service.hash_password(command.password)

                # Email verification
                email_verification_token = str(uuid4())
                email_verification_sent_at = datetime.now(timezone.utc)

                # Create the admin user first (without tenant_id yet)
                admin_user = User(
                    id=new_user_id,
                    email=email,
                    username=command.username,  # <-- Set username
                    first_name=command.first_name,
                    last_name=command.last_name,
                    password_hash=password_hash,
                    role=UserRole.org_admin(),
                    status=UserStatus.active(),
                    tenant_id=None,
                    team_id=None,
                    phone=None,
                    profile_picture_url=None,
                    bio=f"{command.job_title} at {command.organization_name}" if command.job_title else None,
                    is_email_verified=False,  # Require verification
                    email_verification_token=email_verification_token,
                    email_verification_sent_at=email_verification_sent_at,
                    job_title=command.job_title,
                    accept_terms=command.accept_terms,
                    accept_privacy=command.accept_privacy,
                    marketing_opt_in=command.marketing_opt_in
                )

                # Save the user (without tenant_id)
                admin_user = await self._user_repository.save(admin_user)

                # Create the tenant/organization with the new user's ID as owner_id
                tenant_name = TenantName(command.organization_name)
                tenant = await self._tenant_service.create_tenant(
                    name=tenant_name,
                    subscription_tier=command.subscription_tier,
                    slug=command.organization_slug,
                    owner_id=admin_user.id,
                    industry=command.industry,
                    organization_size=command.organization_size,
                    website=command.website
                )

                # Update the user with the tenant_id
                if tenant.id is not None:
                    admin_user.tenant_id = tenant.id.value  # Assign the UUID, not the TenantId object
                else:
                    raise ValueError("Tenant ID is None after tenant creation")
                admin_user = await self._user_repository.update(admin_user)

                # Send verification email
                template_service = EmailTemplateService()
                # Use the frontend_url from the injected email_service if available, else fallback to settings
                frontend_url = getattr(self._email_service, "base_url", None)
                if not frontend_url:
                    # fallback to OAuthConfig or settings if needed
                    try:
                        from infrastructure.config.oauth_config import OAuthConfig
                        frontend_url = OAuthConfig().frontend_url
                    except Exception:
                        frontend_url = "http://localhost:3000"
                verify_url = f"{frontend_url}/verify-email?token={email_verification_token}"
                html_content = template_service.env.get_template("welcome_verify_email.html").render(
                    first_name=admin_user.first_name,
                    organization_name=tenant.name,
                    verify_url=verify_url
                )
                subject = "Welcome to SalesOptimizer! Please verify your email"
                email_message = EmailMessage(
                    to_email=str(admin_user.email),
                    subject=subject,
                    html_content=html_content
                )
                await self._email_service.send_email(email_message)

                await session.commit()
                return admin_user, tenant

            except Exception as e:
                await session.rollback()
                raise Exception(f"Failed to register organization: {e}")
    
    async def complete_invitation_signup(
        self,
        invitation_token: str,
        first_name: str,
        last_name: str,
        password: str,
        job_title: Optional[str] = None
    ) -> Tuple[User, Tenant, str, str]:
        """
        Complete organization admin signup from invitation.
        
        This handles the case where a super admin invited an org admin,
        and the invited user is completing their account setup.
        """
        # Get invitation details
        from domain.organization.value_objects.invitation_token import InvitationToken
        
        invitation_token_obj = InvitationToken(invitation_token)
        invitation = await self._invitation_service.get_invitation_by_token(invitation_token_obj)
        
        if not invitation:
            raise ValueError("Invalid or expired invitation")
        
        if invitation.is_expired():
            raise ValueError("Invitation has expired")
        
        # Create the user account manually
        password_hash = self._password_service.hash_password(password)
        
        admin_user = User(
            id=UserId.generate(),
            email=invitation.email,
            username=None,
            first_name=first_name,
            last_name=last_name,
            password_hash=password_hash,
            role=UserRole.org_admin(),
            status=UserStatus.active(),
            tenant_id=invitation.tenant_id,
            team_id=None,
            phone=None,
            profile_picture_url=None,
            bio=f"{job_title} at {invitation.organization_name}" if job_title else None,
            is_email_verified=True
        )
        
        # Save the user
        admin_user = await self._user_repository.save(admin_user)
        
        # Accept the invitation (this will mark it as used)
        if admin_user.id is None:
            raise ValueError("User ID is None after saving")
        tenant = await self._invitation_service.accept_invitation(invitation, admin_user.id)
        
        # Generate tokens for immediate login
        access_token, refresh_token = await self._auth_service.create_tokens(admin_user)
        
        return admin_user, tenant, access_token, refresh_token
    
    async def verify_email(self, token: str) -> Tuple[str, Optional[str]]:
        import logging
        logger = logging.getLogger("verify-email-usecase")
        logger.info(f"[verify_email] Called with token: {token}")
        async with AsyncSessionLocal() as session:
            user = await self._user_repository.get_by_email_verification_token(token)
            if not user:
                logger.warning(f"[verify_email] No user found for token: {token}")
                return "fail", None
            logger.info(f"[verify_email] Found user: {user.username or user.email}, is_email_verified={user.is_email_verified}, token={user.email_verification_token}")
            if user.is_email_verified:
                logger.warning(f"[verify_email] User already verified: {user.username or user.email}")
                return "already_verified", user.username or str(user.email)
            user.is_email_verified = True
            user.email_verification_token = None
            await self._user_repository.update(user)
            await session.commit()
            logger.info(f"[verify_email] User verified and token cleared: {user.username or user.email}")
            return "success", user.username or str(user.email)
