import sys
import os
import asyncio
import platform
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# Fix Windows event loop policy for psycopg
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from infrastructure.db.database import get_async_database_url
from infrastructure.db.repositories.user_repository_impl import UserRepositoryImpl
from domain.organization.value_objects.email import Email
from domain.organization.value_objects.user_role import Permission

async def test_superadmin_permissions():
    """Test SuperAdmin permissions for invitation creation."""
    engine = create_async_engine(get_async_database_url())
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as session:
        user_repository = UserRepositoryImpl(session)
        
        # Get SuperAdmin user
        superadmin = await user_repository.get_by_email(Email("admin@salesoptimizer.com"))
        
        if superadmin:
            print(f"✅ SuperAdmin found: {superadmin.email}")
            print(f"🔍 Role: {superadmin.role.value}")
            print(f"🔍 Can create invitations: {superadmin.can_create_invitations()}")
            print(f"🔍 Can create tenants: {superadmin.can_create_tenants()}")
            print(f"🔍 Has CREATE_INVITATION permission: {superadmin.has_permission(Permission.CREATE_INVITATION)}")
            print(f"🔍 Has CREATE_TENANT permission: {superadmin.has_permission(Permission.CREATE_TENANT)}")
        else:
            print("❌ SuperAdmin not found!")
            print("Creating SuperAdmin...")
            
            # Create SuperAdmin if not found
            from scripts.fix_super_admin import fix_super_admin
            await fix_super_admin()

if __name__ == "__main__":
    asyncio.run(test_superadmin_permissions())