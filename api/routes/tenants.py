from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from application.dependencies.service_dependencies import get_application_service
from application.services.application_service import ApplicationService
from application.dtos.tenant_dto import TenantCreateDTO, TenantUpdateDTO, TenantResponseDTO
from api.dependencies.auth import require_super_admin, require_org_admin, get_current_user
from domain.organization.entities.user import User

router = APIRouter(prefix="/tenants", tags=["tenants"])

@router.post("/", response_model=TenantResponseDTO, status_code=status.HTTP_201_CREATED)
def create_tenant(
    tenant_data: TenantCreateDTO,
    current_user: Annotated[User, Depends(require_super_admin)],
    app_service: Annotated[ApplicationService, Depends(get_application_service)]
):
    """Create a new tenant (Super Admin only)."""
    try:
        return app_service.tenant_use_cases.create_tenant(tenant_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{tenant_id}", response_model=TenantResponseDTO)
def get_tenant(
    tenant_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    app_service: Annotated[ApplicationService, Depends(get_application_service)]
):
    """Get tenant by ID."""
    tenant = app_service.tenant_use_cases.get_tenant_by_id(tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    return tenant

@router.put("/{tenant_id}", response_model=TenantResponseDTO)
def update_tenant(
    tenant_id: UUID,
    tenant_data: TenantUpdateDTO,
    current_user: Annotated[User, Depends(require_org_admin)],
    app_service: Annotated[ApplicationService, Depends(get_application_service)]
):
    """Update tenant."""
    # Check access permissions
    if not current_user.can_access_tenant(tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this tenant"
        )
    
    tenant = app_service.tenant_use_cases.update_tenant(tenant_id, tenant_data)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    return tenant

@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tenant(
    tenant_id: UUID,
    current_user: Annotated[User, Depends(require_super_admin)],
    app_service: Annotated[ApplicationService, Depends(get_application_service)]
):
    """Delete tenant (Super Admin only)."""
    if not app_service.tenant_use_cases.delete_tenant(tenant_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )