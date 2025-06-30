from typing import Optional
from datetime import datetime, timezone
from uuid import UUID
from dataclasses import dataclass, field

from domain.organization.value_objects.user_id import UserId

@dataclass
class OAuthProvider:
    """OAuth provider entity."""
    
    id: Optional[UUID]
    user_id: UserId
    provider: str
    provider_user_id: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
