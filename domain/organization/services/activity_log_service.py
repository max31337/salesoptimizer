from typing import List, Optional
from uuid import UUID, uuid4

from domain.organization.entities.activity_log import ActivityLog
from domain.organization.repositories.activity_log_repository import ActivityLogRepository
from domain.organization.value_objects.user_id import UserId


class ActivityLogService:
    """Domain service for activity log operations."""
    
    def __init__(self, activity_log_repository: ActivityLogRepository):
        self._activity_log_repository = activity_log_repository
    
    async def record_user_login(
        self,
        user_id: UserId,
        tenant_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> ActivityLog:
        """Record a user login activity."""
        activity_log = ActivityLog.create_user_login(
            id=uuid4(),
            user_id=user_id,
            tenant_id=tenant_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return await self._activity_log_repository.save(activity_log)
    
    async def record_user_created(
        self,
        user_id: UserId,
        tenant_id: Optional[UUID] = None,
        created_by: Optional[UserId] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> ActivityLog:
        """Record a user creation activity."""
        activity_log = ActivityLog.create_user_created(
            id=uuid4(),
            user_id=user_id,
            tenant_id=tenant_id,
            created_by=created_by,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return await self._activity_log_repository.save(activity_log)
    
    async def record_team_joined(
        self,
        user_id: UserId,
        team_id: UUID,
        team_name: str,
        tenant_id: Optional[UUID] = None,
        assigned_by: Optional[UserId] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> ActivityLog:
        """Record a team joined activity."""
        activity_log = ActivityLog.create_team_joined(
            id=uuid4(),
            user_id=user_id,
            team_id=team_id,
            team_name=team_name,
            tenant_id=tenant_id,
            assigned_by=assigned_by,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return await self._activity_log_repository.save(activity_log)
    
    async def get_user_activities(
        self,
        user_id: UserId,
        limit: int = 50,
        offset: int = 0
    ) -> List[ActivityLog]:
        """Get user activities with pagination."""
        return await self._activity_log_repository.get_by_user_id(user_id, limit, offset)
    
    async def get_tenant_activities(
        self,
        tenant_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> List[ActivityLog]:
        """Get tenant activities with pagination."""
        return await self._activity_log_repository.get_by_tenant_id(tenant_id, limit, offset)
    
    async def get_activities_by_type(
        self,
        activity_type: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[ActivityLog]:
        """Get activities by type with pagination."""
        return await self._activity_log_repository.get_by_activity_type(activity_type, limit, offset)
