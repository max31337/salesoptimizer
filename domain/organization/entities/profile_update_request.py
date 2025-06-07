from typing import Optional, Dict, Any
from datetime import datetime, timezone
from uuid import UUID
from dataclasses import dataclass, field
from enum import Enum

from domain.organization.value_objects.user_id import UserId


class ProfileUpdateStatus(Enum):
    """Profile update request status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class ProfileUpdateRequest:
    """Profile update request aggregate root."""
    
    id: Optional[UUID]
    user_id: UserId
    requested_by_id: UserId
    requested_changes: Dict[str, Any]
    status: ProfileUpdateStatus
    reason: Optional[str] = None
    approved_by_id: Optional[UserId] = None
    approved_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        """Validate profile update request data after initialization."""
        if not self.requested_changes:
            raise ValueError("Requested changes cannot be empty")

    def approve(self, approved_by: UserId, reason: Optional[str] = None) -> None:
        """Approve the profile update request."""
        if self.status != ProfileUpdateStatus.PENDING:
            raise ValueError("Only pending requests can be approved")
        
        self.status = ProfileUpdateStatus.APPROVED
        self.approved_by_id = approved_by
        self.approved_at = datetime.now(timezone.utc)
        self.reason = reason
        self.updated_at = datetime.now(timezone.utc)

    def reject(self, rejected_by: UserId, reason: str) -> None:
        """Reject the profile update request."""
        if self.status != ProfileUpdateStatus.PENDING:
            raise ValueError("Only pending requests can be rejected")
        
        if not reason or not reason.strip():
            raise ValueError("Reason is required for rejection")
        
        self.status = ProfileUpdateStatus.REJECTED
        self.approved_by_id = rejected_by
        self.reason = reason.strip()
        self.updated_at = datetime.now(timezone.utc)

    def is_pending(self) -> bool:
        """Check if the request is pending."""
        return self.status == ProfileUpdateStatus.PENDING

    def is_approved(self) -> bool:
        """Check if the request is approved."""
        return self.status == ProfileUpdateStatus.APPROVED

    def is_rejected(self) -> bool:
        """Check if the request is rejected."""
        return self.status == ProfileUpdateStatus.REJECTED
