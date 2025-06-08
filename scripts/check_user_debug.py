import asyncio
import os
import sys
sys.path.append('.')
from uuid import UUID
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from infrastructure.db.models.user_model import UserModel

async def check_user():
    try:
        # Get database URL from environment - use PostgreSQL
        db_url = os.getenv('DATABASE_URL', 'postgresql+asyncpg://postgres:postgres@localhost:5432/salesoptimizer')
        print(f'Using database: {db_url}')
        
        engine = create_async_engine(db_url)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as session:
            # Get user by ID from the logs
            user_id = UUID('2e4f6d87-797c-4af3-a8f4-73e37acbf57a')
            stmt = select(UserModel).where(UserModel.id == user_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if user:
                print(f'User found:')
                print(f'  ID: {user.id}')
                print(f'  Email: {user.email}')
                print(f'  First Name: "{user.first_name}"')
                print(f'  Last Name: "{user.last_name}"')
                print(f'  Username: {user.username}')
                print(f'  Role: {user.role}')
                print(f'  Status: {user.status}')
                print(f'  First name length: {len(user.first_name or "")}')
                print(f'  Last name length: {len(user.last_name or "")}')
                print(f'  First name is empty: {not user.first_name or not user.first_name.strip()}')
                print(f'  Last name is empty: {not user.last_name or not user.last_name.strip()}')
            else:
                print('User not found')
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_user())
