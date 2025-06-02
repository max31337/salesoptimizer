from typing import Annotated
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status

from infrastructure.dependencies.service_container import get_application_service
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
    """
    Create organization admin invitation and create the organization/tenant (SuperAdmin only).
    
    - **email**: Email address of the organization admin to invite
    - **organization_name**: Name of the organization/company
    - **subscription_tier**: Subscription level (basic, pro, enterprise) - defaults to basic
    - **slug**: Custom URL slug for the organization (auto-generated if not provided)
    """
    try:
        command = CreateInvitationCommand(
            email=request.email,
            organization_name=request.organization_name,
            subscription_tier=request.subscription_tier,
            slug=request.slug
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
                id=tenant.id.value,
                name=tenant.name.value,
                slug=tenant.slug,
                subscription_tier=tenant.subscription_tier,
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
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )