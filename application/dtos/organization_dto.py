from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class OrganizationResponse(BaseModel):
    """Response for organization/tenant information (includes UUIDs for admins)."""
    
    id: str
    name: str
    slug: str
    subscription_tier: str
    is_active: bool
    owner_id: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrganizationPublicResponse(BaseModel):
    """Public response for organization/tenant information (no UUIDs for regular users)."""
    
    name: str
    subscription_tier: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrganizationInfoResponse(BaseModel):
    """Response wrapper for organization information endpoint (for admins)."""
    
    organization: Optional[OrganizationResponse] = None
    message: Optional[str] = None

    class Config:
        from_attributes = True


class OrganizationInfoPublicResponse(BaseModel):
    """Public response wrapper for organization information endpoint (for regular users)."""
    
    organization: Optional[OrganizationPublicResponse] = None
    message: Optional[str] = None

    class Config:
        from_attributes = True
