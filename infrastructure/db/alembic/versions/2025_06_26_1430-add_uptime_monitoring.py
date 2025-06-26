"""add uptime monitoring tables

Revision ID: add_uptime_monitoring
Revises: 47cf2e40fa2f
Create Date: 2025-06-26 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from infrastructure.db.models.user_model import GUID

# revision identifiers, used by Alembic.
revision: str = 'add_uptime_monitoring'
down_revision: Union[str, None] = '47cf2e40fa2f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create uptime_events table
    op.create_table('uptime_events',
        sa.Column('id', GUID(), nullable=False),
        sa.Column('event_type', sa.String(length=20), nullable=False),
        sa.Column('service_name', sa.String(length=100), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('duration_seconds', sa.Float(), nullable=True),
        sa.Column('reason', sa.String(length=500), nullable=True),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('auto_detected', sa.Boolean(), nullable=False),
        sa.Column('meta_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for uptime_events
    with op.batch_alter_table('uptime_events', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_uptime_events_event_type'), ['event_type'], unique=False)
        batch_op.create_index(batch_op.f('ix_uptime_events_service_name'), ['service_name'], unique=False)
        batch_op.create_index(batch_op.f('ix_uptime_events_timestamp'), ['timestamp'], unique=False)
    
    # Create uptime_metrics table
    op.create_table('uptime_metrics',
        sa.Column('id', GUID(), nullable=False),
        sa.Column('service_name', sa.String(length=100), nullable=False),
        sa.Column('period_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('period_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('uptime_percentage', sa.Float(), nullable=False),
        sa.Column('total_downtime_seconds', sa.Float(), nullable=False),
        sa.Column('downtime_incidents', sa.Integer(), nullable=False),
        sa.Column('calculated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('meta_data', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for uptime_metrics
    with op.batch_alter_table('uptime_metrics', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_uptime_metrics_service_name'), ['service_name'], unique=False)
        batch_op.create_index(batch_op.f('ix_uptime_metrics_period_start'), ['period_start'], unique=False)
        batch_op.create_index(batch_op.f('ix_uptime_metrics_period_end'), ['period_end'], unique=False)


def downgrade() -> None:
    # Drop uptime_metrics table
    with op.batch_alter_table('uptime_metrics', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_uptime_metrics_period_end'))
        batch_op.drop_index(batch_op.f('ix_uptime_metrics_period_start'))
        batch_op.drop_index(batch_op.f('ix_uptime_metrics_service_name'))
    
    op.drop_table('uptime_metrics')
    
    # Drop uptime_events table
    with op.batch_alter_table('uptime_events', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_uptime_events_timestamp'))
        batch_op.drop_index(batch_op.f('ix_uptime_events_service_name'))
        batch_op.drop_index(batch_op.f('ix_uptime_events_event_type'))
    
    op.drop_table('uptime_events')
