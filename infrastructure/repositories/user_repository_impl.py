from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from domain.entities.user import User, UserRole, UserStatus
from domain.repositories.user_repository import UserRepository
from infrastructure.db.models.user_model import UserModel


class UserRepositoryImpl(UserRepository):
    def __init__(self, db: Session) -> None:
        self.db = db
    
    def create(self, user: User) -> User:
        """Create a new user."""
        # Check for existing email
        existing_email = self.db.query(UserModel).filter(UserModel.email == user.email).first()
        if existing_email:
            raise ValueError("User with this email or username already exists")
            
        # Check for existing username if provided
        if user.username:
            existing_username = self.db.query(UserModel).filter(UserModel.username == user.username).first()
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
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            return self._to_entity(db_user)
        except IntegrityError:
            self.db.rollback()
            raise ValueError("User with this email or username already exists")
    
    def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        return self._to_entity(db_user) if db_user else None
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        db_user = self.db.query(UserModel).filter(UserModel.email == email).first()
        return self._to_entity(db_user) if db_user else None
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        db_user = self.db.query(UserModel).filter(UserModel.username == username).first()
        return self._to_entity(db_user) if db_user else None
    
    def get_by_invitation_token(self, token: str) -> Optional[User]:
        """Get user by invitation token."""
        db_user = self.db.query(UserModel).filter(UserModel.invitation_token == token).first()
        return self._to_entity(db_user) if db_user else None
    
    def get_by_tenant(self, tenant_id: UUID, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users by tenant ID."""
        db_users = (
            self.db.query(UserModel)
            .filter(UserModel.tenant_id == tenant_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_entity(db_user) for db_user in db_users]
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users."""
        db_users = self.db.query(UserModel).offset(skip).limit(limit).all()
        return [self._to_entity(db_user) for db_user in db_users]
    
    def update(self, user: User) -> User:
        """Update user."""
        db_user = self.db.query(UserModel).filter(UserModel.id == user.id).first()
        if not db_user:
            raise ValueError("User not found")
        
        # Update fields
        setattr(db_user, "tenant_id", user.tenant_id)
        setattr(db_user, "email", user.email)
        setattr(db_user, "username", user.username)
        setattr(db_user, "first_name", user.first_name)
        setattr(db_user, "last_name", user.last_name)
        setattr(db_user, "phone", user.phone)
        setattr(db_user, "password_hash", user.password_hash)
        setattr(db_user, "role", user.role.value)
        setattr(db_user, "status", user.status.value)
        setattr(db_user, "is_email_verified", user.is_email_verified)
        setattr(db_user, "last_login", user.last_login)
        setattr(db_user, "invitation_token", user.invitation_token)
        setattr(db_user, "invitation_expires_at", user.invitation_expires_at)
        setattr(db_user, "updated_at", user.updated_at)
        
        self.db.commit()
        self.db.refresh(db_user)
        return self._to_entity(db_user)
    
    def delete(self, user_id: UUID) -> bool:
        """Delete user."""
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not db_user:
            return False
        
        self.db.delete(db_user)
        self.db.commit()
        return True
    
    def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email."""
        return self.db.query(UserModel).filter(UserModel.email == email).first() is not None
    
    def exists_by_username(self, username: str) -> bool:
        """Check if user exists by username."""
        return self.db.query(UserModel).filter(UserModel.username == username).first() is not None
    
    def count_by_tenant_and_role(self, tenant_id: UUID, role: UserRole) -> int:
        """Count users by tenant and role."""
        return (
            self.db.query(UserModel)
            .filter(UserModel.tenant_id == tenant_id, UserModel.role == role.value)
            .count()
        )
    
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