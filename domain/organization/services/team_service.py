from typing import Optional, List, Dict, Any
from uuid import UUID

from domain.organization.repositories.team_repository import TeamRepository
from domain.organization.repositories.user_repository import UserRepository
from domain.organization.value_objects.user_id import UserId
from application.dtos.team_dto import (
    TeamDetailResponse, 
    TeamMemberResponse, 
    TeamManagerResponse,
    TeamResponse
)


class TeamService:
    """Domain service for team operations."""
    
    def __init__(self, team_repository: TeamRepository, user_repository: UserRepository):
        self._team_repository = team_repository
        self._user_repository = user_repository

    async def get_team_by_id(self, team_id: UUID) -> Optional[Dict[str, Any]]:
        """Get basic team information by ID."""
        team_model = await self._team_repository.get_by_id(team_id)
        if not team_model:
            return None
        
        return {
            "id": str(team_model.id),
            "name": team_model.name,
            "description": team_model.description,
            "is_active": team_model.is_active,
            "manager_id": team_model.manager_id,
            "tenant_id": str(team_model.tenant_id),
            "created_at": team_model.created_at,
            "updated_at": team_model.updated_at
        }

    async def get_team_with_members(self, team_id: UUID) -> Optional[TeamDetailResponse]:
        """Get team details with members and manager information."""
        # Get team basic info
        team_info = await self.get_team_by_id(team_id)
        if not team_info:
            return None
        
        # Get team members
        members_data = await self._user_repository.get_team_members(team_id)
        members: List[TeamMemberResponse] = []
        
        for member_model in members_data:
            members.append(TeamMemberResponse(
                id=str(member_model.id),
                email=str(member_model.email),
                username=member_model.username or "",
                full_name=getattr(member_model, 'full_name', None),
                role=member_model.role.value if hasattr(member_model.role, 'value') else str(member_model.role),
                is_active=member_model.is_active(),
                joined_team_at=member_model.updated_at  # When they were assigned to team
            ))
        
        # Get manager information if exists
        manager = None
        if team_info["manager_id"]:
            manager_model = await self._user_repository.get_by_id(team_info["manager_id"])
            if manager_model:
                manager = TeamManagerResponse(
                    id=str(manager_model.id),
                    email=str(manager_model.email),
                    username=manager_model.username or "",
                    full_name=getattr(manager_model, 'full_name', None),
                    role=manager_model.role.value if hasattr(manager_model.role, 'value') else str(manager_model.role)
                )
        
        return TeamDetailResponse(
            id=team_info["id"],
            name=team_info["name"],
            description=team_info["description"],
            is_active=team_info["is_active"],
            created_at=team_info["created_at"],
            updated_at=team_info["updated_at"],
            manager=manager,
            members=members,
            member_count=len(members),
            tenant_id=team_info["tenant_id"]
        )

    async def get_teams_by_tenant(self, tenant_id: UUID) -> List[TeamResponse]:
        """Get all teams for a tenant."""
        teams_data = await self._team_repository.get_by_tenant(tenant_id)
        teams: List[TeamResponse] = []
        
        for team_model in teams_data:
            # Get member count
            members_count = await self._user_repository.count_team_members(team_model.id)
            
            teams.append(TeamResponse(
                id=str(team_model.id),
                name=team_model.name,
                description=team_model.description,
                is_active=team_model.is_active,
                created_at=team_model.created_at,
                updated_at=team_model.updated_at,
                member_count=members_count
            ))
        
        return teams

    async def get_team_member_count(self, team_id: UUID) -> int:
        """Get the number of members in a team."""
        return await self._user_repository.count_team_members(team_id)

    async def get_user_by_id(self, user_id: UUID):
        """Get user by ID."""
        return await self._user_repository.get_by_id(UserId(user_id))
