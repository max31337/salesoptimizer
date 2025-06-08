#!/usr/bin/env python3
"""
System Organization Manager - Ensures system organization exists and manages superadmin assignment.
This module provides utilities for creating and managing the SalesOptimizer Platform system organization.
"""
import uuid
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Any
from uuid import UUID

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from infrastructure.db.database import get_database_url
from infrastructure.db.models.tenant_model import TenantModel
from infrastructure.db.models.user_model import UserModel
from domain.organization.entities.user import UserRole


class SystemOrganizationManager:
    """Manager for system organization operations."""
    
    SYSTEM_ORG_NAME = "SalesOptimizer Platform"
    SYSTEM_ORG_SLUG = "salesoptimizer-platform"
    SYSTEM_SUBSCRIPTION_TIER = "system"
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_system_organization(self) -> Optional[TenantModel]:
        """Get the system organization if it exists."""
        return self.session.query(TenantModel).filter(
            TenantModel.name == self.SYSTEM_ORG_NAME
        ).first()
    
    def create_system_organization(self) -> TenantModel:
        """Create the system organization."""
        system_org = TenantModel(
            id=uuid.uuid4(),
            name=self.SYSTEM_ORG_NAME,
            slug=self.SYSTEM_ORG_SLUG,
            subscription_tier=self.SYSTEM_SUBSCRIPTION_TIER,
            is_active=True,
            owner_id=None,  # No single owner for system org
            settings={
                "is_system_organization": True,
                "description": "SalesOptimizer Platform system organization for superadmins and platform management",
                "created_by": "system_manager",
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        self.session.add(system_org)
        self.session.flush()  # Get the ID without committing
        
        return system_org
    
    def get_or_create_system_organization(self) -> TenantModel:
        """Get existing system organization or create it if it doesn't exist."""
        system_org = self.get_system_organization()
        
        if system_org:
            return system_org
        
        return self.create_system_organization()
    
    def get_orphaned_superadmins(self) -> list[UserModel]:
        """Get all superadmins without an organization (tenant_id is None)."""
        return self.session.query(UserModel).filter(
            UserModel.role == UserRole.SUPER_ADMIN,
            UserModel.tenant_id.is_(None)
        ).all()
    
    def assign_superadmin_to_system_org(self, superadmin: UserModel, system_org: TenantModel) -> None:
        """Assign a superadmin to the system organization."""
        superadmin.tenant_id = system_org.id
        superadmin.updated_at = datetime.now(timezone.utc)
    
    def migrate_orphaned_superadmins(self) -> tuple[TenantModel, int]:
        """Migrate all orphaned superadmins to system organization."""
        # Get or create system organization
        system_org = self.get_or_create_system_organization()
        
        # Get orphaned superadmins
        orphaned_superadmins = self.get_orphaned_superadmins()
        
        # Assign them to system organization
        for admin in orphaned_superadmins:
            self.assign_superadmin_to_system_org(admin, system_org)
        
        return system_org, len(orphaned_superadmins)
    
    def verify_superadmin_assignments(self) -> dict[str, Any]:
        """Verify that all superadmins are properly assigned to organizations."""
        superadmins = self.session.query(UserModel).filter(
            UserModel.role == UserRole.SUPER_ADMIN
        ).all()
        
        assigned_count = 0
        orphaned_count = 0
        assignments = []
        
        for admin in superadmins:
            if admin.tenant_id is None:
                orphaned_count += 1
                assignments.append({
                    "email": admin.email,
                    "status": "orphaned",
                    "organization": None
                })
            else:
                assigned_count += 1
                # Get organization name
                org = self.session.query(TenantModel).filter(TenantModel.id == admin.tenant_id).first()
                org_name = org.name if org else "Unknown Organization"
                assignments.append({
                    "email": admin.email,
                    "status": "assigned",
                    "organization": org_name
                })
        
        return {
            "total_superadmins": len(superadmins),
            "assigned_count": assigned_count,
            "orphaned_count": orphaned_count,
            "assignments": assignments
        }


def ensure_system_organization_exists() -> TenantModel:
    """Standalone function to ensure system organization exists."""
    engine = create_engine(get_database_url())
    SessionLocal = sessionmaker(bind=engine)
    
    with SessionLocal() as session:
        manager = SystemOrganizationManager(session)
        system_org = manager.get_or_create_system_organization()
        session.commit()
        return system_org


def migrate_all_superadmins() -> dict[str, Any]:
    """Standalone function to migrate all orphaned superadmins."""
    engine = create_engine(get_database_url())
    SessionLocal = sessionmaker(bind=engine)
    
    with SessionLocal() as session:
        manager = SystemOrganizationManager(session)
        
        # Check current state
        before_state = manager.verify_superadmin_assignments()
        
        # Migrate orphaned superadmins
        system_org, migrated_count = manager.migrate_orphaned_superadmins()
        
        # Commit changes
        session.commit()
        
        # Check final state
        after_state = manager.verify_superadmin_assignments()
        
        return {
            "system_organization": {
                "id": str(system_org.id),
                "name": system_org.name,
                "slug": system_org.slug
            },
            "migrated_count": migrated_count,
            "before_state": before_state,
            "after_state": after_state
        }


if __name__ == "__main__":
    print("🚀 SalesOptimizer Platform System Organization Manager")
    print("=" * 60)
    
    # Run migration
    result = migrate_all_superadmins()
    
    print(f"\n✅ System Organization: {result['system_organization']['name']}")
    print(f"🆔 ID: {result['system_organization']['id']}")
    print(f"🏷️  Slug: {result['system_organization']['slug']}")
    
    print(f"\n📊 Migration Results:")
    print(f"   Superadmins migrated: {result['migrated_count']}")
    print(f"   Total superadmins: {result['after_state']['total_superadmins']}")
    print(f"   Properly assigned: {result['after_state']['assigned_count']}")
    print(f"   Still orphaned: {result['after_state']['orphaned_count']}")
    
    if result['after_state']['assignments']:
        print(f"\n👥 Superadmin Assignments:")
        for assignment in result['after_state']['assignments']:
            status_icon = "✅" if assignment['status'] == 'assigned' else "❌"
            org_info = f" -> {assignment['organization']}" if assignment['organization'] else " (No Organization)"
            print(f"   {status_icon} {assignment['email']}{org_info}")
    
    if result['after_state']['orphaned_count'] == 0:
        print("\n🎉 All superadmins are properly assigned to organizations!")
    else:
        print(f"\n⚠️  {result['after_state']['orphaned_count']} superadmin(s) still need assignment")
    
    print("\n✨ Migration completed!")
