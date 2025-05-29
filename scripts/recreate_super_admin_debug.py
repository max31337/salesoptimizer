import asyncio
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select

from infrastructure.db.base import get_async_database_url
from infrastructure.db.models.user_model import UserModel
from infrastructure.services.password_service import PasswordService
from domain.organization.entities.user import UserRole, UserStatus

async def recreate_super_admin_debug():
    """Recreate Super Admin with detailed debug info."""
    
    engine = create_async_engine(get_async_database_url())
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    email = "admin@salesoptimizer.com"
    username = "superadmin"
    password = "SuperAdmin123!"
    
    print(f"🔍 Creating Super Admin:")
    print(f"   Email: {email}")
    print(f"   Username: {username}")
    print(f"   Password: {password}")
    
    # Test password service first
    password_service = PasswordService()
    print(f"\n🔍 Testing password service:")
    
    password_hash = password_service.hash_password(password)
    print(f"   Generated hash: {password_hash}")
    print(f"   Hash length: {len(password_hash)}")
    
    # Verify immediately
    verification_result = password_service.verify_password(password, password_hash)
    print(f"   ✅ Immediate verification: {verification_result}")
    
    if not verification_result:
        print("❌ Password service is broken!")
        return
    
    async with async_session() as session:
        # Delete existing
        existing_result = await session.execute(
            select(UserModel).where(
                (UserModel.email == email) | (UserModel.username == username)
            )
        )
        existing_users = existing_result.scalars().all()
        
        for existing in existing_users:
            await session.delete(existing)
            print(f"🗑️ Deleted existing user: {existing.email}")
        
        # Create new user
        super_admin = UserModel(
            id=uuid.uuid4(),
            tenant_id=None,
            team_id=None,
            email=email,
            username=username,
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
        await session.refresh(super_admin)
        
        print(f"\n✅ Super Admin created:")
        print(f"   ID: {super_admin.id}")
        print(f"   Email: {super_admin.email}")
        print(f"   Username: {super_admin.username}")
        print(f"   Role: {super_admin.role}")
        print(f"   Status: {super_admin.status}")
        print(f"   Password hash: {super_admin.password_hash[:20]}...")
        
        # Test verification again with stored hash
        stored_verification = password_service.verify_password(password, super_admin.password_hash if isinstance(super_admin.password_hash, str) else super_admin.password_hash.value)
        print(f"   ✅ Stored hash verification: {stored_verification}")

if __name__ == "__main__":
    asyncio.run(recreate_super_admin_debug())