import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select
from infrastructure.db.base import get_async_database_url
from infrastructure.db.models.user_model import UserModel
from infrastructure.services.password_service import PasswordService

async def debug_super_admin_detailed():
    engine = create_async_engine(get_async_database_url())
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as session:
        # Check both email and username
        result = await session.execute(
            select(UserModel).where(
                (UserModel.email == "admin@salesoptimizer.com") |
                (UserModel.username == "superadmin")
            )
        )
        users = result.scalars().all()
        
        if not users:
            print("❌ No users found!")
            return
            
        for user in users:
            print(f"\n✅ Found user:")
            print(f"   Email: {user.email}")
            print(f"   Username: {user.username}")
            print(f"   Role: {user.role}")
            print(f"   Status: {user.status}")
            password_hash_value = getattr(user, "password_hash", None)
            print(f"   Password hash: {password_hash_value[:20] + '...' if password_hash_value else 'None'}")
            print(f"   Password hash length: {len(password_hash_value) if password_hash_value else 0}")
            
            # Test password verification
            if getattr(user, "password_hash", None) is not None:
                password_service = PasswordService()
                test_password = "SuperAdmin123!"
                
                print(f"\n🔍 Testing password verification:")
                print(f"   Test password: {test_password}")
                
                try:
                    is_valid = password_service.verify_password(test_password, getattr(user, "password_hash", "") or "")
                    print(f"   ✅ Password verification result: {is_valid}")
                    
                    # Test with wrong password
                    is_valid_wrong = password_service.verify_password("wrong_password", getattr(user, "password_hash", "") or "")
                    print(f"   ❌ Wrong password verification result: {is_valid_wrong}")
                    
                except Exception as e:
                    print(f"   ❌ Password verification error: {e}")
            else:
                print("   ❌ No password hash to test!")

if __name__ == "__main__":
    asyncio.run(debug_super_admin_detailed())