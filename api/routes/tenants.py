from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from infrastructure.db.base import get_db
from infrastructure.repositories.tenant_repository_impl import TenantRepositoryImpl
from api.dtos.tenant_dto import TenantCreateDTO, TenantUpdateDTO, TenantResponseDTO
from api.dependencies.auth import require_super_admin, require_org_admin, get_current_user
from domain.entities.user import User
from domain.entities.tenant import Tenant

router = APIRouter(prefix="/tenants", tags=["tenants"])

def get_tenant_repository(db: Session = Depends(get_db)) -> TenantRepositoryImpl:
    return TenantRepositoryImpl(db)

@router.post("/", response_model=TenantResponseDTO, status_code=status.HTTP_201_CREATED)
def create_tenant(
    tenant_data: TenantCreateDTO,
    current_user: User = Depends(require_super_admin),
    tenant_repo: TenantRepositoryImpl = Depends(get_tenant_repository)
):
    """Create a new tenant (Super Admin only)."""
    # Check if slug already exists
    if tenant_repo.exists_by_slug(tenant_data.slug):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant slug already exists"
        )
    
    # Create tenant entity
    tenant = Tenant(
        name=tenant_data.name,
        slug=tenant_data.slug,
        subscription_tier=tenant_data.subscription_tier,
        settings=tenant_data.settings or {}
    )
    
    # Save to database
    created_tenant = tenant_repo.create(tenant)
    
    return TenantResponseDTO.from_entity(created_tenant)

@router.get("/{tenant_id}", response_model=TenantResponseDTO)
def get_tenant(
    tenant_id: UUID,
    current_user: User = Depends(get_current_user),
    tenant_repo: TenantRepositoryImpl = Depends(get_tenant_repository)
):
    """Get tenant by ID."""
    # Check access permissions
    if not current_user.can_access_tenant(tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this tenant"
        )
    
    tenant = tenant_repo.get_by_id(tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    return TenantResponseDTO.from_entity(tenant)

@router.get("/", response_model=List[TenantResponseDTO])
def get_tenants(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_super_admin),
    tenant_repo: TenantRepositoryImpl = Depends(get_tenant_repository)
):
    """Get all tenants (Super Admin only)."""
    tenants = tenant_repo.get_all(skip=skip, limit=limit)
    return [TenantResponseDTO.from_entity(tenant) for tenant in tenants]

@router.put("/{tenant_id}", response_model=TenantResponseDTO)
def update_tenant(
    tenant_id: UUID,
    tenant_data: TenantUpdateDTO,
    current_user: User = Depends(require_org_admin),
    tenant_repo: TenantRepositoryImpl = Depends(get_tenant_repository)
):
    """Update tenant."""
    # Check access permissions
    if not current_user.can_access_tenant(tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this tenant"
        )
    
    tenant = tenant_repo.get_by_id(tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    # Update tenant fields
    for field, value in tenant_data.model_dump(exclude_unset=True).items():
        if hasattr(tenant, field):
            setattr(tenant, field, value)
    
    updated_tenant = tenant_repo.update(tenant)
    return TenantResponseDTO.from_entity(updated_tenant)

@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tenant(
    tenant_id: UUID,
    current_user: User = Depends(require_super_admin),
    tenant_repo: TenantRepositoryImpl = Depends(get_tenant_repository)
):
    """Delete tenant (Super Admin only)."""
    if not tenant_repo.delete(tenant_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )