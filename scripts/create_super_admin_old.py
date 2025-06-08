import uuid
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from infrastructure.db.database import get_database_url
from infrastructure.db.models.user_model import UserModel
from infrastructure.db.models.tenant_model import TenantModel
from infrastructure.services.password_service import PasswordService
from domain.organization.entities.user import UserRole, UserStatus

def get_or_create_system_organization(session: Session) -> Any:
    """Get existing system organization or create it."""
    system_org_name = "SalesOptimizer Platform"
    
    # Check if system organization already exists
    existing_org = session.query(TenantModel).filter(
        TenantModel.name == system_org_name
    ).first()
    
    if existing_org:
        print(f"📋 Using existing system organization: {system_org_name}")
        return existing_org.id
    
    # Create system organization
    system_org = TenantModel(
        id=uuid.uuid4(),
        name=system_org_name,
        slug="salesoptimizer-platform",
        subscription_tier="system",
        is_active=True,
        owner_id=None,
        settings={
            "is_system_organization": True,
            "description": "SalesOptimizer Platform system organization for superadmins",
            "created_by": "superadmin_creation"
        },
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    session.add(system_org)
    session.flush()  # Get the ID without committing
    
    print(f"✅ Created system organization: {system_org_name}")
    return system_org.id

def create_super_admin():
    """Create the initial Super Admin user and assign to system organization."""
    
    # Database setup with psycopg2
    engine = create_engine(get_database_url())
    SessionLocal = sessionmaker(bind=engine)
    
    # User details
    email = "admin@salesoptimizer.com"
    password = "SuperAdmin123!"
    
    with SessionLocal() as session:
        # Check if Super Admin already exists
        existing_admin = session.query(UserModel).filter(UserModel.email == email).first()
        if existing_admin:
            print(f"Super Admin with email {email} already exists!")
            return
        
        # Get or create system organization
        system_org_id = get_or_create_system_organization(session)
        
        # Create password hash
        password_service = PasswordService()
        password_hash = password_service.hash_password(password)
        
        # Create Super Admin user with system organization
        super_admin = UserModel(
            id=uuid.uuid4(),
            tenant_id=system_org_id,  # Assign to system organization
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
        print(f"🏢 Organization: SalesOptimizer Platform ({system_org_id})")
        print(f"🔒 Role: Super Admin (can access all organizations)")

if __name__ == "__main__":
    create_super_admin()