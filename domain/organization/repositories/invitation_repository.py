from abc import ABC, abstractmethod
from typing import Optional, List
from domain.organization.entities.invitation import Invitation
from domain.organization.value_objects.email import Email
from domain.organization.value_objects.invitation_token import InvitationToken
from domain.organization.value_objects.user_id import UserId


class InvitationRepository(ABC):
    """Repository for invitation operations."""
    
    @abstractmethod
    async def save(self, invitation: Invitation) -> Invitation:
        """Save invitation."""
        pass
    
    @abstractmethod
    async def get_by_token(self, token: InvitationToken) -> Optional[Invitation]:
        """Get invitation by token."""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: Email) -> Optional[Invitation]:
        """Get active invitation by email."""
        pass
    
    @abstractmethod
    async def get_all(self) -> List[Invitation]:
        """Get all invitations."""
        pass
    
    @abstractmethod
    async def update(self, invitation: Invitation) -> Invitation:
        """Update invitation."""
        pass
    
    @abstractmethod
    async def delete(self, invitation_id: UserId) -> bool:
        """Delete invitation by ID."""
        pass