from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from domain.organization.entities.user import User


class UserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        pass
    
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        pass
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user."""
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """Update an existing user."""
        pass
    
    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """Delete a user."""
        pass
    
    @abstractmethod
    async def get_by_invitation_token(self, token: str) -> Optional[User]:
        """Get user by invitation token."""
        pass
    
    @abstractmethod
    async def get_by_tenant(self, tenant_id: UUID, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users by tenant ID."""
        pass