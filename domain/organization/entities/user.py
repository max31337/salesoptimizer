import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from dataclasses import dataclass, field

class UserRole(Enum):
    SUPER_ADMIN = "super_admin"
    ORG_ADMIN = "org_admin"
    MANAGER = "manager"
    SALES_REP = "sales_rep"

class UserStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"

@dataclass
class User:
    email: str
    first_name: str
    last_name: str
    id: Optional[uuid.UUID] = field(default_factory=uuid.uuid4)
    tenant_id: Optional[uuid.UUID] = None
    team_id: Optional[uuid.UUID] = None  # Added team assignment
    username: Optional[str] = None
    phone: Optional[str] = None
    password_hash: Optional[str] = None
    role: UserRole = UserRole.SALES_REP
    status: UserStatus = UserStatus.PENDING  # Default to PENDING as per tests
    is_email_verified: bool = False
    last_login: Optional[datetime] = None
    invitation_token: Optional[str] = None
    invitation_expires_at: Optional[datetime] = None
    created_at: Optional[datetime] = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    @property
    def full_name(self) -> str:
        """Get the user's full name."""
        first = self.first_name.strip() if self.first_name else ""
        last = self.last_name.strip() if self.last_name else ""
    
        # Join non-empty parts with a single space
        parts = [part for part in [first, last] if part]
        return " ".join(parts)

    def is_admin(self) -> bool:
        """Check if user has admin privileges."""
        return self.role in [UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN]

    def is_super_admin(self) -> bool:
        """Check if user is a super admin."""
        return self.role == UserRole.SUPER_ADMIN

    def can_manage_users(self) -> bool:
        """Check if user can manage other users."""
        return self.role in [UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN, UserRole.MANAGER]

    def can_access_tenant(self, tenant_id: uuid.UUID) -> bool:
        """Check if user can access a specific tenant."""
        # Super admins can access any tenant
        if self.role == UserRole.SUPER_ADMIN:
            return True
        # Regular users can only access their own tenant
        return self.tenant_id == tenant_id

    def can_manage_tenant(self, tenant_id: Optional[uuid.UUID] = None) -> bool:
        """Check if user can manage a specific tenant."""
        # Super admins can manage any tenant
        if self.role == UserRole.SUPER_ADMIN:
            return True
        # Org admins can only manage their own tenant
        if self.role == UserRole.ORG_ADMIN:
            if tenant_id is None:
                return True  # Can manage their own tenant
            return self.tenant_id == tenant_id
        return False

    def can_access_user_data(self, other_user_id: uuid.UUID) -> bool:
        """Check if user can access another user's data."""
        # Admins can access any user data
        if self.is_admin():
            return True
        # Users can access their own data
        return self.id == other_user_id

    def record_login(self) -> None:
        """Record the user's last login time."""
        self.last_login = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def verify_email(self) -> None:
        """Mark the user's email as verified."""
        self.is_email_verified = True
        self.updated_at = datetime.now(timezone.utc)

    def change_status(self, new_status: UserStatus) -> None:
        """Change the user's status."""
        self.status = new_status
        self.updated_at = datetime.now(timezone.utc)

    def activate(self) -> None:
        """Activate the user account."""
        self.change_status(UserStatus.ACTIVE)

    def deactivate(self) -> None:
        """Deactivate the user account."""
        self.change_status(UserStatus.INACTIVE)

    def suspend(self) -> None:
        """Suspend the user account."""
        self.change_status(UserStatus.SUSPENDED)

    def update_profile(
        self, 
        first_name: Optional[str] = None, 
        last_name: Optional[str] = None, 
        phone: Optional[str] = None
    ) -> None:
        """Update user profile information."""
        if first_name is not None:
            self.first_name = first_name
        if last_name is not None:
            self.last_name = last_name
        if phone is not None:
            self.phone = phone
        self.updated_at = datetime.now(timezone.utc)

    def change_role(self, new_role: UserRole) -> None:
        """Change the user's role."""
        self.role = new_role
        self.updated_at = datetime.now(timezone.utc)

    def set_password(self, password_hash: str) -> None:
        """Set the user's password hash and update the updated_at timestamp."""
        self.password_hash = password_hash
        self.updated_at = datetime.now(timezone.utc)

    def is_active(self) -> bool:
        """Check if user is active."""
        return self.status == UserStatus.ACTIVE

    def is_pending(self) -> bool:
        """Check if user is pending activation."""
        return self.status == UserStatus.PENDING

    def is_suspended(self) -> bool:
        """Check if user is suspended."""
        return self.status == UserStatus.SUSPENDED

    def has_valid_invitation(self) -> bool:
        """Check if user has a valid invitation token."""
        if not self.invitation_token or not self.invitation_expires_at:
            return False
        return datetime.now(timezone.utc) < self.invitation_expires_at

    def clear_invitation(self) -> None:
        """Clear invitation token and expiration."""
        self.invitation_token = None
        self.invitation_expires_at = None
        self.updated_at = datetime.now(timezone.utc)

    def assign_to_team(self, team_id: uuid.UUID) -> None:
        """Assign user to a team."""
        self.team_id = team_id
        self.updated_at = datetime.now(timezone.utc)
    
    def remove_from_team(self) -> None:
        """Remove user from current team."""
        self.team_id = None
        self.updated_at = datetime.now(timezone.utc)
    
    def can_manage_team(self, team_id: Optional[uuid.UUID] = None) -> bool:
        """Check if user can manage a specific team."""
        # Super admins can manage any team
        if self.role == UserRole.SUPER_ADMIN:
            return True
        # Org admins can manage teams within their tenant
        if self.role == UserRole.ORG_ADMIN:
            return True
        # Managers can only manage their assigned team
        if self.role == UserRole.MANAGER:
            if team_id is None:
                return self.team_id is not None  # Can manage their own team
            return self.team_id == team_id
        return False
    
    def can_access_team_data(self, team_id: uuid.UUID) -> bool:
        """Check if user can access team data."""
        # Admins can access any team data
        if self.is_admin():
            return True
        # Users can access their own team data
        return self.team_id == team_id
