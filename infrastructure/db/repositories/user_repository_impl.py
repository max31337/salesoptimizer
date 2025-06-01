from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from domain.organization.entities.user import User, UserRole, UserStatus
from domain.organization.value_objects.email import Email
from domain.organization.value_objects.user_id import UserId
from domain.organization.repositories.user_repository import UserRepository
from infrastructure.db.models.user_model import UserModel


class UserRepositoryImpl(UserRepository):
    """User repository implementation."""
    
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
    
    async def get_by_id(self, user_id: UserId) -> Optional[User]:
        """Get user by ID."""
        stmt = select(UserModel).where(UserModel.id == user_id.value)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            return None
        
        return self._model_to_entity(model)
    
    async def get_by_email(self, email: Email) -> Optional[User]:
        """Get user by email."""
        stmt = select(UserModel).where(UserModel.email == str(email))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            return None
        
        return self._model_to_entity(model)
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        stmt = select(UserModel).where(UserModel.username == username)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            return None
        
        return self._model_to_entity(model)
    
    async def save(self, user: User) -> User:
        """Save user."""
        model = self._entity_to_model(user)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._model_to_entity(model)
    
    async def update(self, user: User) -> User:
        """Update user."""
        if not user.id:
            raise ValueError("User ID is required for update")
        
        stmt = select(UserModel).where(UserModel.id == user.id.value)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            raise ValueError("User not found")
        
        # Update model fields
        setattr(model, "email", str(user.email))
        setattr(model, "username", user.username)
        setattr(model, "first_name", user.first_name)
        setattr(model, "last_name", user.last_name)
        setattr(model, "password_hash", user.password_hash)
        setattr(model, "role", user.role.value)
        setattr(model, "status", user.status.value)
        setattr(model, "tenant_id", user.tenant_id)
        setattr(model, "team_id", user.team_id)
        setattr(model, "phone", user.phone)
        setattr(model, "is_email_verified", user.is_email_verified)
        setattr(model, "last_login", user.last_login)
        setattr(model, "invitation_token", user.invitation_token)
        setattr(model, "invitation_expires_at", user.invitation_expires_at)
        setattr(model, "updated_at", user.updated_at)

        await self._session.commit()
        await self._session.refresh(model)
        return self._model_to_entity(model)
    
    async def exists_by_email(self, email: Email) -> bool:
        """Check if user exists by email."""
        stmt = select(UserModel.id).where(UserModel.email == str(email))
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    def _model_to_entity(self, model: UserModel) -> User:
        """Convert database model to domain entity."""
        return User(
            id=UserId(model.id), #type: ignore
            email=Email(str(model.email)),
            username=getattr(model, "username", ""),
            first_name=getattr(model, "first_name", ""),
            last_name=getattr(model, "last_name", ""),
            password_hash=getattr(model, "password_hash", None),
            role=UserRole(getattr(model, "role", "") or ""),
            status=UserStatus(getattr(model, "status", "") or ""),
            tenant_id=getattr(model, "tenant_id", None),
            team_id=getattr(model, "team_id", None),
            phone=getattr(model, "phone", None),
            is_email_verified=getattr(model, "is_email_verified", False),
            invitation_token=getattr(model, "invitation_token", None),
            invitation_expires_at=getattr(model, "invitation_expires_at", None),
            created_at=getattr(model, "created_at", datetime.now()),
            updated_at=getattr(model, "updated_at", datetime.now()),
            _oauth_provider=getattr(model, "oauth_provider", None),
            _oauth_provider_id=getattr(model, "oauth_provider_id", None)
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
            is_email_verified=user.is_email_verified,
            last_login=user.last_login,
            invitation_token=user.invitation_token,
            invitation_expires_at=user.invitation_expires_at,
            created_at=user.created_at,
            updated_at=user.updated_at,
            oauth_provider=user.oauth_provider,
            oauth_provider_id=user.oauth_provider_id
        )