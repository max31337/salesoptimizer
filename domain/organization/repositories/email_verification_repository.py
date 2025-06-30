from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from domain.organization.entities.email_verification import EmailVerification

class EmailVerificationRepository(ABC):
    """Abstract base class for email verification repository."""

    @abstractmethod
    async def add(self, email_verification: EmailVerification) -> None:
        """Add a new email verification to the repository."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_token(self, token: str) -> Optional[EmailVerification]:
        """Get an email verification by token."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> Optional[EmailVerification]:
        """Get an email verification by user ID."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, email_verification: EmailVerification) -> None:
        """Update an existing email verification."""
        raise NotImplementedError
