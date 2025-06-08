#!/usr/bin/env python3
"""
Create Super Admin Script - Creates a superadmin user, system organization, and platform management team.
This script ensures the system organization exists, creates a platform management team, and assigns the superadmin to both.
"""
import uuid
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from infrastructure.db.database import get_database_url
from infrastructure.db.models.user_model import UserModel
from infrastructure.db.models.tenant_model import TenantModel
from infrastructure.db.models.team_model import TeamModel
from infrastructure.services.password_service import PasswordService
from domain.organization.entities.user import UserRole, UserStatus
from domain.organization.services.superadmin_management_service import SuperadminManagementService
from scripts.system_organization_manager import SystemOrganizationManager


class PlatformInitializationService:
    """Service for initializing platform with superadmin, system org, and management team."""
    
    PLATFORM_TEAM_NAME = "Platform Management"
    PLATFORM_TEAM_DESCRIPTION = "SalesOptimizer Platform management team for superadmins and system operations"
    
    def __init__(self, session: Session):
        self.session = session
        self.org_manager = SystemOrganizationManager(session)
        self.superadmin_service = SuperadminManagementService(session)
    
    def get_platform_management_team(self, system_org: TenantModel) -> Optional[TeamModel]:
        """Get the platform management team if it exists."""
        return self.session.query(TeamModel).filter(
            TeamModel.tenant_id == system_org.id,
            TeamModel.name == self.PLATFORM_TEAM_NAME
        ).first()
    
    def create_platform_management_team(self, system_org: TenantModel, manager: Optional[UserModel] = None) -> TeamModel:
        """Create the platform management team."""
        team = TeamModel(
            id=uuid.uuid4(),
            tenant_id=system_org.id,
            name=self.PLATFORM_TEAM_NAME,
            description=self.PLATFORM_TEAM_DESCRIPTION,
            manager_id=manager.id if manager else None,
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        self.session.add(team)
        self.session.flush()  # Get the ID without committing
        
        return team
    
    def get_or_create_platform_team(self, system_org: TenantModel, manager: Optional[UserModel] = None) -> TeamModel:
        """Get existing platform team or create it if it doesn't exist."""
        team = self.get_platform_management_team(system_org)
        
        if team:
            # Update manager if provided and different
            if manager and team.manager_id != manager.id:
                team.manager_id = manager.id
                team.updated_at = datetime.now(timezone.utc)
            return team
        
        return self.create_platform_management_team(system_org, manager)
    
    def assign_user_to_platform_team(self, user: UserModel, team: TeamModel) -> None:
        """Assign a user to the platform management team."""
        user.team_id = team.id
        user.updated_at = datetime.now(timezone.utc)



def initialize_platform(email: str = "admin@salesoptimizer.com", password: str = "SuperAdmin123!") -> Dict[str, Any]:
    """Initialize the platform with superadmin, system organization, and platform team."""
    
    # Database setup
    engine = create_engine(get_database_url())
    SessionLocal = sessionmaker(bind=engine)
    
    with SessionLocal() as session:
        platform_service = PlatformInitializationService(session)
        
        print("🔍 Checking platform initialization status...")
        
        # Step 1: Validate and handle superadmin constraints
        validation = platform_service.superadmin_service.validate_single_superadmin_constraint()
        
        print(f"📊 Superadmin Status:")
        print(f"   Current superadmins: {validation['current_count']}")
        print(f"   Maximum allowed: {validation['max_allowed']}")
        
        if not validation["is_valid"]:
            print(f"❌ {validation['violation_message']}")
            print("🛠️  Enforcing single superadmin constraint...")
            
            # Show current superadmins
            for admin in validation["superadmins"]:
                print(f"   - {admin['email']} (ID: {admin['id']}, Created: {admin['created_at']})")
            
            # Enforce constraint automatically (keep latest)
            result = platform_service.superadmin_service.ensure_single_superadmin_constraint(keep_latest=True)
            session.commit()
            
            print(f"✅ {result['message']}")
            if result['action'] == 'constraint_enforced':
                print(f"   Kept: {result['kept_superadmin']['email']}")
                for demoted in result['demoted_superadmins']:
                    print(f"   Demoted to org_admin: {demoted['email']}")
        
        # Step 2: Get or create system organization
        print("\n🏢 System Organization Setup...")
        system_org = platform_service.org_manager.get_or_create_system_organization()
        was_org_created = platform_service.org_manager.get_system_organization() is None
        
        print(f"✅ System Organization: {system_org.name}")
        print(f"   ID: {system_org.id}")
        print(f"   Status: {'Created' if was_org_created else 'Already exists'}")
        
        # Step 3: Check if superadmin already exists
        print(f"\n👤 Superadmin Setup...")
        existing_admin = session.query(UserModel).filter(UserModel.email == email).first()
        superadmin = None
        
        if existing_admin:
            print(f"📧 Super Admin with email {email} already exists!")
            
            # Verify they have superadmin role
            if existing_admin.role != UserRole.SUPER_ADMIN:
                print(f"⚠️  User exists but has role '{existing_admin.role}', updating to superadmin...")
                existing_admin.role = UserRole.SUPER_ADMIN
                existing_admin.updated_at = datetime.now(timezone.utc)
            
            # Ensure they're assigned to system organization
            if existing_admin.tenant_id != system_org.id:
                print("📋 Assigning superadmin to system organization...")
                platform_service.org_manager.assign_superadmin_to_system_org(existing_admin, system_org)
            
            superadmin = existing_admin
            print(f"✅ Superadmin verified and updated")
            
        else:
            # Check if we can create a new superadmin
            if not platform_service.superadmin_service.can_create_superadmin():
                print("❌ Cannot create superadmin: constraint violation")
                return {"error": "Cannot create superadmin due to constraint violation"}
            
            # Create password hash
            password_service = PasswordService()
            password_hash = password_service.hash_password(password)
            
            # Create Super Admin user with system organization
            superadmin = UserModel(
                id=uuid.uuid4(),
                tenant_id=system_org.id,
                team_id=None,  # Will be assigned to team later
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
            
            session.add(superadmin)
            session.flush()  # Get the ID
            
            print(f"✅ Super Admin created successfully!")
            print(f"📧 Email: {email}")
            print(f"🔑 Password: {password}")
        
        # Step 4: Get or create platform management team
        print(f"\n👥 Platform Management Team Setup...")
        platform_team = platform_service.get_or_create_platform_team(system_org, superadmin)
        was_team_created = platform_service.get_platform_management_team(system_org) is None
        
        print(f"✅ Platform Team: {platform_team.name}")
        print(f"   ID: {platform_team.id}")
        print(f"   Status: {'Created' if was_team_created else 'Already exists'}")
        print(f"   Manager: {superadmin.email}")
        
        # Step 5: Assign superadmin to platform team if not already assigned
        if superadmin.team_id != platform_team.id:
            print("🔗 Assigning superadmin to platform management team...")
            platform_service.assign_user_to_platform_team(superadmin, platform_team)
            print("✅ Superadmin assigned to platform team")
        else:
            print("✅ Superadmin already assigned to platform team")
        
        # Step 6: Check for other orphaned superadmins and assign them to the team
        other_superadmins = session.query(UserModel).filter(
            UserModel.role == UserRole.SUPER_ADMIN,
            UserModel.id != superadmin.id,
            UserModel.team_id.is_(None)
        ).all()
        
        if other_superadmins:
            print(f"\n🔄 Assigning {len(other_superadmins)} other superadmin(s) to platform team...")
            for admin in other_superadmins:
                if admin.tenant_id != system_org.id:
                    platform_service.org_manager.assign_superadmin_to_system_org(admin, system_org)
                platform_service.assign_user_to_platform_team(admin, platform_team)
                print(f"   ✅ Assigned {admin.email} to platform team")
        
        # Commit all changes
        session.commit()
        
        print(f"\n🎉 Platform initialization completed!")
        
        return {
            "success": True,
            "superadmin": {
                "id": str(superadmin.id),
                "email": superadmin.email,
                "created": existing_admin is None
            },
            "system_organization": {
                "id": str(system_org.id),
                "name": system_org.name,
                "slug": system_org.slug,
                "created": was_org_created
            },
            "platform_team": {
                "id": str(platform_team.id),
                "name": platform_team.name,
                "manager_id": str(platform_team.manager_id),
                "created": was_team_created
            },
            "other_superadmins_processed": len(other_superadmins) if other_superadmins else 0
        }


def create_super_admin():
    """Legacy function for backward compatibility."""
    result = initialize_platform()
    if result.get("success"):
        superadmin = result["superadmin"]
        system_org = result["system_organization"]
        platform_team = result["platform_team"]
        
        print(f"\n📋 Summary:")
        print(f"   🆔 Superadmin ID: {superadmin['id']}")
        print(f"   🏢 Organization: {system_org['name']} ({system_org['id']})")
        print(f"   👥 Team: {platform_team['name']} ({platform_team['id']})")
        print(f"   🔒 Role: Super Admin (can access all organizations)")
        
        return superadmin["id"]
    else:
        print(f"❌ Platform initialization failed: {result.get('error', 'Unknown error')}")
        return None


if __name__ == "__main__":
    print("🚀 Initializing SalesOptimizer Platform...")
    print("=" * 60)
    result = initialize_platform()
    
    if result.get("success"):
        print("✨ Platform initialization completed successfully!")
    else:
        print("❌ Platform initialization failed!")
        sys.exit(1)
