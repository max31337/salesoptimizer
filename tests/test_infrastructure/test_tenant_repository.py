import pytest
from sqlalchemy.orm import Session
from uuid import uuid4

from infrastructure.repositories.tenant_repository_impl import TenantRepositoryImpl
from domain.entities.tenant import Tenant, SubscriptionTier


class TestTenantRepository:
    
    @pytest.fixture
    def sample_tenant(self) -> Tenant:
        """Create a sample tenant for testing."""
        return Tenant(
            name="Test Company",
            slug="test-company",
            subscription_tier=SubscriptionTier.BASIC
        )
    
    def test_create_tenant(self, db_session: Session, sample_tenant: Tenant) -> None:
        """Test creating a tenant in the repository."""
        repo = TenantRepositoryImpl(db_session)
        
        created_tenant = repo.create(sample_tenant)
        
        assert created_tenant.id is not None
        assert created_tenant.name == sample_tenant.name
        assert created_tenant.slug == sample_tenant.slug
        assert created_tenant.subscription_tier == sample_tenant.subscription_tier
        assert created_tenant.is_active is True
        assert created_tenant.created_at is not None
    
    def test_create_tenant_duplicate_slug(self, db_session: Session, sample_tenant: Tenant) -> None:
        """Test creating a tenant with duplicate slug raises error."""
        repo = TenantRepositoryImpl(db_session)
        repo.create(sample_tenant)
        
        duplicate_tenant = Tenant(
            name="Different Company",
            slug=sample_tenant.slug,  # Same slug
            subscription_tier=SubscriptionTier.PROFESSIONAL
        )
        
        with pytest.raises(ValueError, match="Tenant with this slug already exists"):
            repo.create(duplicate_tenant)
    
    def test_get_by_id_existing_tenant(self, db_session: Session, sample_tenant: Tenant) -> None:
        """Test getting a tenant by ID when tenant exists."""
        repo = TenantRepositoryImpl(db_session)
        created_tenant = repo.create(sample_tenant)
        assert created_tenant.id is not None, "Created tenant ID should not be None"
        
        retrieved_tenant = repo.get_by_id(created_tenant.id)
        
        assert retrieved_tenant is not None
        assert retrieved_tenant.id == created_tenant.id
        assert retrieved_tenant.name == created_tenant.name
    
    def test_get_by_id_non_existing_tenant(self, db_session: Session) -> None:
        """Test getting a tenant by ID when tenant doesn't exist."""
        repo = TenantRepositoryImpl(db_session)
        
        retrieved_tenant = repo.get_by_id(uuid4())
        
        assert retrieved_tenant is None
    
    def test_get_by_slug_existing_tenant(self, db_session: Session, sample_tenant: Tenant) -> None:
        """Test getting a tenant by slug when tenant exists."""
        repo = TenantRepositoryImpl(db_session)
        created_tenant = repo.create(sample_tenant)
        
        retrieved_tenant = repo.get_by_slug(created_tenant.slug)
        
        assert retrieved_tenant is not None
        assert retrieved_tenant.slug == created_tenant.slug
        assert retrieved_tenant.name == created_tenant.name
    
    def test_get_by_slug_non_existing_tenant(self, db_session: Session) -> None:
        """Test getting a tenant by slug when tenant doesn't exist."""
        repo = TenantRepositoryImpl(db_session)
        
        retrieved_tenant = repo.get_by_slug("nonexistent-slug")
        
        assert retrieved_tenant is None
    
    def test_get_all_tenants(self, db_session: Session) -> None:
        """Test getting all tenants."""
        repo = TenantRepositoryImpl(db_session)
        
        # Create multiple tenants
        tenants: list[Tenant] = []
        for i in range(3):
            tenant = Tenant(
                name=f"Company {i}",
                slug=f"company-{i}",
                subscription_tier=SubscriptionTier.BASIC
            )
            tenants.append(repo.create(tenant))
        
        all_tenants = repo.get_all()
        
        assert len(all_tenants) == 3
        created_slugs = {t.slug for t in tenants}
        retrieved_slugs = {t.slug for t in all_tenants}
        assert created_slugs == retrieved_slugs
    
    def test_exists_by_slug(self, db_session: Session, sample_tenant: Tenant) -> None:
        """Test checking if tenant exists by slug."""
        repo = TenantRepositoryImpl(db_session)
        
        assert repo.exists_by_slug(sample_tenant.slug) is False
        
        repo.create(sample_tenant)
        
        assert repo.exists_by_slug(sample_tenant.slug) is True
        assert repo.exists_by_slug("nonexistent-slug") is False