"""Add card-to-card payment fields and system_settings table.

Revision ID: 20251214_c2c
Revises: 20251213_full
Create Date: 2025-12-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20251214_c2c'
down_revision: Union[str, None] = '20251213_full'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add AWAITING_APPROVAL to paymentstatus enum
    op.execute("ALTER TYPE paymentstatus ADD VALUE IF NOT EXISTS 'AWAITING_APPROVAL' AFTER 'PENDING'")
    
    # Add new columns to payments table for card-to-card payment
    op.add_column('payments', sa.Column('receipt_image_url', sa.String(500), nullable=True))
    op.add_column('payments', sa.Column('rejection_reason', sa.String(500), nullable=True))
    op.add_column('payments', sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('payments', sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True))
    
    # Add foreign key constraint for approved_by
    op.create_foreign_key(
        'fk_payments_approved_by_users',
        'payments',
        'users',
        ['approved_by'],
        ['id']
    )
    
    # Create system_settings table
    op.create_table(
        'system_settings',
        sa.Column('key', sa.String(100), primary_key=True),
        sa.Column('value', sa.String(1000), nullable=False),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_system_settings_key', 'system_settings', ['key'])


def downgrade() -> None:
    # Drop system_settings table
    op.drop_index('ix_system_settings_key', table_name='system_settings')
    op.drop_table('system_settings')
    
    # Drop foreign key constraint
    op.drop_constraint('fk_payments_approved_by_users', 'payments', type_='foreignkey')
    
    # Remove columns from payments table
    op.drop_column('payments', 'approved_at')
    op.drop_column('payments', 'approved_by')
    op.drop_column('payments', 'rejection_reason')
    op.drop_column('payments', 'receipt_image_url')
    
    # Note: Cannot remove enum value in PostgreSQL, would need to recreate the type
    # For full rollback, manually run:
    # ALTER TYPE paymentstatus RENAME TO paymentstatus_old;
    # CREATE TYPE paymentstatus AS ENUM ('PENDING', 'SUCCESS', 'FAILED');
    # ... migrate data ...
    # DROP TYPE paymentstatus_old;

