from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from domain.organization.entities.team import Team
from domain.organization.repositories.team_repository import TeamRepository
from infrastructure.db.models.team_model import TeamModel

class TeamRepositoryImpl(TeamRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, team_id: UUID) -> Optional[Team]:
        """Get team by ID."""
        stmt = select(TeamModel).where(TeamModel.id == team_id)
        result = await self.session.execute(stmt)
        team_model = result.scalar_one_or_none()
        
        if not team_model:
            return None
            
        return self._model_to_entity(team_model)
    
    async def get_by_name(self, tenant_id: UUID, name: str) -> Optional[Team]:
        """Get team by name within a tenant."""
        stmt = select(TeamModel).where(
            and_(
                TeamModel.tenant_id == tenant_id,
                TeamModel.name == name
            )
        )
        result = await self.session.execute(stmt)
        team_model = result.scalar_one_or_none()
        
        if not team_model:
            return None
            
        return self._model_to_entity(team_model)
    
    async def create(self, team: Team) -> Team:
        """Create new team."""
        team_model = self._entity_to_model(team)
        self.session.add(team_model)
        await self.session.flush()  # Get the ID without committing
        
        return self._model_to_entity(team_model)
    
    async def update(self, team: Team) -> Team:
        """Update existing team."""
        stmt = select(TeamModel).where(TeamModel.id == team.id)
        result = await self.session.execute(stmt)
        team_model = result.scalar_one_or_none()
        
        if not team_model:
            raise ValueError(f"Team with ID {team.id} not found")
        
        # Update model with entity data
        setattr(team_model, "name", team.name)
        setattr(team_model, "description", team.description)
        setattr(team_model, "manager_id", team.manager_id)
        setattr(team_model, "is_active", team.is_active)
        setattr(team_model, "updated_at", team.updated_at)

        await self.session.flush()
        return self._model_to_entity(team_model)
    
    async def delete(self, team_id: UUID) -> bool:
        """Delete team by ID."""
        stmt = select(TeamModel).where(TeamModel.id == team_id)
        result = await self.session.execute(stmt)
        team_model = result.scalar_one_or_none()
        
        if not team_model:
            return False
        
        await self.session.delete(team_model)
        return True
    
    async def list_by_tenant(self, tenant_id: UUID) -> List[Team]:
        """List all teams in a tenant."""
        stmt = select(TeamModel).where(TeamModel.tenant_id == tenant_id)
        result = await self.session.execute(stmt)
        team_models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in team_models]
    
    async def list_by_manager(self, manager_id: UUID) -> List[Team]:
        """List all teams managed by a specific manager."""
        stmt = select(TeamModel).where(TeamModel.manager_id == manager_id)
        result = await self.session.execute(stmt)
        team_models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in team_models]
    
    async def list_active_by_tenant(self, tenant_id: UUID) -> List[Team]:
        """List all active teams in a tenant."""
        stmt = select(TeamModel).where(
            and_(
                TeamModel.tenant_id == tenant_id,
                TeamModel.is_active == True
            )
        )
        result = await self.session.execute(stmt)
        team_models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in team_models]
    
    async def exists_by_name(self, tenant_id: UUID, name: str) -> bool:
        """Check if team exists by name within a tenant."""
        stmt = select(TeamModel).where(
            and_(
                TeamModel.tenant_id == tenant_id,
                TeamModel.name == name
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    async def count_by_tenant(self, tenant_id: UUID) -> int:
        """Count teams in a tenant."""
        stmt = select(TeamModel).where(TeamModel.tenant_id == tenant_id)
        result = await self.session.execute(stmt)
        teams = result.scalars().all()
        return len(teams)
    
    async def count_by_manager(self, manager_id: UUID) -> int:
        """Count teams managed by a specific manager."""
        stmt = select(TeamModel).where(TeamModel.manager_id == manager_id)
        result = await self.session.execute(stmt)
        teams = result.scalars().all()
        return len(teams)
    
    def _model_to_entity(self, model: TeamModel) -> Team:
        """Convert database model to domain entity."""
        return Team(
            id=getattr(model, "id"),
            tenant_id=getattr(model, "tenant_id"),
            name=getattr(model, "name"),
            description=getattr(model, "description"),
            manager_id=getattr(model, "manager_id"),
            is_active=getattr(model, "is_active"),
            created_at=getattr(model, "created_at"),
            updated_at=getattr(model, "updated_at")
        )
    
    def _entity_to_model(self, entity: Team) -> TeamModel:
        """Convert domain entity to database model."""
        return TeamModel(
            id=entity.id,
            tenant_id=entity.tenant_id,
            name=entity.name,
            description=entity.description,
            manager_id=entity.manager_id,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )