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


class OrganizationRegistrationRequest(BaseModel):
    """Request for organization registration."""
    
    # Organization details
    organization_name: str
    organization_slug: Optional[str] = None
    industry: str = ""
    organization_size: str = ""
    website: Optional[str] = None
    
    # Admin user details
    first_name: str
    last_name: str
    email: str
    password: str
    job_title: str = ""
    
    # Subscription details
    subscription_tier: str = "trial"  # trial, basic, pro
    
    # Legal agreements
    accept_terms: bool
    accept_privacy: bool
    marketing_opt_in: bool = False


class OrganizationRegistrationResponse(BaseModel):
    """Response for organization registration."""
    
    # User details
    user_id: str
    email: str
    first_name: str
    last_name: str
    role: str
    
    # Organization details
    tenant_id: str
    organization_name: str
    organization_slug: str
    subscription_tier: str
    
    # Status
    message: str = "Organization registered successfully"


class InvitationSignupRequest(BaseModel):
    """Request for completing invitation signup."""
    
    invitation_token: str
    first_name: str
    last_name: str
    password: str
    job_title: Optional[str] = None


class InvitationSignupResponse(BaseModel):
    """Response for invitation signup completion."""
    
    # User details
    user_id: str
    email: str
    first_name: str
    last_name: str
    role: str
    
    # Organization details
    tenant_id: str
    organization_name: str
    
    message: str = "Account setup completed successfully"
