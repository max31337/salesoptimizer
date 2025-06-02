from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from uuid import UUID


class CreateInvitationRequest(BaseModel):
    """Create invitation request DTO."""
    
    email: EmailStr
    organization_name: str


class InvitationResponse(BaseModel):
    """Invitation response DTO."""
    
    id: UUID
    email: EmailStr
    role: str
    token: str
    invited_by_id: UUID
    organization_name: str
    tenant_id: UUID  # Include tenant_id
    expires_at: datetime
    is_used: bool
    used_at: Optional[datetime] = None
    created_at: datetime


class TenantResponse(BaseModel):
    """Tenant response DTO."""
    
    id: UUID
    name: str
    slug: str
    is_active: bool
    owner_id: Optional[UUID] = None
    created_at: datetime


class InvitationWithTenantResponse(BaseModel):
    """Invitation with tenant response DTO."""
    
    invitation: InvitationResponse
    tenant: TenantResponse