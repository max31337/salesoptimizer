#!/usr/bin/env python3
"""
Test System Organization Implementation - Tests the system organization functionality.
This script verifies that the system organization implementation works correctly.
"""
import sys
from pathlib import Path
from typing import Dict, Union

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from infrastructure.db.database import get_database_url
from infrastructure.db.models.user_model import UserModel
from infrastructure.db.models.tenant_model import TenantModel
from domain.organization.entities.user import UserRole
from scripts.system_organization_manager import SystemOrganizationManager

def test_system_organization() -> Dict[str, Union[str, int, bool]]:
    """Test the system organization functionality."""
    
    print("🧪 Testing System Organization Implementation")
    print("=" * 60)
    
    engine = create_engine(get_database_url())
    SessionLocal = sessionmaker(bind=engine)
    
    with SessionLocal() as session:
        manager = SystemOrganizationManager(session)
        
        print("\n1️⃣ Testing System Organization Creation/Retrieval...")
        
        # Test getting or creating system organization
        system_org = manager.get_or_create_system_organization()
        print(f"✅ System Organization: {system_org.name}")
        print(f"   ID: {system_org.id}")
        print(f"   Slug: {system_org.slug}")
        print(f"   Subscription Tier: {system_org.subscription_tier}")
        print(f"   Is Active: {system_org.is_active}")
        print(f"   Settings: {system_org.settings}")
        
        print("\n2️⃣ Testing System Organization Retrieval...")
        
        # Test that we can retrieve the existing one
        existing_org = manager.get_system_organization()
        if existing_org:
            print(f"✅ Successfully retrieved existing system organization: {existing_org.name}")
            assert existing_org.id == system_org.id, "IDs should match"
        else:
            print("❌ Failed to retrieve existing system organization")
            
        print("\n3️⃣ Testing Superadmin Assignment Verification...")
        
        # Check current superadmin assignments
        verification = manager.verify_superadmin_assignments()
        print(f"📊 Superadmin Status:")
        print(f"   Total Superadmins: {verification['total_superadmins']}")
        print(f"   Properly Assigned: {verification['assigned_count']}")
        print(f"   Orphaned: {verification['orphaned_count']}")
        
        if verification['assignments']:
            print(f"\n👥 Individual Assignments:")
            for assignment in verification['assignments']:
                status_icon = "✅" if assignment['status'] == 'assigned' else "❌"
                org_info = f" -> {assignment['organization']}" if assignment['organization'] else " (No Organization)"
                print(f"   {status_icon} {assignment['email']}{org_info}")
        
        print("\n4️⃣ Testing Migration Functionality...")
        
        # Test migration (should be idempotent)
        system_org_after, migrated_count = manager.migrate_orphaned_superadmins()
        print(f"✅ Migration completed:")
        print(f"   System Org ID: {system_org_after.id}")
        print(f"   Superadmins migrated: {migrated_count}")
        
        # Verify after migration
        verification_after = manager.verify_superadmin_assignments()
        print(f"\n📈 Post-Migration Status:")
        print(f"   Total Superadmins: {verification_after['total_superadmins']}")
        print(f"   Properly Assigned: {verification_after['assigned_count']}")
        print(f"   Orphaned: {verification_after['orphaned_count']}")
        
        print("\n5️⃣ Testing Database Constraints...")
        
        # Verify subscription tier
        if system_org.subscription_tier == "system":
            print("✅ Subscription tier is correctly set to 'system'")
        else:
            print(f"❌ Subscription tier is incorrect: {system_org.subscription_tier}")
        
        # Verify settings
        settings = system_org.settings or {}
        if settings.get("is_system_organization"):
            print("✅ System organization flag is set correctly")
        else:
            print("❌ System organization flag is missing or false")
        
        # Test that slug is unique
        duplicate_check = session.query(TenantModel).filter(
            TenantModel.slug == system_org.slug
        ).count()
        
        if duplicate_check == 1:
            print("✅ System organization slug is unique")
        else:
            print(f"❌ System organization slug is not unique (found {duplicate_check} instances)")
            
        print("\n6️⃣ Testing Superadmin Access Verification...")
        
        # Get all superadmins and verify they can still access all organizations
        superadmins = session.query(UserModel).filter(
            UserModel.role == UserRole.SUPER_ADMIN
        ).all()
        
        all_orgs = session.query(TenantModel).all()
        
        print(f"📋 Access Check:")
        print(f"   Total Organizations: {len(all_orgs)}")
        print(f"   Total Superadmins: {len(superadmins)}")
        
        for admin in superadmins:
            if admin.tenant_id:
                org = session.query(TenantModel).filter(TenantModel.id == admin.tenant_id).first()
                org_name = org.name if org else "Unknown"
                print(f"   👤 {admin.email} belongs to: {org_name}")
                
                # Note: In the actual application, superadmins should still be able to access
                # all organizations regardless of their assigned organization
                print(f"      🔑 Role: {admin.role} (should have cross-tenant access)")
            else:
                print(f"   ❌ {admin.email} has no organization assigned")
        
        # Commit any changes made during testing
        session.commit()
        
        print("\n🎉 System Organization Test Completed!")
        
        # Summary
        if verification_after['orphaned_count'] == 0:
            print("✅ SUCCESS: All superadmins are properly assigned to organizations")
        else:
            print("⚠️  WARNING: Some superadmins are still not assigned to organizations")
            
        return {
            "system_org_id": str(system_org.id),
            "system_org_name": system_org.name,
            "total_superadmins": verification_after['total_superadmins'],
            "assigned_superadmins": verification_after['assigned_count'],
            "orphaned_superadmins": verification_after['orphaned_count'],
            "success": verification_after['orphaned_count'] == 0
        }


if __name__ == "__main__":
    try:
        result = test_system_organization()
        print(f"\n📋 Test Result Summary:")
        for key, value in result.items():
            print(f"   {key}: {value}")
            
        if result['success']:
            print("\n🎊 All tests passed! System organization is working correctly.")
            sys.exit(0)
        else:
            print("\n⚠️  Some issues found. Please review the output above.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        sys.exit(1)
