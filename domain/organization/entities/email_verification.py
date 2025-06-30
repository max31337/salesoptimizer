from typing import Optional
from datetime import datetime, timezone
from uuid import UUID
from dataclasses import dataclass, field

from domain.organization.value_objects.user_id import UserId

@dataclass
class EmailVerification:
    """Email verification entity."""
    
    id: Optional[UUID]
    user_id: UserId
    token: str
    sent_at: datetime
    expires_at: datetime
    is_verified: bool = False
    verified_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def verify(self) -> None:
        """Mark the email as verified."""
        if not self.is_verified:
            self.is_verified = True
            self.verified_at = datetime.now(timezone.utc)
            self.updated_at = datetime.now(timezone.utc)

    def is_expired(self) -> bool:
        """Check if the verification token has expired."""
        return datetime.now(timezone.utc) > self.expires_at
