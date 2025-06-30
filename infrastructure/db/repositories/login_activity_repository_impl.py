from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from domain.organization.entities.login_activity import LoginActivity
from domain.organization.repositories.login_activity_repository import LoginActivityRepository
from domain.organization.value_objects.user_id import UserId
from infrastructure.db.models.login_activity_model import LoginActivityModel


class LoginActivityRepositoryImpl(LoginActivityRepository):
    """SQLAlchemy implementation of the login activity repository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: LoginActivityModel) -> LoginActivity:
        """Convert a model to a domain entity."""
        return LoginActivity(
            id=model.id,
            user_id=UserId(model.user_id),
            login_at=model.login_at,
            logout_at=model.logout_at,
            ip_address=model.ip_address,
            user_agent=model.user_agent,
        )

    def _from_entity(self, entity: LoginActivity) -> LoginActivityModel:
        """Convert a domain entity to a model."""
        return LoginActivityModel(
            id=entity.id,
            user_id=entity.user_id.value,
            login_at=entity.login_at,
            logout_at=entity.logout_at,
            ip_address=entity.ip_address,
            user_agent=entity.user_agent,
        )

    async def save(self, login_activity: LoginActivity) -> LoginActivity:
        """Save login activity."""
        login_activity_model = self._from_entity(login_activity)
        merged_model = await self.session.merge(login_activity_model)
        await self.session.flush()
        await self.session.refresh(merged_model)
        return self._to_entity(merged_model)

    async def get_latest_by_user_id(self, user_id: UserId) -> Optional[LoginActivity]:
        """Get the latest login activity for a user."""
        stmt = (
            select(LoginActivityModel)
            .filter_by(user_id=user_id.value)
            .order_by(LoginActivityModel.login_at.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        login_activity_model = result.scalar_one_or_none()
        return self._to_entity(login_activity_model) if login_activity_model else None
