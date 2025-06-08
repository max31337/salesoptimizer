from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from uuid import UUID

from domain.organization.value_objects.user_id import UserId


@dataclass
class ActivityLog:
    """Activity log domain entity."""
    
    id: UUID
    user_id: UserId
    tenant_id: Optional[UUID]
    activity_type: str
    description: str
    metadata: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert activity log to dictionary."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id.value),
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
            "activity_type": self.activity_type,
            "description": self.description,
            "metadata": self.metadata,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    @classmethod
    def create_user_login(
        cls,
        id: UUID,
        user_id: UserId,
        tenant_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        created_at: Optional[datetime] = None
    ) -> "ActivityLog":
        """Create a user login activity log."""
        return cls(
            id=id,
            user_id=user_id,
            tenant_id=tenant_id,
            activity_type="user_login",
            description="User logged in",
            metadata={"login_method": "credentials"},
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=created_at or datetime.now(timezone.utc)
        )

    @classmethod
    def create_user_created(
        cls,
        id: UUID,
        user_id: UserId,
        tenant_id: Optional[UUID] = None,
        created_by: Optional[UserId] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        created_at: Optional[datetime] = None
    ) -> "ActivityLog":
        """Create a user created activity log."""
        metadata: Dict[str, Any] = {}
        if created_by:
            metadata["created_by"] = str(created_by.value)
        
        return cls(
            id=id,
            user_id=user_id,
            tenant_id=tenant_id,
            activity_type="user_created",
            description="User account created",
            metadata=metadata,
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=created_at or datetime.now(timezone.utc)
        )

    @classmethod
    def create_team_joined(
        cls,
        id: UUID,
        user_id: UserId,
        team_id: UUID,
        team_name: str,
        tenant_id: Optional[UUID] = None,
        assigned_by: Optional[UserId] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        created_at: Optional[datetime] = None
    ) -> "ActivityLog":
        """Create a team joined activity log."""
        metadata: Dict[str, Any] = {
            "team_id": str(team_id),
            "team_name": team_name
        }
        if assigned_by:
            metadata["assigned_by"] = str(assigned_by.value)
        
        return cls(
            id=id,
            user_id=user_id,
            tenant_id=tenant_id,
            activity_type="team_joined",
            description=f"User joined team '{team_name}'",
            metadata=metadata,
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=created_at or datetime.now(timezone.utc)
        )
