
from typing import Optional, List
from datetime import datetime, timezone
from uuid import UUID
from dataclasses import dataclass, field


from domain.organization.value_objects.email import Email
from domain.organization.value_objects.user_id import UserId
from domain.organization.value_objects.user_role import UserRole, Permission
from domain.organization.value_objects.user_status import UserStatus
from domain.organization.entities.login_activity import LoginActivity


@dataclass
class User:

    """User aggregate root (cleaned up, no invitation/email_verification/oauth_provider fields)."""
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
    profile_picture_url: Optional[str] = None
    bio: Optional[str] = None
    is_email_verified: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    job_title: Optional[str] = None
    accept_terms: Optional[bool] = None
    accept_privacy: Optional[bool] = None
    marketing_opt_in: Optional[bool] = None
    password_strength: Optional[str] = None
    # Track login activities for this user
    login_activities: List["LoginActivity"] = field(default_factory=list) #type: ignore

    def __post_init__(self) -> None:
        if not self.first_name or not self.first_name.strip():
            raise ValueError("First name cannot be empty")
        if not self.last_name or not self.last_name.strip():
            raise ValueError("Last name cannot be empty")
        if self.job_title is None:
            self.job_title = ""
        if self.accept_terms is None:
            self.accept_terms = False
        if self.accept_privacy is None:
            self.accept_privacy = False
        if self.marketing_opt_in is None:
            self.marketing_opt_in = False

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def is_active(self) -> bool:
        return self.status.value == "active"

    def has_password(self) -> bool:
        return self.password_hash is not None and len(self.password_hash) > 0

    def has_permission(self, permission: Permission) -> bool:
        return self.role.has_permission(permission)

    def can_create_invitations(self) -> bool:
        return self.role.can_create_invitations()

    def can_create_tenants(self) -> bool:
        return self.role.can_create_tenants()

    def can_manage_invitations(self) -> bool:
        return self.role.can_manage_invitations()

    def can_update_profile_directly(self) -> bool:
        return self.role.hierarchy_level >= UserRole.sales_manager().hierarchy_level

    def update_profile(self, first_name: Optional[str] = None, last_name: Optional[str] = None,
                      phone: Optional[str] = None, bio: Optional[str] = None,
                      profile_picture_url: Optional[str] = None) -> None:
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
