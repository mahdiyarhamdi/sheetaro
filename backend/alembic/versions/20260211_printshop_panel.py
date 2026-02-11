"""Add PRINTED order status and settlements table for print shop panel.

Revision ID: a1b2c3d4e5f6
Revises: 20260202_1010_add_full_payment_type
Create Date: 2026-02-11
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '20260202_1010_add_full_payment_type'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add PRINTED to orderstatus enum
    op.execute("ALTER TYPE orderstatus ADD VALUE IF NOT EXISTS 'PRINTED' AFTER 'PRINTING'")

    # Create settlementstatus enum
    op.execute("CREATE TYPE settlementstatus AS ENUM ('PENDING', 'PAID')")

    # Create settlements table
    op.create_table(
        'settlements',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('printshop_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),
        sa.Column('total_orders', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_revenue', sa.Numeric(12, 0), nullable=False, server_default='0'),
        sa.Column('platform_commission', sa.Numeric(12, 0), nullable=False, server_default='0'),
        sa.Column('net_amount', sa.Numeric(12, 0), nullable=False, server_default='0'),
        sa.Column('status', sa.Enum('PENDING', 'PAID', name='settlementstatus', create_type=False), nullable=False, server_default='PENDING'),
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('settlements')
    op.execute("DROP TYPE IF EXISTS settlementstatus")
    # Note: Cannot remove enum value from PostgreSQL in downgrade
