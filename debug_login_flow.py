#!/usr/bin/env python3
"""Debug script to test login flow and activity logging."""

import asyncio
import os
import sys
sys.path.append('.')

from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from infrastructure.db.repositories.user_repository_impl import UserRepositoryImpl
from infrastructure.db.repositories.activity_log_repository_impl import ActivityLogRepositoryImpl
from domain.organization.services.auth_service import AuthService
from domain.organization.services.activity_log_service import ActivityLogService
from infrastructure.services.password_service import PasswordService
from infrastructure.services.jwt_service import JWTService
from application.use_cases.auth_use_cases import AuthUseCases
from application.commands.auth_command import LoginCommand
from infrastructure.db.models.user_model import UserModel
from infrastructure.db.models.activity_log_model import ActivityLogModel
from sqlalchemy import select


async def debug_login_flow():
    """Debug the login flow to see where the issue is."""
    
    # Get database URL from environment
    db_url = os.getenv('DATABASE_URL', 'postgresql+asyncpg://postgres:postgres@localhost:5432/salesoptimizer_db')
    print(f'Using database: {db_url}')
    
    engine = create_async_engine(db_url)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # Setup repositories and services
            user_repository = UserRepositoryImpl(session)
            activity_log_repository = ActivityLogRepositoryImpl(session)
            
            password_service = PasswordService()
            jwt_service = JWTService()
            
            auth_service = AuthService(user_repository, password_service, jwt_service)
            activity_log_service = ActivityLogService(activity_log_repository)
            
            auth_use_cases = AuthUseCases(auth_service, None, activity_log_service)
            
            # Test user credentials
            email = "admin@salesoptimizer.com"
            password = "SuperAdmin123!"
            
            print(f"\n🔍 Testing login for: {email}")
            
            # Create login command
            command = LoginCommand(email_or_username=email, password=password)
              # Check initial state
            print("\n📊 Before login:")
            from domain.organization.value_objects.email import Email
            user_before = await user_repository.get_by_email(Email(email))
            if user_before:
                print(f"  User ID: {user_before.id}")
                print(f"  Last login: {user_before.last_login}")
                print(f"  Updated at: {user_before.updated_at}")
                
                # Check activity logs before
                activity_count_before = await activity_log_repository.count_by_user_id(user_before.id)
                print(f"  Activity logs count: {activity_count_before}")
            else:
                print("  User not found!")
                return
            
            # Perform login with device info
            print("\n🔑 Performing login...")
            user_agent = "Mozilla/5.0 (Test Browser)"
            ip_address = "127.0.0.1"
            
            try:
                user, access_token, refresh_token = await auth_use_cases.login_with_device_info(
                    command, user_agent, ip_address
                )
                print(f"  ✅ Login successful!")
                print(f"  User ID: {user.id}")
                print(f"  Access token length: {len(access_token)}")
                print(f"  Refresh token length: {len(refresh_token)}")
                
                # Commit the transaction
                await session.commit()
                print("  💾 Transaction committed")
                
            except Exception as e:
                print(f"  ❌ Login failed: {e}")
                import traceback
                traceback.print_exc()
                return
            
            # Check state after login
            print("\n📊 After login:")
            user_after = await user_repository.get_by_email(Email(email))
            if user_after:
                print(f"  User ID: {user_after.id}")
                print(f"  Last login: {user_after.last_login}")
                print(f"  Updated at: {user_after.updated_at}")
                
                # Check if last_login was updated
                if user_after.last_login != user_before.last_login:
                    print("  ✅ Last login was updated!")
                else:
                    print("  ❌ Last login was NOT updated!")
                
                # Check activity logs after
                activity_count_after = await activity_log_repository.count_by_user_id(user_after.id)
                print(f"  Activity logs count: {activity_count_after}")
                
                if activity_count_after > activity_count_before:
                    print("  ✅ Activity log was created!")
                    
                    # Get the latest activity log
                    recent_activities = await activity_log_repository.get_by_user_id(
                        user_after.id, limit=1, offset=0
                    )
                    if recent_activities:
                        activity = recent_activities[0]
                        print(f"    Activity type: {activity.activity_type}")
                        print(f"    Description: {activity.description}")
                        print(f"    IP address: {activity.ip_address}")
                        print(f"    User agent: {activity.user_agent}")
                        print(f"    Created at: {activity.created_at}")
                else:
                    print("  ❌ Activity log was NOT created!")
            
            # Check database directly
            print("\n🔍 Checking database directly:")
            
            # Check user table
            stmt = select(UserModel).where(UserModel.email == email)
            result = await session.execute(stmt)
            user_model = result.scalar_one_or_none()
            
            if user_model:
                print(f"  DB User last_login: {user_model.last_login}")
                print(f"  DB User updated_at: {user_model.updated_at}")
            
            # Check activity logs table
            stmt = select(ActivityLogModel).where(
                ActivityLogModel.user_id == user_model.id
            ).order_by(ActivityLogModel.created_at.desc()).limit(5)
            result = await session.execute(stmt)
            activity_models = result.scalars().all()
            
            print(f"  DB Activity logs count: {len(activity_models)}")
            for i, activity in enumerate(activity_models):
                print(f"    {i+1}. {activity.activity_type} - {activity.created_at}")
                
        except Exception as e:
            print(f"Error during testing: {e}")
            import traceback
            traceback.print_exc()
            await session.rollback()
        
        finally:
            await session.close()


if __name__ == "__main__":
    asyncio.run(debug_login_flow())
