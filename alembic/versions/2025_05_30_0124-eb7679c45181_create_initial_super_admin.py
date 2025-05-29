"""create initial super admin

Revision ID: eb7679c45181
Revises: 31b83c508171
Create Date: 2025-05-30 01:24:25.400330

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import table, column
import uuid
from datetime import datetime, timezone


# revision identifiers, used by Alembic.
revision: str = 'eb7679c45181'
down_revision: Union[str, None] = '31b83c508171'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create a table reference for the users table
    users_table = table(
        'users',
        column('id'),
        column('email'),
        column('username'),
        column('first_name'),
        column('last_name'),
        column('password_hash'),
        column('role'),
        column('status'),
        column('is_email_verified'),
        column('created_at'),
        column('updated_at')
    )
    
    # Insert Super Admin
    # Note: You'll need to hash the password beforehand
    op.bulk_insert(users_table, [
        {
            'id': str(uuid.uuid4()),
            'email': 'admin@salesoptimizer.com',
            'username': 'superadmin',
            'first_name': 'Super',
            'last_name': 'Admin',
            'password_hash': '$2b$12$hashed_password_here',  # Use bcrypt to hash
            'role': 'super_admin',
            'status': 'active',
            'is_email_verified': True,
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc)
        }
    ])

def downgrade() -> None:
    op.execute("DELETE FROM users WHERE email = 'admin@salesoptimizer.com'")