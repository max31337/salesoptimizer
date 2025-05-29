from typing import List, Optional
from uuid import UUID
from domain.organization.entities.user import User
from domain.organization.repositories.user_repository import UserRepository


class UserUseCases:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        return await self.user_repository.get_by_id(user_id)
    
    async def get_users_by_tenant(self, tenant_id: UUID, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users by tenant."""
        return await self.user_repository.get_by_tenant(tenant_id, skip, limit)
    
    async def create_user(self, user: User) -> User:
        """Create a new user."""
        return await self.user_repository.create(user)
    
    async def update_user(self, user: User) -> User:
        """Update user."""
        return await self.user_repository.update(user)
    
    async def delete_user(self, user_id: UUID) -> bool:
        """Delete user."""
        return await self.user_repository.delete(user_id)
