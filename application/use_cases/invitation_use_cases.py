from typing import Tuple, List
from application.commands.invitation_command import CreateInvitationCommand
from domain.organization.entities.invitation import Invitation
from domain.organization.entities.tenant import Tenant
from domain.organization.entities.user import User
from domain.organization.services.invitation_service import InvitationService
from domain.organization.services.auth_service import AuthService
from domain.organization.value_objects.email import Email


class InvitationUseCases:
    """Invitation use cases."""
    
    def __init__(
        self,
        invitation_service: InvitationService,
        auth_service: AuthService
    ):
        self._invitation_service = invitation_service
        self._auth_service = auth_service
    
    async def create_org_admin_invitation_with_tenant(
        self,
        command: CreateInvitationCommand,
        current_user: User
    ) -> Tuple[Invitation, Tenant]:
        """Create organization admin invitation and create the tenant/organization."""
        # Check permissions for both invitation creation AND tenant creation
        if not current_user.can_create_invitations():
            raise PermissionError("Permission required: create invitations")
        
        if not current_user.can_create_tenants():
            raise PermissionError("Permission required: create tenants")
        
        if current_user.id is None:
            raise ValueError("User ID cannot be None")
        
        email = Email(command.email)
        
        # Get invited by name
        invited_by_name = f"{current_user.first_name} {current_user.last_name}".strip()
        if not invited_by_name:
            invited_by_name = str(current_user.email)
        
        return await self._invitation_service.create_org_admin_invitation_with_tenant(
            email,
            current_user.id,
            command.organization_name,
            command.subscription_tier,
            command.slug,
            invited_by_name
        )
    
    async def list_invitations(self) -> List[Invitation]:
        """Get all invitations."""
        return await self._invitation_service.get_all_invitations()
    
    async def get_invitation_by_token(self, token: str) -> Invitation:
        """Get invitation by token."""
        from domain.organization.value_objects.invitation_token import InvitationToken
        invitation_token = InvitationToken(token)
        invitation = await self._invitation_service.get_invitation_by_token(invitation_token)
        if not invitation:
            raise ValueError("Invitation not found")
        return invitation
    
    async def accept_invitation(self, token: str, user_id: str) -> Tenant:
        """Accept invitation and assign user to tenant."""
        from domain.organization.value_objects.invitation_token import InvitationToken
        from domain.organization.value_objects.user_id import UserId
        from uuid import UUID
        
        invitation_token = InvitationToken(token)
        user_id_obj = UserId(UUID(user_id))
        
        invitation = await self._invitation_service.get_invitation_by_token(invitation_token)
        if not invitation:
            raise ValueError("Invitation not found")
        
        return await self._invitation_service.accept_invitation(invitation, user_id_obj)
    
    async def delete_invitation(self, invitation_id: str) -> bool:
        """Delete an invitation."""
        from domain.organization.value_objects.user_id import UserId
        from uuid import UUID
        
        invitation_id_obj = UserId(UUID(invitation_id))
        return await self._invitation_service.delete_invitation(invitation_id_obj)