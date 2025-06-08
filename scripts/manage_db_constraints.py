#!/usr/bin/env python3
"""
Manually Apply Database-Level Superadmin Constraints

This script manually adds database-level constraints to prevent multiple superadmins.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text

from infrastructure.db.database import get_database_url


def apply_database_constraints():
    """Manually apply database-level constraints."""
    
    engine = create_engine(get_database_url())
    
    print("🔧 Applying Database-Level Superadmin Constraints")
    print("=" * 60)
    
    with engine.connect() as connection:
        # Check database type
        dialect_name = connection.dialect.name
        print(f"📊 Database type: {dialect_name}")
        
        if dialect_name == 'postgresql':
            print("🐘 Applying PostgreSQL constraints...")
            
            # 1. Create partial unique index
            try:
                connection.execute(text("""
                    CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS idx_users_single_superadmin 
                    ON users (role) 
                    WHERE role = 'super_admin'
                """))
                print("✅ Partial unique index created")
            except Exception as e:
                print(f"⚠️  Index creation: {e}")
            
            # 2. Create validation function
            try:
                connection.execute(text("""
                    CREATE OR REPLACE FUNCTION validate_single_superadmin()
                    RETURNS TRIGGER AS $$
                    BEGIN
                        IF NEW.role = 'super_admin' THEN
                            IF EXISTS (
                                SELECT 1 FROM users 
                                WHERE role = 'super_admin' 
                                AND (TG_OP = 'INSERT' OR id != NEW.id)
                            ) THEN
                                RAISE EXCEPTION 'Only one superadmin is allowed in the system';
                            END IF;
                        END IF;
                        RETURN NEW;
                    END;
                    $$ LANGUAGE plpgsql;
                """))
                print("✅ Validation function created")
            except Exception as e:
                print(f"⚠️  Function creation: {e}")
            
            # 3. Create trigger
            try:
                connection.execute(text("""
                    DROP TRIGGER IF EXISTS trigger_validate_single_superadmin ON users;
                    CREATE TRIGGER trigger_validate_single_superadmin
                        BEFORE INSERT OR UPDATE ON users
                        FOR EACH ROW
                        EXECUTE FUNCTION validate_single_superadmin();
                """))
                print("✅ Trigger created")
            except Exception as e:
                print(f"⚠️  Trigger creation: {e}")
        
        elif dialect_name == 'sqlite':
            print("🗃️  Applying SQLite constraints...")
            
            # 1. Create trigger for INSERT
            try:
                connection.execute(text("""
                    CREATE TRIGGER IF NOT EXISTS trigger_insert_single_superadmin
                    BEFORE INSERT ON users
                    FOR EACH ROW
                    WHEN NEW.role = 'super_admin'
                    BEGIN
                        SELECT CASE
                            WHEN (SELECT COUNT(*) FROM users WHERE role = 'super_admin') > 0
                            THEN RAISE(ABORT, 'Only one superadmin is allowed in the system')
                        END;
                    END
                """))
                print("✅ INSERT trigger created")
            except Exception as e:
                print(f"⚠️  INSERT trigger: {e}")
            
            # 2. Create trigger for UPDATE
            try:
                connection.execute(text("""
                    CREATE TRIGGER IF NOT EXISTS trigger_update_single_superadmin
                    BEFORE UPDATE ON users
                    FOR EACH ROW
                    WHEN NEW.role = 'super_admin' AND OLD.role != 'super_admin'
                    BEGIN
                        SELECT CASE
                            WHEN (SELECT COUNT(*) FROM users WHERE role = 'super_admin') > 0
                            THEN RAISE(ABORT, 'Only one superadmin is allowed in the system')
                        END;
                    END
                """))
                print("✅ UPDATE trigger created")
            except Exception as e:
                print(f"⚠️  UPDATE trigger: {e}")
        
        else:
            print(f"❌ Unsupported database type: {dialect_name}")
            return False
        
        # Commit the changes
        connection.commit()
        print("✅ All constraints applied successfully!")
        return True


def remove_database_constraints():
    """Remove database-level constraints."""
    
    engine = create_engine(get_database_url())
    
    print("🗑️  Removing Database-Level Superadmin Constraints")
    print("=" * 60)
    
    with engine.connect() as connection:
        dialect_name = connection.dialect.name
        
        if dialect_name == 'postgresql':
            print("🐘 Removing PostgreSQL constraints...")
            
            try:
                connection.execute(text("DROP TRIGGER IF EXISTS trigger_validate_single_superadmin ON users;"))
                connection.execute(text("DROP FUNCTION IF EXISTS validate_single_superadmin();"))
                connection.execute(text("DROP INDEX IF EXISTS idx_users_single_superadmin;"))
                print("✅ PostgreSQL constraints removed")
            except Exception as e:
                print(f"⚠️  Removal error: {e}")
        
        elif dialect_name == 'sqlite':
            print("🗃️  Removing SQLite constraints...")
            
            try:
                connection.execute(text("DROP TRIGGER IF EXISTS trigger_insert_single_superadmin;"))
                connection.execute(text("DROP TRIGGER IF EXISTS trigger_update_single_superadmin;"))
                print("✅ SQLite constraints removed")
            except Exception as e:
                print(f"⚠️  Removal error: {e}")
        
        connection.commit()
        return True


def check_constraints_status():
    """Check if constraints are currently applied."""
    
    engine = create_engine(get_database_url())
    
    print("🔍 Checking Database Constraint Status")
    print("=" * 40)
    
    with engine.connect() as connection:
        dialect_name = connection.dialect.name
        
        if dialect_name == 'postgresql':
            # Check for index
            result = connection.execute(text("""
                SELECT indexname FROM pg_indexes 
                WHERE tablename = 'users' AND indexname = 'idx_users_single_superadmin'
            """))
            index_exists = result.fetchone() is not None
            print(f"📊 Unique index: {'✅ EXISTS' if index_exists else '❌ MISSING'}")
            
            # Check for function
            result = connection.execute(text("""
                SELECT proname FROM pg_proc WHERE proname = 'validate_single_superadmin'
            """))
            function_exists = result.fetchone() is not None
            print(f"🔧 Function: {'✅ EXISTS' if function_exists else '❌ MISSING'}")
            
            # Check for trigger
            result = connection.execute(text("""
                SELECT trigger_name FROM information_schema.triggers 
                WHERE event_object_table = 'users' AND trigger_name = 'trigger_validate_single_superadmin'
            """))
            trigger_exists = result.fetchone() is not None
            print(f"⚡ Trigger: {'✅ EXISTS' if trigger_exists else '❌ MISSING'}")
            
        elif dialect_name == 'sqlite':
            # Check for triggers
            result = connection.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type = 'trigger' AND name IN ('trigger_insert_single_superadmin', 'trigger_update_single_superadmin')
            """))
            triggers = [row[0] for row in result.fetchall()]
            
            insert_trigger = 'trigger_insert_single_superadmin' in triggers
            update_trigger = 'trigger_update_single_superadmin' in triggers
            
            print(f"⚡ INSERT trigger: {'✅ EXISTS' if insert_trigger else '❌ MISSING'}")
            print(f"⚡ UPDATE trigger: {'✅ EXISTS' if update_trigger else '❌ MISSING'}")
        
        return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage database-level superadmin constraints')
    parser.add_argument('action', choices=['apply', 'remove', 'check'], 
                       help='Action to perform')
    
    args = parser.parse_args()
    
    try:
        if args.action == 'apply':
            apply_database_constraints()
        elif args.action == 'remove':
            remove_database_constraints()
        elif args.action == 'check':
            check_constraints_status()
        
        print("✨ Done!")
        
    except Exception as e:
        print(f"💥 Error: {e}")
        sys.exit(1)
