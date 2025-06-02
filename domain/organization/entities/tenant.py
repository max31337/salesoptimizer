from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Optional, Dict, Any
import re

from domain.organization.value_objects.user_id import UserId
from domain.organization.value_objects.tenant_name import TenantName


@dataclass
class Tenant:
    """Tenant aggregate root representing an organization."""

    id: UserId
    name: TenantName
    slug: str
    subscription_tier: str
    is_active: bool = True
    owner_id: Optional[UserId] = None
    settings: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)

        # Ensure slug is generated from name if not provided
        if not self.slug:
            self.slug = self.name.to_slug()

    @classmethod
    def create(
        cls,
        name: TenantName,
        subscription_tier: str = "basic",
        slug: Optional[str] = None,
        owner_id: Optional[UserId] = None,
    ) -> "Tenant":
        """Create a new tenant."""
        if subscription_tier not in ["basic", "pro", "enterprise"]:
            raise ValueError("Invalid subscription tier. Must be: basic, pro, or enterprise")

        # Generate slug if not provided
        if slug is None:
            slug = cls._generate_slug_from_name(name.value)
        else:
            slug = cls._validate_and_normalize_slug(slug)

        return cls(
            id=UserId.generate(),
            name=name,
            slug=slug,
            subscription_tier=subscription_tier,
            owner_id=owner_id,
            settings={},
        )

    @staticmethod
    def _generate_slug_from_name(name: str) -> str:
        """Generate a URL-friendly slug from organization name."""
        # Convert to lowercase and replace spaces/special chars with hyphens
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower().strip())
        # Remove leading/trailing hyphens and limit length
        slug = slug.strip("-")[:50]
        # Add random suffix to ensure uniqueness
        import secrets

        suffix = secrets.token_hex(3)
        return f"{slug}-{suffix}"

    @staticmethod
    def _validate_and_normalize_slug(slug: str) -> str:
        """Validate and normalize a custom slug."""
        if not slug or len(slug.strip()) < 3:
            raise ValueError("Slug must be at least 3 characters long")

        # Normalize the slug
        normalized = re.sub(r"[^a-z0-9-]", "", slug.lower().strip())
        if len(normalized) < 3:
            raise ValueError("Slug must contain at least 3 valid characters (a-z, 0-9, -)")

        if len(normalized) > 50:
            raise ValueError("Slug cannot be longer than 50 characters")

        if normalized.startswith("-") or normalized.endswith("-"):
            raise ValueError("Slug cannot start or end with a hyphen")

        return normalized

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