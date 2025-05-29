from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from domain.organization.entities.team import Team

class TeamRepository(ABC):
    """Abstract repository for team operations."""
    
    @abstractmethod
    async def get_by_id(self, team_id: UUID) -> Optional[Team]:
        """Get team by ID."""
        pass
    
    @abstractmethod
    async def get_by_name(self, tenant_id: UUID, name: str) -> Optional[Team]:
        """Get team by name within a tenant."""
        pass
    
    @abstractmethod
    async def create(self, team: Team) -> Team:
        """Create new team."""
        pass
    
    @abstractmethod
    async def update(self, team: Team) -> Team:
        """Update existing team."""
        pass
    
    @abstractmethod
    async def delete(self, team_id: UUID) -> bool:
        """Delete team by ID."""
        pass
    
    @abstractmethod
    async def list_by_tenant(self, tenant_id: UUID) -> List[Team]:
        """List all teams in a tenant."""
        pass
    
    @abstractmethod
    async def list_by_manager(self, manager_id: UUID) -> List[Team]:
        """List all teams managed by a specific manager."""
        pass