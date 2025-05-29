from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from domain.organization.entities.user import User, UserRole


class UserRepository(ABC):
    @abstractmethod
    def create(self, user: User) -> User:
        pass
    
    @abstractmethod
    def get_by_id(self, user_id: UUID) -> Optional[User]:
        pass
    
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        pass
    
    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        pass
    
    @abstractmethod
    def get_by_invitation_token(self, token: str) -> Optional[User]:
        pass
    
    @abstractmethod
    def get_by_tenant(self, tenant_id: UUID, skip: int = 0, limit: int = 100) -> List[User]:
        pass
    
    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        pass
    
    @abstractmethod
    def update(self, user: User) -> User:
        pass
    
    @abstractmethod
    def delete(self, user_id: UUID) -> bool:
        pass
    
    @abstractmethod
    def exists_by_email(self, email: str) -> bool:
        pass
    
    @abstractmethod
    def exists_by_username(self, username: str) -> bool:
        pass
    
    @abstractmethod
    def count_by_tenant_and_role(self, tenant_id: UUID, role: UserRole) -> int:
        pass