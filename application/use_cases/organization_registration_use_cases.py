from typing import Tuple, Optional

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


class OrganizationRegistrationUseCases:
    """Use cases for self-serve organization registration."""
    
    def __init__(
        self,
        auth_service: AuthService,
        tenant_service: TenantService,
        invitation_service: InvitationService,
        user_repository: UserRepository,
        password_service: PasswordService
    ):
        self._auth_service = auth_service
        self._tenant_service = tenant_service
        self._invitation_service = invitation_service
        self._user_repository = user_repository
        self._password_service = password_service
    
    async def register_organization(
        self, 
        command: OrganizationRegistrationCommand
    ) -> Tuple[User, Tenant, str, str]:
        """
        Register a new organization with admin user (self-serve).
        
        Returns:
            Tuple of (admin_user, tenant, access_token, refresh_token)
        """
        try:
            # Check if user already exists
            email = Email(command.email)
            existing_user = await self._user_repository.get_by_email(email)
            if existing_user:
                raise ValueError(f"User with email {command.email} already exists")
            
            # Create the organization/tenant first
            tenant_name = TenantName(command.organization_name)
            tenant = await self._tenant_service.create_tenant(
                name=tenant_name,
                subscription_tier=command.subscription_tier
            )
            
            # Create the admin user manually
            password_hash = self._password_service.hash_password(command.password)
            
            admin_user = User(
                id=UserId.generate(),
                email=email,
                username=None,
                first_name=command.first_name,
                last_name=command.last_name,
                password_hash=password_hash,
                role=UserRole.org_admin(),
                status=UserStatus.active(),
                tenant_id=tenant.id.value,
                team_id=None,
                phone=None,
                profile_picture_url=None,
                bio=f"{command.job_title} at {command.organization_name}" if command.job_title else None,
                is_email_verified=True  # Auto-verify for self-registration
            )
            
            # Save the user
            admin_user = await self._user_repository.save(admin_user)
            
            # Generate tokens for immediate login
            access_token, refresh_token = await self._auth_service.create_tokens(admin_user)
            
            # TODO: Send welcome email to admin user
            # TODO: Send notification to super admins about new organization
            # TODO: Store additional metadata (industry, size, etc.) in tenant settings
            
            return admin_user, tenant, access_token, refresh_token
            
        except Exception as e:
            # If anything fails, we should clean up any partially created resources
            # This would be handled by a proper transaction/unit of work pattern
            raise e
    
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
