from typing import Tuple
from domain.organization.entities.invitation import Invitation
from domain.organization.entities.user import User
from domain.organization.entities.tenant import Tenant
from domain.organization.services.invitation_service import InvitationService
from domain.organization.services.auth_service import AuthService
from domain.organization.value_objects.email import Email
from application.commands.invitation_command import CreateInvitationCommand


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
        return await self._invitation_service.create_org_admin_invitation_with_tenant(
            email,
            current_user.id,
            command.organization_name
        )