import asyncio
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select

from infrastructure.db.base import get_database_url
from infrastructure.db.models.user_model import UserModel
from infrastructure.services.password_service import PasswordService
from domain.organization.entities.user import UserRole, UserStatus

async def create_super_admin():
    """Create the initial Super Admin user."""
    
    # Database setup
    engine = create_async_engine(get_database_url())
    engine = create_async_engine(get_database_url())
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    # User details
    email = "admin@salesoptimizer.com"
    password = "SuperAdmin123!"  # Change this to a secure password
    
    # Check if Super Admin already exists
    async with async_session() as session:
        existing_admin = await session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        if existing_admin.scalar_one_or_none():
            print(f"Super Admin with email {email} already exists!")
            return
        
        # Create password hash
        password_service = PasswordService()
        password_hash = password_service.hash_password(password)
        
        # Create Super Admin user
        super_admin = UserModel(
            id=uuid.uuid4(),
            tenant_id=None,  # Super Admin has no tenant
            team_id=None,    # Super Admin has no team
            email=email,
            username="superadmin",
            first_name="Super",
            last_name="Admin",
            password_hash=password_hash,
            role=UserRole.SUPER_ADMIN.value,
            status=UserStatus.ACTIVE.value,
            is_email_verified=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        session.add(super_admin)
        await session.commit()
        
        print(f"✅ Super Admin created successfully!")
        print(f"📧 Email: {email}")
        print(f"🔑 Password: {password}")
        print(f"🆔 ID: {super_admin.id}")

if __name__ == "__main__":
    asyncio.run(create_super_admin())