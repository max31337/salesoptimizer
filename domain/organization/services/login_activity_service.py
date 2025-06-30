from typing import Optional
from domain.organization.entities.login_activity import LoginActivity
from domain.organization.repositories.login_activity_repository import LoginActivityRepository
from domain.organization.value_objects.user_id import UserId

class LoginActivityService:
    """Domain service for login activity operations."""

    def __init__(self, login_activity_repository: LoginActivityRepository):
        self._login_activity_repository = login_activity_repository

    async def record_login(
        self,
        user_id: UserId,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> LoginActivity:
        """Record a user login activity."""
        login_activity = LoginActivity(
            id=None,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return await self._login_activity_repository.save(login_activity)

    async def record_logout(self, user_id: UserId) -> Optional[LoginActivity]:
        """Record a user logout activity."""
        latest_activity = await self._login_activity_repository.get_latest_by_user_id(user_id)
        if latest_activity and latest_activity.logout_at is None:
            latest_activity.mark_logout()
            return await self._login_activity_repository.save(latest_activity)
        return None
