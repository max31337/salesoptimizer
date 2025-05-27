from typing import List, Optional
from sqlalchemy.orm import Session
from domain.entities.user import User, UserRole, UserStatus
from domain.repositories.user_repository import UserRepository
from infrastructure.db.models.user_model import UserModel

class UserRepositoryImpl(UserRepository):
    
    def __init__(self, db: Session):
        self.db = db
    
    def _model_to_entity(self, model: UserModel) -> User:
        return User(
            id=getattr(model, "id", None),
            email=getattr(model, "email", "") or "",
            username=getattr(model, "username", "") or "",
            first_name=getattr(model, "first_name", "") or "",
            last_name=getattr(model, "last_name", "") or "",
            phone=getattr(model, "phone", None),
            role=UserRole(model.role) if getattr(model, "role", None) else UserRole.SALES_REP,
            status=UserStatus(model.status) if getattr(model, "status", None) else UserStatus.ACTIVE,
            is_email_verified=bool(model.is_email_verified) if getattr(model, "is_email_verified", None) is not None else False,
            created_at=getattr(model, "created_at", None),
            updated_at=getattr(model, "updated_at", None),
            last_login=getattr(model, "last_login", None)
        )
    
    def _entity_to_model(self, entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            email=entity.email,
            username=entity.username,
            first_name=entity.first_name,
            last_name=entity.last_name,
            phone=entity.phone,
            role=entity.role,
            status=entity.status,
            is_email_verified=entity.is_email_verified,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            last_login=entity.last_login
        )
    
    def create(self, user: User) -> User:
        db_user = UserModel(
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            role=user.role,
            status=user.status,
            is_email_verified=user.is_email_verified
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return self._model_to_entity(db_user)
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        return self._model_to_entity(db_user) if db_user else None
    
    def get_by_email(self, email: str) -> Optional[User]:
        db_user = self.db.query(UserModel).filter(UserModel.email == email).first()
        return self._model_to_entity(db_user) if db_user else None
    
    def get_by_username(self, username: str) -> Optional[User]:
        db_user = self.db.query(UserModel).filter(UserModel.username == username).first()
        return self._model_to_entity(db_user) if db_user else None
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        db_users = self.db.query(UserModel).offset(skip).limit(limit).all()
        return [self._model_to_entity(db_user) for db_user in db_users]
    
    def update(self, user: User) -> User:
        db_user = self.db.query(UserModel).filter(UserModel.id == user.id).first()
        if db_user:
            for key, value in user.__dict__.items():
                if value is not None and hasattr(db_user, key) and key != 'id':
                    setattr(db_user, key, value)
            self.db.commit()
            self.db.refresh(db_user)
            return self._model_to_entity(db_user)
        return user
    
    def delete(self, user_id: int) -> bool:
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if db_user:
            self.db.delete(db_user)
            self.db.commit()
            return True
        return False
    
    def exists_by_email(self, email: str) -> bool:
        return self.db.query(UserModel).filter(UserModel.email == email).first() is not None
    
    def exists_by_username(self, username: str) -> bool:
        return self.db.query(UserModel).filter(UserModel.username == username).first() is not None