from typing import Tuple
from domain.organization.entities.invitation import Invitation
from domain.organization.entities.tenant import Tenant
from domain.organization.value_objects.email import Email
from domain.organization.value_objects.user_id import UserId
from domain.organization.value_objects.tenant_name import TenantName
from domain.organization.repositories.invitation_repository import InvitationRepository
from domain.organization.repositories.tenant_repository import TenantRepository
from domain.shared.services.email_service import EmailService


class InvitationService:
    """Domain service for invitation operations."""
    
    def __init__(
        self,
        invitation_repository: InvitationRepository,
        tenant_repository: TenantRepository,
        email_service: EmailService
    ):
        self._invitation_repository = invitation_repository
        self._tenant_repository = tenant_repository
        self._email_service = email_service
    
    async def create_org_admin_invitation_with_tenant(
        self,
        email: Email,
        invited_by_id: UserId,
        organization_name: str,
        subscription_tier: str = "basic",
        custom_slug: str | None = None,
        invited_by_name: str = "SalesOptimizer Admin"
    ) -> Tuple[Invitation, Tenant]:
        """Create invitation for organization admin and create the tenant/organization."""
        # Check if there's already an active invitation for this email
        existing_invitation = await self._invitation_repository.get_by_email(email)
        if existing_invitation and existing_invitation.is_valid():
            raise ValueError(f"Active invitation already exists for {email}")
        
        # Check if slug is already taken (if custom slug provided)
        if custom_slug:
            existing_tenant = await self._tenant_repository.get_by_slug(custom_slug)
            if existing_tenant:
                raise ValueError(f"Slug '{custom_slug}' is already taken")
        
        # Create the tenant/organization first
        tenant = Tenant.create(
            name=TenantName(organization_name),
            subscription_tier=subscription_tier,
            slug=custom_slug,  # Will auto-generate if None
            owner_id=None  # Will be set when invitation is accepted
        )
        created_tenant = await self._tenant_repository.save(tenant)
        
        # Create invitation with the created tenant
        invitation = Invitation.create_org_admin_invitation(
            email, 
            invited_by_id, 
            organization_name,
            created_tenant.id.value
        )
        
        created_invitation = await self._invitation_repository.save(invitation)
        
        # Send invitation email
        email_sent = await self._email_service.send_invitation_email(
            to_email=str(email),
            organization_name=organization_name,
            invitation_token=created_invitation.token.value,
            invited_by_name=invited_by_name,
            expires_at=str(created_invitation.expires_at)
        )
        
        if not email_sent:
            # Log warning but don't fail the operation
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to send invitation email to {email}")
        
        return created_invitation, created_tenant
    
    async def accept_invitation(
        self,
        invitation: Invitation,
        user_id: UserId
    ) -> Tenant:
        """Accept invitation and set user as tenant owner."""
        # Mark invitation as used
        invitation.mark_as_used()
        await self._invitation_repository.update(invitation)
        
        # Get the tenant and set the owner
        tenant = await self._tenant_repository.get_by_id(UserId(invitation.tenant_id))
        if not tenant:
            raise ValueError("Tenant not found for invitation")
        
        # Set the user as tenant owner
        tenant.set_owner(user_id)
        updated_tenant = await self._tenant_repository.update(tenant)
        
        return updated_tenant