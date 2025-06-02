from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from domain.organization.entities.invitation import Invitation
from domain.organization.repositories.invitation_repository import InvitationRepository
from domain.organization.value_objects.email import Email
from domain.organization.value_objects.invitation_token import InvitationToken
from domain.organization.value_objects.user_id import UserId
from domain.organization.value_objects.user_role import UserRole
from infrastructure.db.models.invitation_model import InvitationModel


class InvitationRepositoryImpl(InvitationRepository):
    """Implementation of invitation repository."""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def save(self, invitation: Invitation) -> Invitation:
        """Save invitation."""
        model = InvitationModel(
            id=invitation.id.value,
            email=str(invitation.email),
            role=invitation.role.value,
            token=invitation.token.value,
            invited_by_id=invitation.invited_by_id.value,
            organization_name=invitation.organization_name,
            tenant_id=invitation.tenant_id,
            expires_at=invitation.expires_at,
            is_used=invitation.is_used,
            used_at=invitation.used_at,
            created_at=invitation.created_at,
            updated_at=invitation.updated_at
        )
        
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        
        return self._model_to_entity(model)
    
    async def get_by_token(self, token: InvitationToken) -> Optional[Invitation]:
        """Get invitation by token."""
        result = await self._session.execute(
            select(InvitationModel)
            .options(selectinload(InvitationModel.invited_by))
            .where(InvitationModel.token == token.value)
        )
        model = result.scalar_one_or_none()
        
        return self._model_to_entity(model) if model else None
    
    async def get_by_email(self, email: Email) -> Optional[Invitation]:
        """Get active invitation by email."""
        result = await self._session.execute(
            select(InvitationModel)
            .options(selectinload(InvitationModel.invited_by))
            .where(
                InvitationModel.email == str(email),
                InvitationModel.is_used == False
            )
            .order_by(InvitationModel.created_at.desc())
        )
        model = result.scalar_one_or_none()
        
        return self._model_to_entity(model) if model else None
    
    async def update(self, invitation: Invitation) -> Invitation:
        """Update invitation."""
        result = await self._session.execute(
            select(InvitationModel).where(InvitationModel.id == invitation.id.value)
        )
        model = result.scalar_one()
        
        setattr(model, 'is_used', invitation.is_used)
        setattr(model, 'used_at', invitation.used_at)
        setattr(model, 'updated_at', invitation.updated_at)
        
        await self._session.flush()
        await self._session.refresh(model)
        
        return self._model_to_entity(model)
    
    def _model_to_entity(self, model: InvitationModel) -> Invitation:
        """Convert database model to domain entity."""
        return Invitation(
            id=UserId(model.id),
            email=Email(model.email),
            role=UserRole(model.role),
            token=InvitationToken(model.token),
            invited_by_id=UserId(model.invited_by_id),
            organization_name=model.organization_name,
            tenant_id=model.tenant_id,
            expires_at=model.expires_at,
            is_used=model.is_used,
            used_at=model.used_at,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    def _entity_to_model(self, invitation: Invitation) -> InvitationModel:
        """Convert domain entity to database model."""
        return InvitationModel(
            id=invitation.id.value if invitation.id else None,
            email=str(invitation.email),
            role=invitation.role.value,
            token=invitation.token.value,
            invited_by_id=invitation.invited_by_id.value,
            organization_name=invitation.organization_name,
            tenant_id=invitation.tenant_id, 
            expires_at=invitation.expires_at,
            is_used=invitation.is_used,
            used_at=invitation.used_at,
            created_at=invitation.created_at,
            updated_at=invitation.updated_at
        )