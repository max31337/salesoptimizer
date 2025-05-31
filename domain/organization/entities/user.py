from typing import Optional
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID
from dataclasses import dataclass, field

from domain.organization.value_objects.email import Email
from domain.organization.value_objects.user_id import UserId


class UserRole(Enum):
    """User roles in the system."""
    SUPER_ADMIN = "super_admin"
    ORG_ADMIN = "org_admin"
    SALES_MANAGER = "sales_manager"
    SALES_REP = "sales_rep"


class UserStatus(Enum):
    """User status in the system."""
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


@dataclass
class User:
    """User aggregate root."""
    
    id: Optional[UserId]
    email: Email
    username: Optional[str]
    first_name: str
    last_name: str
    password_hash: Optional[str]
    role: UserRole
    status: UserStatus
    tenant_id: Optional[UUID] = None
    team_id: Optional[UUID] = None
    phone: Optional[str] = None
    is_email_verified: bool = False
    last_login: Optional[datetime] = None
    invitation_token: Optional[str] = None
    invitation_expires_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self) -> None:
        """Validate user data after initialization."""
        if not self.first_name or not self.first_name.strip():
            raise ValueError("First name cannot be empty")
        
        if not self.last_name or not self.last_name.strip():
            raise ValueError("Last name cannot be empty")
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}".strip()
    
    def record_login(self) -> None:
        """Record the user's login time."""
        self.last_login = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
    
    def is_active(self) -> bool:
        """Check if user is active."""
        return self.status == UserStatus.ACTIVE
    
    def has_password(self) -> bool:
        """Check if user has a password set."""
        return self.password_hash is not None and len(self.password_hash) > 0
