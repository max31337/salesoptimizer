from typing import Optional
from datetime import datetime, timezone
from uuid import UUID
from dataclasses import dataclass, field

from domain.organization.value_objects.email import Email
from domain.organization.value_objects.user_id import UserId
from domain.organization.value_objects.user_role import UserRole, Permission
from domain.organization.value_objects.user_status import UserStatus


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
    password_strength: Optional[str] = None
    tenant_id: Optional[UUID] = None
    team_id: Optional[UUID] = None
    phone: Optional[str] = None
    profile_picture_url: Optional[str] = None
    bio: Optional[str] = None
    is_email_verified: bool = False
    last_login: Optional[datetime] = None
    invitation_token: Optional[str] = None
    invitation_expires_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    _oauth_provider: Optional[str] = None
    _oauth_provider_id: Optional[str] = None


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
        return self.status.value == "active"
    
    def has_password(self) -> bool:
        """Check if user has a password set."""
        return self.password_hash is not None and len(self.password_hash) > 0
    
    @property
    def oauth_provider(self) -> Optional[str]:
        return self._oauth_provider
    
    @property
    def oauth_provider_id(self) -> Optional[str]:
        return self._oauth_provider_id
    
    def is_oauth_user(self) -> bool:
        """Check if user was created via OAuth."""
        return self._oauth_provider is not None

    # Permission-based checks
    def has_permission(self, permission: Permission) -> bool:
        """Check if user has specific permission."""
        return self.role.has_permission(permission)
    
    def can_create_invitations(self) -> bool:
        """Check if user can create org admin invitations."""
        return self.role.can_create_invitations()
    
    def can_create_tenants(self) -> bool:
        """Check if user can create tenants/organizations."""
        return self.role.can_create_tenants()
    
    def can_manage_invitations(self) -> bool:
        """Check if user can manage invitations."""
        return self.role.can_manage_invitations()
    
    def can_update_profile_directly(self) -> bool:
        """Check if user can update their profile without approval."""
        # Sales managers and above can update their profile directly
        return self.role.hierarchy_level >= UserRole.sales_manager().hierarchy_level
    
    def update_profile(self, first_name: Optional[str] = None, last_name: Optional[str] = None, 
                      phone: Optional[str] = None, bio: Optional[str] = None, 
                      profile_picture_url: Optional[str] = None) -> None:
        """Update user profile information."""
        if first_name is not None:
            if not first_name or not first_name.strip():
                raise ValueError("First name cannot be empty")
            self.first_name = first_name.strip()
        
        if last_name is not None:
            if not last_name or not last_name.strip():
                raise ValueError("Last name cannot be empty")
            self.last_name = last_name.strip()
        
        if phone is not None:
            self.phone = phone.strip() if phone else None
        
        if bio is not None:
            self.bio = bio.strip() if bio else None
        
        if profile_picture_url is not None:
            self.profile_picture_url = profile_picture_url.strip() if profile_picture_url else None
        
        self.updated_at = datetime.now(timezone.utc)
