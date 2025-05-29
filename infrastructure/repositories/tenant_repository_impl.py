from typing import List, Optional
from uuid import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from domain.organization.entities.tenant import Tenant, SubscriptionTier
from domain.organization.repositories.tenant_repository import TenantRepository
from infrastructure.db.models.tenant_model import TenantModel


class TenantRepositoryImpl(TenantRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, tenant: Tenant) -> Tenant:
        """Create a new tenant."""
        # Check for existing slug
        stmt = select(TenantModel).where(TenantModel.slug == tenant.slug)
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()
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
            await self.db.commit()
            await self.db.refresh(db_tenant)
            return self._to_entity(db_tenant)
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("Tenant with this slug already exists")
    
    async def get_by_id(self, tenant_id: UUID) -> Optional[Tenant]:
        """Get tenant by ID."""
        stmt = select(TenantModel).where(TenantModel.id == tenant_id)
        result = await self.db.execute(stmt)
        db_tenant = result.scalar_one_or_none()
        return self._to_entity(db_tenant) if db_tenant else None
    
    async def get_by_slug(self, slug: str) -> Optional[Tenant]:
        """Get tenant by slug."""
        stmt = select(TenantModel).where(TenantModel.slug == slug)
        result = await self.db.execute(stmt)
        db_tenant = result.scalar_one_or_none()
        return self._to_entity(db_tenant) if db_tenant else None
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Tenant]:
        """Get all tenants."""
        stmt = select(TenantModel).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        db_tenants = result.scalars().all()
        return [self._to_entity(db_tenant) for db_tenant in db_tenants]
    
    async def update(self, tenant: Tenant) -> Tenant:
        """Update tenant."""
        stmt = select(TenantModel).where(TenantModel.id == tenant.id)
        result = await self.db.execute(stmt)
        db_tenant: TenantModel = result.scalar_one_or_none()
        if not db_tenant:
            raise ValueError("Tenant not found")
        
        # Update fields
        setattr(db_tenant, "name", tenant.name)
        setattr(db_tenant, "slug", tenant.slug)
        setattr(db_tenant, "subscription_tier", tenant.subscription_tier.value)
        setattr(db_tenant, "is_active", tenant.is_active)
        setattr(db_tenant, "settings", tenant.settings or {})
        setattr(db_tenant, "updated_at", tenant.updated_at)

        await self.db.commit()
        await self.db.refresh(db_tenant)
        return self._to_entity(db_tenant)
    
    async def delete(self, tenant_id: UUID) -> bool:
        """Delete tenant."""
        stmt = select(TenantModel).where(TenantModel.id == tenant_id)
        result = await self.db.execute(stmt)
        db_tenant = result.scalar_one_or_none()
        if not db_tenant:
            return False
        
        await self.db.delete(db_tenant)
        await self.db.commit()
        return True
    
    async def exists_by_slug(self, slug: str) -> bool:
        """Check if tenant exists by slug."""
        stmt = select(TenantModel).where(TenantModel.slug == slug)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    def _to_entity(self, db_tenant: TenantModel) -> Tenant:
        """Convert database model to entity."""
        return Tenant(
            id=getattr(db_tenant, "id"),
            name=getattr(db_tenant, "name"),
            slug=getattr(db_tenant, "slug"),
            subscription_tier=SubscriptionTier(getattr(db_tenant, "subscription_tier")),
            is_active=getattr(db_tenant, "is_active"),
            settings=getattr(db_tenant, "settings") or {},
            created_at=getattr(db_tenant, "created_at"),
            updated_at=getattr(db_tenant, "updated_at")
        )