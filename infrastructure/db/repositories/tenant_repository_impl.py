from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from domain.organization.entities.tenant import Tenant
from domain.organization.repositories.tenant_repository import TenantRepository
from domain.organization.value_objects.user_id import UserId
from domain.organization.value_objects.tenant_name import TenantName
from domain.organization.value_objects.tenant_id import TenantId
from infrastructure.db.models.tenant_model import TenantModel


class TenantRepositoryImpl(TenantRepository):
    """Implementation of tenant repository using SQLAlchemy."""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def save(self, tenant: Tenant) -> Tenant:
        """Save a new tenant."""
        # Check for slug uniqueness
        if not tenant.slug:
            raise ValueError("Tenant slug cannot be None or empty")
        if await self.exists_by_slug(tenant.slug):
            # Generate unique slug by appending number
            base_slug = tenant.slug
            counter = 1
            while await self.exists_by_slug(f"{base_slug}-{counter}"):
                counter += 1
            tenant.slug = f"{base_slug}-{counter}"
        
        model = self._entity_to_model(tenant)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        
        return self._model_to_entity(model)
    
    async def get_by_id(self, tenant_id: TenantId) -> Optional[Tenant]:
        """Get tenant by ID."""
        result = await self._session.execute(
            select(TenantModel)
            .options(
                selectinload(TenantModel.users),
                selectinload(TenantModel.teams),
                selectinload(TenantModel.invitations)
            )
            .where(TenantModel.id == tenant_id.value)
        )
        model = result.scalar_one_or_none()
        
        return self._model_to_entity(model) if model else None
    
    async def get_by_slug(self, slug: str) -> Optional[Tenant]:
        """Get tenant by slug."""
        result = await self._session.execute(
            select(TenantModel)
            .options(
                selectinload(TenantModel.users),
                selectinload(TenantModel.teams),
                selectinload(TenantModel.invitations)
            )
            .where(TenantModel.slug == slug)
        )
        model = result.scalar_one_or_none()
        
        return self._model_to_entity(model) if model else None
    
    async def get_by_name(self, name: str) -> Optional[Tenant]:
        """Get tenant by name."""
        result = await self._session.execute(
            select(TenantModel)
            .where(TenantModel.name == name)
        )
        model = result.scalar_one_or_none()
        
        return self._model_to_entity(model) if model else None
    
    async def get_by_owner(self, owner_id: UserId) -> List[Tenant]:
        """Get tenants owned by a specific user."""
        result = await self._session.execute(
            select(TenantModel)
            .where(TenantModel.owner_id == owner_id.value)
            .order_by(TenantModel.created_at.desc())
        )
        models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in models]
    
    async def get_all_active(self) -> List[Tenant]:
        """Get all active tenants."""
        result = await self._session.execute(
            select(TenantModel)
            .where(TenantModel.is_active == True)
            .order_by(TenantModel.created_at.desc())
        )
        models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in models]
    
    async def update(self, tenant: Tenant) -> Tenant:
        """Update existing tenant."""
        if tenant.id is None: # type: ignore
            raise ValueError("Cannot update tenant without an ID")
        
        result = await self._session.execute(
            select(TenantModel).where(TenantModel.id == tenant.id.value)
        )
        model = result.scalar_one()
        
        # Update model fields
        setattr(model, 'name', tenant.name)
        setattr(model, 'slug', tenant.slug)
        setattr(model, 'subscription_tier', tenant.subscription_tier)
        setattr(model, 'is_active', tenant.is_active)
        setattr(model, 'owner_id', tenant.owner_id.value if tenant.owner_id else None)
        setattr(model, 'settings', tenant.settings or {})
        setattr(model, 'updated_at', tenant.updated_at)

        await self._session.flush()
        await self._session.refresh(model)
        
        return self._model_to_entity(model)
    
    async def delete(self, tenant_id: TenantId) -> bool:
        """Delete tenant."""
        result = await self._session.execute(
            select(TenantModel).where(TenantModel.id == tenant_id.value)
        )
        model = result.scalar_one_or_none()
        
        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        
        return False
    
    async def exists_by_slug(self, slug: str) -> bool:
        """Check if tenant exists by slug."""
        result = await self._session.execute(
            select(TenantModel.id).where(TenantModel.slug == slug)
        )
        return result.scalar_one_or_none() is not None
    
    async def exists_by_name(self, name: str) -> bool:
        """Check if tenant exists by name."""        
        result = await self._session.execute(
            select(TenantModel.id).where(TenantModel.name == name)
        )
        return result.scalar_one_or_none() is not None
    
    def _model_to_entity(self, model: TenantModel) -> Tenant:
        """Convert database model to domain entity."""
        return Tenant(
            id=TenantId(model.id), # type: ignore
            name=str(model.name),
            slug=getattr(model, 'slug', ''),
            subscription_tier=getattr(model, 'subscription_tier', ''),
            is_active=getattr(model, 'is_active', False),
            owner_id=UserId(getattr(model, 'owner_id')) if getattr(model, 'owner_id') else None,
            settings=getattr(model, 'settings', {}) or {},
            created_at=getattr(model, 'created_at'),
            updated_at=getattr(model, 'updated_at')
        )
    
    def _entity_to_model(self, tenant: Tenant) -> TenantModel:
        """Convert domain entity to database model."""
        return TenantModel(
            id=tenant.id.value if tenant.id else None,
            name=tenant.name,
            slug=tenant.slug,
            subscription_tier=tenant.subscription_tier,
            is_active=tenant.is_active,
            owner_id=tenant.owner_id.value if tenant.owner_id else None,
            settings=tenant.settings or {},
            created_at=tenant.created_at,
            updated_at=tenant.updated_at
        )