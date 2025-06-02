from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

@dataclass
class EmailMessage:
    """Email message data."""
    to_email: str
    subject: str
    html_content: str
    text_content: Optional[str] = None
    from_email: Optional[str] = None
    from_name: Optional[str] = None

class EmailService(ABC):
    """Abstract email service interface."""
    
    @abstractmethod
    async def send_email(self, message: EmailMessage) -> bool:
        """Send an email message."""
        pass
    
    @abstractmethod
    async def send_invitation_email(
        self,
        to_email: str,
        organization_name: str,
        invitation_token: str,
        invited_by_name: str,
        expires_at: str
    ) -> bool:
        """Send an organization admin invitation email."""
        pass