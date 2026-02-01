"""Add payment-related order statuses to OrderStatus enum

Revision ID: add_payment_order_statuses
Revises: make_product_id_nullable
Create Date: 2026-02-01
"""
from alembic import op

revision = 'add_payment_order_statuses'
down_revision = 'make_product_id_nullable'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new enum values to orderstatus
    # PostgreSQL requires ALTER TYPE to add new enum values
    op.execute("ALTER TYPE orderstatus ADD VALUE IF NOT EXISTS 'PENDING_PAYMENT'")
    op.execute("ALTER TYPE orderstatus ADD VALUE IF NOT EXISTS 'PAYMENT_UPLOADED'")
    op.execute("ALTER TYPE orderstatus ADD VALUE IF NOT EXISTS 'PAYMENT_APPROVED'")
    op.execute("ALTER TYPE orderstatus ADD VALUE IF NOT EXISTS 'PAYMENT_REJECTED'")


def downgrade() -> None:
    # PostgreSQL doesn't support removing enum values easily
    # To truly downgrade, would need to:
    # 1. Create new enum type without the values
    # 2. Update all tables to use new type
    # 3. Drop old type
    # For now, we leave the values in place as they don't cause issues
    pass
