from typing import List, Optional
from uuid import UUID

from domain.organization.entities.tenant import Tenant
from domain.organization.repositories.tenant_repository import TenantRepository


class TenantUseCases:
    def __init__(self, tenant_repository: TenantRepository):
        self.tenant_repository = tenant_repository
    
    async def get_tenant_by_id(self, tenant_id: UUID) -> Optional[Tenant]:
        """Get tenant by ID."""
        return await self.tenant_repository.get_by_id(tenant_id)
    
    async def get_tenant_by_slug(self, slug: str) -> Optional[Tenant]:
        """Get tenant by slug."""
        return await self.tenant_repository.get_by_slug(slug)
    
    async def get_all_tenants(self, skip: int = 0, limit: int = 100) -> List[Tenant]:
        """Get all tenants."""
        return await self.tenant_repository.get_all(skip, limit)
    
    async def create_tenant(self, tenant: Tenant) -> Tenant:
        """Create a new tenant."""
        return await self.tenant_repository.create(tenant)
    
    async def update_tenant(self, tenant: Tenant) -> Tenant:
        """Update tenant."""
        return await self.tenant_repository.update(tenant)
    
    async def delete_tenant(self, tenant_id: UUID) -> bool:
        """Delete tenant."""
        return await self.tenant_repository.delete(tenant_id)