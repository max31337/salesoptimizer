from typing import Optional
from uuid import UUID

from domain.organization.entities.tenant import Tenant
from domain.organization.repositories.tenant_repository import TenantRepository
from domain.organization.value_objects.user_id import UserId
from domain.organization.value_objects.tenant_name import TenantName
from domain.organization.value_objects.tenant_id import TenantId


class TenantService:
    """Domain service for tenant operations."""
    
    def __init__(self, tenant_repository: TenantRepository):
        self._tenant_repository = tenant_repository

    async def get_tenant_by_id(self, tenant_id: UUID) -> Optional[Tenant]:
        """Get a tenant by ID."""
        return await self._tenant_repository.get_by_id(TenantId(tenant_id))
    
    async def create_tenant(
        self,
        name: TenantName,
        owner_id: Optional[UserId] = None,
        subscription_tier: str = "basic"
    ) -> Tenant:
        """Create a new tenant."""
        # Check if tenant with same name already exists
        existing_tenant = await self._tenant_repository.get_by_name(name.value)
        if existing_tenant:
            raise ValueError(f"Tenant with name '{name.value}' already exists")
        
        # Create the tenant
        tenant = Tenant.create(name, owner_id, subscription_tier) #type: ignore
        return await self._tenant_repository.save(tenant)
    
  
    async def update_tenant_name(self, tenant_id: UUID, name: TenantName) -> Tenant:
        """Update tenant name."""
        # Check if another tenant with same name exists
        existing_tenant = await self._tenant_repository.get_by_name(name.value)
        if existing_tenant and existing_tenant.id and existing_tenant.id.value != tenant_id:
            raise ValueError(f"Tenant with name '{name.value}' already exists")
        
        tenant = await self._tenant_repository.get_by_id(TenantId(tenant_id))
        if not tenant:
            raise ValueError("Tenant not found")
        
        tenant.update_name(name)
        return await self._tenant_repository.update(tenant)
    async def deactivate_tenant(self, tenant_id: UUID) -> Tenant:
        """Deactivate a tenant."""
        tenant = await self._tenant_repository.get_by_id(TenantId(tenant_id))
        if not tenant:
            raise ValueError("Tenant not found")
        
        tenant.deactivate()
        return await self._tenant_repository.update(tenant)
    async def activate_tenant(self, tenant_id: UUID) -> Tenant:
        """Activate a tenant."""
        tenant = await self._tenant_repository.get_by_id(TenantId(tenant_id))
        if not tenant:
            raise ValueError("Tenant not found")
        
        tenant.activate()
        return await self._tenant_repository.update(tenant)