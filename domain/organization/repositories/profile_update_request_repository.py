from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from domain.organization.entities.profile_update_request import ProfileUpdateRequest
from domain.organization.value_objects.user_id import UserId


class ProfileUpdateRequestRepository(ABC):
    """Profile update request repository interface."""

    @abstractmethod
    async def save(self, request: ProfileUpdateRequest) -> ProfileUpdateRequest:
        """Save a profile update request."""
        pass

    @abstractmethod
    async def get_by_id(self, request_id: UUID) -> Optional[ProfileUpdateRequest]:
        """Get profile update request by ID."""
        pass

    @abstractmethod
    async def get_pending_for_user(self, user_id: UserId) -> Optional[ProfileUpdateRequest]:
        """Get pending profile update request for a user."""
        pass

    @abstractmethod
    async def get_pending_requests_for_approval(self, tenant_id: UUID) -> List[ProfileUpdateRequest]:
        """Get all pending profile update requests for a tenant that require approval."""
        pass

    @abstractmethod
    async def update(self, request: ProfileUpdateRequest) -> ProfileUpdateRequest:
        """Update existing profile update request."""
        pass

    @abstractmethod
    async def delete(self, request_id: UUID) -> bool:
        """Delete profile update request by ID."""
        pass
