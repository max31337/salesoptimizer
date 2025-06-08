#!/usr/bin/env python3
"""
Create Super Admin Script - Creates a superadmin user and assigns to system organization.
This script ensures the system organization exists and assigns the superadmin to it.
"""
import uuid
import sys
from pathlib import Path
from datetime import datetime, timezone

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from infrastructure.db.database import get_database_url
from infrastructure.db.models.user_model import UserModel
from infrastructure.db.models.tenant_model import TenantModel
from infrastructure.services.password_service import PasswordService
from domain.organization.entities.user import UserRole, UserStatus
from domain.organization.services.superadmin_management_service import SuperadminManagementService
from scripts.system_organization_manager import SystemOrganizationManager


def create_super_admin():
    """Create the initial Super Admin user and assign to system organization."""
    
    # Database setup
    engine = create_engine(get_database_url())
    SessionLocal = sessionmaker(bind=engine)
    
    # User details
    email = "admin@salesoptimizer.com"
    password = "SuperAdmin123!"
    with SessionLocal() as session:
        # First, validate superadmin constraints
        superadmin_service = SuperadminManagementService(session)
        validation = superadmin_service.validate_single_superadmin_constraint()
        
        print(f"🔍 Superadmin Constraint Check:")
        print(f"   Current superadmins: {validation['current_count']}")
        print(f"   Maximum allowed: {validation['max_allowed']}")
        
        if not validation["is_valid"]:
            print(f"❌ {validation['violation_message']}")
            print("🛠️  Enforcing single superadmin constraint...")
            
            # Show current superadmins
            for admin in validation["superadmins"]:
                print(f"   - {admin['email']} (ID: {admin['id']}, Created: {admin['created_at']})")
            
            # Ask user to confirm constraint enforcement
            print("\n⚠️  Multiple superadmins detected. This violates the system constraint.")
            print("   The system will keep the most recent superadmin and demote others to org_admin.")
            response = input("   Continue with constraint enforcement? (y/N): ")
            
            if response.lower() not in ['y', 'yes']:
                print("❌ Operation cancelled by user.")
                return None
            
            # Enforce constraint
            result = superadmin_service.ensure_single_superadmin_constraint(keep_latest=True)
            session.commit()
            
            print(f"✅ {result['message']}")
            if result['action'] == 'constraint_enforced':
                print(f"   Kept: {result['kept_superadmin']['email']}")
                for demoted in result['demoted_superadmins']:
                    print(f"   Demoted to org_admin: {demoted['email']}")
        
        # Check if Super Admin already exists
        existing_admin = session.query(UserModel).filter(UserModel.email == email).first()
        if existing_admin:
            print(f"\n📧 Super Admin with email {email} already exists!")
            
            # Verify they have superadmin role
            if existing_admin.role != UserRole.SUPER_ADMIN:
                print(f"⚠️  User exists but has role '{existing_admin.role}', not superadmin!")
                return existing_admin.id            
            # Check if they're assigned to system organization
            manager = SystemOrganizationManager(session)
            system_org = manager.get_or_create_system_organization()
            
            if existing_admin.tenant_id != system_org.id:
                print("📋 Existing superadmin is not assigned to system organization. Fixing...")
                
                # Assign to system org
                manager.assign_superadmin_to_system_org(existing_admin, system_org)
                session.commit()
                
                print(f"✅ Assigned existing superadmin to system organization: {system_org.name}")
                print(f"🆔 Organization ID: {system_org.id}")
            else:
                # Check if assigned to system org
                org = session.query(TenantModel).filter(TenantModel.id == existing_admin.tenant_id).first()
                org_name = org.name if org else "Unknown Organization"
                print(f"✅ Superadmin is already assigned to organization: {org_name}")
            
            return existing_admin.id
        
        # Check if we can create a new superadmin (should be allowed now after constraint enforcement)
        if not superadmin_service.can_create_superadmin():
            print("❌ Cannot create superadmin: constraint violation (this shouldn't happen after enforcement)")
            return None
        
        # Create system organization manager
        manager = SystemOrganizationManager(session)
        system_org = manager.get_or_create_system_organization()
        
        # Create password hash
        password_service = PasswordService()
        password_hash = password_service.hash_password(password)
        
        # Create Super Admin user with system organization
        super_admin = UserModel(
            id=uuid.uuid4(),
            tenant_id=system_org.id,  # Assign to system organization
            team_id=None,
            email=email,
            username="superadmin",
            first_name="Super",
            last_name="Admin",
            password_hash=password_hash,
            role=UserRole.SUPER_ADMIN,
            status=UserStatus.ACTIVE,
            is_email_verified=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            oauth_provider=None,
            oauth_provider_id=None
        )
        
        session.add(super_admin)
        session.commit()
        
        print(f"✅ Super Admin created successfully!")
        print(f"📧 Email: {email}")
        print(f"🔑 Password: {password}")
        print(f"🆔 ID: {super_admin.id}")
        print(f"🏢 Organization: {system_org.name} ({system_org.id})")
        print(f"🔒 Role: Super Admin (can access all organizations)")
        print(f"📊 Subscription Tier: {system_org.subscription_tier}")
        
        return super_admin.id


if __name__ == "__main__":
    print("🚀 Creating SalesOptimizer Super Admin...")
    print("=" * 50)
    create_super_admin()
    print("✨ Done!")
