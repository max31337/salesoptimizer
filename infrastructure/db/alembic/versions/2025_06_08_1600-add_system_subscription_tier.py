"""Add system subscription tier

Revision ID: add_system_subscription_tier
Revises: c0c3f55f76d8
Create Date: 2025-06-08 16:00:00.000000

"""

# revision identifiers
revision = 'add_system_subscription_tier'
down_revision = 'c0c3f55f76d8'
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Add system subscription tier."""
    # No schema changes needed - just documenting that 'system' is now valid
    # The subscription_tier field is already a VARCHAR(50) that can accept any string
    pass

def downgrade() -> None:
    """Remove system subscription tier."""
    # No schema changes to revert
    pass
