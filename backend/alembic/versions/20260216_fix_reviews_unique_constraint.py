"""Fix reviews unique constraint to allow separate printshop and designer reviews.

Drop old uq_reviews_order_id (order_id only) that prevents having both
PRINTSHOP and DESIGNER reviews for the same order. The correct constraint
uq_review_order_type (order_id, review_type) already exists.

Revision ID: e5f6g7h8i9j0
Revises: d4e5f6g7h8i9
Create Date: 2026-02-16
"""
from alembic import op

revision = 'e5f6g7h8i9j0'
down_revision = 'd4e5f6g7h8i9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE reviews DROP CONSTRAINT IF EXISTS uq_reviews_order_id
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE reviews ADD CONSTRAINT uq_reviews_order_id UNIQUE (order_id)
    """)
