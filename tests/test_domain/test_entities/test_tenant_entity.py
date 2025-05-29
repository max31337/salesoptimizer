from datetime import datetime, timezone
from uuid import UUID
from typing import Any, Dict

from domain.organization.entities.tenant import Tenant, SubscriptionTier


class TestTenantEntity:
    
    def test_tenant_creation_with_defaults(self) -> None:
        """Test creating a tenant with default values."""
        tenant = Tenant(
            name="Test Company",
            slug="test-company",
            settings={}
        )
        
        assert tenant.name == "Test Company"
        assert tenant.slug == "test-company"
        assert tenant.subscription_tier == SubscriptionTier.BASIC
        assert tenant.is_active is True
        assert tenant.settings == {}  # This should be set by __post_init__
        assert isinstance(tenant.id, UUID)  # This should be set by __post_init__
        assert tenant.created_at is None  # Set by database
        assert tenant.updated_at is None
    
    def test_tenant_creation_with_all_fields(self) -> None:
        """Test creating a tenant with all fields specified."""
        tenant_id = UUID('12345678-1234-5678-1234-567812345678')
        settings = {"theme": "dark", "timezone": "UTC"}
        created_at = datetime.now(timezone.utc)
        
        tenant = Tenant(
            id=tenant_id,  # Explicitly set ID
            name="Enterprise Corp",
            slug="enterprise-corp",
            subscription_tier=SubscriptionTier.ENTERPRISE,
            is_active=False,
            settings=settings,
            created_at=created_at
        )
        
        assert tenant.id == tenant_id
        assert tenant.name == "Enterprise Corp"
        assert tenant.slug == "enterprise-corp"
        assert tenant.subscription_tier == SubscriptionTier.ENTERPRISE
        assert tenant.is_active is False
        assert tenant.settings == settings
        assert tenant.created_at == created_at
    
    def test_activate_method(self) -> None:
        """Test the activate method."""
        tenant = Tenant(
            name="Test Company",
            slug="test-company",
            is_active=False,
            settings={}
        )
        
        tenant.activate()
        
        assert tenant.is_active is True
        assert tenant.updated_at is not None
        assert isinstance(tenant.updated_at, datetime)
    
    def test_deactivate_method(self) -> None:
        """Test the deactivate method."""
        tenant = Tenant(
            name="Test Company",
            slug="test-company",
            is_active=True,
            settings={}
        )
        
        tenant.deactivate()
        
        assert tenant.is_active is False
        assert tenant.updated_at is not None
        assert isinstance(tenant.updated_at, datetime)
    
    def test_upgrade_subscription_method(self) -> None:
        """Test the upgrade_subscription method."""
        tenant = Tenant(
            name="Test Company",
            slug="test-company",
            subscription_tier=SubscriptionTier.BASIC,
            settings={}
        )
        
        tenant.upgrade_subscription(SubscriptionTier.PROFESSIONAL)
        
        assert tenant.subscription_tier == SubscriptionTier.PROFESSIONAL
        assert tenant.updated_at is not None
        assert isinstance(tenant.updated_at, datetime)
    
    def test_subscription_tier_enum_values(self) -> None:
        """Test SubscriptionTier enum values."""
        assert SubscriptionTier.BASIC.value == "basic"
        assert SubscriptionTier.PROFESSIONAL.value == "professional"
        assert SubscriptionTier.ENTERPRISE.value == "enterprise"
    
        """Test tenant with complex settings object."""
        complex_settings: Dict[str, Any] = {
            "ui": {
                "theme": "dark",
                "language": "en",
                "compact_mode": True
            },
            "features": {
                "advanced_analytics": True,
                "api_access": True,
                "custom_fields": ["priority", "source"]
            },
            "limits": {
                "users": 100,
                "storage_gb": 50
            }
        }
        
        tenant = Tenant(
            name="Complex Corp",
            slug="complex-corp",
            settings=complex_settings
        )
        
        assert tenant.settings == complex_settings
        assert tenant.settings["ui"]["theme"] == "dark"
        assert tenant.settings.get("features") is not None
        assert tenant.settings["features"].get("advanced_analytics") is True
        assert tenant.settings["limits"]["users"] == 100
        assert tenant.settings["limits"]["users"] == 100
    
    def test_tenant_settings_default_initialization(self) -> None:
        """Test that settings are properly initialized as empty dict."""
        tenant = Tenant(
            name="Test Company",
            slug="test-company",
            settings={}
        )
        
        # Should be initialized as empty dict by __post_init__
        assert isinstance(tenant.settings, dict)
        assert len(tenant.settings) == 0
        
        # Should be able to add settings
        tenant.settings["test_key"] = "test_value"
        assert tenant.settings["test_key"] == "test_value"
    
    def test_tenant_id_auto_generation(self) -> None:
        """Test that ID is automatically generated."""
        tenant1 = Tenant(name="Company 1", slug="company-1", settings={})
        tenant2 = Tenant(name="Company 2", slug="company-2", settings={})
        
        assert isinstance(tenant1.id, UUID)
        assert isinstance(tenant2.id, UUID)
        assert tenant1.id != tenant2.id