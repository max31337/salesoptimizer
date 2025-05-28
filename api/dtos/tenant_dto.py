from datetime import datetime, timezone
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from domain.entities.tenant import SubscriptionTier, Tenant

class TenantCreateDTO(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=100, pattern=r'^[a-z0-9-]+$')
    subscription_tier: SubscriptionTier = SubscriptionTier.BASIC
    settings: Optional[Dict[str, Any]] = None

class TenantUpdateDTO(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    subscription_tier: Optional[SubscriptionTier] = None
    is_active: Optional[bool] = None
    settings: Optional[Dict[str, Any]] = None

class TenantResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[UUID]
    name: str
    slug: str
    subscription_tier: SubscriptionTier
    is_active: bool
    settings: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]
    
    @classmethod
    def from_entity(cls, tenant: Tenant) -> "TenantResponseDTO":
        return cls(
            id=tenant.id,
            name=tenant.name,
            slug=tenant.slug,
            subscription_tier=tenant.subscription_tier,
            is_active=tenant.is_active,
            settings=tenant.settings or {},
            created_at=tenant.created_at or datetime.now(timezone.utc),
            updated_at=tenant.updated_at
        )