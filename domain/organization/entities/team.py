import uuid
from datetime import datetime, timezone
from typing import Optional
from dataclasses import dataclass, field



@dataclass
class Team:
    """Team entity representing a sales team within an organization."""
    
    tenant_id: uuid.UUID
    name: str
    description: Optional[str] = None
    id: Optional[uuid.UUID] = field(default_factory=uuid.uuid4)
    manager_id: Optional[uuid.UUID] = None  # Team Manager user ID
    is_active: bool = True
    created_at: Optional[datetime] = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    
    def update_info(self, name: Optional[str] = None, description: Optional[str] = None) -> None:
        """Update team information."""
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        self.updated_at = datetime.now(timezone.utc)
    
    def assign_manager(self, manager_id: uuid.UUID) -> None:
        """Assign a manager to this team."""
        self.manager_id = manager_id
        self.updated_at = datetime.now(timezone.utc)
    
    def deactivate(self) -> None:
        """Deactivate the team."""
        self.is_active = False
        self.updated_at = datetime.now(timezone.utc)
    
    def activate(self) -> None:
        """Activate the team."""
        self.is_active = True
        self.updated_at = datetime.now(timezone.utc)