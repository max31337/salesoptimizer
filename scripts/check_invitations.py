import sys
import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select, text

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from infrastructure.db.database import get_async_database_url
from infrastructure.db.models.invitation_model import InvitationModel
from infrastructure.db.models.tenant_model import TenantModel

async def check_database():
    """Check if invitations and tenants are in the database."""
    engine = create_async_engine(get_async_database_url())
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # Check invitations
            invitation_result = await session.execute(select(InvitationModel))
            invitations = invitation_result.scalars().all()
            
            print(f"📧 Invitations in database: {len(invitations)}")
            for inv in invitations:
                print(f"   - ID: {inv.id}")
                print(f"   - Email: {inv.email}")
                print(f"   - Organization: {inv.organization_name}")
                print(f"   - Tenant ID: {inv.tenant_id}")
                print(f"   - Created: {inv.created_at}")
                print()
            
            # Check tenants
            tenant_result = await session.execute(select(TenantModel))
            tenants = tenant_result.scalars().all()
            
            print(f"🏢 Tenants in database: {len(tenants)}")
            for tenant in tenants:
                print(f"   - ID: {tenant.id}")
                print(f"   - Name: {tenant.name}")
                print(f"   - Slug: {tenant.slug}")
                print(f"   - Created: {tenant.created_at}")
                print()
                
            # Check if specific IDs from your response exist
            specific_invitation_id = "a96507f1-40d0-4483-9266-26d151c10eb2"
            specific_tenant_id = "1ca3465b-af64-4816-bb2b-809af1b08eeb"
            
            inv_check = await session.execute(
                text("SELECT * FROM invitations WHERE id = :id"),
                {"id": specific_invitation_id}
            )
            tenant_check = await session.execute(
                text("SELECT * FROM tenants WHERE id = :id"),
                {"id": specific_tenant_id}
            )
            
            print(f"🔍 Specific invitation exists: {inv_check.first() is not None}")
            print(f"🔍 Specific tenant exists: {tenant_check.first() is not None}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_database())