from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4



@dataclass
class Team:
    """Team entity representing a sales team within an organization."""
    
    name: str
    tenant_id: UUID
    id: Optional[UUID] = field(default_factory=uuid4)
    manager_id: Optional[UUID] = None
    description: Optional[str] = None
    is_active: bool = True
    max_members: Optional[int] = None
    created_at: Optional[datetime] = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    
    def __post_init__(self) -> None:
        """Validate team data after initialization."""
        if not self.name or not self.name.strip():
            raise ValueError("Team name is required")
        
        if not self.tenant_id:
            raise ValueError("Tenant ID is required")
        
        # Clean up name
        self.name = self.name.strip()
    
    @property
    def display_name(self) -> str:
        """Get display name for the team."""
        return self.name
    
    def can_add_member(self, current_member_count: int) -> bool:
        """Check if team can accept new members."""
        if not self.is_active:
            return False
        
        if self.max_members is None:
            return True
        
        return current_member_count < self.max_members
    
    def has_manager(self) -> bool:
        """Check if team has a manager assigned."""
        return self.manager_id is not None