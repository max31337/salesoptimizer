from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists

from domain.organization.entities.tenant import Tenant, SubscriptionTier
from domain.organization.repositories.tenant_repository import TenantRepository
from infrastructure.db.models.tenant_model import TenantModel

class TenantRepositoryImpl(TenantRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, tenant: Tenant) -> Tenant:
        """Create new tenant."""
        tenant_model = self._entity_to_model(tenant)
        self.session.add(tenant_model)
        await self.session.flush()  # Get the ID without committing
        
        return self._model_to_entity(tenant_model)
    
    async def get_by_id(self, tenant_id: UUID) -> Optional[Tenant]:
        """Get tenant by ID."""
        stmt = select(TenantModel).where(TenantModel.id == tenant_id)
        result = await self.session.execute(stmt)
        tenant_model = result.scalar_one_or_none()
        
        if not tenant_model:
            return None
            
        return self._model_to_entity(tenant_model)
    
    async def get_by_slug(self, slug: str) -> Optional[Tenant]:
        """Get tenant by slug."""
        stmt = select(TenantModel).where(TenantModel.slug == slug)
        result = await self.session.execute(stmt)
        tenant_model = result.scalar_one_or_none()
        
        if not tenant_model:
            return None
            
        return self._model_to_entity(tenant_model)
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Tenant]:
        """Get all tenants with pagination."""
        stmt = select(TenantModel).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        tenant_models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in tenant_models]
    
    async def update(self, tenant: Tenant) -> Tenant:
        """Update existing tenant."""
        stmt = select(TenantModel).where(TenantModel.id == tenant.id)
        result = await self.session.execute(stmt)
        tenant_model = result.scalar_one_or_none()
        
        if not tenant_model:
            raise ValueError(f"Tenant with ID {tenant.id} not found")
        
        # Update model with entity data
        setattr(tenant_model, "name", tenant.name)
        setattr(tenant_model, "slug", tenant.slug)
        setattr(tenant_model, "subscription_tier", tenant.subscription_tier.value)
        setattr(tenant_model, "is_active", tenant.is_active)
        setattr(tenant_model, "settings", tenant.settings)
        setattr(tenant_model, "updated_at", tenant.updated_at)

        await self.session.flush()
        return self._model_to_entity(tenant_model)
    
    async def delete(self, tenant_id: UUID) -> bool:
        """Delete tenant by ID."""
        stmt = select(TenantModel).where(TenantModel.id == tenant_id)
        result = await self.session.execute(stmt)
        tenant_model = result.scalar_one_or_none()
        
        if not tenant_model:
            return False
        
        await self.session.delete(tenant_model)
        return True
    
    async def exists_by_slug(self, slug: str) -> bool:
        """Check if tenant exists by slug."""
        stmt = select(exists().where(TenantModel.slug == slug))
        result = await self.session.execute(stmt)
        return bool(result.scalar())
    
    async def list_active(self) -> List[Tenant]:
        """List all active tenants."""
        stmt = select(TenantModel).where(TenantModel.is_active == True)
        result = await self.session.execute(stmt)
        tenant_models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in tenant_models]
    
    async def list_by_subscription_tier(self, tier: SubscriptionTier) -> List[Tenant]:
        """List tenants by subscription tier."""
        stmt = select(TenantModel).where(TenantModel.subscription_tier == tier.value)
        result = await self.session.execute(stmt)
        tenant_models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in tenant_models]
    
    def _model_to_entity(self, model: TenantModel) -> Tenant:
        """Convert database model to domain entity."""
        return Tenant(
            id=getattr(model, "id"),
            name=getattr(model, "name"),
            slug=getattr(model, "slug"),
            subscription_tier=SubscriptionTier(getattr(model, "subscription_tier")),
            is_active=getattr(model, "is_active"),
            settings=getattr(model, "settings") or {},
            created_at=getattr(model, "created_at"),
            updated_at=getattr(model, "updated_at")
        )
    
    def _entity_to_model(self, entity: Tenant) -> TenantModel:
        """Convert domain entity to database model."""
        return TenantModel(
            id=entity.id,
            name=entity.name,
            slug=entity.slug,
            subscription_tier=entity.subscription_tier.value,
            is_active=entity.is_active,
            settings=entity.settings,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )