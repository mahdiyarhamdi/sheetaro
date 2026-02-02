"""add_full_payment_type

Revision ID: add_full_payment_type
Revises: add_payment_order_statuses
Create Date: 2026-02-02 10:10:00.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = 'add_full_payment_type'
down_revision = 'add_payment_order_statuses'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add FULL value to paymenttype enum
    op.execute("ALTER TYPE paymenttype ADD VALUE IF NOT EXISTS 'FULL'")


def downgrade() -> None:
    # Note: PostgreSQL doesn't support removing enum values
    # The FULL value will remain in the enum
    pass
