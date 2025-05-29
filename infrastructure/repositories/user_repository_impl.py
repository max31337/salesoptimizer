from typing import List, Optional
from uuid import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from domain.organization.entities.user import User, UserRole, UserStatus
from domain.organization.repositories.user_repository import UserRepository
from infrastructure.db.models.user_model import UserModel


class UserRepositoryImpl(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.db = session  # For backward compatibility with sync methods, if needed
    async def create(self, user: User) -> User:
        """Create a new user."""
        # Check for existing email
        stmt_email = select(UserModel).where(UserModel.email == user.email)
        result_email = await self.session.execute(stmt_email)
        existing_email = result_email.scalar_one_or_none()
        if existing_email:
            raise ValueError("User with this email or username already exists")
            
        # Check for existing username if provided
        if user.username:
            stmt_username = select(UserModel).where(UserModel.username == user.username)
            result_username = await self.session.execute(stmt_username)
            existing_username = result_username.scalar_one_or_none()
            if existing_username:
                raise ValueError("User with this email or username already exists")
        
        db_user = UserModel(
            id=user.id,
            tenant_id=user.tenant_id,
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            password_hash=user.password_hash,
            role=user.role.value,
            status=user.status.value,
            is_email_verified=user.is_email_verified,
            last_login=user.last_login,
            invitation_token=user.invitation_token,
            invitation_expires_at=user.invitation_expires_at
        )
        
        try:
            self.session.add(db_user)
            await self.session.commit()
            await self.session.refresh(db_user)
            return self._to_entity(db_user)
        except IntegrityError:
            await self.session.rollback()
            raise ValueError("User with this email or username already exists")
            raise ValueError("User with this email or username already exists")
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID - MUST be async."""
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        return self._model_to_entity(user_model) if user_model else None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email - MUST be async."""
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        
        if not user_model:
            return None
            
        return self._model_to_entity(user_model)

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username - MUST be async."""
        stmt = select(UserModel).where(UserModel.username == username)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        
        if not user_model:
            return None
            
        return self._model_to_entity(user_model)
    
    async def get_by_invitation_token(self, token: str) -> Optional[User]:
        """Get user by invitation token."""
        stmt = select(UserModel).where(UserModel.invitation_token == token)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        return self._model_to_entity(user_model) if user_model else None
    
    async def get_by_tenant(self, tenant_id: UUID, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users by tenant ID - MUST be async."""
        stmt = (
            select(UserModel)
            .where(UserModel.tenant_id == tenant_id)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        db_users = result.scalars().all()
        return [self._to_entity(db_user) for db_user in db_users]
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users - MUST be async."""
        stmt = select(UserModel).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        db_users = result.scalars().all()
        return [self._to_entity(db_user) for db_user in db_users]
    
    async def update(self, user: User) -> User:
        """Update user - MUST be async."""
        # Find existing user
        stmt = select(UserModel).where(UserModel.id == user.id)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        
        if not user_model:
            raise ValueError(f"User with id {user.id} not found")
        
        # Update fields
        setattr(user_model, "first_name", user.first_name)
        setattr(user_model, "last_name", user.last_name)
        setattr(user_model, "email", user.email)
        setattr(user_model, "username", user.username)
        setattr(user_model, "password_hash", user.password_hash)
        setattr(user_model, "role", user.role.value if hasattr(user.role, 'value') else user.role)
        setattr(user_model, "status", user.status.value if hasattr(user.status, 'value') else user.status)
        setattr(user_model, "is_email_verified", user.is_email_verified)
        setattr(user_model, "last_login", user.last_login)
        setattr(user_model, "updated_at", user.updated_at)

        await self.session.commit()
        await self.session.refresh(user_model)
        
        return self._model_to_entity(user_model)

    async def delete(self, user_id: UUID) -> bool:
        """Delete user."""
        db_user = await self.session.get(UserModel, user_id)
        if not db_user:
            return False

        await self.session.delete(db_user)
        await self.session.commit()
        return True

    async def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email."""
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def exists_by_username(self, username: str) -> bool:
        """Check if user exists by username."""
        stmt = select(UserModel).where(UserModel.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def count_by_tenant_and_role(self, tenant_id: UUID, role: UserRole) -> int:
        """Count users by tenant and role."""
        stmt = (
            select(func.count())
            .where(UserModel.tenant_id == tenant_id, UserModel.role == role.value)
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    def _to_entity(self, db_user: UserModel) -> User:
        """Convert database model to entity."""
        return User(
            id=getattr(db_user, "id", None),
            tenant_id=getattr(db_user, "tenant_id", None),
            email=getattr(db_user, "email", "") or "",
            username=getattr(db_user, "username", None),
            first_name=getattr(db_user, "first_name", "") or "",
            last_name=getattr(db_user, "last_name", "") or "",
            phone=getattr(db_user, "phone", None),
            password_hash=getattr(db_user, "password_hash", None),
            role=UserRole(getattr(db_user, "role", None)),
            status=UserStatus(getattr(db_user, "status", None)),
            is_email_verified=bool(getattr(db_user, "is_email_verified", False)),
            last_login=getattr(db_user, "last_login", None),
            invitation_token=getattr(db_user, "invitation_token", None),
            invitation_expires_at=getattr(db_user, "invitation_expires_at", None),
            created_at=getattr(db_user, "created_at", None),
            updated_at=getattr(db_user, "updated_at", None)
        )

    def _model_to_entity(self, user_model: UserModel) -> User:
        """Convert UserModel to User entity."""
        return User(
            id=getattr(user_model, "id", None),
            tenant_id=getattr(user_model, "tenant_id", None),
            team_id=getattr(user_model, "team_id", None),
            email=getattr(user_model, "email", "") or "",
            username=getattr(user_model, "username", None),
            first_name=getattr(user_model, "first_name", "") or "",
            last_name=getattr(user_model, "last_name", "") or "",
            phone=getattr(user_model, "phone", None),
            password_hash=getattr(user_model, "password_hash", None),
            role=UserRole(getattr(user_model, "role")) if isinstance(getattr(user_model, "role"), str) else getattr(user_model, "role"),
            status=UserStatus(getattr(user_model, "status")) if isinstance(getattr(user_model, "status"), str) else getattr(user_model, "status"),
            is_email_verified=getattr(user_model, "is_email_verified", False),
            last_login=getattr(user_model, "last_login", None),
            invitation_token=getattr(user_model, "invitation_token", None),
            invitation_expires_at=getattr(user_model, "invitation_expires_at", None),
            created_at=getattr(user_model, "created_at", None),
            updated_at=getattr(user_model, "updated_at", None)
        )

    def _entity_to_model(self, user: User) -> UserModel:
        """Convert User entity to UserModel."""
        return UserModel(
            id=user.id,
            tenant_id=user.tenant_id,
            team_id=user.team_id,
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            password_hash=user.password_hash,
            role=user.role.value if hasattr(user.role, 'value') else user.role,
            status=user.status.value if hasattr(user.status, 'value') else user.status,
            is_email_verified=user.is_email_verified,
            last_login=user.last_login,
            invitation_token=user.invitation_token,
            invitation_expires_at=user.invitation_expires_at,
            created_at=user.created_at,
            updated_at=user.updated_at
        )