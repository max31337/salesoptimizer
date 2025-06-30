from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from domain.organization.entities.oauth_provider import OAuthProvider

class OAuthProviderRepository(ABC):
    """Abstract base class for OAuth provider repository."""

    @abstractmethod
    async def add(self, oauth_provider: OAuthProvider) -> None:
        """Add a new OAuth provider to the repository."""
        raise NotImplementedError
    
    @abstractmethod
    async def get_by_provider_user_id(self, provider: str, provider_user_id: str) -> Optional[OAuthProvider]:
        """Get an OAuth provider by provider and provider user ID."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> List[OAuthProvider]:
        """Get all OAuth providers for a user."""
        raise NotImplementedError
