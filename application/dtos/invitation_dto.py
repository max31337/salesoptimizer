from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
import uuid


class CreateInvitationRequest(BaseModel):
    """Request to create an organization admin invitation with tenant."""
    
    email: EmailStr = Field(..., description="Email of the organization admin to invite")
    organization_name: str = Field(..., min_length=1, max_length=255, description="Name of the organization")
    subscription_tier: str = Field(default="basic", description="Subscription tier (basic, pro, enterprise)")
    slug: Optional[str] = Field(None, min_length=3, max_length=50, description="Custom slug for the organization (auto-generated if not provided)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "admin@example.com",
                "organization_name": "Acme Corporation",
                "subscription_tier": "pro",
                "slug": "acme-corp"
            }
        }


class InvitationResponse(BaseModel):
    """Response for invitation data."""
    
    id: uuid.UUID
    email: str
    role: str
    token: str
    invited_by_id: uuid.UUID
    organization_name: str
    tenant_id: uuid.UUID
    expires_at: datetime
    is_used: bool
    used_at: Optional[datetime]
    created_at: datetime


class TenantResponse(BaseModel):
    """Response for tenant data."""
    
    id: uuid.UUID
    name: str
    slug: str
    subscription_tier: str
    is_active: bool
    owner_id: Optional[uuid.UUID]
    created_at: datetime


class InvitationWithTenantResponse(BaseModel):
    """Response containing both invitation and tenant data."""
    
    invitation: InvitationResponse
    tenant: TenantResponse