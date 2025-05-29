from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from domain.organization.entities.tenant import Tenant, SubscriptionTier
from domain.organization.repositories.tenant_repository import TenantRepository
from infrastructure.db.models.tenant_model import TenantModel


class TenantRepositoryImpl(TenantRepository):
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, tenant: Tenant) -> Tenant:
        """Create a new tenant."""
        # Check for existing slug
        existing = self.db.query(TenantModel).filter(TenantModel.slug == tenant.slug).first()
        if existing:
            raise ValueError("Tenant with this slug already exists")
        
        db_tenant = TenantModel(
            id=tenant.id,
            name=tenant.name,
            slug=tenant.slug,
            subscription_tier=tenant.subscription_tier.value,
            is_active=tenant.is_active,
            settings=tenant.settings or {}
        )
        
        try:
            self.db.add(db_tenant)
            self.db.commit()
            self.db.refresh(db_tenant)
            return self._to_entity(db_tenant)
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Tenant with this slug already exists")
    
    def get_by_id(self, tenant_id: UUID) -> Optional[Tenant]:
        """Get tenant by ID."""
        db_tenant = self.db.query(TenantModel).filter(TenantModel.id == tenant_id).first()
        return self._to_entity(db_tenant) if db_tenant else None
    
    def get_by_slug(self, slug: str) -> Optional[Tenant]:
        """Get tenant by slug."""
        db_tenant = self.db.query(TenantModel).filter(TenantModel.slug == slug).first()
        return self._to_entity(db_tenant) if db_tenant else None
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Tenant]:
        """Get all tenants."""
        db_tenants = self.db.query(TenantModel).offset(skip).limit(limit).all()
        return [self._to_entity(db_tenant) for db_tenant in db_tenants]
    
    def update(self, tenant: Tenant) -> Tenant:
        """Update tenant."""
        db_tenant = self.db.query(TenantModel).filter(TenantModel.id == tenant.id).first()
        if not db_tenant:
            raise ValueError("Tenant not found")
        
        # Update fields
        setattr(db_tenant, "name", tenant.name)
        setattr(db_tenant, "slug", tenant.slug)
        setattr(db_tenant, "subscription_tier", tenant.subscription_tier.value)
        setattr(db_tenant, "is_active", tenant.is_active)
        setattr(db_tenant, "settings", tenant.settings or {})
        setattr(db_tenant, "updated_at", tenant.updated_at)

        self.db.commit()
        self.db.refresh(db_tenant)
        return self._to_entity(db_tenant)
    
    def delete(self, tenant_id: UUID) -> bool:
        """Delete tenant."""
        db_tenant = self.db.query(TenantModel).filter(TenantModel.id == tenant_id).first()
        if not db_tenant:
            return False
        
        self.db.delete(db_tenant)
        self.db.commit()
        return True
    
    def exists_by_slug(self, slug: str) -> bool:
        """Check if tenant exists by slug."""
        return self.db.query(TenantModel).filter(TenantModel.slug == slug).first() is not None
    
    def _to_entity(self, db_tenant: TenantModel) -> Tenant:
        """Convert database model to entity."""
        return Tenant(
            id=getattr(db_tenant, "id", None),
            name=getattr(db_tenant, "name", "") or "",
            slug=getattr(db_tenant, "slug", "") or "",
            subscription_tier=SubscriptionTier(getattr(db_tenant, "subscription_tier", "")),
            is_active=getattr(db_tenant, "is_active", False) if getattr(db_tenant, "is_active", None) is not None else False,
            settings=getattr(db_tenant, "settings", {}) or {},
            created_at=getattr(db_tenant, "created_at", None),
            updated_at=getattr(db_tenant, "updated_at", None)
        )