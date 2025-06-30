"""Add database-level superadmin constraint

Revision ID: add_superadmin_constraint
Revises: b112295d15e8
Create Date: 2025-06-29 22:20:23.562942

"""
from alembic import op
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = 'add_superadmin_constraint'
down_revision = 'b112295d15e8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add database-level constraints to ensure only one superadmin exists."""
    
    # Get database connection
    connection = op.get_bind()
    
    # Check if we're using PostgreSQL or SQLite
    if connection.dialect.name == 'postgresql':
        # PostgreSQL approach: Use partial unique index + function-based constraint
        
        # 1. Create a partial unique index - only one record with role='super_admin' allowed
        op.execute(text("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_users_single_superadmin 
            ON users (role) 
            WHERE role = 'super_admin'
        """))
        
        # 2. Create a function to validate superadmin count
        op.execute(text("""
            CREATE OR REPLACE FUNCTION validate_single_superadmin()
            RETURNS TRIGGER AS $$
            BEGIN
                -- If we're inserting/updating to super_admin role
                IF NEW.role = 'super_admin' THEN
                    -- Check if another super_admin already exists (excluding current record if updating)
                    IF EXISTS (
                        SELECT 1 FROM users 
                        WHERE role = 'super_admin' 
                        AND (TG_OP = 'INSERT' OR id != NEW.id)
                    ) THEN
                        RAISE EXCEPTION 'Only one superadmin is allowed in the system. Current operation would violate this constraint.';
                    END IF;
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """))
          # 3. Create trigger to enforce the constraint
        op.execute(text("""
            DROP TRIGGER IF EXISTS trigger_validate_single_superadmin ON users;
            CREATE TRIGGER trigger_validate_single_superadmin
                BEFORE INSERT OR UPDATE ON users
                FOR EACH ROW
                EXECUTE FUNCTION validate_single_superadmin();
        """))
        
        # Note: We don't add a CHECK constraint because PostgreSQL doesn't support subqueries in CHECK constraints.
        # The partial unique index + trigger function already provides comprehensive enforcement.
        
    else:
        # SQLite approach: Use triggers (SQLite doesn't support partial unique indexes)
        
        # 1. Create trigger for INSERT
        op.execute(text("""
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
        
        # 2. Create trigger for UPDATE
        op.execute(text("""
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
    
    print("✅ Database-level superadmin constraints added successfully!")


def downgrade() -> None:
    """Remove database-level superadmin constraints."""
    
    # Get database connection
    connection = op.get_bind()
    
    if connection.dialect.name == 'postgresql':
        # Remove PostgreSQL constraints
        
        # Remove trigger
        op.execute(text("DROP TRIGGER IF EXISTS trigger_validate_single_superadmin ON users;"))
        
        # Remove function
        op.execute(text("DROP FUNCTION IF EXISTS validate_single_superadmin();"))
          # Remove unique index
        op.execute(text("DROP INDEX IF EXISTS idx_users_single_superadmin;"))
        
        # Note: No check constraint to remove since we don't create one in upgrade()
        
    else:
        # Remove SQLite triggers
        op.execute(text("DROP TRIGGER IF EXISTS trigger_insert_single_superadmin;"))
        op.execute(text("DROP TRIGGER IF EXISTS trigger_update_single_superadmin;"))
    
    print("✅ Database-level superadmin constraints removed successfully!")
