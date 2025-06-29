from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime

from application.services.application_service import ApplicationService
from application.dtos.invitation_dto import (
    CreateInvitationRequest,
    InvitationResponse,
    InvitationWithTenantResponse,
    TenantResponse
)
from application.commands.invitation_command import CreateInvitationCommand
from domain.organization.entities.user import User
from infrastructure.dependencies.service_container import get_application_service
from api.dependencies.auth import get_current_user_from_cookie  

router = APIRouter(prefix="/invitations", tags=["invitations"])


@router.post("/", response_model=InvitationWithTenantResponse)
async def create_org_admin_invitation_with_tenant(
    request: CreateInvitationRequest,
    app_service: Annotated[ApplicationService, Depends(get_application_service)],
    current_user: User = Depends(get_current_user_from_cookie)  # Use cookie auth instead
) -> InvitationWithTenantResponse:
    """
    Create organization admin invitation and create the organization/tenant (SuperAdmin only).
    
    - **email**: Email address of the organization admin to invite
    - **organization_name**: Name of the organization/company
    - **subscription_tier**: Subscription level (basic, pro, enterprise) - defaults to basic
    - **slug**: Custom URL slug for the organization (auto-generated if not provided)
    """
    
    # Check permissions manually since we're using cookie auth
    if not current_user.can_create_invitations() or not current_user.can_create_tenants():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create invitations and tenants"
        )
    
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
        
        assert tenant.id is not None

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
                name=tenant.name,
                slug=tenant.slug if tenant.slug else "",
                subscription_tier=tenant.subscription_tier if tenant.subscription_tier else "basic",
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


@router.get("/", response_model=List[InvitationResponse])
async def get_invitations(
    app_service: Annotated[ApplicationService, Depends(get_application_service)],
    current_user: User = Depends(get_current_user_from_cookie)  # Use cookie auth
) -> List[InvitationResponse]:
    """Get all invitations (SuperAdmin only)."""
    if not current_user.can_create_invitations():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view invitations"
        )
    
    try:
        invitations = await app_service.invitation_use_cases.list_invitations()
        return [
            InvitationResponse(
                id=inv.id.value,
                email=str(inv.email),
                role=inv.role.value,
                token=inv.token.value,
                invited_by_id=inv.invited_by_id.value,
                organization_name=inv.organization_name,
                tenant_id=inv.tenant_id,
                expires_at=inv.expires_at,
                is_used=inv.is_used,
                used_at=inv.used_at,
                created_at=inv.created_at or datetime.now()
            )
            for inv in invitations
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


# TODO: Implement delete_invitation method in InvitationUseCases class
# @router.delete("/{invitation_id}")
# async def delete_invitation(
#     invitation_id: str,
#     app_service: Annotated[ApplicationService, Depends(get_application_service)],
#     current_user: User = Depends(get_current_user_from_cookie)  # Use cookie auth
# ):
#     """Delete an invitation (SuperAdmin only)."""
#     if not current_user.can_create_invitations():
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Insufficient permissions to delete invitations"
#         )
#     
#     try:
#         success = await app_service.invitation_use_cases.delete_invitation(invitation_id)
#         if not success:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Invitation not found"
#             )
#         return {"message": "Invitation deleted successfully"}
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"An unexpected error occurred: {str(e)}"
#         )
