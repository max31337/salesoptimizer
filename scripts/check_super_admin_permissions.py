import sys
import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from infrastructure.db.database import get_async_database_url
from infrastructure.db.repositories.user_repository_impl import UserRepositoryImpl
from domain.organization.value_objects.email import Email
from domain.organization.value_objects.user_role import Permission

async def check_super_admin():
    engine = create_async_engine(get_async_database_url())
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as session:
        user_repository = UserRepositoryImpl(session)
        
        # Get the super admin user
        superadmin = await user_repository.get_by_email(Email("admin@salesoptimizer.com"))
        
        if superadmin:
            print(f"✅ Super Admin found: {superadmin.email}")
            print(f"Role: {superadmin.role.value}")
            print(f"Status: {superadmin.status.value}")
            print(f"Active: {superadmin.is_active()}")
            print("\nPermission checks:")
            print(f"- CREATE_INVITATION: {superadmin.has_permission(Permission.CREATE_INVITATION)}")
            print(f"- CREATE_TENANT: {superadmin.has_permission(Permission.CREATE_TENANT)}")
            print(f"- MANAGE_SYSTEM: {superadmin.has_permission(Permission.MANAGE_SYSTEM)}")
            print(f"- can_create_invitations(): {superadmin.can_create_invitations()}")
            print(f"- can_create_tenants(): {superadmin.can_create_tenants()}")
        else:
            print("❌ Super Admin not found!")

if __name__ == "__main__":
    asyncio.run(check_super_admin())