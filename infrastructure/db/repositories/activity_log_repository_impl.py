from typing import List, Optional, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
import json

from domain.organization.entities.activity_log import ActivityLog
from domain.organization.repositories.activity_log_repository import ActivityLogRepository
from domain.organization.value_objects.user_id import UserId
from infrastructure.db.models.activity_log_model import ActivityLogModel


class ActivityLogRepositoryImpl(ActivityLogRepository):
    """SQLAlchemy implementation of activity log repository."""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def save(self, activity_log: ActivityLog) -> ActivityLog:
        """Save activity log."""        
        activity_log_model = ActivityLogModel(
            id=activity_log.id,
            user_id=activity_log.user_id.value,
            tenant_id=activity_log.tenant_id,
            activity_type=activity_log.activity_type,
            activity_metadata=json.dumps(activity_log.metadata) if activity_log.metadata else None,
            ip_address=activity_log.ip_address,
            user_agent=activity_log.user_agent,
            created_at=activity_log.created_at
        )
        
        self._session.add(activity_log_model)
        await self._session.flush()
        
        return self._model_to_entity(activity_log_model)
    
    async def get_by_id(self, activity_log_id: UUID) -> Optional[ActivityLog]:
        """Get activity log by ID."""
        stmt = select(ActivityLogModel).where(ActivityLogModel.id == activity_log_id)
        result = await self._session.execute(stmt)
        activity_log_model = result.scalar_one_or_none()
        
        if activity_log_model:
            return self._model_to_entity(activity_log_model)
        return None
    
    async def get_by_user_id(
        self, 
        user_id: UserId, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[ActivityLog]:
        """Get activity logs by user ID with pagination."""
        stmt = (
            select(ActivityLogModel)
            .where(ActivityLogModel.user_id == user_id.value)
            .order_by(desc(ActivityLogModel.created_at))
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        activity_log_models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in activity_log_models]
    
    async def get_by_tenant_id(
        self, 
        tenant_id: UUID, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[ActivityLog]:
        """Get activity logs by tenant ID with pagination."""
        stmt = (
            select(ActivityLogModel)
            .where(ActivityLogModel.tenant_id == tenant_id)
            .order_by(desc(ActivityLogModel.created_at))
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        activity_log_models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in activity_log_models]
    
    async def get_by_activity_type(
        self, 
        activity_type: str, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[ActivityLog]:
        """Get activity logs by activity type with pagination."""
        stmt = (
            select(ActivityLogModel)
            .where(ActivityLogModel.activity_type == activity_type)
            .order_by(desc(ActivityLogModel.created_at))
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        activity_log_models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in activity_log_models]
    
    async def count_by_user_id(self, user_id: UserId) -> int:
        """Count activity logs by user ID."""
        stmt = select(func.count(ActivityLogModel.id)).where(
            ActivityLogModel.user_id == user_id.value
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0
    
    async def count_by_tenant_id(self, tenant_id: UUID) -> int:
        """Count activity logs by tenant ID."""
        stmt = select(func.count(ActivityLogModel.id)).where(
            ActivityLogModel.tenant_id == tenant_id
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0
    
    def _model_to_entity(self, model: ActivityLogModel) -> ActivityLog:
        """Convert database model to domain entity."""
        metadata = None
        if model.activity_metadata:
            try:
                if isinstance(model.activity_metadata, str):
                    metadata = json.loads(model.activity_metadata)
                else:
                    metadata = model.activity_metadata
            except (json.JSONDecodeError, TypeError):
                metadata = None
        
        return ActivityLog(
            id=model.id,
            user_id=UserId(model.user_id),
            tenant_id=model.tenant_id,
            activity_type=model.activity_type,
            description=self._get_description_from_type(model.activity_type, metadata),
            metadata=metadata,
            ip_address=model.ip_address,
            user_agent=model.user_agent,
            created_at=model.created_at
        )
    
    def _get_description_from_type(self, activity_type: str, metadata: Optional[dict[str, Any]] = None) -> str:
        """Generate description from activity type and metadata."""
        if activity_type == "user_login":
            return "User logged in"
        elif activity_type == "user_created":
            return "User account created"
        elif activity_type == "team_joined":
            team_name = metadata.get("team_name", "Unknown") if metadata else "Unknown"
            return f"User joined team '{team_name}'"
        else:
            return f"Activity: {activity_type}"
