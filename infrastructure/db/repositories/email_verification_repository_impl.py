from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from domain.organization.entities.email_verification import EmailVerification as EmailVerificationEntity
from domain.organization.repositories.email_verification_repository import EmailVerificationRepository
from infrastructure.db.models.email_verification_model import EmailVerificationModel
from domain.organization.value_objects.user_id import UserId

class EmailVerificationRepositoryImpl(EmailVerificationRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, email_verification: EmailVerificationEntity) -> None:
        model = self._to_model(email_verification)
        self.session.add(model)
        await self.session.flush()

    async def get_by_token(self, token: str) -> Optional[EmailVerificationEntity]:
        stmt = select(EmailVerificationModel).filter_by(token=token)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_user_id(self, user_id: UUID) -> Optional[EmailVerificationEntity]:
        stmt = select(EmailVerificationModel).filter_by(user_id=user_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def update(self, email_verification: EmailVerificationEntity) -> None:
        stmt = select(EmailVerificationModel).filter_by(id=email_verification.id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            model.is_verified = email_verification.is_verified
            model.verified_at = email_verification.verified_at
            model.updated_at = email_verification.updated_at
            await self.session.flush()

    def _to_entity(self, model: EmailVerificationModel) -> EmailVerificationEntity:
        return EmailVerificationEntity(
            id=model.id,
            user_id=UserId(model.user_id),
            token=model.token,
            sent_at=model.sent_at,
            expires_at=model.expires_at,
            is_verified=model.is_verified,
            verified_at=model.verified_at,
            created_at=model.created_at,
            updated_at=model.updated_at or model.created_at,
        )

    def _to_model(self, entity: EmailVerificationEntity) -> EmailVerificationModel:
        return EmailVerificationModel(
            id=entity.id,
            user_id=entity.user_id.value,
            token=entity.token,
            sent_at=entity.sent_at,
            expires_at=entity.expires_at,
            is_verified=entity.is_verified,
            verified_at=entity.verified_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
