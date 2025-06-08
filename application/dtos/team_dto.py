from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class TeamMemberResponse(BaseModel):
    """Response model for team member information."""
    id: str
    email: str
    username: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
    joined_team_at: Optional[datetime] = None


class TeamManagerResponse(BaseModel):
    """Response model for team manager information."""
    id: str
    email: str
    username: str
    full_name: Optional[str] = None
    role: str


class TeamResponse(BaseModel):
    """Basic team response model."""
    id: str
    name: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    member_count: int


class TeamDetailResponse(BaseModel):
    """Detailed team response model with members and manager."""
    id: str
    name: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Manager information
    manager: Optional[TeamManagerResponse] = None
    
    # Team members
    members: List[TeamMemberResponse] = []
    member_count: int
    
    # Organization context
    tenant_id: str
