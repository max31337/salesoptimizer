from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from domain.organization.repositories.team_repository import TeamRepository
from infrastructure.db.models.team_model import TeamModel


class TeamRepositoryImpl(TeamRepository):
    """Implementation of team repository using SQLAlchemy."""
    
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, team_id: UUID) -> Optional[TeamModel]:
        """Get team by ID."""
        result = await self._session.execute(
            select(TeamModel).where(TeamModel.id == team_id)
        )
        return result.scalar_one_or_none()

    async def get_by_tenant(self, tenant_id: UUID) -> List[TeamModel]:
        """Get all teams for a tenant."""
        result = await self._session.execute(
            select(TeamModel)
            .where(TeamModel.tenant_id == tenant_id)
            .order_by(TeamModel.created_at.desc())
        )
        return list(result.scalars().all())

    async def save(self, team: TeamModel) -> TeamModel:
        """Save team."""
        self._session.add(team)
        await self._session.flush()
        return team

    async def update(self, team: TeamModel) -> TeamModel:
        """Update team."""
        await self._session.merge(team)
        await self._session.flush()
        return team

    async def delete(self, team_id: UUID) -> bool:
        """Delete team."""
        team = await self.get_by_id(team_id)
        if team:
            await self._session.delete(team)
            await self._session.flush()
            return True
        return False
