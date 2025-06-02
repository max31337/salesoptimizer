from abc import ABC, abstractmethod
from typing import Optional
from domain.organization.entities.tenant import Tenant
from domain.organization.value_objects.user_id import UserId


class TenantRepository(ABC):
    """Repository interface for tenant persistence."""
    
    @abstractmethod
    async def save(self, tenant: Tenant) -> Tenant:
        """Save a tenant."""
        pass
    
    @abstractmethod
    async def get_by_id(self, tenant_id: UserId) -> Optional[Tenant]:
        """Get tenant by ID."""
        pass
    
    @abstractmethod
    async def get_by_slug(self, slug: str) -> Optional[Tenant]:
        """Get tenant by slug."""
        pass
    
    @abstractmethod
    async def update(self, tenant: Tenant) -> Tenant:
        """Update a tenant."""
        pass