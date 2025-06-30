from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from domain.organization.entities.oauth_provider import OAuthProvider as OAuthProviderEntity
from domain.organization.repositories.oauth_provider_repository import OAuthProviderRepository
from infrastructure.db.models.oauth_provider_model import OAuthProviderModel
from domain.organization.value_objects.user_id import UserId

class OAuthProviderRepositoryImpl(OAuthProviderRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, oauth_provider: OAuthProviderEntity) -> None:
        model = self._to_model(oauth_provider)
        self.session.add(model)
        await self.session.flush()

    async def get_by_provider_user_id(self, provider: str, provider_user_id: str) -> Optional[OAuthProviderEntity]:
        stmt = select(OAuthProviderModel).filter_by(provider=provider, provider_user_id=provider_user_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_user_id(self, user_id: UUID) -> List[OAuthProviderEntity]:
        stmt = select(OAuthProviderModel).filter_by(user_id=user_id)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    def _to_entity(self, model: OAuthProviderModel) -> OAuthProviderEntity:
        return OAuthProviderEntity(
            id=model.id,
            user_id=UserId(model.user_id),
            provider=model.provider,
            provider_user_id=model.provider_user_id,
            created_at=model.created_at,
            updated_at=model.updated_at or model.created_at,
        )

    def _to_model(self, entity: OAuthProviderEntity) -> OAuthProviderModel:
        return OAuthProviderModel(
            id=entity.id,
            user_id=entity.user_id.value,
            provider=entity.provider,
            provider_user_id=entity.provider_user_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
