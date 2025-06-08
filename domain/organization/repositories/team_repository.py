from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from infrastructure.db.models.team_model import TeamModel


class TeamRepository(ABC):
    """Repository interface for team operations."""
    
    @abstractmethod
    async def get_by_id(self, team_id: UUID) -> Optional[TeamModel]:
        """Get team by ID."""
        pass
    
    @abstractmethod
    async def get_by_tenant(self, tenant_id: UUID) -> List[TeamModel]:
        """Get all teams for a tenant."""
        pass
    
    @abstractmethod
    async def save(self, team: TeamModel) -> TeamModel:
        """Save team."""
        pass
    
    @abstractmethod
    async def update(self, team: TeamModel) -> TeamModel:
        """Update team."""
        pass
    
    @abstractmethod
    async def delete(self, team_id: UUID) -> bool:
        """Delete team."""
        pass
