from typing import Optional
from uuid import UUID

from domain.organization.entities.tenant import Tenant
from infrastructure.repositories.tenant_repository_impl import TenantRepositoryImpl
from application.dtos.tenant_dto import TenantCreateDTO, TenantUpdateDTO, TenantResponseDTO


class TenantUseCases:
    def __init__(self, tenant_repository: TenantRepositoryImpl):
        self.tenant_repository = tenant_repository
    
    def create_tenant(self, tenant_data: TenantCreateDTO) -> TenantResponseDTO:
        """Create a new tenant."""
        # Check if slug already exists
        if self.tenant_repository.exists_by_slug(tenant_data.slug):
            raise ValueError("Tenant slug already exists")
        
        # Create tenant entity
        tenant = Tenant(
            name=tenant_data.name,
            slug=tenant_data.slug,
            subscription_tier=tenant_data.subscription_tier,
            settings=tenant_data.settings or {}
        )
        
        # Save to database
        created_tenant = self.tenant_repository.create(tenant)
        
        return TenantResponseDTO.from_entity(created_tenant)
    
    def get_tenant_by_id(self, tenant_id: UUID) -> Optional[TenantResponseDTO]:
        """Get tenant by ID."""
        tenant = self.tenant_repository.get_by_id(tenant_id)
        if not tenant:
            return None
        
        return TenantResponseDTO.from_entity(tenant)
    
    def update_tenant(self, tenant_id: UUID, tenant_data: TenantUpdateDTO) -> Optional[TenantResponseDTO]:
        """Update tenant."""
        tenant = self.tenant_repository.get_by_id(tenant_id)
        if not tenant:
            return None
        
        # Update tenant fields
        for field, value in tenant_data.model_dump(exclude_unset=True).items():
            if hasattr(tenant, field):
                setattr(tenant, field, value)
        
        updated_tenant = self.tenant_repository.update(tenant)
        return TenantResponseDTO.from_entity(updated_tenant)
    
    def delete_tenant(self, tenant_id: UUID) -> bool:
        """Delete tenant."""
        return self.tenant_repository.delete(tenant_id)