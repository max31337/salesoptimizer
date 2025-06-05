from abc import ABC, abstractmethod
from typing import Optional, List
from domain.organization.entities.tenant import Tenant
from domain.organization.value_objects.tenant_id import TenantId
from domain.organization.value_objects.user_id import UserId


class TenantRepository(ABC):
    """Repository for tenant operations."""
    
    @abstractmethod
    async def save(self, tenant: Tenant) -> Tenant:
        """Save tenant."""
        pass
    
    @abstractmethod
    async def get_by_id(self, tenant_id: TenantId) -> Optional[Tenant]:
        """Get tenant by ID."""
        pass
    
    @abstractmethod
    async def get_by_slug(self, slug: str) -> Optional[Tenant]:
        """Get tenant by slug."""
        pass
    
    @abstractmethod
    async def update(self, tenant: Tenant) -> Tenant:
        """Update tenant."""
        pass
    
    @abstractmethod
    async def delete(self, tenant_id: TenantId) -> bool:
        """Delete tenant."""
        pass
    
    @abstractmethod
    async def get_by_owner(self, owner_id: UserId) -> List[Tenant]:
        """Get tenants owned by user."""
        pass