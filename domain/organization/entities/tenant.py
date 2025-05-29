from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Any, Dict
from uuid import UUID, uuid4
from enum import Enum

class SubscriptionTier(Enum):
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

@dataclass
class Tenant:
    name: str
    slug: str
    settings: Dict[str, Any] = field(default_factory=dict)  # type: ignore[type-arg]
    subscription_tier: SubscriptionTier = SubscriptionTier.BASIC
    is_active: bool = True
    id: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if self.id is None:
            self.id = uuid4()

    def activate(self):
        self.is_active = True
        self.updated_at = datetime.now(timezone.utc)

    def deactivate(self):
        self.is_active = False
        self.updated_at = datetime.now(timezone.utc)

    def upgrade_subscription(self, tier: SubscriptionTier):
        self.subscription_tier = tier
        self.updated_at = datetime.now(timezone.utc)
