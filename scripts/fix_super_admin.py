import sys
import os
import asyncio
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select
from infrastructure.db.base import get_async_database_url
from infrastructure.db.models.user_model import UserModel
from infrastructure.services.password_service import PasswordService

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


async def fix_super_admin():
    """Fix the Super Admin with correct password hash."""
    
    engine = create_async_engine(get_async_database_url())
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    email = "admin@salesoptimizer.com"
    username = "superadmin"
    password = "SuperAdmin123!"
    
    print(f"🔧 Fixing Super Admin password hash...")
    print(f"   Email: {email}")
    print(f"   Username: {username}")
    print(f"   Password: {password}")
    
    # Create proper password hash
    password_service = PasswordService()
    password_hash = password_service.hash_password(password)
    print(f"   New hash: {password_hash}")
    print(f"   Hash length: {len(password_hash)}")
    
    # Verify the hash immediately
    verification_result = password_service.verify_password(password, password_hash)
    print(f"   ✅ Hash verification: {verification_result}")
    
    if not verification_result:
        print("❌ Password hash creation failed!")
        return
    
    async with async_session() as session:
        # Find existing super admin
        result = await session.execute(
            select(UserModel).where(
                (UserModel.email == email) | (UserModel.username == username)
            )
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print(f"📝 Updating existing Super Admin...")
            print(f"   Old hash: {existing_user.password_hash}")
            old_hash_value = getattr(existing_user, "password_hash", "") or ""
            print(f"   Old hash length: {len(old_hash_value)}")
            
            # Update the password hash
            setattr(existing_user, "password_hash", password_hash)
            setattr(existing_user, "role", "super_admin")
            setattr(existing_user, "status", "active")
            setattr(existing_user, "is_email_verified", True)
            setattr(existing_user, "updated_at", datetime.now(timezone.utc))

            await session.commit()
            await session.refresh(existing_user)
            
            print(f"✅ Super Admin password updated!")
            print(f"   New hash: {getattr(existing_user, 'password_hash', '')[:30]}...")
            print(f"   New hash length: {len(getattr(existing_user, 'password_hash', '') or '')}")
            
            # Test the updated hash
            final_verification = password_service.verify_password(password, getattr(existing_user, "password_hash", "") or "")
            print(f"   ✅ Final verification: {final_verification}")
            
        else:
            print("❌ No existing Super Admin found to update!")

if __name__ == "__main__":
    asyncio.run(fix_super_admin())