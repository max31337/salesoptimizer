from abc import ABC, abstractmethod
from typing import Optional

from domain.organization.entities.login_activity import LoginActivity
from domain.organization.value_objects.user_id import UserId


class LoginActivityRepository(ABC):
    """Login activity repository interface."""

    @abstractmethod
    async def save(self, login_activity: LoginActivity) -> LoginActivity:
        """Save login activity."""
        pass

    @abstractmethod
    async def get_latest_by_user_id(self, user_id: UserId) -> Optional[LoginActivity]:
        """Get the latest login activity for a user."""
        pass
