from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from domain.organization.entities.tenant import Tenant
from domain.organization.value_objects.user_id import UserId
from domain.organization.value_objects.tenant_name import TenantName


class TenantRepository(ABC):
    """Repository interface for tenant operations."""
    
    @abstractmethod
    async def save(self, tenant: Tenant) -> Tenant:
        """Save a new tenant."""
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
    async def get_by_name(self, name: TenantName) -> Optional[Tenant]:
        """Get tenant by name."""
        pass
    
    @abstractmethod
    async def get_by_owner(self, owner_id: UserId) -> List[Tenant]:
        """Get tenants owned by a specific user."""
        pass
    
    @abstractmethod
    async def get_all_active(self) -> List[Tenant]:
        """Get all active tenants."""
        pass
    
    @abstractmethod
    async def update(self, tenant: Tenant) -> Tenant:
        """Update existing tenant."""
        pass
    
    @abstractmethod
    async def delete(self, tenant_id: UUID) -> bool:
        """Delete tenant."""
        pass
    
    @abstractmethod
    async def exists_by_slug(self, slug: str) -> bool:
        """Check if tenant exists by slug."""
        pass
    
    @abstractmethod
    async def exists_by_name(self, name: TenantName) -> bool:
        """Check if tenant exists by name."""
        pass