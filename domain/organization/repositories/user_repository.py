from abc import ABC, abstractmethod
from typing import Optional

from domain.organization.entities.user import User
from domain.organization.value_objects.email import Email
from domain.organization.value_objects.user_id import UserId


class UserRepository(ABC):
    """User repository interface."""
    
    @abstractmethod
    async def get_by_id(self, user_id: UserId) -> Optional[User]:
        """Get user by ID."""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: Email) -> Optional[User]:
        """Get user by email."""
        pass
    
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        pass
    
    @abstractmethod
    async def save(self, user: User) -> User:
        """Save user."""
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """Update user."""
        pass
    
    @abstractmethod
    async def exists_by_email(self, email: Email) -> bool:
        """Check if user exists by email."""
        pass
    
    @abstractmethod
    async def count_superadmins(self) -> int:
        """Count the number of superadmin users."""
        pass