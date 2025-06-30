from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from domain.organization.value_objects.user_id import UserId

@dataclass
class LoginActivity:
    """Domain entity for user login/logout activity."""
    id: Optional[UUID]
    user_id: UserId
    login_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    logout_at: Optional[datetime] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


    def record_login(self, login_time: Optional[datetime] = None, ip_address: Optional[str] = None, user_agent: Optional[str] = None):
        self.login_at = login_time or datetime.now(timezone.utc)
        self.ip_address = ip_address
        self.user_agent = user_agent

    def mark_logout(self, logout_time: Optional[datetime] = None):
        self.logout_at = logout_time or datetime.now(timezone.utc)
