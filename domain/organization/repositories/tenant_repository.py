from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from domain.organization.entities.tenant import Tenant


class TenantRepository(ABC):
    @abstractmethod
    def create(self, tenant: Tenant) -> Tenant:
        pass
    
    @abstractmethod
    def get_by_id(self, tenant_id: UUID) -> Optional[Tenant]:
        pass
    
    @abstractmethod
    def get_by_slug(self, slug: str) -> Optional[Tenant]:
        pass
    
    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Tenant]:
        pass
    
    @abstractmethod
    def update(self, tenant: Tenant) -> Tenant:
        pass
    
    @abstractmethod
    def delete(self, tenant_id: UUID) -> bool:
        pass
    
    @abstractmethod
    def exists_by_slug(self, slug: str) -> bool:
        pass