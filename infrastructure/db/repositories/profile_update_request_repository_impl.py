from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from domain.organization.entities.profile_update_request import ProfileUpdateRequest, ProfileUpdateStatus
from domain.organization.value_objects.user_id import UserId
from domain.organization.repositories.profile_update_request_repository import ProfileUpdateRequestRepository
from infrastructure.db.models.profile_update_request_model import ProfileUpdateRequestModel


class ProfileUpdateRequestRepositoryImpl(ProfileUpdateRequestRepository):
    """Profile update request repository implementation."""
    
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, request: ProfileUpdateRequest) -> ProfileUpdateRequest:
        """Save a profile update request."""
        model = self._entity_to_model(request)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        
        return self._model_to_entity(model)

    async def get_by_id(self, request_id: UUID) -> Optional[ProfileUpdateRequest]:
        """Get profile update request by ID."""
        stmt = select(ProfileUpdateRequestModel).where(ProfileUpdateRequestModel.id == request_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        return self._model_to_entity(model) if model else None

    async def get_pending_for_user(self, user_id: UserId) -> Optional[ProfileUpdateRequest]:
        """Get pending profile update request for a user."""
        stmt = select(ProfileUpdateRequestModel).where(
            ProfileUpdateRequestModel.user_id == user_id.value,
            ProfileUpdateRequestModel.status == "pending"
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        return self._model_to_entity(model) if model else None

    async def get_pending_requests_for_approval(self, tenant_id: UUID) -> List[ProfileUpdateRequest]:
        """Get all pending profile update requests for a tenant that require approval."""
        # Import here to avoid circular imports
        from infrastructure.db.models.user_model import UserModel
        
        # Join with user table to filter by tenant_id
        stmt = select(ProfileUpdateRequestModel).join(
            UserModel, ProfileUpdateRequestModel.user_id == UserModel.id
        ).where(
            ProfileUpdateRequestModel.status == "pending",
            UserModel.tenant_id == tenant_id
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in models]

    async def update(self, request: ProfileUpdateRequest) -> ProfileUpdateRequest:
        """Update existing profile update request."""
        if request.id is None:
            raise ValueError("Profile update request ID cannot be None for update operation")
        
        stmt = select(ProfileUpdateRequestModel).where(ProfileUpdateRequestModel.id == request.id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            raise ValueError(f"Profile update request with ID {request.id} not found")
        
        # Update model fields
        model.requested_changes = request.requested_changes
        model.status = request.status.value
        if request.reason is not None:
            model.reason = request.reason
        if request.approved_by_id is not None:
            model.approved_by_id = request.approved_by_id.value
        if request.approved_at is not None:
            model.approved_at = request.approved_at
        model.updated_at = request.updated_at
        
        await self._session.flush()
        await self._session.refresh(model)
        
        return self._model_to_entity(model)

    async def delete(self, request_id: UUID) -> bool:
        """Delete profile update request by ID."""
        stmt = select(ProfileUpdateRequestModel).where(ProfileUpdateRequestModel.id == request_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if model:
            await self._session.delete(model)
            return True
        return False

    def _model_to_entity(self, model: ProfileUpdateRequestModel) -> ProfileUpdateRequest:
        """Convert database model to domain entity."""
        return ProfileUpdateRequest(
            id=model.id,
            user_id=UserId(model.user_id),
            requested_by_id=UserId(model.requested_by_id),
            requested_changes=model.requested_changes or {},
            status=ProfileUpdateStatus(model.status),
            approved_by_id=UserId(model.approved_by_id) if model.approved_by_id else None,
            approved_at=model.approved_at,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def _entity_to_model(self, request: ProfileUpdateRequest) -> ProfileUpdateRequestModel:
        """Convert domain entity to database model."""
        return ProfileUpdateRequestModel(
            id=request.id,
            user_id=request.user_id.value,
            requested_by_id=request.requested_by_id.value,
            requested_changes=request.requested_changes,
            status=request.status.value,
            reason=request.reason,
            approved_by_id=request.approved_by_id.value if request.approved_by_id else None,
            approved_at=request.approved_at,
            created_at=request.created_at,
            updated_at=request.updated_at
        )
