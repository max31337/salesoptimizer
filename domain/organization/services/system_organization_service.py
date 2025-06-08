"""
System Organization Service - Domain service for managing the system organization.
This service ensures the system organization exists and provides utilities for superadmin management.
"""
from typing import Optional
from datetime import datetime, timezone

from domain.organization.entities.tenant import Tenant
from domain.organization.repositories.tenant_repository import TenantRepository
from domain.organization.value_objects.tenant_name import TenantName
from domain.organization.value_objects.user_id import UserId


class SystemOrganizationService:
    """Domain service for system organization operations."""
    
    SYSTEM_ORG_NAME = "SalesOptimizer Platform"
    SYSTEM_SUBSCRIPTION_TIER = "system"
    
    def __init__(self, tenant_repository: TenantRepository):
        self._tenant_repository = tenant_repository
    
    async def get_system_organization(self) -> Optional[Tenant]:
        """Get the system organization if it exists."""
        system_name = TenantName(self.SYSTEM_ORG_NAME)
        return await self._tenant_repository.get_by_name(system_name.value)
    
    async def create_system_organization(self) -> Tenant:
        """Create the system organization."""
        system_name = TenantName(self.SYSTEM_ORG_NAME)
        
        # Create the system tenant with special settings
        tenant = Tenant.create(
            name=system_name,
            subscription_tier=self.SYSTEM_SUBSCRIPTION_TIER,
            slug="salesoptimizer-platform",
            owner_id=None  # No single owner for system org
        )
        
        # Add system-specific settings
        tenant.update_setting("is_system_organization", True)
        tenant.update_setting("description", "SalesOptimizer Platform system organization for superadmins and platform management")
        tenant.update_setting("created_by", "system_service")
        tenant.update_setting("created_at", datetime.now(timezone.utc).isoformat())
        
        return await self._tenant_repository.save(tenant)
    
    async def get_or_create_system_organization(self) -> Tenant:
        """Get existing system organization or create it if it doesn't exist."""
        system_org = await self.get_system_organization()
        
        if system_org:
            return system_org
        
        return await self.create_system_organization()
    
    async def ensure_system_organization_exists(self) -> Tenant:
        """Ensure the system organization exists and return it."""
        return await self.get_or_create_system_organization()
    
    def get_system_tenant_id(self, system_org: Tenant) -> UserId:
        """Get the system organization's ID as a UserId for user assignment."""
        if not system_org.id:
            raise ValueError("System organization ID is missing")
        return system_org.id
    
    async def is_system_organization(self, tenant_id: UserId) -> bool:
        """Check if a tenant ID belongs to the system organization."""
        system_org = await self.get_system_organization()
        if not system_org or not system_org.id:
            return False
        return system_org.id == tenant_id
