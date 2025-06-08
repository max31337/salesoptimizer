#!/usr/bin/env python3
"""
Migration script to assign existing superadmins to the system organization.
This script ensures all superadmins belong to the SalesOptimizer Platform organization.
"""
import uuid
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from infrastructure.db.database import get_database_url
from infrastructure.db.models.user_model import UserModel
from infrastructure.db.models.tenant_model import TenantModel
from domain.organization.entities.user import UserRole


def migrate_superadmins_to_system_org():
    """Migrate existing superadmins to the system organization."""
    
    engine = create_engine(get_database_url())
    SessionLocal = sessionmaker(bind=engine)
    
    with SessionLocal() as session:
        # Get or create system organization
        system_org = session.query(TenantModel).filter(
            TenantModel.name == "SalesOptimizer Platform"
        ).first()
        
        if not system_org:
            print("📋 Creating system organization...")
            system_org = TenantModel(
                id=uuid.uuid4(),
                name="SalesOptimizer Platform",
                slug="salesoptimizer-platform",
                subscription_tier="system",
                is_active=True,
                owner_id=None,
                settings={
                    "is_system_organization": True,
                    "description": "SalesOptimizer Platform system organization for superadmins",
                    "created_by": "migration_script"
                },
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            session.add(system_org)
            session.flush()
            print(f"✅ Created system organization: {system_org.name}")
        else:
            print(f"📋 System organization already exists: {system_org.name}")
        
        # Find all superadmins without an organization (tenant_id is None)
        orphaned_superadmins = session.query(UserModel).filter(
            UserModel.role == UserRole.SUPER_ADMIN,
            UserModel.tenant_id.is_(None)
        ).all()
        
        if not orphaned_superadmins:
            print("✅ No orphaned superadmins found. All superadmins are properly assigned.")
            return
        
        print(f"🔍 Found {len(orphaned_superadmins)} superadmin(s) without organization assignment")
        
        # Assign them to the system organization
        for admin in orphaned_superadmins:
            admin.tenant_id = system_org.id
            admin.updated_at = datetime.now(timezone.utc)
            print(f"📝 Assigned {admin.email} to system organization")
        
        # Commit all changes
        session.commit()
        
        print(f"✅ Migration completed! {len(orphaned_superadmins)} superadmin(s) assigned to system organization.")
        print(f"🏢 System Organization: {system_org.name} ({system_org.id})")


def verify_superadmin_assignments():
    """Verify that all superadmins are properly assigned to organizations."""
    
    engine = create_engine(get_database_url())
    SessionLocal = sessionmaker(bind=engine)
    
    with SessionLocal() as session:
        # Get all superadmins
        superadmins = session.query(UserModel).filter(
            UserModel.role == UserRole.SUPER_ADMIN
        ).all()
        
        print(f"🔍 Found {len(superadmins)} superadmin(s)")
        
        orphaned_count = 0
        for admin in superadmins:
            if admin.tenant_id is None: #type: ignore
                print(f"❌ {admin.email} - NOT ASSIGNED TO ORGANIZATION")
                orphaned_count += 1
            else:
                # Get organization name
                org = session.query(TenantModel).filter(TenantModel.id == admin.tenant_id).first()
                org_name = org.name if org else "Unknown Organization"
                print(f"✅ {admin.email} - Assigned to: {org_name}")
        
        if orphaned_count == 0:
            print("🎉 All superadmins are properly assigned to organizations!")
        else:
            print(f"⚠️  {orphaned_count} superadmin(s) need to be assigned to organizations")
            print("💡 Run the migration to fix this: python scripts/migrate_superadmins.py")


if __name__ == "__main__":
    print("🚀 Starting superadmin organization migration...")
    print("=" * 60)
    
    print("\n📊 Current State:")
    verify_superadmin_assignments()
    
    print("\n🔄 Running Migration:")
    migrate_superadmins_to_system_org()
    
    print("\n📊 Final State:")
    verify_superadmin_assignments()
    
    print("\n✨ Migration completed!")
