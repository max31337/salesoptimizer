from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from domain.organization.entities.activity_log import ActivityLog
from domain.organization.value_objects.user_id import UserId


class ActivityLogRepository(ABC):
    """Activity log repository interface."""
    
    @abstractmethod
    async def save(self, activity_log: ActivityLog) -> ActivityLog:
        """Save activity log."""
        pass
    
    @abstractmethod
    async def get_by_id(self, activity_log_id: UUID) -> Optional[ActivityLog]:
        """Get activity log by ID."""
        pass
    
    @abstractmethod
    async def get_by_user_id(
        self, 
        user_id: UserId, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[ActivityLog]:
        """Get activity logs by user ID with pagination."""
        pass
    
    @abstractmethod
    async def get_by_tenant_id(
        self, 
        tenant_id: UUID, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[ActivityLog]:
        """Get activity logs by tenant ID with pagination."""
        pass
    
    @abstractmethod
    async def get_by_activity_type(
        self, 
        activity_type: str, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[ActivityLog]:
        """Get activity logs by activity type with pagination."""
        pass
    
    @abstractmethod
    async def count_by_user_id(self, user_id: UserId) -> int:
        """Count activity logs by user ID."""
        pass
    
    @abstractmethod
    async def count_by_tenant_id(self, tenant_id: UUID) -> int:
        """Count activity logs by tenant ID."""
        pass
