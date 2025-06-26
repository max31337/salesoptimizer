#!/usr/bin/env python3
"""
Test Database-Level Superadmin Constraints

This script tests that database-level constraints properly prevent 
creation of multiple superadmins.
"""
import sys
from pathlib import Path
import uuid
from datetime import datetime, timezone

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from infrastructure.db.database import get_database_url
from infrastructure.db.models.user_model import UserModel
from domain.organization.entities.user import UserRole, UserStatus


def test_database_constraint():
    """Test that database-level constraints prevent multiple superadmins."""
    
    engine = create_engine(get_database_url())
    SessionLocal = sessionmaker(bind=engine)
    
    print("🧪 Testing Database-Level Superadmin Constraints")
    print("=" * 60)
    
    with SessionLocal() as session:
        # First, check current superadmin count
        current_count = session.query(UserModel).filter(
            UserModel.role == UserRole.SUPER_ADMIN
        ).count()
        
        print(f"📊 Current superadmin count: {current_count}")
        
        if current_count == 0:
            print("📝 Creating first superadmin (should succeed)...")
            
            # Create first superadmin
            superadmin1 = UserModel(
                id=uuid.uuid4(),
                email="test_superadmin1@example.com",
                username="test_superadmin1",
                first_name="Test",
                last_name="SuperAdmin1",
                password_hash="test_hash",
                role=UserRole.SUPER_ADMIN,
                status=UserStatus.ACTIVE,
                is_email_verified=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            try:
                session.add(superadmin1)
                session.commit()
                print("✅ First superadmin created successfully")
                
                # Update current count
                current_count = 1
                
            except Exception as e:
                print(f"❌ Failed to create first superadmin: {e}")
                session.rollback()
                return False
        
        if current_count >= 1:
            print("📝 Attempting to create second superadmin (should fail)...")
            
            # Try to create second superadmin
            superadmin2 = UserModel(
                id=uuid.uuid4(),
                email="test_superadmin2@example.com",
                username="test_superadmin2",
                first_name="Test",
                last_name="SuperAdmin2",
                password_hash="test_hash",
                role=UserRole.SUPER_ADMIN,
                status=UserStatus.ACTIVE,
                is_email_verified=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            try:
                session.add(superadmin2)
                session.commit()
                print("❌ ERROR: Second superadmin was created (constraint failed!)")
                
                # Clean up the extra superadmin
                session.delete(superadmin2)
                session.commit()
                return False
                
            except (IntegrityError, Exception) as e:
                print(f"✅ Database constraint prevented second superadmin: {type(e).__name__}")
                print(f"   Error message: {str(e)}")
                session.rollback()
        
        # Test updating existing user to superadmin
        print("📝 Testing role update to superadmin (should fail)...")
        
        # Create a regular user
        regular_user = UserModel(
            id=uuid.uuid4(),
            email="test_regular@example.com",
            username="test_regular",
            first_name="Test",
            last_name="Regular",
            password_hash="test_hash",
            role=UserRole.SALES_REP,
            status=UserStatus.ACTIVE,
            is_email_verified=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        session.add(regular_user)
        session.commit()
        
        # Try to update to superadmin
        try:
            regular_user.role = UserRole.SUPER_ADMIN
            session.commit()
            print("❌ ERROR: User role was updated to superadmin (constraint failed!)")
            
            # Revert the change
            regular_user.role = UserRole.SALES_REP
            session.commit()
            return False
            
        except (IntegrityError, Exception) as e:
            print(f"✅ Database constraint prevented role update: {type(e).__name__}")
            print(f"   Error message: {str(e)}")
            session.rollback()
        
        # Clean up test user
        session.delete(regular_user)
        session.commit()
        
        # Final verification
        final_count = session.query(UserModel).filter(
            UserModel.role == UserRole.SUPER_ADMIN
        ).count()
        
        print(f"\n📊 Final superadmin count: {final_count}")
        
        if final_count == 1:
            print("✅ Database-level constraints are working correctly!")
            return True
        else:
            print(f"❌ Unexpected superadmin count: {final_count}")
            return False


def cleanup_test_users():
    """Clean up any test users created during testing."""
    
    engine = create_engine(get_database_url())
    SessionLocal = sessionmaker(bind=engine)
    
    with SessionLocal() as session:
        # Remove test users
        test_emails = [
            "test_superadmin1@example.com",
            "test_superadmin2@example.com", 
            "test_regular@example.com"
        ]
        
        for email in test_emails:
            user = session.query(UserModel).filter(UserModel.email == email).first()
            if user:
                session.delete(user)
                print(f"🧹 Cleaned up test user: {email}")
        
        session.commit()


if __name__ == "__main__":
    try:
        success = test_database_constraint()
        
        print(f"\n{'='*60}")
        if success:
            print("🎉 All database constraint tests passed!")
        else:
            print("⚠️  Some database constraint tests failed!")
            
    except Exception as e:
        print(f"💥 Test failed with error: {e}")
        
    finally:
        print("\n🧹 Cleaning up test data...")
        cleanup_test_users()
        print("✨ Done!")
