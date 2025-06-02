from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from domain.organization.value_objects.tenant_id import TenantId
from domain.organization.value_objects.user_id import UserId
from domain.organization.value_objects.tenant_name import TenantName


@dataclass
class Tenant:
    """Tenant aggregate root representing an organization."""

    id: Optional[TenantId] 
    name: TenantName
    slug: str
    subscription_tier: str = "basic"
    is_active: bool = True
    owner_id: Optional[UserId] = None
    settings: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        if self.settings is None:
            self.settings = {}
        
        # Ensure slug is generated from name if not provided
        if not self.slug:
            self.slug = self.name.to_slug()
    
    @classmethod
    def create(
        cls,
        name: TenantName,
        owner_id: Optional[UserId] = None,
        subscription_tier: str = "basic"
    ) -> 'Tenant':
        """Create a new tenant."""
        slug = name.to_slug()
        
        return cls(
            id=TenantId.generate(),
            name=name,
            slug=slug,
            subscription_tier=subscription_tier,
            is_active=True,
            owner_id=owner_id,
            settings={}
        )
    
    def set_owner(self, owner_id: UserId) -> None:
        """Set the tenant owner."""
        if not owner_id:
            raise ValueError("Owner ID cannot be empty")
        
        self.owner_id = owner_id
        self.updated_at = datetime.now(timezone.utc)
    
    def activate(self) -> None:
        """Activate the tenant."""
        self.is_active = True
        self.updated_at = datetime.now(timezone.utc)
    
    def deactivate(self) -> None:
        """Deactivate the tenant."""
        self.is_active = False
        self.updated_at = datetime.now(timezone.utc)
    
    def update_name(self, name: TenantName) -> None:
        """Update tenant name and regenerate slug."""
        self.name = name
        self.slug = name.to_slug()
        self.updated_at = datetime.now(timezone.utc)
    
    def update_subscription_tier(self, tier: str) -> None:
        """Update subscription tier."""
        valid_tiers = ["basic", "professional", "enterprise"]
        if tier not in valid_tiers:
            raise ValueError(f"Invalid subscription tier: {tier}. Must be one of {valid_tiers}")
        
        self.subscription_tier = tier
        self.updated_at = datetime.now(timezone.utc)
    
    def update_setting(self, key: str, value: Any) -> None:
        """Update a specific setting."""
        if not key:
            raise ValueError("Setting key cannot be empty")
        
        if self.settings is None:
            self.settings = {}
        
        self.settings[key] = value
        self.updated_at = datetime.now(timezone.utc)
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a specific setting."""
        if not self.settings:
            return default
        return self.settings.get(key, default)
    
    def remove_setting(self, key: str) -> None:
        """Remove a specific setting."""
        if self.settings and key in self.settings:
            del self.settings[key]
            self.updated_at = datetime.now(timezone.utc)
    
    def has_owner(self) -> bool:
        """Check if tenant has an owner."""
        return self.owner_id is not None
    
    def is_owned_by(self, user_id: UserId) -> bool:
        """Check if tenant is owned by specific user."""
        return self.owner_id is not None and self.owner_id == user_id
    
    def __str__(self) -> str:
        return f"Tenant({self.name.value})"