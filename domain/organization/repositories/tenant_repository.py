from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from domain.organization.entities.tenant import Tenant


class TenantRepository(ABC):
    
    @abstractmethod
    async def create(self, tenant: Tenant) -> Tenant:
        """Create a new tenant."""
        pass
    
    @abstractmethod
    async def get_by_id(self, tenant_id: UUID) -> Optional[Tenant]:
        """Get tenant by ID."""
        pass
    
    @abstractmethod
    async def get_by_slug(self, slug: str) -> Optional[Tenant]:
        """Get tenant by slug."""
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Tenant]:
        """Get all tenants."""
        pass
    
    @abstractmethod
    async def update(self, tenant: Tenant) -> Tenant:
        """Update tenant."""
        pass
    
    @abstractmethod
    async def delete(self, tenant_id: UUID) -> bool:
        """Delete tenant."""
        pass
    
    @abstractmethod
    async def exists_by_slug(self, slug: str) -> bool:
        """Check if tenant exists by slug."""
        pass