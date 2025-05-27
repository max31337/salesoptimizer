from datetime import datetime, timezone
from typing import Optional
from dataclasses import dataclass
from enum import Enum

class UserRole(Enum):
    ADMIN = "admin"
    SALES_REP = "sales_rep"
    MANAGER = "manager"
    VIEWER = "viewer"

class UserStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

@dataclass
class User:
    id: Optional[int] = None
    email: str = ""
    username: str = ""
    first_name: str = ""
    last_name: str = ""
    phone: Optional[str] = None
    role: UserRole = UserRole.SALES_REP
    status: UserStatus = UserStatus.ACTIVE
    is_email_verified: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()
    
    def is_active(self) -> bool:
        return self.status == UserStatus.ACTIVE
    
    def can_manage_users(self) -> bool:
        return self.role in [UserRole.ADMIN, UserRole.MANAGER]
    
    def activate(self):
        self.status = UserStatus.ACTIVE
        self.updated_at = datetime.now(timezone.utc)
    
    def deactivate(self):
        self.status = UserStatus.INACTIVE
        self.updated_at = datetime.now(timezone.utc)
    
    def verify_email(self):
        self.is_email_verified = True
        self.updated_at = datetime.now(timezone.utc)
