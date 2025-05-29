from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from domain.organization.entities.user import User, UserRole, UserStatus
from domain.organization.repositories.user_repository import UserRepository
from infrastructure.db.models.user_model import UserModel

class UserRepositoryImpl(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        
        if not user_model:
            return None
            
        return self._model_to_entity(user_model)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        
        if not user_model:
            return None
            
        return self._model_to_entity(user_model)
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        stmt = select(UserModel).where(UserModel.username == username)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        
        if not user_model:
            return None
            
        return self._model_to_entity(user_model)
    
    async def create(self, user: User) -> User:
        """Create new user."""
        user_model = self._entity_to_model(user)
        self.session.add(user_model)
        await self.session.flush()  # Get the ID without committing
        
        return self._model_to_entity(user_model)
    
    async def update(self, user: User) -> User:
        """Update existing user."""
        stmt = select(UserModel).where(UserModel.id == user.id)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        
        if not user_model:
            raise ValueError(f"User with ID {user.id} not found")
        
        # Update model with entity data
        setattr(user_model, "email", user.email)
        setattr(user_model, "username", user.username)
        setattr(user_model, "first_name", user.first_name)
        setattr(user_model, "last_name", user.last_name)
        setattr(user_model, "phone", user.phone)
        setattr(user_model, "password_hash", user.password_hash)
        setattr(user_model, "role", user.role.value)
        setattr(user_model, "status", user.status.value)
        setattr(user_model, "is_email_verified", user.is_email_verified)
        setattr(user_model, "last_login", user.last_login)
        setattr(user_model, "invitation_token", user.invitation_token)
        setattr(user_model, "invitation_expires_at", user.invitation_expires_at)
        setattr(user_model, "updated_at", user.updated_at)

        await self.session.flush()
        return self._model_to_entity(user_model)
    
    async def delete(self, user_id: UUID) -> bool:
        """Delete user by ID."""
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        
        if not user_model:
            return False
        
        await self.session.delete(user_model)
        return True
    
    async def list_by_tenant(self, tenant_id: UUID) -> List[User]:
        """List all users in a tenant."""
        stmt = select(UserModel).where(UserModel.tenant_id == tenant_id)
        result = await self.session.execute(stmt)
        user_models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in user_models]
    
    def _model_to_entity(self, model: UserModel) -> User:
        """Convert database model to domain entity."""
        return User(
            id=getattr(model, "id"),
            tenant_id=getattr(model, "tenant_id"),
            team_id=getattr(model, "team_id"),  # Add this line
            email=getattr(model, "email"),
            username=getattr(model, "username"),
            first_name=getattr(model, "first_name"),
            last_name=getattr(model, "last_name"),
            phone=getattr(model, "phone"),
            password_hash=getattr(model, "password_hash"),
            role=UserRole(getattr(model, "role")),
            status=UserStatus(getattr(model, "status")),
            is_email_verified=getattr(model, "is_email_verified"),
            last_login=getattr(model, "last_login"),
            invitation_token=getattr(model, "invitation_token"),
            invitation_expires_at=getattr(model, "invitation_expires_at"),
            created_at=getattr(model, "created_at"),
            updated_at=getattr(model, "updated_at")
        )
    
    def _entity_to_model(self, entity: User) -> UserModel:
        """Convert domain entity to database model."""
        return UserModel(
            id=entity.id,
            tenant_id=entity.tenant_id,
            team_id=entity.team_id,  # Add this line
            email=entity.email,
            username=entity.username,
            first_name=entity.first_name,
            last_name=entity.last_name,
            phone=entity.phone,
            password_hash=entity.password_hash,
            role=entity.role.value,
            status=entity.status.value,
            is_email_verified=entity.is_email_verified,
            last_login=entity.last_login,
            invitation_token=entity.invitation_token,
            invitation_expires_at=entity.invitation_expires_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
    
    async def list_by_team(self, team_id: UUID) -> List[User]:
        """List all users in a team."""
        stmt = select(UserModel).where(UserModel.team_id == team_id)
        result = await self.session.execute(stmt)
        user_models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in user_models]