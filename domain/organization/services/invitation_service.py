from typing import Tuple, List, Optional
from domain.organization.entities.invitation import Invitation
from domain.organization.entities.tenant import Tenant
from domain.organization.value_objects.email import Email
from domain.organization.value_objects.user_id import UserId
from domain.organization.value_objects.tenant_id import TenantId
from domain.organization.value_objects.tenant_name import TenantName
from domain.organization.value_objects.invitation_token import InvitationToken
from domain.organization.repositories.invitation_repository import InvitationRepository
from domain.organization.repositories.tenant_repository import TenantRepository
from domain.organization.repositories.user_repository import UserRepository
from domain.shared.services.email_service import EmailService
from domain.organization.entities.user import UserRole


class InvitationService:
    """Domain service for invitation operations."""
    
    def __init__(
        self,
        invitation_repository: InvitationRepository,
        tenant_repository: TenantRepository,
        user_repository: UserRepository,
        email_service: EmailService
    ):
        self._invitation_repository = invitation_repository
        self._tenant_repository = tenant_repository
        self._user_repository = user_repository
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
        
        # Ensure the created tenant has a valid id before proceeding
        tenant_id_value = getattr(created_tenant.id, "value", None)
        if tenant_id_value is None:
            raise ValueError("Created tenant does not have a valid id.")
        # Create invitation with the created tenant
        invitation = Invitation.create_org_admin_invitation(
            email, 
            invited_by_id, 
            organization_name,
            tenant_id_value
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

    async def create_user_invitation(
        self,
        email: Email,
        invited_by_id: UserId,
        tenant_id: TenantId,
        role: UserRole,
        invited_by_name: str = "Your administrator"
    ) -> Invitation:
        """Create and send an invitation for a new user to join an existing organization."""
        # Check if there's already an active invitation for this email
        existing_invitation = await self._invitation_repository.get_by_email(email)
        if existing_invitation and existing_invitation.is_valid():
            raise ValueError(f"Active invitation already exists for {email}")

        # Check if a user with this email already exists in the tenant
        existing_user = await self._user_repository.get_by_email(email)
        if existing_user and existing_user.tenant_id == tenant_id.value:
            raise ValueError(f"User with email {email} already exists in this organization.")

        # Create invitation
        invitation = Invitation.create_user_invitation(
            email=email,
            invited_by_id=invited_by_id,
            tenant_id=tenant_id.value,
            role=role
        )
        created_invitation = await self._invitation_repository.save(invitation)

        # Send invitation email
        tenant = await self._tenant_repository.get_by_id(tenant_id)
        organization_name = str(tenant.name) if tenant and tenant.name else "Your Organization"

        email_sent = await self._email_service.send_invitation_email(
            to_email=str(email),
            organization_name=organization_name,
            invitation_token=created_invitation.token.value,
            invited_by_name=invited_by_name,
            expires_at=str(created_invitation.expires_at)
        )

        if not email_sent:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to send invitation email to {email}")

        return created_invitation

    async def get_all_invitations(self) -> List[Invitation]:
        """Get all invitations."""
        return await self._invitation_repository.get_all()
    
    async def get_invitation_by_token(self, token: InvitationToken) -> Optional[Invitation]:
        """Get invitation by token."""
        return await self._invitation_repository.get_by_token(token)
    
    async def accept_invitation(
        self,
        invitation: Invitation,
        user_id: UserId
    ) -> Tenant:
        """Accept invitation and set user as tenant owner."""
        if invitation.is_used:
            raise ValueError("Invitation has already been used")
        
        if invitation.is_expired():
            raise ValueError("Invitation has expired")
        
        # Mark invitation as used
        invitation.mark_as_used()
        await self._invitation_repository.update(invitation)
        # Get the tenant and set the user as owner
        tenant = await self._tenant_repository.get_by_id(TenantId(invitation.tenant_id))
        if not tenant:
            raise ValueError("Associated tenant not found")
        
        # Update tenant owner
        tenant.set_owner(user_id)
        updated_tenant = await self._tenant_repository.update(tenant)
        
        return updated_tenant
    
    async def delete_invitation(self, invitation_id: UserId) -> bool:
        """Delete an invitation."""
        return await self._invitation_repository.delete(invitation_id)
