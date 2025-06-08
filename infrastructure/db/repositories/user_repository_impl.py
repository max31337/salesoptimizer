from typing import Optional, List
from datetime import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from domain.organization.entities.user import User, UserRole, UserStatus
from domain.organization.value_objects.email import Email
from domain.organization.value_objects.user_id import UserId
from domain.organization.repositories.user_repository import UserRepository
from infrastructure.db.models.user_model import UserModel


class UserRepositoryImpl(UserRepository):
    """User repository implementation."""
    
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, user: User) -> User:
        """Save a new user."""
        model = self._entity_to_model(user)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        
        return self._model_to_entity(model)

    async def get_by_id(self, user_id: UserId) -> Optional[User]:
        """Get user by ID."""
        stmt = select(UserModel).where(UserModel.id == user_id.value)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        return self._model_to_entity(model) if model else None

    async def get_by_email(self, email: Email) -> Optional[User]:
        """Get user by email."""
        stmt = select(UserModel).where(UserModel.email == str(email))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        return self._model_to_entity(model) if model else None

    async def exists_by_email(self, email: Email) -> bool:
        """Check if user exists by email."""
        stmt = select(UserModel.id).where(UserModel.email == str(email))
        result = await self._session.execute(stmt)
        
        return result.scalar_one_or_none() is not None

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        stmt = select(UserModel).where(UserModel.username == username)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        return self._model_to_entity(model) if model else None
    
    async def count_superadmins(self) -> int:
        """Count the number of superadmin users."""
        stmt = select(func.count(UserModel.id)).where(UserModel.role == 'super_admin')
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def get_team_members(self, team_id: UUID) -> List[User]:
        """Get all users who are members of a specific team."""
        stmt = select(UserModel).where(UserModel.team_id == team_id)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in models]
    
    async def count_team_members(self, team_id: UUID) -> int:
        """Count the number of members in a specific team."""
        stmt = select(func.count(UserModel.id)).where(UserModel.team_id == team_id)
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def update(self, user: User) -> User:
        """Update existing user."""
        if user.id is None:
            raise ValueError("User ID cannot be None for update operation")
        
        stmt = select(UserModel).where(UserModel.id == user.id.value)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            raise ValueError(f"User with ID {user.id.value} not found")
        
        # Update model fields
        model.email = str(user.email)
        model.username = user.username or ""
        model.first_name = user.first_name
        model.last_name = user.last_name
        if user.password_hash is not None:
            model.password_hash = user.password_hash
        model.role = user.role.value
        model.status = user.status.value
        if user.tenant_id is not None:
            model.tenant_id = user.tenant_id        
        if user.team_id is not None:
            model.team_id = user.team_id
        if user.phone is not None:
            model.phone = user.phone
        if user.profile_picture_url is not None:
            model.profile_picture_url = user.profile_picture_url
        if user.bio is not None:
            model.bio = user.bio
        model.is_email_verified = user.is_email_verified
        if user.oauth_provider is not None:
            model.oauth_provider = user.oauth_provider
        if user.oauth_provider_id is not None:
            model.oauth_provider_id = user.oauth_provider_id
        model.updated_at = datetime.now()
        
        await self._session.flush()
        await self._session.refresh(model)
        
        return self._model_to_entity(model)

    async def delete(self, user_id: UserId) -> bool:
        """Delete user by ID."""
        stmt = select(UserModel).where(UserModel.id == user_id.value)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if model:
                await self._session.delete(model)
                return True
        return False
    
    def _model_to_entity(self, model: UserModel) -> User:
        """Convert database model to domain entity."""
        return User(
            id=UserId(model.id),
            email=Email(str(model.email)),
            username=model.username,
            first_name=model.first_name,
            last_name=model.last_name,
            password_hash=model.password_hash,
            role=UserRole(model.role),
            status=UserStatus(model.status),
            tenant_id=model.tenant_id,
            team_id=model.team_id,
            phone=model.phone,
            profile_picture_url=model.profile_picture_url,
            bio=model.bio,
            is_email_verified=model.is_email_verified,
            invitation_token=model.invitation_token,
            invitation_expires_at=model.invitation_expires_at,
            _oauth_provider=model.oauth_provider,
            _oauth_provider_id=model.oauth_provider_id
        )
    
    def _entity_to_model(self, user: User) -> UserModel:
        """Convert domain entity to database model."""
        return UserModel(
            id=user.id.value if user.id else None,
            email=str(user.email),
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            password_hash=user.password_hash,
            role=user.role.value,
            status=user.status.value,
            tenant_id=user.tenant_id,
            team_id=user.team_id,
            phone=user.phone,
            profile_picture_url=user.profile_picture_url,
            bio=user.bio,
            is_email_verified=user.is_email_verified,
            last_login=user.last_login,
            invitation_token=user.invitation_token,
            invitation_expires_at=user.invitation_expires_at,
            created_at=user.created_at,
            updated_at=user.updated_at,
            oauth_provider=user.oauth_provider,
            oauth_provider_id=user.oauth_provider_id
        )