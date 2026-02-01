"""Make product_id nullable in orders table

Revision ID: make_product_id_nullable
Revises: add_price_type
Create Date: 2026-02-01
"""
from alembic import op

revision = 'make_product_id_nullable'
down_revision = 'add_price_type'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('orders', 'product_id', nullable=True)


def downgrade() -> None:
    op.alter_column('orders', 'product_id', nullable=False)
