from typing import Annotated
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status

from infrastructure.dependencies.service_container import get_application_service  # Updated import
from application.services.application_service import ApplicationService
from application.dtos.invitation_dto import (
    CreateInvitationRequest,
    InvitationWithTenantResponse,
    InvitationResponse,
    TenantResponse
)
from application.commands.invitation_command import CreateInvitationCommand
from api.dependencies.auth import require_invitation_and_tenant_creation
from domain.organization.entities.user import User

router = APIRouter(prefix="/invitations", tags=["invitations"])


@router.post("/", response_model=InvitationWithTenantResponse)
async def create_org_admin_invitation_with_tenant(
    request: CreateInvitationRequest,
    app_service: Annotated[ApplicationService, Depends(get_application_service)],
    current_user: User = Depends(require_invitation_and_tenant_creation)
) -> InvitationWithTenantResponse:
    """Create organization admin invitation and create the organization/tenant (SuperAdmin only)."""
    try:
        command = CreateInvitationCommand(
            email=request.email,
            organization_name=request.organization_name
        )
        invitation, tenant = await app_service.invitation_use_cases.create_org_admin_invitation_with_tenant(
            command,
            current_user
        )
        
        return InvitationWithTenantResponse(
            invitation=InvitationResponse(
                id=invitation.id.value,
                email=str(invitation.email),
                role=invitation.role.value,
                token=invitation.token.value,
                invited_by_id=invitation.invited_by_id.value,
                organization_name=invitation.organization_name,
                tenant_id=invitation.tenant_id,
                expires_at=invitation.expires_at,
                is_used=invitation.is_used,
                used_at=invitation.used_at,
                created_at=invitation.created_at or datetime.now()
            ),
            tenant=TenantResponse(
                id=tenant.id.value,  # type: ignore
                name=tenant.name.value,
                slug=tenant.slug,
                is_active=tenant.is_active,
                owner_id=tenant.owner_id.value if tenant.owner_id else None,
                created_at=tenant.created_at or datetime.now()
            )
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )