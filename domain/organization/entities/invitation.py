from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Optional
from uuid import UUID

from domain.organization.value_objects.user_id import UserId
from domain.organization.value_objects.email import Email
from domain.organization.value_objects.invitation_token import InvitationToken
from domain.organization.entities.user import UserRole


@dataclass
class Invitation:
    """Invitation aggregate root."""
    
    id: UserId
    email: Email
    role: UserRole
    token: InvitationToken
    invited_by_id: UserId
    organization_name: str
    tenant_id: UUID 
    expires_at: datetime
    is_used: bool = False
    used_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc)
        if not self.updated_at:
            self.updated_at = datetime.now(timezone.utc)
    
    @classmethod
    def create_org_admin_invitation(
        cls,
        email: Email,
        invited_by_id: UserId,
        organization_name: str,
        tenant_id: UUID,  # Tenant is already created
        expires_in_days: int = 7
    ) -> 'Invitation':
        """Create a new organization admin invitation with pre-created tenant."""
        if not organization_name or not organization_name.strip():
            raise ValueError("Organization name is required")
        
        if not tenant_id:
            raise ValueError("Tenant ID is required")
            
        expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)
        
        return cls(
            id=UserId.generate(),
            email=email,
            role=UserRole.org_admin(),
            token=InvitationToken.generate(),
            invited_by_id=invited_by_id,
            organization_name=organization_name.strip(),
            tenant_id=tenant_id,
            expires_at=expires_at
        )
    
    def is_expired(self) -> bool:
        """Check if invitation has expired."""
        return datetime.now(timezone.utc) > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if invitation is valid (not used and not expired)."""
        return not self.is_used and not self.is_expired()
    
    def mark_as_used(self) -> None:
        """Mark invitation as used."""
        if self.is_used:
            raise ValueError("Invitation has already been used")
        if self.is_expired():
            raise ValueError("Invitation has expired")
        
        self.is_used = True
        self.used_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)