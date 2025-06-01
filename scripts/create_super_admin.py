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
from infrastructure.services.password_service import PasswordService
from domain.organization.entities.user import UserRole, UserStatus

def create_super_admin():
    """Create the initial Super Admin user (synchronous version)."""
    
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
        
        # Create password hash
        password_service = PasswordService()
        password_hash = password_service.hash_password(password)
        
        # Create Super Admin user
        super_admin = UserModel(
            id=uuid.uuid4(),
            tenant_id=None,
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

if __name__ == "__main__":
    create_super_admin()